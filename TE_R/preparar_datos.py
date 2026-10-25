"""
Prepara las series para la transfer entropy en R (RTransferEntropy).

Entrada : ../Data_limpia_completa/EPM_completo.csv y TPM_completo.csv
Salida  : data/series_diferencias_6h.csv  (18 columnas: 4 EPM + 14 TPM)

Pasos:
1. Tramo previo a la brecha (antes de 2023-06-20).
2. Rejilla comun de 6 h: promedio de cada serie en ventanas de 6 h. Antes de la
   brecha el EPM se lee a las 01, 07, 13 y 19 h y el TPM a las 00, 06, 12 y 18 h;
   ambas lecturas caen en la misma ventana.
3. Union de EPM y TPM por fecha. No se rellenan huecos: las ventanas vacias
   quedan como NA (RTransferEntropy elimina las filas con NA).
4. Primeras diferencias: Behrendt et al. (2019), SoftwareX 10, 100265, sec. 6:
   "As the calculation of transfer entropy requires stationary data, we
   calculate log-returns". Las primeras diferencias son la adaptacion de esa
   exigencia a estas series (no son precios); es una adaptacion declarada.

Ejecutar desde la carpeta TE_R:  python preparar_datos.py
"""
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DATOS = AQUI.parent / 'Data_limpia_completa'
SALIDA = AQUI / 'data' / 'series_diferencias_6h.csv'
BRECHA_INICIO = pd.Timestamp('2023-06-20')

epm = pd.read_csv(DATOS / 'EPM_completo.csv', parse_dates=['date'])
tpm = pd.read_csv(DATOS / 'TPM_completo.csv', parse_dates=['date'])

epm_6h = epm[epm['date'] < BRECHA_INICIO].set_index('date').sort_index().resample('6h').mean()
tpm_6h = (tpm[tpm['date'] < BRECHA_INICIO].drop(columns=['freq'])
          .set_index('date').sort_index().resample('6h').mean())

niveles = epm_6h.join(tpm_6h, how='inner')
diferencias = niveles.diff().iloc[1:]

SALIDA.parent.mkdir(exist_ok=True)
diferencias.to_csv(SALIDA, index_label='date')

print(f'Ventana: {niveles.index.min()} a {niveles.index.max()}  ({len(niveles)} posiciones de 6 h)')
print(f'Filas en diferencias: {len(diferencias)}  |  filas con algun NA: {diferencias.isna().any(axis=1).sum()}')
print(f'Guardado: {SALIDA}')
