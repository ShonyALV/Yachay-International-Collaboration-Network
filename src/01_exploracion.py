"""Fase 1 — Exploración del export de Scopus de Yachay Tech.

No modifica ningún dato. Genera un reporte en consola y en output/reporte_exploracion.md.
Ejecutar desde cualquier carpeta:  .venv/Scripts/python.exe src/01_exploracion.py
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date

import pandas as pd
import pycountry_convert as pcc

from utils import (DIR_OUTPUT, detectar_csv, leer_scopus, limpiar_html, normalizar_nombre,
                   normalizar_titulo, pais_ultimo_segmento, paises_en_segmentos, separar)

COLS_RELEVANTES = ["Authors", "Author full names", "Author(s) ID", "Authors with affiliations",
                   "Affiliations", "Year", "EID", "DOI", "Title", "Document Type"]
CONTINENTES = {"AF": "Africa", "AS": "Asia", "EU": "Europe", "NA": "North America",
               "SA": "South America", "OC": "Oceania", "AN": "Antarctica"}
ANIO_ACTUAL = date.today().year

lineas: list[str] = []


def md(texto: str = "") -> None:
    """Agrega al reporte y lo imprime en consola."""
    lineas.append(texto)
    print(texto)


def tabla(df: pd.DataFrame, max_filas: int | None = None) -> None:
    d = df if max_filas is None else df.head(max_filas)
    md(d.to_markdown(index=False) if len(d) else "_(sin casos)_")
    if max_filas is not None and len(df) > max_filas:
        md(f"\n_… {len(df) - max_filas} filas más no mostradas._")
    md()


def continente(p) -> str:
    try:
        return CONTINENTES[pcc.country_alpha2_to_continent_code(p.alpha_2)]
    except Exception:
        return "¿?"


def corto(t: str, n: int = 90) -> str:
    t = str(t).replace("|", "/").replace("\n", " ")
    return t if len(t) <= n else t[: n - 1] + "…"


# ---------------------------------------------------------------------------
ruta = detectar_csv()
df = leer_scopus(ruta)
df["Year_int"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

md("# Reporte de exploración — Scopus Yachay Tech (AF-ID 60105012)")
md()
md(f"- Archivo: `data/raw/{ruta.name}`")
md(f"- Fecha de generación: {date.today().isoformat()}")
md()

# 1. Estructura ---------------------------------------------------------------
md("## 1. Estructura general")
md()
md(f"- Filas: **{len(df)}**, columnas: **{df.shape[1] - 1}**")
md(f"- Columnas: {', '.join(f'`{c}`' for c in df.columns if c != 'Year_int')}")
md()
info = pd.DataFrame({
    "columna": COLS_RELEVANTES,
    "tipo (lectura como texto)": [str(df[c].dtype) for c in COLS_RELEVANTES],
    "nulos": [int(df[c].isna().sum()) for c in COLS_RELEVANTES],
    "% nulos": [round(100 * df[c].isna().mean(), 2) for c in COLS_RELEVANTES],
    "valores únicos": [int(df[c].nunique()) for c in COLS_RELEVANTES],
})
tabla(info)

# 2. Años ----------------------------------------------------------------------
md("## 2. Documentos por año")
md()
por_anio = df.groupby("Year_int").size().rename("documentos").reset_index()
med = por_anio["documentos"].median()
notas = []
for _, r in por_anio.iterrows():
    a, n = int(r["Year_int"]), int(r["documentos"])
    if a > ANIO_ACTUAL:
        notas.append("FUTURO (publicación con fecha posterior a hoy)")
    elif a == ANIO_ACTUAL:
        notas.append("AÑO EN CURSO (incompleto)")
    elif n < 0.25 * med:
        notas.append("bajo (año de arranque)")
    else:
        notas.append("")
por_anio["nota"] = notas
tabla(por_anio)

md("### Etapa de publicación por año (años atípicos)")
md()
etapa = pd.crosstab(df["Year_int"], df["Publication Stage"]).reset_index()
tabla(etapa)

md("### Tipos de documento")
md()
tabla(df["Document Type"].value_counts().rename_axis("tipo").reset_index(name="documentos"))

futuros = df[df["Year_int"] > ANIO_ACTUAL]
if len(futuros):
    md(f"### Documentos con año > {ANIO_ACTUAL}")
    md()
    tabla(futuros[["EID", "Year", "Document Type", "Publication Stage", "Source title"]]
          .assign(**{"Source title": lambda d: d["Source title"].map(corto)}))

# 3. Duplicados de documentos ---------------------------------------------------
md("## 3. Documentos duplicados")
md()
dup_eid = df[df["EID"].duplicated(keep=False)]
md(f"- Duplicados por `EID`: **{df['EID'].duplicated().sum()}**")
con_doi = df[df["DOI"].notna()].copy()
con_doi["doi_norm"] = con_doi["DOI"].str.lower().str.strip()
dup_doi = con_doi[con_doi["doi_norm"].duplicated(keep=False)].sort_values("doi_norm")
md(f"- Duplicados por `DOI` (sin contar nulos): **{con_doi['doi_norm'].duplicated().sum()}** "
   f"({len(dup_doi)} filas implicadas)")
df["titulo_norm"] = df["Title"].map(normalizar_titulo)
dup_tit = df[df["titulo_norm"].duplicated(keep=False)].sort_values("titulo_norm")
dup_tit_anio = df[df[["titulo_norm", "Year"]].duplicated(keep=False)]
md(f"- Duplicados por título normalizado: **{df['titulo_norm'].duplicated().sum()}** "
   f"({len(dup_tit)} filas); por título normalizado + año: "
   f"**{df[['titulo_norm', 'Year']].duplicated().sum()}**")
md()
if len(dup_doi):
    md("### Casos por DOI")
    md()
    tabla(dup_doi[["DOI", "EID", "Year", "Document Type", "Title"]]
          .assign(Title=lambda d: d["Title"].map(corto)))
if len(dup_tit):
    md("### Casos por título normalizado")
    md()
    tabla(dup_tit[["EID", "Year", "Document Type", "DOI", "Title"]]
          .assign(Title=lambda d: d["Title"].map(lambda t: corto(t, 70))), 40)

# 4. Autores -------------------------------------------------------------------
md("## 4. Autores")
md()
patron = re.compile(r"^(.*?)\s*\((\d+)\)$")
id_a_nombres: dict[str, Counter] = defaultdict(Counter)
nombre_a_ids: dict[str, Counter] = defaultdict(Counter)
nombre_mostrar: dict[str, str] = {}
desalineados = []
sin_patron = 0
for _, r in df.iterrows():
    ids = separar(r["Author(s) ID"])
    full = separar(r["Author full names"])
    cortos = separar(r["Authors"])
    awa = separar(r["Authors with affiliations"])
    if not (len(ids) == len(full) == len(cortos)) or len(awa) != len(ids):
        desalineados.append((r["EID"], len(ids), len(full), len(cortos), len(awa)))
    for f in full:
        m = patron.match(f)
        if not m:
            sin_patron += 1
            continue
        nombre, aid = m.group(1).strip(), m.group(2)
        id_a_nombres[aid][nombre] += 1
        k = normalizar_nombre(nombre)
        nombre_a_ids[k][aid] += 1
        nombre_mostrar.setdefault(k, nombre)

n_ids = len(id_a_nombres)
total_firmas = sum(sum(c.values()) for c in id_a_nombres.values())
md(f"- Firmas autor–documento: **{total_firmas}**; `Author(s) ID` únicos: **{n_ids}**")
md(f"- Entradas de `Author full names` sin el formato `Nombre (ID)`: **{sin_patron}**")
md(f"- Documentos donde #IDs, #nombres completos, #nombres cortos y #entradas de "
   f"`Authors with affiliations` no coinciden: **{len(desalineados)}**")
md()

varios_nombres = [(aid, c) for aid, c in id_a_nombres.items() if len(c) > 1]
md(f"### 4.1 IDs con varias variantes de nombre: {len(varios_nombres)}")
md()
varios_nombres.sort(key=lambda x: -sum(x[1].values()))
tabla(pd.DataFrame([{
    "Author ID": aid, "documentos": sum(c.values()), "n variantes": len(c),
    "variantes (frecuencia)": " / ".join(f"{n} ({k})" for n, k in c.most_common()),
} for aid, c in varios_nombres]), 20)

varios_ids = [(k, c) for k, c in nombre_a_ids.items() if len(c) > 1]
md(f"### 4.2 Nombres (normalizados) con varios IDs — posibles perfiles duplicados: "
   f"{len(varios_ids)}")
md()
varios_ids.sort(key=lambda x: -sum(x[1].values()))
tabla(pd.DataFrame([{
    "nombre": nombre_mostrar[k], "documentos": sum(c.values()), "n IDs": len(c),
    "IDs (documentos)": ", ".join(f"{i} ({n})" for i, n in c.most_common()),
} for k, c in varios_ids]), 25)

# Iniciales + apellido: misma persona con nombre corto/largo y distinto ID
md("_Nota: un mismo nombre con varios IDs puede ser un perfil duplicado de Scopus o "
   "dos personas homónimas; no se unifican sin evidencia (p. ej., misma afiliación)._")
md()

# 5. Formato de afiliaciones -----------------------------------------------------
md("## 5. Formato de las afiliaciones")
md()
crudo_con_entidad = df["Affiliations"].str.contains(r"&#x|&amp;|& amp;", regex=True).sum()
md(f"- `Affiliations` separa instituciones con `;` y los niveles de cada institución con `,`.")
md(f"- Documentos con entidades HTML (`&#x..;`, `& amp;`) que rompen la separación por `;` si "
   f"no se decodifican antes: **{crudo_con_entidad}**")

filas_af = []  # (EID, afiliación, último segmento, país resuelto)
for _, r in df.iterrows():
    for af in separar(r["Affiliations"]):
        ult, p = pais_ultimo_segmento(af)
        filas_af.append((r["EID"], r["Year_int"], af, ult, p))
total_af = len(filas_af)
ok_ult = sum(1 for f in filas_af if f[4] is not None)
md(f"- Afiliaciones (instancias documento–institución): **{total_af}**; el último segmento es un "
   f"país reconocido en **{ok_ult}** (**{100 * ok_ult / total_af:.2f} %**).")
afs_por_doc = df["Affiliations"].map(lambda x: len(separar(x)))
md(f"- Afiliaciones por documento: mediana {afs_por_doc.median():.0f}, máx. {afs_por_doc.max()}")
md()

md("### 5.1 Afiliaciones cuyo último segmento NO es un país")
md()
no_pais = [f for f in filas_af if f[4] is None]
recuperables = []
for eid, anio, af, ult, _ in no_pais:
    otros = paises_en_segmentos(af)
    yach = bool(re.search(r"yachay|urcuqu", af, re.I))
    recuperables.append({
        "EID": eid, "último segmento": corto(ult, 40),
        "país en otro segmento": ", ".join(p.name for p in otros) or "—",
        "menciona Yachay/Urcuquí": "sí" if yach else "no",
        "afiliación": corto(af, 80),
    })
tabla(pd.DataFrame(recuperables))

md("### 5.2 Alineación de `Authors with affiliations` con `Author(s) ID`")
md()
ok_orden, total_ent, multi_pais = 0, 0, 0
for _, r in df.iterrows():
    cortos = separar(r["Authors"])
    awa = separar(r["Authors with affiliations"])
    for nom, ent in zip(cortos, awa):
        total_ent += 1
        if ent.startswith(nom):
            ok_orden += 1
        if len(paises_en_segmentos(ent)) > 1:
            multi_pais += 1
md(f"- Entradas de `Authors with affiliations` que empiezan con el nombre corto del autor en la "
   f"misma posición de `Authors`: **{ok_orden} / {total_ent}** "
   f"({100 * ok_orden / max(total_ent, 1):.2f} %) → el orden está alineado con `Author(s) ID`.")
md(f"- Formato de cada entrada: `Apellido I., Inst1 nivel, …, País1, Inst2 …, País2`. Un autor con "
   f"varias afiliaciones las tiene **unidas por comas** dentro de la misma entrada, así que el "
   f"último segmento NO basta: hay que buscar países en todos los segmentos.")
md(f"- Entradas autor–documento con más de un país: **{multi_pais}**")
md()
if desalineados:
    md("Documentos con conteos desalineados (EID, #IDs, #nombres completos, #nombres cortos, "
       "#entradas con afiliación):")
    md()
    tabla(pd.DataFrame(desalineados, columns=["EID", "IDs", "full names", "Authors", "AwA"]), 20)

# Comparar países por documento: Affiliations (último segmento) vs AwA (todos los segmentos)
md("### 5.3 Consistencia de países entre `Affiliations` y `Authors with affiliations`")
md()
diffs = []
doc_paises: dict[str, set] = {}
for _, r in df.iterrows():
    p_af = {p.alpha_3 for a in separar(r["Affiliations"])
            if (p := pais_ultimo_segmento(a)[1]) is not None}
    p_awa = {p.alpha_3 for ent in separar(r["Authors with affiliations"])
             for p in paises_en_segmentos(ent)}
    doc_paises[r["EID"]] = p_af
    if p_af != p_awa:
        diffs.append({"EID": r["EID"], "solo en Affiliations": ", ".join(sorted(p_af - p_awa)) or "—",
                      "solo en AwA": ", ".join(sorted(p_awa - p_af)) or "—"})
md(f"- Documentos cuyo conjunto de países difiere entre ambas columnas: **{len(diffs)}**")
md("  (los países 'solo en AwA' pueden ser falsos positivos, p. ej. un segmento 'Georgia' que es "
   "un estado de EE. UU., o recuperaciones válidas de afiliaciones sin país).")
md()
tabla(pd.DataFrame(diffs), 30)

# 6. Países ----------------------------------------------------------------------
md("## 6. Países detectados")
md()
cnt_af, cnt_doc, texto_por_iso = Counter(), Counter(), defaultdict(Counter)
obj_por_iso = {}
for eid, anio, af, ult, p in filas_af:
    if p is not None:
        cnt_af[p.alpha_3] += 1
        texto_por_iso[p.alpha_3][ult] += 1
        obj_por_iso[p.alpha_3] = p
for eid, ps in doc_paises.items():
    for iso in ps:
        cnt_doc[iso] += 1
filas_p = []
# Orden determinista: documentos desc. y, en empate, código ISO (los sets no tienen orden fijo).
for iso, n in sorted(cnt_doc.items(), key=lambda kv: (-kv[1], kv[0])):
    p = obj_por_iso[iso]
    textos = texto_por_iso[iso]
    filas_p.append({
        "texto en Scopus": " / ".join(textos),
        "nombre ISO": p.name, "ISO3": iso, "ISO num": p.numeric,
        "continente": continente(p), "documentos": n, "afiliaciones": cnt_af[iso],
        "revisar": "sí" if (len(textos) > 1 or p.name not in textos
                           or continente(p) == "¿?") else "",
    })
tabla_p = pd.DataFrame(filas_p)
md(f"- Países únicos reconocidos: **{len(tabla_p)}** (incluido Ecuador); socios: "
   f"**{len(tabla_p) - 1}**")
md(f"- Continentes presentes: {', '.join(sorted(tabla_p['continente'].unique()))}")
md()
tabla(tabla_p)
md("Variantes sospechosas (columna *revisar* = sí): el texto de Scopus difiere del nombre ISO, "
   "o es un territorio (Hong Kong, Puerto Rico, Guayana Francesa, Taiwán) que puede no existir "
   "como polígono propio en `world-atlas` 110m.")
md()

# 7. Yachay Tech -----------------------------------------------------------------
md("## 7. Variantes del nombre de Yachay Tech")
md()
var_y = Counter()
for _, r in df.iterrows():
    for af in separar(r["Affiliations"]):
        for seg in af.split(","):
            if re.search(r"yachay", seg, re.I):
                var_y[seg.strip()] += 1
tabla(pd.DataFrame(var_y.most_common(), columns=["segmento con 'Yachay'", "frecuencia"]), 40)
sin_y = df[~df["Affiliations"].fillna("").str.contains("yachay", case=False)]
md(f"- Documentos cuyo campo `Affiliations` no menciona 'Yachay': **{len(sin_y)}**")
md()
if len(sin_y):
    tabla(sin_y[["EID", "Year", "Title", "Affiliations"]]
          .assign(Title=lambda d: d["Title"].map(corto),
                  Affiliations=lambda d: d["Affiliations"].map(lambda t: corto(t, 120))))

# 8. Sin país / sin Ecuador ------------------------------------------------------
md("## 8. Documentos sin país identificable y sin Ecuador")
md()
sin_pais = [e for e, ps in doc_paises.items() if not ps]
md(f"- Documentos sin ningún país identificable (regla del último segmento): **{len(sin_pais)}**")
md()
if sin_pais:
    tabla(df[df["EID"].isin(sin_pais)][["EID", "Year", "Affiliations"]]
          .assign(Affiliations=lambda d: d["Affiliations"].map(lambda t: corto(t, 140))))
sin_ecu = [e for e, ps in doc_paises.items() if "ECU" not in ps]
md(f"- Documentos donde Ecuador no aparece como país: **{len(sin_ecu)}**")
md()
tabla(df[df["EID"].isin(sin_ecu)][["EID", "Year", "Title", "Affiliations"]]
      .assign(Title=lambda d: d["Title"].map(lambda t: corto(t, 60)),
              Affiliations=lambda d: d["Affiliations"].map(lambda t: corto(t, 120))))

# 9. Vista previa de la pregunta ---------------------------------------------------
md("## 9. Vista previa (sin limpiar) de la colaboración internacional por año")
md()
prev = []
for a, g in df.groupby("Year_int"):
    ps = [doc_paises[e] for e in g["EID"]]
    socios = set().union(*ps) - {"ECU"}
    intl = sum(1 for s in ps if s - {"ECU"})
    conts = {continente(obj_por_iso[i]) for i in socios}
    prev.append({"año": int(a), "documentos": len(g), "docs internacionales": intl,
                 "% internacional": round(100 * intl / len(g), 1),
                 "países socios": len(socios), "continentes socios": len(conts)})
tabla(pd.DataFrame(prev))

# Guardar ------------------------------------------------------------------------------
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)
salida = DIR_OUTPUT / "reporte_exploracion.md"
salida.write_text("\n".join(lineas), encoding="utf-8")
print(f"\n[OK] Reporte guardado en {salida.relative_to(salida.parents[1])}")
