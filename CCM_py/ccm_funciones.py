"""
Funciones del analisis CCM (convergent cross mapping) entre TPM y EPM.

Procedimiento: Yuan, A. E. y Shou, W. (2020). Data-driven causal analysis of
observational time series: a synthesis. bioRxiv 2020.08.03.233692 (preprint),
seccion "Methods" (criterios de CCM). Software: pyEDM (laboratorio de Sugihara),
implementacion `legacy` de CCM (la nueva falla con numpy < 2.0).

Se usa en el cuaderno ccm_yuan_shou.ipynb. Esta en un modulo aparte para poder
repartir los 56 pares entre varios procesos (en Windows, las funciones que usa
un proceso hijo deben poder importarse desde un archivo).

Direccion analizada: la variedad (manifold) del EPM estima al TPM. Segun la
logica del CCM (Sugihara et al. 2012, segun Yuan y Shou, Fig. 8), eso busca la
huella de TPM -> EPM.
"""
import random
import warnings

import numpy as np
import pandas as pd
import pyEDM
from scipy.stats import kendalltau

# pyEDM.SurrogateData arma su tabla columna por columna y pandas avisa en cada una
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

N_SUSTITUTOS = 1000          # Yuan y Shou, Methods: 1000 sustitutos de fase aleatoria
L_MIN = 15                   # Yuan y Shou, Methods (Kendall): biblioteca minima de 15 vectores
PASO_L = 3                   # ... en incrementos de 3 vectores
MUESTRAS_POR_L = 50          # ... 50 bibliotecas por tamano, sin reemplazo
ALFA = 0.05
GRILLA_TAU = range(1, 7)     # Yuan y Shou, Methods: tau de 1 a 6
GRILLA_E = range(1, 7)       # ... y E de 1 a 6


def _df_par(y, x=None):
    """DataFrame con nombres sin espacios (pyEDM separa los nombres de columna por espacios)."""
    d = {'Time': np.arange(1, len(y) + 1), 'Y': y}
    if x is not None:
        d['X'] = x
    return pd.DataFrame(d)


def _rho(simplex_out):
    o = simplex_out[['Observations', 'Predictions']].dropna()
    return float(np.corrcoef(o['Observations'], o['Predictions'])[0, 1])


def elegir_E_tau(y):
    """
    E y tau que maximizan la prediccion univariada a un paso (Tp = 1) de la serie
    que recibe (EPM), por proyeccion simplex con leave-one-out (lib = pred = todo).
    Yuan y Shou, Methods. Devuelve (E, tau, rho, tabla_completa).
    """
    df = _df_par(y)
    n = len(y)
    filas = []
    for tau in GRILLA_TAU:
        for E in GRILLA_E:
            s = pyEDM.Simplex(dataFrame=df, columns='Y', target='Y', lib=f'1 {n}', pred=f'1 {n}',
                              E=E, tau=-tau, Tp=1)
            filas.append({'tau': tau, 'E': E, 'rho_prediccion': _rho(s)})
    tabla = pd.DataFrame(filas)
    mejor = tabla.loc[tabla['rho_prediccion'].idxmax()]
    return int(mejor['E']), int(mejor['tau']), float(mejor['rho_prediccion']), tabla


def habilidad_xmap(y, x, E, tau):
    """Habilidad de cross-map: la variedad de y estima x (Tp = 0), biblioteca completa, leave-one-out."""
    n = len(y)
    s = pyEDM.Simplex(dataFrame=_df_par(y, x), columns='Y', target='X', lib=f'1 {n}', pred=f'1 {n}',
                      E=E, tau=-tau, Tp=0)
    return _rho(s)


def criterio_2_sustitutos(y, x, E, tau, rho_real, semilla, n_sust=N_SUSTITUTOS):
    """
    Criterio 2 (Yuan y Shou, Methods): se reemplaza la serie estimada (TPM) por
    sustitutos de fase aleatoria de Ebisuzaki (pyEDM.SurrogateData) y se recalcula
    la habilidad. p = fraccion de sustitutos con habilidad >= la real.
    """
    random.seed(semilla)   # SurrogateData usa el generador `random` de Python
    sust = pyEDM.SurrogateData(dataFrame=_df_par(y, x), column='X', method='ebisuzaki',
                               numSurrogates=n_sust)
    rhos = np.array([habilidad_xmap(y, sust.iloc[:, k].to_numpy(), E, tau) for k in range(1, n_sust + 1)])
    p = float(np.mean(rhos >= rho_real))
    return p, rhos


def criterio_3_kendall(y, x, E, tau, semilla):
    """
    Criterio 3, procedimiento alternativo de Yuan y Shou (Methods), siguiendo a
    Chang et al. (2017): tamanos de biblioteca de 15 al maximo, de 3 en 3; 50
    bibliotecas sin reemplazo por tamano; mediana de la habilidad por tamano;
    prueba de Kendall tau de una cola (p de dos colas / 2).
    Pasa si tau > 0 y p <= 0.05.
    """
    n = len(y)
    L_max = n - (E - 1) * tau - 1
    tamanos = list(range(L_MIN, L_max + 1, PASO_L))
    r = pyEDM.CCM(dataFrame=_df_par(y, x), columns='Y', target='X', E=E, tau=-tau, Tp=0,
                  libSizes=tamanos, sample=MUESTRAS_POR_L, includeData=True, legacy=True, seed=semilla)
    # PredictStats1 = direccion columns -> target (Y estima X); se verifica contra libMeans
    st = r['PredictStats1']
    medias = st.groupby('LibSize')['rho'].mean()
    chequeo = r['libMeans'].set_index('LibSize')['Y:X']
    assert np.allclose(medias.values, chequeo.loc[medias.index].values, atol=1e-4), 'PredictStats1 no es Y:X'
    medianas = st.groupby('LibSize')['rho'].median()
    tau_k, p2 = kendalltau(medianas.index.values, medianas.values)
    return float(tau_k), float(p2 / 2), medianas


def procesar_par(args):
    """Un par TPM-EPM completo. Devuelve un dict con todos los resultados."""
    epm, tpm, y, x, E, tau, semilla = args
    rho_real = habilidad_xmap(y, x, E, tau)
    p2, rhos_sust = criterio_2_sustitutos(y, x, E, tau, rho_real, semilla)
    tau_k, p3, medianas = criterio_3_kendall(y, x, E, tau, semilla)
    return {
        'EPM': epm, 'TPM': tpm, 'E': E, 'tau': tau, 'n': len(y),
        'rho': rho_real,
        'criterio1_rho_positivo': rho_real > 0,
        'p_sustitutos': p2,
        'criterio2_significativo': p2 <= ALFA,
        'rho_sust_p95': float(np.percentile(rhos_sust, 95)),
        'kendall_tau': tau_k, 'p_kendall': p3,
        'criterio3_converge': (tau_k > 0) and (p3 <= ALFA),
        'rho_Lmin': float(medianas.iloc[0]), 'rho_Lmax': float(medianas.iloc[-1]),
    }
