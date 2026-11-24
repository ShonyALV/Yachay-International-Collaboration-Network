"""Utilidades compartidas por los scripts del proyecto.

Todas las rutas son relativas a la raíz del proyecto (la carpeta padre de src/),
para que los scripts funcionen sin importar desde dónde se ejecuten.
"""
from __future__ import annotations

import html
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import pycountry

# La consola de Windows puede usar cp1252/cp1251: forzamos UTF-8 en la salida.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = Path(__file__).resolve().parents[1]
DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"
DIR_OUTPUT = RAIZ / "output"
DIR_JSON = DIR_OUTPUT / "json"
DIR_GEXF = DIR_OUTPUT / "gexf"

AF_ID_YACHAY = "60105012"


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------
def detectar_csv() -> Path:
    """Devuelve el único CSV en data/raw/. Falla si hay cero o varios."""
    csvs = sorted(DIR_RAW.glob("*.csv"))
    if len(csvs) != 1:
        raise FileNotFoundError(
            f"Se esperaba exactamente 1 CSV en {DIR_RAW}, se encontraron {len(csvs)}: "
            f"{[c.name for c in csvs]}"
        )
    return csvs[0]


def leer_scopus(ruta: Path | None = None) -> pd.DataFrame:
    """Lee el export de Scopus como texto (sin inferir tipos)."""
    ruta = ruta or detectar_csv()
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False,
                       na_values=[""])


# ---------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------
def limpiar_html(texto: str) -> str:
    """Decodifica entidades HTML (&#x00ED; -> í, '& amp;' -> &) ANTES de separar por ';'.

    Scopus a veces deja entidades cuyo ';' rompería la separación de afiliaciones.
    """
    if not isinstance(texto, str):
        return ""
    t = texto.replace("& amp;", "&").replace("&amp;", "&")
    # Repetimos por si hay doble codificación
    for _ in range(2):
        t = html.unescape(t)
    return t


def sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto)
                   if not unicodedata.combining(c))


def normalizar_titulo(titulo: str) -> str:
    """Minúsculas, sin acentos ni puntuación, espacios colapsados."""
    if not isinstance(titulo, str):
        return ""
    t = sin_acentos(limpiar_html(titulo)).lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def normalizar_nombre(nombre: str) -> str:
    """Clave para comparar nombres de autor: sin acentos, minúsculas, solo letras."""
    t = sin_acentos(nombre or "").lower()
    t = re.sub(r"[^a-z ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# Afiliaciones y países
# ---------------------------------------------------------------------------
def separar(campo: str, sep: str = ";") -> list[str]:
    """Limpia HTML y separa un campo multivalor de Scopus."""
    return [s.strip() for s in limpiar_html(campo).split(sep) if s.strip()]


# Nombres que Scopus usa y que pycountry no resuelve directamente (o resuelve mal).
# Clave: texto tal como aparece en Scopus. Valor: nombre buscable en pycountry.
ALIAS_PAISES = {
    "Russian Federation": "Russian Federation",
    "Viet Nam": "Viet Nam",
    "South Korea": "Korea, Republic of",
    "North Korea": "Korea, Democratic People's Republic of",
    "Iran": "Iran, Islamic Republic of",
    "Laos": "Lao People's Democratic Republic",
    "Democratic Republic Congo": "Congo, The Democratic Republic of the",
    "Congo": "Congo",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Brunei Darussalam": "Brunei Darussalam",
    "Taiwan": "Taiwan, Province of China",
    "Tanzania": "Tanzania, United Republic of",
    "Turkey": "Türkiye",
    "Czech Republic": "Czechia",
    "Bolivia": "Bolivia, Plurinational State of",
    "Venezuela": "Venezuela, Bolivarian Republic of",
    "Syria": "Syrian Arab Republic",
    "Moldova": "Moldova, Republic of",
    "Macedonia": "North Macedonia",
    "Palestine": "Palestine, State of",
    "United States": "United States",
    "United Kingdom": "United Kingdom",
    "Hong Kong": "Hong Kong",
    "Macau": "Macao",
}

CODIGOS_PERMITIDOS = {"USA": "United States", "UK": "United Kingdom",
                      "UAE": "United Arab Emirates"}

_cache_pais: dict[str, object | None] = {}


def resolver_pais(texto: str):
    """Devuelve el objeto pycountry del país o None si el texto no es un país."""
    t = (texto or "").strip().rstrip(".")
    if t in _cache_pais:
        return _cache_pais[t]
    res = None
    # Los textos de <=3 letras (p. ej. "CA", "MA", "NY") NO se buscan como códigos ISO:
    # en las direcciones suelen ser estados de EE. UU. y producirían falsos positivos.
    if t in CODIGOS_PERMITIDOS:
        t_busq = CODIGOS_PERMITIDOS[t]
    elif len(t) <= 3:
        t_busq = ""
    else:
        t_busq = t
    if t_busq and len(t_busq) <= 40 and not any(ch.isdigit() for ch in t_busq):
        objetivo = ALIAS_PAISES.get(t_busq, t_busq)
        try:
            res = pycountry.countries.lookup(objetivo)
        except LookupError:
            res = None
    _cache_pais[t] = res
    return res


def pais_ultimo_segmento(afiliacion: str) -> tuple[str, object | None]:
    """Regla simple: el país es el último segmento separado por comas."""
    ultimo = afiliacion.split(",")[-1].strip()
    return ultimo, resolver_pais(ultimo)


def paises_en_segmentos(texto: str) -> list:
    """Busca países en CUALQUIER segmento separado por comas (orden de aparición, únicos).

    Necesario en 'Authors with affiliations', donde un autor con varias afiliaciones
    tiene todas unidas por comas dentro de la misma entrada.
    """
    vistos, salida = set(), []
    for seg in texto.split(","):
        p = resolver_pais(seg)
        if p is not None and p.alpha_3 not in vistos:
            vistos.add(p.alpha_3)
            salida.append(p)
    return salida


# ---------------------------------------------------------------------------
# Reglas de limpieza aprobadas (Fase 2) — compartidas por las fases siguientes
# ---------------------------------------------------------------------------
ANIO_MIN, ANIO_MAX = 2014, 2026          # R1
ANIO_PARCIAL = 2026                      # año en curso, incompleto
TIPOS_EXCLUIDOS = {"Erratum", "Retracted"}   # R2
UMBRAL_MEGA = 10                         # R11: documentos con >= 10 países (incl. Ecuador)

# R10: territorios que se reasignan al país soberano (no tienen polígono propio en
# world-atlas 110m). Puerto Rico (630) se mantiene porque sí tiene polígono.
TERRITORIOS = {"HKG": "CHN", "MAC": "CHN", "GUF": "FRA"}

# Nombres cortos para mostrar en la visualización (el resto usa el nombre de pycountry).
NOMBRES_MOSTRAR = {
    "VEN": "Venezuela", "BOL": "Bolivia", "KOR": "South Korea", "PRK": "North Korea",
    "IRN": "Iran", "TZA": "Tanzania", "LAO": "Laos", "COD": "DR Congo", "COG": "Congo",
    "RUS": "Russia", "VNM": "Vietnam", "TWN": "Taiwan", "CZE": "Czechia", "TUR": "Türkiye",
    "CIV": "Côte d'Ivoire", "BRN": "Brunei", "SYR": "Syria", "MDA": "Moldova",
    "PSE": "Palestine", "MKD": "North Macedonia",
}

RE_YACHAY = re.compile(r"yacha[yi]|urcuqu", re.I)
RE_EMAIL = re.compile(r"\.\s*Electronic address:[^,;]*", re.I)


def quitar_email(texto: str) -> str:
    """R6: elimina el correo que Scopus a veces pega tras el país ('Brazil. Electronic address: …')."""
    return RE_EMAIL.sub("", texto or "")


def pais_soberano(p):
    """Aplica R10 y devuelve el objeto pycountry final."""
    destino = TERRITORIOS.get(p.alpha_3)
    return pycountry.countries.get(alpha_3=destino) if destino else p


def pais_de_afiliacion(af: str) -> tuple[object | None, str, str]:
    """R5 + R6 + R10. Devuelve (pais, texto_original_del_segmento, regla_aplicada)."""
    ultimo, p = pais_ultimo_segmento(af)
    if p is not None:
        regla = "directo" if p.name == ultimo else "alias"
        final = pais_soberano(p)
        if final.alpha_3 != p.alpha_3:
            regla = "territorio"
        return final, ultimo, regla
    if RE_YACHAY.search(af):
        return pycountry.countries.get(alpha_3="ECU"), ultimo, "yachay_sin_pais"
    return None, ultimo, "descartada"


def nombre_mostrar(p) -> str:
    return NOMBRES_MOSTRAR.get(p.alpha_3) or getattr(p, "common_name", None) or p.name


CONTINENTES = {"AF": "Africa", "AS": "Asia", "EU": "Europe", "NA": "North America",
               "SA": "South America", "OC": "Oceania", "AN": "Antarctica"}


# R12 (aprobada): regiones según la agrupación M49 de la ONU. "Latin America & Caribbean"
# reúne México, Centroamérica, el Caribe y Sudamérica; "North America" queda solo para
# EE. UU., Canadá y territorios del norte (Groenlandia, Bermudas, San Pedro y Miquelón).
NORTEAMERICA = {"USA", "CAN", "GRL", "BMU", "SPM"}
LATAM = "Latin America & Caribbean"
ORDEN_REGIONES = [LATAM, "North America", "Europe", "Asia", "Africa", "Oceania"]


def continente(p) -> str:
    """Región (continente) usada en todo el proyecto."""
    import pycountry_convert as pcc
    try:
        codigo = pcc.country_alpha2_to_continent_code(p.alpha_2)
    except Exception:
        return "Unknown"
    if codigo == "SA" or (codigo == "NA" and p.alpha_3 not in NORTEAMERICA):
        return LATAM
    return CONTINENTES[codigo]
