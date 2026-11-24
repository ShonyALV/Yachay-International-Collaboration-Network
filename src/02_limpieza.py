"""Fase 2 — Limpieza del export de Scopus según las reglas aprobadas (R1–R11).

Entradas : data/raw/*.csv (nunca se modifica)
Salidas  : data/processed/
    documentos_limpios.csv      una fila por documento
    documento_pais.csv          relación documento–país (pares únicos)
    autor_documento_pais.csv    relación autor (ID canónico)–documento–país
    mapeo_paises.csv            tabla de normalización de países usada
    mapeo_autores.csv           fusiones explícitas de perfiles de autor (R9)
    documentos_excluidos.csv    documentos eliminados y motivo
    afiliaciones_descartadas.csv afiliaciones sin país recuperable (R6)
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

import pandas as pd
import pycountry

from utils import (ANIO_MAX, ANIO_MIN, ANIO_PARCIAL, DIR_PROCESSED, RE_YACHAY, TIPOS_EXCLUIDOS,
                   UMBRAL_MEGA, continente, leer_scopus, limpiar_html, nombre_mostrar,
                   normalizar_nombre, normalizar_titulo, pais_de_afiliacion, pais_soberano,
                   paises_en_segmentos, quitar_email, separar)

ECU = "ECU"
DIR_PROCESSED.mkdir(parents=True, exist_ok=True)


def titulo(t: str) -> None:
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


excluidos: list[dict] = []


def excluir(df: pd.DataFrame, mascara: pd.Series, motivo: str) -> pd.DataFrame:
    for _, r in df[mascara].iterrows():
        excluidos.append({"EID": r["EID"], "Year": r["Year"], "Title": r["Title"], "motivo": motivo})
    print(f"  - {motivo}: {int(mascara.sum())} documentos excluidos")
    return df[~mascara].copy()


# ---------------------------------------------------------------------------
titulo("1. Lectura")
df = leer_scopus()
n0 = len(df)
print(f"  Filas leídas: {n0}")

# R4: decodificar HTML y quitar correos pegados ANTES de separar por ';'
for col in ["Affiliations", "Authors with affiliations"]:
    df[col] = df[col].fillna("").map(limpiar_html).map(quitar_email)
df["Year_int"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

# ---------------------------------------------------------------------------
titulo("2. Filtros de años y tipos (R1, R2)")
df = excluir(df, df["Year_int"].isna(), "Año no numérico")
df = excluir(df, df["Year_int"] > ANIO_MAX, f"Año > {ANIO_MAX} (publicación con fecha futura)")
df = excluir(df, df["Year_int"] < ANIO_MIN, f"Año < {ANIO_MIN}")
df = excluir(df, df["Document Type"].isin(TIPOS_EXCLUIDOS),
             f"Tipo de documento excluido ({', '.join(sorted(TIPOS_EXCLUIDOS))})")
df = excluir(df, df["Affiliations"].str.strip() == "", "Documento sin afiliaciones")

# ---------------------------------------------------------------------------
titulo("3. Duplicados (R3): EID → DOI → título normalizado + año")
df["n_afiliaciones"] = df["Affiliations"].map(lambda a: len(separar(a)))
# Se conserva el registro con más afiliaciones; desempate estable por EID.
df = df.sort_values(["n_afiliaciones", "EID"], ascending=[False, True]).reset_index(drop=True)

df = excluir(df, df["EID"].duplicated(), "Duplicado por EID")
doi = df["DOI"].fillna("").str.lower().str.strip()
df = excluir(df, (doi != "") & doi.duplicated(), "Duplicado por DOI")
df["titulo_norm"] = df["Title"].map(normalizar_titulo)
# Solo títulos con >= 4 palabras: evita fusionar títulos genéricos ("Preface", "Editorial").
largo = df["titulo_norm"].str.split().str.len() >= 4
df = excluir(df, largo & df[["titulo_norm", "Year"]].duplicated(), "Duplicado por título + año")
print(f"  Documentos tras filtros y deduplicación: {len(df)} (de {n0})")

# ---------------------------------------------------------------------------
titulo("4. Países por documento (R5, R6, R7, R10)")
mapeo_rows: dict[tuple[str, str], dict] = {}
descartadas: list[dict] = []
doc_paises: dict[str, set[str]] = {}
ecu_agregado: set[str] = set()
cont_reglas = Counter()
obj_pais: dict[str, object] = {}

for _, r in df.iterrows():
    eid, ps = r["EID"], set()
    for af in separar(r["Affiliations"]):
        p, texto, regla = pais_de_afiliacion(af)
        cont_reglas[regla] += 1
        if p is None:
            descartadas.append({"EID": eid, "Year": r["Year"], "afiliacion": af})
            continue
        ps.add(p.alpha_3)
        obj_pais[p.alpha_3] = p
        clave = (texto if regla != "yachay_sin_pais" else "(afiliación de Yachay sin país)", regla)
        fila = mapeo_rows.setdefault(clave, {
            "texto_scopus": clave[0], "regla": regla, "pais": nombre_mostrar(p),
            "nombre_iso": p.name, "iso3": p.alpha_3, "iso_num": p.numeric,
            "continente": continente(p), "afiliaciones": 0})
        fila["afiliaciones"] += 1
    if ECU not in ps:                     # R7
        ps.add(ECU)
        ecu_agregado.add(eid)
    doc_paises[eid] = ps
obj_pais[ECU] = pycountry.countries.get(alpha_3=ECU)

print(f"  Afiliaciones procesadas: {sum(cont_reglas.values())}")
for regla, n in cont_reglas.most_common():
    print(f"    · {regla:<16} {n}")
print(f"  Afiliaciones descartadas (sin país recuperable): {len(descartadas)}")
print(f"  Documentos a los que se agregó Ecuador (R7): {len(ecu_agregado)}")
sin_pais_real = [e for e, ps in doc_paises.items() if ps == {ECU} and e in ecu_agregado]
print(f"    de ellos, sin ningún otro país detectado: {len(sin_pais_real)}")

# ---------------------------------------------------------------------------
titulo("5. Autores (R8, R9)")
patron = re.compile(r"^(.*?)\s*\((\d+)\)$")
nombres_id: dict[str, Counter] = defaultdict(Counter)
firmas: list[dict] = []            # (id, eid, year, paises, segmentos)
realineados, sin_pais_autor = 0, 0

for _, r in df.iterrows():
    eid, anio = r["EID"], int(r["Year_int"])
    ids = separar(r["Author(s) ID"])
    full = separar(r["Author full names"])
    cortos = separar(r["Authors"])
    entradas = separar(r["Authors with affiliations"])
    # Alineación: si sobran entradas (un ';' dentro de una afiliación), se unen al autor anterior.
    if len(entradas) != len(ids) and len(cortos) == len(ids):
        realineados += 1
        nuevas, k = [], 0
        for ent in entradas:
            if k < len(cortos) and ent.startswith(cortos[k]):
                nuevas.append(ent)
                k += 1
            elif nuevas:
                nuevas[-1] += ", " + ent
        entradas = nuevas
    for i, aid in enumerate(ids):
        m = patron.match(full[i]) if i < len(full) else None
        nombre = m.group(1).strip() if m else (cortos[i] if i < len(cortos) else aid)
        nombres_id[aid][nombre] += 1
        ent = entradas[i] if i < len(entradas) else ""
        # R8: países en cualquier segmento, validados contra los países del documento.
        ps = {pais_soberano(p).alpha_3 for p in paises_en_segmentos(ent)} & doc_paises[eid]
        if not ps and RE_YACHAY.search(ent):
            ps = {ECU}
        if not ps:
            sin_pais_autor += 1
        segs = {normalizar_nombre(s) for s in ent.split(",")[1:]}
        firmas.append({"author_id": aid, "EID": eid, "Year": anio, "paises": ps, "segs": segs})

print(f"  Firmas autor–documento: {len(firmas)}; IDs únicos: {len(nombres_id)}")
print(f"  Documentos con entradas realineadas: {realineados}")
print(f"  Firmas sin país identificable (se omiten en autor_documento_pais): {sin_pais_autor}")


def canonico(c: Counter) -> str:
    """Variante más frecuente; empate → la más larga; luego orden alfabético."""
    return sorted(c.items(), key=lambda kv: (-kv[1], -len(kv[0]), kv[0]))[0][0]


def nombre_completo(nombre: str) -> bool:
    """True si el nombre de pila tiene al menos una palabra completa (no solo iniciales)."""
    if "," not in nombre:
        return False
    pila = nombre.split(",", 1)[1]
    return any(len(t) >= 2 and not t.endswith(".") for t in re.split(r"[\s\-]+", pila.strip()))


RE_INST = re.compile(r"univ|instit|escuela|school|facult|centro|center|centre|college|laborat|"
                     r"hospital|museo|museum|academ|fundaci|foundation|research|investigaci", re.I)
inst_id: dict[str, set[str]] = defaultdict(set)
docs_id: Counter = Counter()
for f in firmas:
    docs_id[f["author_id"]] += 1
    inst_id[f["author_id"]].update(s for s in f["segs"] if RE_INST.search(s) and len(s) > 8)

canon_nombre = {aid: canonico(c) for aid, c in nombres_id.items()}
por_nombre: dict[str, list[str]] = defaultdict(list)
for aid, c in nombres_id.items():
    for variante in c:
        if nombre_completo(variante):
            k = normalizar_nombre(variante)
            if aid not in por_nombre[k]:
                por_nombre[k].append(aid)

# Union-find sobre pares (mismo nombre completo + institución en común)
padre = {aid: aid for aid in nombres_id}


def raiz(a: str) -> str:
    while padre[a] != a:
        padre[a] = padre[padre[a]]
        a = padre[a]
    return a


evidencia: dict[tuple[str, str], tuple[str, str]] = {}
for k, ids_ in por_nombre.items():
    for i in range(len(ids_)):
        for j in range(i + 1, len(ids_)):
            a, b = ids_[i], ids_[j]
            comun = inst_id[a] & inst_id[b]
            if comun:
                ra, rb = raiz(a), raiz(b)
                if ra != rb:
                    padre[rb] = ra
                evidencia[(a, b)] = (k, sorted(comun, key=len)[-1])

grupos: dict[str, list[str]] = defaultdict(list)
for aid in nombres_id:
    grupos[raiz(aid)].append(aid)
id_canon: dict[str, str] = {}
mapeo_aut = []
for miembros in grupos.values():
    principal = sorted(miembros, key=lambda a: (-docs_id[a], a))[0]
    for a in miembros:
        id_canon[a] = principal
    if len(miembros) > 1:
        nombres_grupo = Counter()
        for a in miembros:
            nombres_grupo.update(nombres_id[a])
        nombre_final = canonico(nombres_grupo)
        for a in miembros:
            canon_nombre[a] = nombre_final
            if a == principal:
                continue
            ev = next((v for (x, y), v in evidencia.items() if a in (x, y)), ("", ""))
            mapeo_aut.append({
                "author_id_original": a, "author_id_canonico": principal,
                "nombre_original": canonico(nombres_id[a]), "nombre_canonico": nombre_final,
                "docs_original": docs_id[a], "docs_canonico": docs_id[principal],
                "motivo": "mismo nombre completo + institución en común",
                "institucion_comun": ev[1]})
print(f"  IDs con varias variantes de nombre (resueltas por ID): "
      f"{sum(1 for c in nombres_id.values() if len(c) > 1)}")
print(f"  Perfiles fusionados por R9: {len(mapeo_aut)} → IDs canónicos: {len(set(id_canon.values()))}")

# ---------------------------------------------------------------------------
titulo("6. Escritura de salidas")
anio_doc = dict(zip(df["EID"], df["Year_int"].astype(int)))
docs = pd.DataFrame({
    "EID": df["EID"], "Year": df["Year_int"].astype(int), "Title": df["Title"],
    "DOI": df["DOI"], "Document Type": df["Document Type"], "Source title": df["Source title"],
    "n_autores": df["Author(s) ID"].map(lambda a: len(separar(a))),
    "n_afiliaciones": df["n_afiliaciones"],
})
docs["paises_iso3"] = docs["EID"].map(lambda e: ";".join(sorted(doc_paises[e])))
docs["n_paises"] = docs["EID"].map(lambda e: len(doc_paises[e]))
docs["internacional"] = docs["n_paises"] > 1
docs["mega_colaboracion"] = docs["n_paises"] >= UMBRAL_MEGA
docs["ecuador_agregado"] = docs["EID"].isin(ecu_agregado)
docs["anio_parcial"] = docs["Year"] == ANIO_PARCIAL
docs = docs.sort_values(["Year", "EID"]).reset_index(drop=True)


def info_pais(iso: str) -> dict:
    p = obj_pais[iso]
    return {"pais": nombre_mostrar(p), "iso3": iso, "iso_num": p.numeric,
            "continente": continente(p)}


dp = pd.DataFrame([{"EID": e, "Year": anio_doc[e], **info_pais(i)}
                   for e, ps in doc_paises.items() for i in sorted(ps)])
dp = dp.sort_values(["Year", "EID", "iso3"]).reset_index(drop=True)

adp_rows = set()
for f in firmas:
    for iso in f["paises"]:
        adp_rows.add((id_canon[f["author_id"]], f["EID"], f["Year"], iso))
adp = pd.DataFrame(sorted(adp_rows), columns=["author_id", "EID", "Year", "iso3"])
adp.insert(1, "nombre_canonico", adp["author_id"].map(canon_nombre))
adp["pais"] = adp["iso3"].map(lambda i: info_pais(i)["pais"])

mp = pd.DataFrame(mapeo_rows.values()).sort_values(["iso3", "texto_scopus"])
ma = pd.DataFrame(mapeo_aut, columns=["author_id_original", "author_id_canonico", "nombre_original",
                                      "nombre_canonico", "docs_original", "docs_canonico",
                                      "motivo", "institucion_comun"])
ex = pd.DataFrame(excluidos, columns=["EID", "Year", "Title", "motivo"])
de = pd.DataFrame(descartadas, columns=["EID", "Year", "afiliacion"])

salidas = {
    "documentos_limpios.csv": docs, "documento_pais.csv": dp, "autor_documento_pais.csv": adp,
    "mapeo_paises.csv": mp, "mapeo_autores.csv": ma, "documentos_excluidos.csv": ex,
    "afiliaciones_descartadas.csv": de,
}
for nombre, d in salidas.items():
    d.to_csv(DIR_PROCESSED / nombre, index=False, encoding="utf-8")
    print(f"  data/processed/{nombre:<30} {len(d):>6} filas")

# ---------------------------------------------------------------------------
titulo("7. Resumen")
print(f"  Documentos: {n0} → {len(docs)} ({n0 - len(docs)} excluidos)")
for motivo, n in ex["motivo"].value_counts().items():
    print(f"    · {motivo}: {n}")
print(f"  Años: {docs['Year'].min()}–{docs['Year'].max()} ({ANIO_PARCIAL} marcado como parcial)")
print(f"  Documentos internacionales: {int(docs['internacional'].sum())} "
      f"({100 * docs['internacional'].mean():.1f} %)")
print(f"  Megacolaboraciones (>= {UMBRAL_MEGA} países): {int(docs['mega_colaboracion'].sum())}")
print(f"  Países: {dp['iso3'].nunique()} (socios sin Ecuador: {dp['iso3'].nunique() - 1}); "
      f"continentes: {dp['continente'].nunique()}")
print(f"  Autores canónicos con país: {adp['author_id'].nunique()}")
print("\n[OK] Limpieza terminada.")
