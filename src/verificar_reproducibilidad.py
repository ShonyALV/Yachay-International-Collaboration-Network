"""Verificación de reproducibilidad del pipeline (scripts 01–04).

Ejecuta el pipeline completo dos veces con distinta semilla de hash de Python
(PYTHONHASHSEED=0 y 12345) y compara el SHA-256 de todas las salidas generadas.
Si existen salidas previas, también las compara con ellas.

La línea "Fecha de generación" de output/reporte_exploracion.md se ignora (cambia a propósito).
Uso (desde la raíz del proyecto):  .venv/Scripts/python.exe src/verificar_reproducibilidad.py
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

from utils import DIR_OUTPUT, DIR_PROCESSED, RAIZ, detectar_csv

SCRIPTS = ["01_exploracion.py", "02_limpieza.py", "03_construccion_grafos.py", "04_metricas.py"]
EXCLUIR = {"hallazgos.md"}  # redactado a mano, no lo genera el pipeline


def salidas() -> list[Path]:
    archivos = [p for d in (DIR_PROCESSED, DIR_OUTPUT) for p in d.rglob("*") if p.is_file()]
    return sorted(p for p in archivos if p.name not in EXCLUIR)


def huella(p: Path) -> str:
    datos = p.read_bytes()
    if p.name == "reporte_exploracion.md":
        datos = b"\n".join(l for l in datos.split(b"\n") if "Fecha de generaci".encode() not in l)
    return hashlib.sha256(datos).hexdigest()


def huellas() -> dict[str, str]:
    return {p.relative_to(RAIZ).as_posix(): huella(p) for p in salidas()}


def ejecutar(semilla: str) -> None:
    entorno = dict(os.environ, PYTHONHASHSEED=semilla, PYTHONIOENCODING="utf-8")
    for s in SCRIPTS:
        r = subprocess.run([sys.executable, str(RAIZ / "src" / s)], cwd=RAIZ, env=entorno,
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:])
            sys.exit(f"[ERROR] {s} falló con PYTHONHASHSEED={semilla}")
        print(f"  ✓ {s} (PYTHONHASHSEED={semilla})")


def comparar(a: dict, b: dict, etiqueta: str) -> bool:
    distintos = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
    if distintos:
        print(f"  ✗ {etiqueta}: {len(distintos)} archivo(s) difieren:")
        for k in distintos:
            print(f"      - {k}")
        return False
    print(f"  ✓ {etiqueta}: {len(a)} archivos idénticos")
    return True


if __name__ == "__main__":
    csv = detectar_csv()
    hash_csv = hashlib.sha256(csv.read_bytes()).hexdigest()
    print("=" * 78 + "\nVerificación de reproducibilidad\n" + "=" * 78)
    print(f"  CSV original: data/raw/{csv.name}  SHA-256 {hash_csv[:16]}…")

    previas = huellas()
    print(f"  Salidas previas encontradas: {len(previas)}")

    print("\n1. Ejecución A")
    ejecutar("0")
    a = huellas()
    print("\n2. Ejecución B")
    ejecutar("12345")
    b = huellas()

    print("\n3. Comparación")
    ok = comparar(a, b, "Ejecución A vs. B")
    if previas:
        ok &= comparar(previas, a, "Salidas previas vs. nuevas")
    csv_intacto = hashlib.sha256(csv.read_bytes()).hexdigest() == hash_csv
    print(f"  {'✓' if csv_intacto else '✗'} CSV original sin modificar")
    ok &= csv_intacto

    print("\n" + ("[OK] El pipeline es reproducible." if ok else "[ERROR] Hay diferencias entre ejecuciones."))
    sys.exit(0 if ok else 1)
