"""Fase 4 — Métricas de la red por año y por modo (anual y acumulado).

Lee los snapshots de output/json/ (generados en la Fase 3) y calcula:
  - documentos, documentos internacionales y %
  - países socios (sin Ecuador), países nuevos, regiones (continentes)
  - aristas, densidad, grado y grado ponderado de Ecuador
  - diversidad de los socios de Ecuador: Shannon, equitatividad de Pielou, HHI y nº efectivo de socios
  - top 10 socios por peso y distribución por región
  - betweenness y comunidades Louvain (semilla fija) sobre la red acumulada
Todas las métricas clave se calculan también SIN megacolaboraciones (sufijo _nm, R11).

Salidas: output/json/metricas.json y output/metricas_por_anio.csv
"""
from __future__ import annotations

import json
import math
from collections import defaultdict

import networkx as nx
import pandas as pd

from utils import DIR_JSON, DIR_OUTPUT, ORDEN_REGIONES, UMBRAL_MEGA

ECU = "ECU"
SEMILLA = 42

print("=" * 78 + "\n1. Lectura de snapshots\n" + "=" * 78)
redes = {}
for modo, archivo in (("annual", "red_anual.json"), ("cumulative", "red_acumulada.json")):
    redes[modo] = json.loads((DIR_JSON / archivo).read_text(encoding="utf-8"))
    print(f"  output/json/{archivo}: {len(redes[modo]['years'])} años")
ANIOS = redes["annual"]["years"]
PARCIAL = redes["annual"]["partial_year"]


def grafo(snap: dict, sin_mega: bool) -> nx.Graph:
    """Reconstruye un snapshot como grafo de networkx (opcionalmente sin megacolaboraciones)."""
    g = nx.Graph()
    sw, sd = ("weight_nm", "docs_nm") if sin_mega else ("weight", "docs")
    for n in snap["nodes"]:
        if n[sd] > 0:
            g.add_node(n["id"], **n)
    for l in snap["links"]:
        if l[sw] > 0:
            g.add_edge(l["source"], l["target"], weight=l[sw])
    return g


def diversidad(pesos: list[float]) -> dict:
    """Shannon (ln), equitatividad de Pielou, HHI y nº efectivo de socios (1/HHI)."""
    total = sum(pesos)
    if total == 0:
        return {"shannon": 0.0, "pielou": None, "hhi": None, "effective_partners": 0.0}
    p = [w / total for w in pesos if w > 0]
    h = -sum(x * math.log(x) for x in p)
    hhi = sum(x * x for x in p)
    return {"shannon": round(h, 4),
            "pielou": round(h / math.log(len(p)), 4) if len(p) > 1 else None,
            "hhi": round(hhi, 4), "effective_partners": round(1 / hhi, 2)}


def metricas(snap: dict, anio: int, sin_mega: bool) -> dict:
    g = grafo(snap, sin_mega)
    sd = "docs_nm" if sin_mega else "docs"
    n_docs = snap["n_docs_nm"] if sin_mega else snap["n_docs"]
    ecu_docs = g.nodes[ECU][sd] if ECU in g else 0
    # Ecuador aparece en todos los documentos (R7): los no internacionales son solo-Ecuador.
    # docs internacionales = total - documentos solo con Ecuador. Se obtiene de la tabla limpia.
    socios = sorted((v for v in g[ECU]) if ECU in g else [], key=lambda v: -g[ECU][v]["weight"])
    pesos = [g[ECU][v]["weight"] for v in socios]
    clave_nuevo = "is_new_nm" if sin_mega else "is_new"
    nuevos = sorted(g.nodes[v]["name"] for v in socios if g.nodes[v][clave_nuevo])
    regiones = defaultdict(lambda: {"partners": 0, "collaborations": 0})
    for v in socios:
        r = regiones[g.nodes[v]["continent"]]
        r["partners"] += 1
        r["collaborations"] += g[ECU][v]["weight"]
    total_colab = sum(pesos) or 1
    por_region = {r: {**regiones[r], "share": round(regiones[r]["collaborations"] / total_colab, 4)}
                  for r in ORDEN_REGIONES if r in regiones}
    return {
        "year": anio, "partial_year": anio == PARCIAL, "documents": n_docs,
        "partners": len(socios), "new_partners": nuevos, "n_new_partners": len(nuevos),
        "continents": len(por_region), "edges": g.number_of_edges(),
        "density": round(nx.density(g), 4) if g.number_of_nodes() > 1 else 0.0,
        "ecuador_degree": g.degree(ECU) if ECU in g else 0,
        "ecuador_strength": sum(pesos), "ecuador_docs": ecu_docs,
        **diversidad(pesos),
        "top10": [{"iso3": v, "name": g.nodes[v]["name"], "continent": g.nodes[v]["continent"],
                   "weight": g[ECU][v]["weight"], "share": round(g[ECU][v]["weight"] / total_colab, 4)}
                  for v in socios[:10]],
        "by_continent": por_region,
    }


# Documentos internacionales por año (desde la tabla limpia)
docs = pd.read_csv(DIR_OUTPUT.parent / "data" / "processed" / "documentos_limpios.csv",
                   dtype={"EID": str})


def internacionales(modo: str, anio: int, sin_mega: bool) -> tuple[int, int]:
    d = docs[docs["Year"] == anio] if modo == "annual" else docs[docs["Year"] <= anio]
    if sin_mega:
        d = d[~d["mega_colaboracion"]]
    return len(d), int(d["internacional"].sum())


# ---------------------------------------------------------------------------
print("=" * 78 + "\n2. Métricas por año y modo\n" + "=" * 78)
resultado = {"years": ANIOS, "partial_year": PARCIAL, "mega_threshold": UMBRAL_MEGA,
             "regions": ORDEN_REGIONES, "louvain_seed": SEMILLA,
             "annual": {}, "cumulative": {}}
for modo in ("annual", "cumulative"):
    for anio in ANIOS:
        snap = redes[modo]["snapshots"][str(anio)]
        m = metricas(snap, anio, False)
        m_nm = metricas(snap, anio, True)
        for dic, sm in ((m, False), (m_nm, True)):
            total, intl = internacionales(modo, anio, sm)
            assert total == dic["documents"]
            dic["international_docs"] = intl
            dic["pct_international"] = round(100 * intl / total, 2) if total else 0.0
        m["without_mega"] = {k: m_nm[k] for k in (
            "documents", "international_docs", "pct_international", "partners", "n_new_partners",
            "continents", "edges", "density", "ecuador_strength", "shannon", "pielou", "hhi",
            "effective_partners", "top10")}
        resultado[modo][str(anio)] = m

# ---------------------------------------------------------------------------
print("=" * 78 + "\n3. Betweenness y comunidades Louvain (red acumulada)\n" + "=" * 78)


def louvain(g: nx.Graph) -> dict[str, int]:
    """Louvain ponderado con semilla fija; comunidades numeradas por tamaño (0 = la mayor)."""
    coms = nx.community.louvain_communities(g, weight="weight", seed=SEMILLA)
    coms = sorted(coms, key=lambda c: (-len(c), min(c)))
    return {n: i for i, c in enumerate(coms) for n in sorted(c)}


for anio in ANIOS:
    g = grafo(redes["cumulative"]["snapshots"][str(anio)], False)
    # Para betweenness ponderado la "distancia" es 1/peso (más documentos = más cerca).
    for u, v, d in g.edges(data=True):
        d["dist"] = 1 / d["weight"]
    bt = nx.betweenness_centrality(g, normalized=True)
    btw = nx.betweenness_centrality(g, weight="dist", normalized=True)
    com = louvain(g)
    assert com == louvain(g), "Louvain no es reproducible con la semilla fija"
    m = resultado["cumulative"][str(anio)]
    m["betweenness"] = {n: round(bt[n], 5) for n in sorted(bt, key=lambda n: -bt[n])}
    m["betweenness_weighted"] = {n: round(btw[n], 5) for n in sorted(btw, key=lambda n: -btw[n])}
    m["communities"] = com
    m["n_communities"] = len(set(com.values()))
    m["modularity"] = round(nx.community.modularity(
        g, [{n for n in com if com[n] == c} for c in set(com.values())], weight="weight"), 4)

final = resultado["cumulative"][str(ANIOS[-1])]
resultado["final_communities"] = final["communities"]
g_fin = grafo(redes["cumulative"]["snapshots"][str(ANIOS[-1])], False)
nombres = {n: d["name"] for n, d in g_fin.nodes(data=True)}
print(f"  Red acumulada {ANIOS[-1]}: {final['n_communities']} comunidades, "
      f"modularidad {final['modularity']} (Louvain reproducible con semilla {SEMILLA})")
for c in range(final["n_communities"]):
    miembros = [nombres[n] for n, k in final["communities"].items() if k == c]
    print(f"    Comunidad {c} ({len(miembros)}): {', '.join(miembros[:12])}"
          f"{' …' if len(miembros) > 12 else ''}")
print("  Top 5 betweenness (sin ponderar, sin contar Ecuador): " + ", ".join(
    f"{nombres[n]} {v:.4f}" for n, v in list(final["betweenness"].items())[1:6]))
print("  Top 5 betweenness ponderado (distancia = 1/peso): " + ", ".join(
    f"{nombres[n]} {v:.4f}" for n, v in list(final["betweenness_weighted"].items())[:5]))

# ---------------------------------------------------------------------------
print("=" * 78 + "\n4. Exportación\n" + "=" * 78)
ruta_json = DIR_JSON / "metricas.json"
ruta_json.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"  output/json/metricas.json        {ruta_json.stat().st_size / 1024:.0f} KB")

filas = []
for modo in ("annual", "cumulative"):
    for anio in ANIOS:
        m = resultado[modo][str(anio)]
        nm = m["without_mega"]
        fila = {"mode": modo, "year": anio, "partial_year": m["partial_year"]}
        fila.update({k: m[k] for k in (
            "documents", "international_docs", "pct_international", "partners", "n_new_partners",
            "continents", "edges", "density", "ecuador_degree", "ecuador_strength",
            "shannon", "pielou", "hhi", "effective_partners")})
        fila["new_partners"] = "; ".join(m["new_partners"])
        fila["top10"] = "; ".join(f"{t['name']} ({t['weight']})" for t in m["top10"])
        for r in ORDEN_REGIONES:
            fila[f"share_{r}"] = m["by_continent"].get(r, {}).get("share", 0.0)
        for k in ("pct_international", "partners", "edges", "shannon", "hhi", "effective_partners"):
            fila[f"{k}_nm"] = nm[k]
        fila["n_communities"] = m.get("n_communities")
        fila["modularity"] = m.get("modularity")
        filas.append(fila)
tabla = pd.DataFrame(filas)
tabla.to_csv(DIR_OUTPUT / "metricas_por_anio.csv", index=False, encoding="utf-8")
print(f"  output/metricas_por_anio.csv     {len(tabla)} filas × {tabla.shape[1]} columnas")

# ---------------------------------------------------------------------------
print("=" * 78 + "\n5. Resumen\n" + "=" * 78)
cols = ["year", "documents", "pct_international", "partners", "n_new_partners", "continents",
        "shannon", "hhi", "effective_partners", "partners_nm", "hhi_nm"]
for modo, titulo in (("annual", "ANUAL"), ("cumulative", "ACUMULADO")):
    print(f"\n  {titulo}")
    print(tabla[tabla["mode"] == modo][cols].to_string(index=False))
print("\n[OK] Métricas calculadas.")
