"""
Limpieza de Data_cruda/EPM.csv y Data_cruda/TPM.csv -> Data_limpia_completa/.

Reemplaza el script original de limpieza (no encontrado en este proyecto; el README
solo documenta su resultado, no su codigo). Aplica el mismo tipo de correcciones que
describe README.md seccion 7.1 (NaNs, bug de escala x1000 en POT, timestamps), pero
sobre los archivos crudos nuevos de Data_cruda, que cubren un rango mucho mayor
(incluye la brecha real del EPM y ~5 anios mas de historia de TPM).

Regla de diseno explicita: NO se interpola sobre la brecha real del EPM (680 dias,
2023-06-20 a 2025-05-01). Esa brecha es el objeto de estudio de la tesis (MNAR) y
rellenarla aqui seria fabricar datos. Solo se interpolan huecos cortos (<= 24h),
igual que el criterio documentado para el dataset anterior.

No se usa pandas (no disponible de forma confiable en los entornos locales); todo
el procesamiento es con csv/datetime de la libreria estandar.
"""
import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

RAW_DIR = Path("Data_cruda")
OUT_DIR = Path("Data_limpia_completa")
OUT_DIR.mkdir(exist_ok=True)

SHORT_GAP_LIMIT = timedelta(hours=24)  # por encima de esto, no se interpola


def parse_tpm_date(d):
    d = d.replace(" UTC", "")
    try:
        dt = datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f")
    # 0.15% de las filas traen fraccion de segundo con el reloj ligeramente
    # desfasado de la rejilla nominal (ej. "01:00:15.942" en vez de "01:00:00").
    # Se redondean al minuto para que no generen timestamps "fantasma" separados
    # de la rejilla real y así puedan deduplicarse/promediarse correctamente.
    return dt.replace(second=0, microsecond=0)


def to_float(s):
    s = s.strip()
    if s == "" or s.upper() in ("NAN", "NULL", "NA"):
        return None
    return float(s)


# ---------------------------------------------------------------------------
# EPM: date;alias;R1  (separador ';', decimal ',', encoding utf-8-sig)
# ---------------------------------------------------------------------------
print("=== EPM ===")
epm_long = defaultdict(dict)  # date -> {alias: value}
aliases = set()
with open(RAW_DIR / "EPM.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=";")
    for r in reader:
        d = datetime.strptime(r["date"], "%d/%m/%Y %H:%M:%S")
        val = to_float(r["R1"].replace(",", "."))
        epm_long[d][r["alias"]] = val
        aliases.add(r["alias"])

aliases = sorted(aliases)
dates_epm = sorted(epm_long)
print(f"Timestamps unicos: {len(dates_epm)}  columnas: {aliases}")
print(f"Rango: {dates_epm[0]} -> {dates_epm[-1]}")

# huecos y politica de interpolacion corta
gap_report = []
for i in range(1, len(dates_epm)):
    delta = dates_epm[i] - dates_epm[i - 1]
    if delta > timedelta(hours=6, minutes=1):  # 6h es el paso nominal historico
        gap_report.append((dates_epm[i - 1], dates_epm[i], delta))

print(f"Huecos > 6h detectados: {len(gap_report)}")
for prev, curr, delta in gap_report:
    tag = "CORTO (se interpola)" if delta <= SHORT_GAP_LIMIT else "LARGO (se deja como NaN, no se inventa dato)"
    print(f"  {prev} -> {curr}  ({delta})  [{tag}]")

rows_out = []
for i, d in enumerate(dates_epm):
    row = {"date": d}
    for a in aliases:
        row[a] = epm_long[d].get(a)
    rows_out.append(row)

# interpolacion lineal solo para huecos cortos, columna por columna
for a in aliases:
    series = [(r["date"], r[a]) for r in rows_out]
    known_idx = [i for i, (_, v) in enumerate(series) if v is not None]
    for gi in range(len(known_idx) - 1):
        i0, i1 = known_idx[gi], known_idx[gi + 1]
        if i1 - i0 <= 1:
            continue
        t0, v0 = series[i0]
        t1, v1 = series[i1]
        if t1 - t0 > SHORT_GAP_LIMIT:
            continue  # hueco largo (incluye la brecha real) -> se deja en None
        total_sec = (t1 - t0).total_seconds()
        for j in range(i0 + 1, i1):
            tj = series[j][0]
            frac = (tj - t0).total_seconds() / total_sec
            rows_out[j][a] = v0 + frac * (v1 - v0)

with open(OUT_DIR / "EPM_completo.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date"] + aliases)
    for r in rows_out:
        writer.writerow([r["date"].isoformat()] + [r[a] for a in aliases])

n_nan_final = sum(1 for r in rows_out for a in aliases if r[a] is None)
print(f"Guardado {OUT_DIR / 'EPM_completo.csv'}: {len(rows_out)} filas, {n_nan_final} celdas NaN "
      f"(huecos largos, incluida la brecha real, dejados intencionalmente sin rellenar)")

# ---------------------------------------------------------------------------
# TPM: instrument,variable,value,date (UTC, a veces con fraccion de segundo)
# ---------------------------------------------------------------------------
print()
print("=== TPM ===")
# clave de deduplicacion = (datetime YA redondeado al minuto, variable), no el
# string crudo -- si no, las 1148 filas con fraccion de segundo (reloj desfasado
# de la rejilla nominal) quedarian como timestamps "fantasma" sin fusionarse
# con la lectura real de ese mismo instante.
raw_values = defaultdict(list)  # (datetime,variable) -> [valores]
with open(RAW_DIR / "TPM.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for r in reader:
        v = to_float(r["value"])
        if v is not None and "POT" in r["variable"] and v > 1000:
            # bug de separador decimal documentado en README 7.1 (x1000)
            v = v / 1000.0
        d = parse_tpm_date(r["date"])
        raw_values[(d, r["variable"])].append(v)

n_dup_keys = sum(1 for k, vs in raw_values.items() if len(vs) > 1)
print(f"Claves (date,variable) con mas de una lectura: {n_dup_keys} "
      f"(se promedian; valores tipicamente difieren <1%, ver analisis previo)")

tpm_long = defaultdict(dict)
variables = set()
for (d, var), vals in raw_values.items():
    vals_clean = [v for v in vals if v is not None]
    mean_v = sum(vals_clean) / len(vals_clean) if vals_clean else None
    tpm_long[d][var] = mean_v
    variables.add(var)

variables = sorted(variables)
dates_tpm = sorted(tpm_long)
print(f"Timestamps unicos: {len(dates_tpm)}  columnas: {variables}")
print(f"Rango: {dates_tpm[0]} -> {dates_tpm[-1]}")

with open(OUT_DIR / "TPM_completo.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "freq"] + variables)
    prev_d = None
    for d in dates_tpm:
        freq_min = (d - prev_d).total_seconds() / 60.0 if prev_d else ""
        prev_d = d
        row = [d.isoformat(), freq_min] + [tpm_long[d].get(v) for v in variables]
        writer.writerow(row)

n_nan_tpm = sum(1 for d in dates_tpm for v in variables if tpm_long[d].get(v) is None)
print(f"Guardado {OUT_DIR / 'TPM_completo.csv'}: {len(dates_tpm)} filas, {n_nan_tpm} celdas NaN (sin rellenar)")
