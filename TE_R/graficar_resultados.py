"""
Figuras de los resultados de transfer entropy (TE) para la presentacion.

Entrada : data/te_resultados_56_pares.csv  (generado por te_56_pares.R)
Salida  : figuras/te_valores_heatmap.png   (TE y TE efectiva, TPM -> EPM)
          figuras/te_pvalor_heatmap.png    (p-valor por bootstrap de Markov, TPM -> EPM)

No calcula nada nuevo: solo dibuja los valores que entrego RTransferEntropy.
Un p-valor de 0 significa que ninguna de las 300 replicas del bootstrap
alcanzo la TE real; se rotula "<1/300".

Ejecutar desde la carpeta TE_R:  python graficar_resultados.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
FIG = AQUI / 'figuras'
FIG.mkdir(exist_ok=True)
N_BOOT = 300      # replicas del bootstrap (valor por defecto del paquete)
ALFA = 0.05

series_tpm = ['POT(1)', 'POT(2)', 'POT(3)', 'POT(4)', 'POT(5)', 'POT(6)', 'POT(7)',
              'Tilt(1)', 'Tilt(2)', 'Tilt(3)', 'Tilt(4)', 'Tilt(5)', 'Tilt(6)', 'Tilt(7)']
series_epm = ['Sensor 1 (5m)', 'Sensor 2 (10m)', 'Sensor 3 (5m)', 'Sensor 4 (10m)']

r = pd.read_csv(AQUI / 'data' / 'te_resultados_56_pares.csv')


def matriz(col):
    return r.pivot(index='EPM', columns='TPM', values=col).loc[series_epm, series_tpm]


def dibujar(ax, mat, titulo, etiqueta_barra, fmt, cmap, marcar=None, vmin=None, vmax=None,
            texto_blanco=None, tam_texto=11):
    """texto_blanco(v) -> True si la celda es oscura y el texto debe ser blanco."""
    im = ax.imshow(mat.values, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
    tope = np.nanmax(mat.values) if vmax is None else vmax
    if texto_blanco is None:
        texto_blanco = lambda v: v > 0.6 * tope
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.values[i, j]
            txt = fmt(v)
            if marcar is not None and marcar.values[i, j]:
                txt += '*'
            ax.text(j, i, txt, ha='center', va='center', fontsize=tam_texto,
                    color='white' if texto_blanco(v) else 'black')
    ax.set_xticks(range(len(series_tpm)), series_tpm, rotation=45, ha='right', fontsize=12)
    ax.set_yticks(range(len(series_epm)), series_epm, fontsize=12)
    ax.set_title(titulo, fontsize=13)
    plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label=etiqueta_barra)


significativo = matriz('p_tpm_a_epm') < ALFA

# --- Figura 1: TE real y TE efectiva ---
fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.6), constrained_layout=True)
tope = float(matriz('te_tpm_a_epm').values.max())
dibujar(a1, matriz('te_tpm_a_epm'), 'TE real, TPM → EPM (bits)', 'bits',
        lambda v: f'{v:.3f}', 'Blues', vmin=0, vmax=tope)
dibujar(a2, matriz('ete_tpm_a_epm'), 'TE efectiva = TE real − promedio de 100 TE con TPM barajado (bits)',
        'bits', lambda v: f'{v:.3f}', 'Blues', vmin=0, vmax=tope)
fig.savefig(FIG / 'te_valores_heatmap.png', dpi=200)
plt.close(fig)

# --- Figura 2: p-valor ---
fig, ax = plt.subplots(figsize=(11, 3.7), constrained_layout=True)
pmat = matriz('p_tpm_a_epm')
dibujar(ax, pmat, f'p-valor, TPM → EPM (bootstrap de Markov, {N_BOOT} réplicas).  * = p < {ALFA}',
        'p-valor', lambda v: '<1/300' if v == 0 else f'{v:.3f}', 'Greens_r',
        marcar=significativo, vmin=0, vmax=1, texto_blanco=lambda v: v < 0.25, tam_texto=9)
fig.savefig(FIG / 'te_pvalor_heatmap.png', dpi=200)
plt.close(fig)

print(f'Pares TPM -> EPM con p < {ALFA}: {int(significativo.values.sum())} de {significativo.size}')
print(f'Guardadas en {FIG}')
