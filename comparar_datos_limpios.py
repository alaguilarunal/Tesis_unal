"""
Compara Data_limpia_completa/{EPM,TPM}_completo.csv (generados a partir de Data_cruda)
contra data/EPMDATA_INTERPOLATED_v2.csv y data/TPMDATA_CLEANED.csv (los que ya se usan
en libro 1.ipynb), restringiendo ambos al periodo que se superpone.
"""
import csv
from datetime import datetime
from pathlib import Path

OLD_EPM = Path("data/EPMDATA_INTERPOLATED_v2.csv")
OLD_TPM = Path("data/TPMDATA_CLEANED.csv")
NEW_EPM = Path("Data_limpia_completa/EPM_completo.csv")
NEW_TPM = Path("Data_limpia_completa/TPM_completo.csv")


def load_wide(path, date_fmt="%Y-%m-%d %H:%M:%S"):
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = [c for c in reader.fieldnames if c != "date"]
        data = {}
        for r in reader:
            d = datetime.strptime(r["date"], date_fmt)
            data[d] = {c: (float(r[c]) if r[c] not in ("", None) else None) for c in cols}
    return cols, data


def compare(name, old_cols, old_data, new_cols, new_data, tol=1e-3):
    print(f"\n=== {name} ===")
    old_dates = sorted(old_data)
    new_dates = sorted(new_data)
    print(f"Antiguo: {len(old_dates)} filas, rango {old_dates[0]} -> {old_dates[-1]}")
    print(f"Nuevo (recortado al mismo rango): {len(new_dates)} filas totales en Data_limpia_completa")

    common_cols = [c for c in old_cols if c in new_cols]
    missing_cols = [c for c in old_cols if c not in new_cols]
    extra_cols = [c for c in new_cols if c not in old_cols]
    print(f"Columnas en comun: {common_cols}")
    if missing_cols:
        print(f"  Columnas del antiguo que NO estan en el nuevo: {missing_cols}")
    if extra_cols:
        print(f"  Columnas nuevas que no estaban antes: {extra_cols}")

    matched, missing_date, diffs = 0, 0, {c: [] for c in common_cols}
    for d in old_dates:
        if d not in new_data:
            missing_date += 1
            continue
        matched += 1
        for c in common_cols:
            ov, nv = old_data[d].get(c), new_data[d].get(c)
            if ov is None or nv is None:
                continue
            diffs[c].append(abs(ov - nv))

    print(f"Timestamps del antiguo encontrados tambien en el nuevo: {matched}/{len(old_dates)}")
    if missing_date:
        print(f"  Timestamps del antiguo AUSENTES en el nuevo: {missing_date}")

    for c in common_cols:
        vals = diffs[c]
        if not vals:
            print(f"  {c}: sin pares comparables")
            continue
        max_d, mean_d = max(vals), sum(vals) / len(vals)
        n_bad = sum(1 for v in vals if v > tol)
        flag = "OK" if n_bad == 0 else f"*** {n_bad} valores difieren > {tol} ***"
        print(f"  {c:16s}  n={len(vals):5d}  diff_max={max_d:.6f}  diff_media={mean_d:.6f}  {flag}")


# --- EPM ---
old_cols, old_data = load_wide(OLD_EPM)
new_cols, new_data_full = load_wide(NEW_EPM, date_fmt="%Y-%m-%dT%H:%M:%S")
lo, hi = min(old_data), max(old_data)
new_data = {d: v for d, v in new_data_full.items() if lo <= d <= hi}
compare("EPM", old_cols, old_data, new_cols, new_data)

# --- TPM ---
old_cols, old_data = load_wide(OLD_TPM)
old_cols = [c for c in old_cols if c != "freq"]
new_cols, new_data_full = load_wide(NEW_TPM, date_fmt="%Y-%m-%dT%H:%M:%S")
new_cols = [c for c in new_cols if c != "freq"]
lo, hi = min(old_data), max(old_data)
new_data = {d: v for d, v in new_data_full.items() if lo <= d <= hi}
compare("TPM", old_cols, old_data, new_cols, new_data, tol=1e-2)
