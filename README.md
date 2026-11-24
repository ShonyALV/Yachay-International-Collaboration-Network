# Quiz 2 — Temporal Graph Visualization of Scientific Collaboration at Yachay Tech

Red de **colaboración internacional entre países** construida a partir de las publicaciones de
Yachay Tech University en Scopus (AF-ID 60105012), analizada como grafo temporal en dos modos:
**anual** (solo los documentos de cada año) y **acumulado** (todos los documentos hasta ese año).

**Pregunta analítica:** ¿Cómo ha evolucionado la red de colaboración internacional de Yachay Tech
desde 2014? ¿Su alcance geográfico acumulado sigue creciendo mientras la colaboración de cada año
se concentra en menos socios y una menor proporción de documentos internacionales?

- Nodos = países. Aristas = dos países aparecen en las afiliaciones de un mismo documento.
- Grafo no dirigido y ponderado (peso = nº de documentos en común, conteo completo). Ecuador incluido.

## Estructura

```
data/raw/         CSV original de Scopus (no se modifica)
data/processed/   tablas limpias y de mapeo
src/              scripts numerados 01–04, utils.py (funciones y reglas compartidas)
                  y verificar_reproducibilidad.py
output/           reportes, métricas, json/ (d3) y gexf/ (Gephi)
viz/              visualización d3 (index.html, app.js, styles.css)
```

## Instalación (Windows, PowerShell o Git Bash)

```bash
py -3.12 -m venv .venv
".venv/Scripts/python.exe" -m pip install -r requirements.txt
```

## Orden de ejecución

Desde la raíz del proyecto:

```bash
".venv/Scripts/python.exe" "src/01_exploracion.py"   # reporte -> output/reporte_exploracion.md
".venv/Scripts/python.exe" "src/02_limpieza.py"      # tablas limpias -> data/processed/
".venv/Scripts/python.exe" "src/03_construccion_grafos.py"  # grafos -> output/json/ y output/gexf/
".venv/Scripts/python.exe" "src/04_metricas.py"       # métricas -> output/json/metricas.json y output/metricas_por_anio.csv
```

En macOS/Linux, el intérprete del entorno es `.venv/bin/python` en lugar de `.venv/Scripts/python.exe`.

### Verificación de reproducibilidad

Todo lo aleatorio usa semilla fija (Louvain `seed=42`, layout de d3-force con `randomLcg(42)`) y
todas las salidas se ordenan de forma determinista. Para comprobarlo, desde la raíz del proyecto:

```bash
".venv/Scripts/python.exe" "src/verificar_reproducibilidad.py"
```

El script:

1. Guarda el SHA-256 de las salidas actuales de `data/processed/` y `output/`, si existen.
2. Ejecuta el pipeline completo (01 → 04) **dos veces** con distinta semilla de hash de Python
   (`PYTHONHASHSEED=0` y `12345`), para detectar cualquier dependencia del orden de los `set`/`dict`.
3. Compara las huellas de las 14 salidas entre ambas ejecuciones y con las salidas previas.
4. Comprueba que el CSV original de `data/raw/` no se haya modificado.

Termina con `[OK] El pipeline es reproducible.` y código de salida 0, o lista los archivos que
difieren y sale con código 1. Se ignoran la línea *Fecha de generación* de
`output/reporte_exploracion.md`, que cambia a propósito, y `output/hallazgos.md`, que se redactó
a mano. Tarda menos de un minuto.

**Verificación realizada (2026-11-24):**

- Entorno nuevo creado solo desde `requirements.txt`.
- Salidas borradas y regeneradas desde cero.
- Ejecuciones con `PYTHONHASHSEED` 0, 1 y 12345: las 14 salidas son idénticas byte a byte entre sí y respecto a las originales.

### Salidas de la Fase 3

- `output/json/red_anual.json` y `output/json/red_acumulada.json`: `{ "years": [...], "snapshots": { "2014": { "nodes": [...], "links": [...] }, ... } }`.
  Cada nodo y arista incluye también sus valores sin megacolaboraciones (sufijo `_nm`).
- `output/gexf/red_dinamica.gexf` (modo anual) y `output/gexf/red_dinamica_acumulada.gexf`:
  GEXF 1.2 dinámico (`timeformat="date"`, un intervalo por año) con peso de arista dinámico.
  En Gephi: *Archivo → Abrir*, luego *Ventana → Timeline* y activar la línea de tiempo.

## Reglas de limpieza aplicadas (Fase 2)

| Regla | Descripción |
|---|---|
| R1 | Años 2014–2026; 2026 marcado como parcial; se excluyen los documentos con año 2027. |
| R2 | Se excluyen Erratum y Retracted. |
| R3 | Duplicados por EID → DOI → título normalizado (≥ 4 palabras) + año; se conserva el registro con más afiliaciones. |
| R4 | Entidades HTML decodificadas antes de separar afiliaciones por `;`. |
| R5 | País = último segmento de cada afiliación en `Affiliations`, normalizado (`mapeo_paises.csv`). |
| R6 | Afiliaciones sin país que mencionan Yachay/Urcuquí → Ecuador; se elimina el correo pegado al país; el resto se descarta (`afiliaciones_descartadas.csv`). |
| R7 | Ecuador se agrega a todo documento que no lo tenga (todos provienen de la afiliación de Yachay Tech). |
| R8 | País del autor = países en su entrada de `Authors with affiliations`, validados contra los países del documento. |
| R9 | `Author(s) ID` como clave; nombre canónico = variante más frecuente. Perfiles fusionados solo con nombre completo idéntico + institución en común (`mapeo_autores.csv`). |
| R10 | Hong Kong → China, Guayana Francesa → Francia; Puerto Rico se mantiene (ISO 630). |
| R11 | Megacolaboraciones (≥ 10 países) se conservan y se marcan en `documentos_limpios.csv`. |
| R12 | Regiones según la agrupación M49 de la ONU: *Latin America & Caribbean* (México, Centroamérica, Caribe y Sudamérica), *North America* (EE. UU. y Canadá), *Europe*, *Asia*, *Africa*, *Oceania*. |

### Métricas (Fase 4)

Por año y modo: documentos, % internacional, países socios (sin Ecuador), países nuevos,
regiones, aristas, densidad, grado y grado ponderado de Ecuador, diversidad de los socios de
Ecuador (Shannon, equitatividad de Pielou, HHI y nº efectivo de socios = 1/HHI), top 10 socios y
reparto por región. Sobre la red acumulada: betweenness (sin ponderar y ponderado con
distancia = 1/peso) y comunidades Louvain (`seed=42`). Las métricas clave se repiten sin
megacolaboraciones (sufijo `_nm`).

## Visualización (Fase 5)

`viz/index.html` + `viz/app.js` + `viz/styles.css` (d3 7.9.0, topojson-client 3.1.0 y
world-atlas 2.0.2 desde jsDelivr; requiere conexión a internet para estas librerías).
Lee los JSON de `output/json/`, así que **debe servirse por HTTP desde la raíz del proyecto**:

```bash
cd "QUIZ 2 - Temporal Graph Visualization of Scientific Collaboration at Yachay Tech"
python -m http.server 8000
```

Abrir <http://localhost:8000/viz/> (diseñada para 1920×1080).

- **Controles:** Annual / Cumulative, Map / Network, Play/Pausa (1,4 s por año), slider de años,
  color por región o comunidad Louvain (vista Red) y filtro *Exclude mega-collaborations*.
- **Teclado:** `Espacio` = Play/Pausa, `←` / `→` = año anterior/siguiente.
- **Tema claro/oscuro:** selector *Theme* en la esquina inferior izquierda. El navegador recuerda la elección. Ambos temas usan los mismos tonos por región, ajustados al fondo.
- **Zoom y desplazamiento** en Mapa y Red: rueda del ratón = zoom, arrastrar = mover, doble clic = acercar; botones +, − y *Reset* abajo a la derecha. Los círculos, etiquetas y grosores conservan su tamaño en pantalla (al acercar, los países se separan y aparecen más etiquetas). El zoom se mantiene al cambiar de año o durante el Play.
- **Clic en un sparkline** salta a ese año.
- **Estados por `#hash`** (útiles para grabar): `vista-modo-año[-sinmega][-comunidad]`, p. ej.
  `#mapa-acumulado-2020`, `#red-anual-2015-sinmega`, `#red-acumulado-2026-comunidad`.
- 2026 se marca con `*` como año parcial (datos hasta noviembre de 2026).
- La posición de cada país en la vista Red se calcula una sola vez con d3-force sobre la red
  acumulada final, así que los nodos no saltan entre años.

## Hallazgos (Fase 6)

`output/hallazgos.md`: 6 hallazgos con cifras y el estado de la visualización donde se observan,
la comparación entre la vista anual y la acumulada, las limitaciones y el guion del video (máx. 5 min).
