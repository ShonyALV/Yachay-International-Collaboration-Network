"""Fase 3 — Construcción de los grafos temporales país–país.

Para cada año (2014–2026) y en dos modos:
  - anual:     solo los documentos de ese año
  - acumulado: todos los documentos desde 2014 hasta ese año

Nodos  = países (Ecuador incluido). Aristas = coocurrencia en un mismo documento.
Grafo no dirigido y ponderado (peso = nº de documentos en común, conteo completo).

Cada nodo y arista también lleva sus valores SIN megacolaboraciones (sufijo "_nm",
R11: documentos con >= 10 países) para el filtro de la visualización.

Salidas:
  output/json/red_anual.json, output/json/red_acumulada.json
  output/gexf/red_dinamica.gexf             (modo anual: spells = años activos)
  output/gexf/red_dinamica_acumulada.gexf   (modo acumulado: presente desde su 1.er año)
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from itertools import combinations

import networkx as nx
import pandas as pd

from utils import (ANIO_MAX, ANIO_MIN, ANIO_PARCIAL, DIR_GEXF, DIR_JSON, DIR_PROCESSED,
                   ORDEN_REGIONES, UMBRAL_MEGA)

ECU = "ECU"
ANIOS = list(range(ANIO_MIN, ANIO_MAX + 1))
COLORES_REGION = {  # mismos colores que viz/app.js
    "Latin America & Caribbean": (57, 135, 229), "Europe": (217, 89, 38),
    "North America": (25, 158, 112), "Asia": (213, 81, 129), "Africa": (201, 133, 0),
    "Oceania": (144, 133, 233),
}

DIR_JSON.mkdir(parents=True, exist_ok=True)
DIR_GEXF.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
print("=" * 78 + "\n1. Lectura de tablas limpias\n" + "=" * 78)
docs = pd.read_csv(DIR_PROCESSED / "documentos_limpios.csv", dtype={"EID": str})
dp = pd.read_csv(DIR_PROCESSED / "documento_pais.csv", dtype=str)
adp = pd.read_csv(DIR_PROCESSED / "autor_documento_pais.csv", dtype=str)
dp["Year"] = dp["Year"].astype(int)
adp["Year"] = adp["Year"].astype(int)
print(f"  Documentos: {len(docs)}, pares documento–país: {len(dp)}, "
      f"filas autor–documento–país: {len(adp)}")

mega = set(docs.loc[docs["mega_colaboracion"], "EID"])
anio_doc = dict(zip(docs["EID"], docs["Year"]))
paises_doc: dict[str, list[str]] = dp.groupby("EID")["iso3"].apply(sorted).to_dict()
info = (dp.drop_duplicates("iso3").set_index("iso3")[["pais", "iso_num", "continente"]]
        .to_dict("index"))
print(f"  Megacolaboraciones marcadas: {len(mega)}; países: {len(info)}")

# Año de primera aparición (global, con y sin megacolaboraciones)
def primeros(excluir_mega: bool):
    pn, pa = {}, {}
    for eid in sorted(paises_doc, key=lambda e: anio_doc[e]):
        if excluir_mega and eid in mega:
            continue
        a, ps = anio_doc[eid], paises_doc[eid]
        for p in ps:
            pn.setdefault(p, a)
        for u, v in combinations(ps, 2):
            pa.setdefault((u, v), a)
    return pn, pa


primer_nodo, primer_arista = primeros(False)
primer_nodo_nm, primer_arista_nm = primeros(True)

# Autores por (EID, país)
autores_doc_pais: dict[tuple[str, str], set[str]] = defaultdict(set)
for eid, iso, aid in adp[["EID", "iso3", "author_id"]].itertuples(index=False):
    autores_doc_pais[(eid, iso)].add(aid)


# ---------------------------------------------------------------------------
def construir(eids: list[str], anio: int) -> nx.Graph:
    """Grafo para un conjunto de documentos, con atributos completos y sin megacolaboraciones."""
    g = nx.Graph()
    docs_n, docs_nm = defaultdict(int), defaultdict(int)
    aut, aut_nm = defaultdict(set), defaultdict(set)
    w, w_nm = defaultdict(int), defaultdict(int)
    for eid in eids:
        es_mega = eid in mega
        ps = paises_doc[eid]
        for p in ps:
            docs_n[p] += 1
            aut[p] |= autores_doc_pais.get((eid, p), set())
            if not es_mega:
                docs_nm[p] += 1
                aut_nm[p] |= autores_doc_pais.get((eid, p), set())
        for u, v in combinations(ps, 2):
            w[(u, v)] += 1
            if not es_mega:
                w_nm[(u, v)] += 1
    for p in docs_n:
        i = info[p]
        g.add_node(p, name=i["pais"], iso3=p, iso_num=str(i["iso_num"]).zfill(3),
                   continent=i["continente"], docs=docs_n[p], authors=len(aut[p]),
                   first_year=primer_nodo[p], is_new=primer_nodo[p] == anio,
                   docs_nm=docs_nm[p], authors_nm=len(aut_nm[p]),
                   first_year_nm=primer_nodo_nm.get(p), is_new_nm=primer_nodo_nm.get(p) == anio)
    for (u, v), peso in w.items():
        g.add_edge(u, v, weight=peso, first_year=primer_arista[(u, v)],
                   is_new=primer_arista[(u, v)] == anio, weight_nm=w_nm.get((u, v), 0),
                   first_year_nm=primer_arista_nm.get((u, v)))
    for p in g.nodes:
        g.nodes[p]["degree"] = g.degree(p)
        g.nodes[p]["strength"] = g.degree(p, weight="weight")
        vec_nm = [x for x in g[p] if g[p][x]["weight_nm"] > 0]
        g.nodes[p]["degree_nm"] = len(vec_nm)
        g.nodes[p]["strength_nm"] = sum(g[p][x]["weight_nm"] for x in vec_nm)
    return g


def a_json(g: nx.Graph) -> dict:
    nodos = sorted((dict(d, id=n) for n, d in g.nodes(data=True)),
                   key=lambda d: (d["id"] != ECU, -d["docs"], d["id"]))
    enlaces = sorted(({"source": u, "target": v, **d} for u, v, d in g.edges(data=True)),
                     key=lambda d: (-d["weight"], d["source"], d["target"]))
    return {"n_docs": g.graph["n_docs"], "n_docs_nm": g.graph["n_docs_nm"],
            "nodes": nodos, "links": enlaces}


# ---------------------------------------------------------------------------
print("=" * 78 + "\n2. Construcción de snapshots\n" + "=" * 78)
grafos: dict[str, dict[int, nx.Graph]] = {"anual": {}, "acumulado": {}}
print(f"  {'año':<6}{'modo':<11}{'docs':>6}{'nodos':>7}{'aristas':>9}{'nuevos':>8}"
      f"{'peso ECU':>10}")
for anio in ANIOS:
    for modo in ("anual", "acumulado"):
        eids = [e for e, a in anio_doc.items() if (a == anio if modo == "anual" else a <= anio)]
        g = construir(eids, anio)
        g.graph["n_docs"] = len(eids)
        g.graph["n_docs_nm"] = sum(1 for e in eids if e not in mega)
        grafos[modo][anio] = g
        nuevos = sum(1 for _, d in g.nodes(data=True) if d["is_new"])
        print(f"  {anio:<6}{modo:<11}{len(eids):>6}{g.number_of_nodes():>7}"
              f"{g.number_of_edges():>9}{nuevos:>8}{g.nodes[ECU]['strength']:>10}")

# Verificaciones de consistencia
g_final = grafos["acumulado"][ANIO_MAX]
assert g_final.number_of_nodes() == len(info), "El acumulado final debe contener todos los países"
assert sum(grafos["anual"][a].graph["n_docs"] for a in ANIOS) == len(docs)
for a in ANIOS:
    ga, gc = grafos["anual"][a], grafos["acumulado"][a]
    assert set(ga.nodes) <= set(gc.nodes)
print("  [OK] Verificaciones: el acumulado final contiene todos los países y "
      "la suma de documentos anuales coincide con el total.")

# ---------------------------------------------------------------------------
print("=" * 78 + "\n3. Exportación JSON\n" + "=" * 78)
meta = {
    "source": "Scopus, afiliación Yachay Tech (AF-ID 60105012)",
    "partial_year": ANIO_PARCIAL, "mega_threshold": UMBRAL_MEGA,
    "regions": ORDEN_REGIONES,
    "edge_weight": "number of co-authored documents (full counting)",
}
for modo, archivo in (("anual", "red_anual.json"), ("acumulado", "red_acumulada.json")):
    salida = {"mode": "annual" if modo == "anual" else "cumulative", "years": ANIOS, **meta,
              "snapshots": {str(a): a_json(grafos[modo][a]) for a in ANIOS}}
    ruta = DIR_JSON / archivo
    ruta.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  output/json/{archivo:<22} {ruta.stat().st_size / 1024:>8.1f} KB")


# ---------------------------------------------------------------------------
print("=" * 78 + "\n4. Exportación GEXF dinámico\n" + "=" * 78)
NS = "http://www.gexf.net/1.2draft"
NS_VIZ = "http://www.gexf.net/1.2draft/viz"
ET.register_namespace("", NS)
ET.register_namespace("viz", NS_VIZ)


def ini(a: int) -> str:
    return f"{a}-01-01"


def fin(a: int) -> str:
    return f"{a}-12-31"


def gexf(modo: str, ruta) -> None:
    """GEXF 1.2 dinámico (timeformat=date). Cada año es el intervalo [aaaa-01-01, aaaa-12-31].

    - spells: años en que el nodo/arista está activo en el modo dado.
    - atributos dinámicos: docs, authors (nodos) y weight (aristas) por año.
    """
    snaps = grafos[modo]
    raiz = ET.Element(f"{{{NS}}}gexf", {"version": "1.2"})
    m = ET.SubElement(raiz, f"{{{NS}}}meta", {"lastmodifieddate": pd.Timestamp.today().date().isoformat()})
    ET.SubElement(m, f"{{{NS}}}creator").text = "src/03_construccion_grafos.py"
    ET.SubElement(m, f"{{{NS}}}description").text = (
        f"Red de colaboración internacional de Yachay Tech — modo {modo}. {meta['source']}.")
    g = ET.SubElement(raiz, f"{{{NS}}}graph", {
        "mode": "dynamic", "defaultedgetype": "undirected", "timeformat": "date",
        "start": ini(ANIOS[0]), "end": fin(ANIOS[-1])})

    an = ET.SubElement(g, f"{{{NS}}}attributes", {"class": "node", "mode": "static"})
    for t, tipo in ([("iso3", "string"), ("iso_num", "string"),
                                   ("continent", "string"), ("first_year", "integer")]):
        ET.SubElement(an, f"{{{NS}}}attribute", {"id": t, "title": t, "type": tipo})
    and_ = ET.SubElement(g, f"{{{NS}}}attributes", {"class": "node", "mode": "dynamic"})
    for t in ("docs", "authors", "strength"):
        ET.SubElement(and_, f"{{{NS}}}attribute", {"id": t, "title": t, "type": "integer"})
    ae = ET.SubElement(g, f"{{{NS}}}attributes", {"class": "edge", "mode": "static"})
    ET.SubElement(ae, f"{{{NS}}}attribute", {"id": "first_year", "title": "first_year",
                                            "type": "integer"})
    aed = ET.SubElement(g, f"{{{NS}}}attributes", {"class": "edge", "mode": "dynamic"})
    # Gephi interpreta un atributo dinámico con id "weight" como peso dinámico de la arista.
    ET.SubElement(aed, f"{{{NS}}}attribute", {"id": "weight", "title": "Weight", "type": "float"})

    # Nodos
    nodos_el = ET.SubElement(g, f"{{{NS}}}nodes")
    for iso in sorted(info, key=lambda p: (primer_nodo[p], p)):
        datos = g_final.nodes[iso]
        n = ET.SubElement(nodos_el, f"{{{NS}}}node", {"id": iso, "label": datos["name"]})
        av = ET.SubElement(n, f"{{{NS}}}attvalues")
        for k in ("iso3", "iso_num", "continent", "first_year"):
            ET.SubElement(av, f"{{{NS}}}attvalue", {"for": k, "value": str(datos[k])})
        activos = [a for a in ANIOS if iso in snaps[a]]
        for a in activos:
            d = snaps[a].nodes[iso]
            for k in ("docs", "authors", "strength"):
                ET.SubElement(av, f"{{{NS}}}attvalue",
                              {"for": k, "value": str(d[k]), "start": ini(a), "end": fin(a)})
        sp = ET.SubElement(n, f"{{{NS}}}spells")
        for a in activos:
            ET.SubElement(sp, f"{{{NS}}}spell", {"start": ini(a), "end": fin(a)})
        r, gg, b = COLORES_REGION.get(datos["continent"], (150, 150, 150))
        ET.SubElement(n, f"{{{NS_VIZ}}}color", {"r": str(r), "g": str(gg), "b": str(b)})
        ET.SubElement(n, f"{{{NS_VIZ}}}size", {"value": str(max(1.0, datos["docs"] ** 0.5))})

    # Aristas
    aristas_el = ET.SubElement(g, f"{{{NS}}}edges")
    for k, (u, v, datos) in enumerate(sorted(g_final.edges(data=True),
                                             key=lambda e: (e[2]["first_year"], e[0], e[1]))):
        e = ET.SubElement(aristas_el, f"{{{NS}}}edge", {
            "id": str(k), "source": u, "target": v, "weight": str(datos["weight"])})
        av = ET.SubElement(e, f"{{{NS}}}attvalues")
        ET.SubElement(av, f"{{{NS}}}attvalue", {"for": "first_year",
                                                "value": str(datos["first_year"])})
        activos = [a for a in ANIOS if snaps[a].has_edge(u, v)]
        for a in activos:
            peso = snaps[a][u][v]["weight"]
            ET.SubElement(av, f"{{{NS}}}attvalue",
                          {"for": "weight", "value": str(peso), "start": ini(a), "end": fin(a)})
        sp = ET.SubElement(e, f"{{{NS}}}spells")
        for a in activos:
            ET.SubElement(sp, f"{{{NS}}}spell", {"start": ini(a), "end": fin(a)})

    ET.indent(raiz, space="  ")
    ET.ElementTree(raiz).write(ruta, encoding="utf-8", xml_declaration=True)


for modo, archivo in (("anual", "red_dinamica.gexf"), ("acumulado", "red_dinamica_acumulada.gexf")):
    ruta = DIR_GEXF / archivo
    gexf(modo, ruta)
    # Verificación: XML bien formado y conteos correctos
    arbol = ET.parse(ruta)
    n_nodos = len(arbol.getroot().findall(f".//{{{NS}}}node"))
    n_aristas = len(arbol.getroot().findall(f".//{{{NS}}}edge"))
    assert n_nodos == g_final.number_of_nodes() and n_aristas == g_final.number_of_edges()
    print(f"  output/gexf/{archivo:<30} XML válido · {n_nodos} nodos · {n_aristas} aristas · "
          f"{ruta.stat().st_size / 1024:.0f} KB")

# ---------------------------------------------------------------------------
print("=" * 78 + "\n5. Resumen\n" + "=" * 78)
print(f"  Años: {ANIOS[0]}–{ANIOS[-1]} ({len(ANIOS)} snapshots por modo; {ANIO_PARCIAL} parcial)")
print(f"  Red acumulada final: {g_final.number_of_nodes()} países, "
      f"{g_final.number_of_edges()} aristas "
      f"({g_final.degree(ECU)} directas con Ecuador, "
      f"{g_final.number_of_edges() - g_final.degree(ECU)} entre países extranjeros)")
top = sorted(((g_final.nodes[v]["name"], g_final[ECU][v]["weight"]) for v in g_final[ECU]),
             key=lambda x: -x[1])[:5]
print("  Top 5 socios de Ecuador (acumulado final): "
      + ", ".join(f"{n} ({w})" for n, w in top))
print("\n[OK] Grafos construidos.")
