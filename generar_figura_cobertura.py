"""
Genera img/cobertura_temporal.png para la diapositiva "Cobertura temporal".

Un unico mensaje: cuando hay datos de EPM vs. MPT, y donde cae la brecha real
del EPM. Se usan 2 filas (EPM, MPT), no 18: las 4 series EPM comparten
exactamente el mismo rango entre si (verificado), y las 14 series MPT tambien
(verificado: todas 2017-12-04 a 2025-10-10) -- desagregar por sensor/nodo no
anade ninguna informacion a este nivel, solo ruido visual.

Datos: Data_limpia_completa/{EPM,TPM}_completo.csv (cubren la brecha real; ver
limpiar_datos_crudos.py). No se fabrica ningun numero: todo sale de estos CSV.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

BRECHA_INICIO = pd.Timestamp("2023-06-20")
BRECHA_FIN = pd.Timestamp("2025-05-01")

epm = pd.read_csv("Data_limpia_completa/EPM_completo.csv", parse_dates=["date"])
tpm = pd.read_csv("Data_limpia_completa/TPM_completo.csv", parse_dates=["date"])

epm_t0, epm_t1 = epm["date"].min(), epm["date"].max()
tpm_t0, tpm_t1 = tpm["date"].min(), tpm["date"].max()

fig, ax = plt.subplots(figsize=(10, 2.8))

BAR_H = 0.35
ax.broken_barh(
    [(mdates.date2num(tpm_t0), mdates.date2num(tpm_t1) - mdates.date2num(tpm_t0))],
    (2 - BAR_H / 2, BAR_H), facecolors="seagreen",
)
ax.broken_barh(
    [(mdates.date2num(epm_t0), mdates.date2num(BRECHA_INICIO) - mdates.date2num(epm_t0)),
     (mdates.date2num(BRECHA_FIN), mdates.date2num(epm_t1) - mdates.date2num(BRECHA_FIN))],
    (1 - BAR_H / 2, BAR_H), facecolors="steelblue",
)

ax.axvspan(BRECHA_INICIO, BRECHA_FIN, color="gray", alpha=0.25)
ax.axvline(BRECHA_INICIO, color="black", linestyle="--", linewidth=0.8)
ax.axvline(BRECHA_FIN, color="black", linestyle="--", linewidth=0.8)
ax.annotate(
    "681 días sin EPM\n(MPT sigue midiendo)",
    xy=(BRECHA_INICIO + (BRECHA_FIN - BRECHA_INICIO) / 2, 2.75),
    ha="center", va="center", fontsize=10,
)

ax.set_yticks([1, 2])
ax.set_yticklabels(["EPM\n(4 sensores de deformación)", "MPT\n(14 series: POT + Tilt)"], fontsize=10)
ax.set_ylim(0.3, 3.1)
ax.set_xlabel("Fecha", fontsize=10)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

plt.tight_layout()
out_path = "../Presentaciones/Template_Beamer_UFC/img/cobertura_temporal.png"
plt.savefig(out_path, dpi=150)
print(f"Guardado: {out_path}")
