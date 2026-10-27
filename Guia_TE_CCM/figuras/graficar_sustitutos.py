"""Figura ilustrativa de los sustitutos (guia de estudio). Usa pyEDM.SurrogateData real."""
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyEDM

d = pd.read_csv('figuras/sustitutos_ejemplo.csv')
random.seed(2026)
df = pd.DataFrame({'Time': d['t'], 'X': d['tpm']})
d['tpm_ebisuzaki'] = pyEDM.SurrogateData(dataFrame=df, column='X', method='ebisuzaki', numSurrogates=1).iloc[:, 1]
v = d.iloc[:120]

fig, ax = plt.subplots(5, 1, figsize=(10, 11), sharex=True, constrained_layout=True)
paneles = [('tpm', '(a) TPM Tilt(5) original (primeras diferencias cada 6 h)', 'k'),
           ('tpm_barajado', '(b) Sustituto barajado del TPM (para la TE efectiva)', 'tab:orange'),
           ('tpm_ebisuzaki', '(c) Sustituto de fase aleatoria (Ebisuzaki) del TPM (para el CCM)', 'tab:purple'),
           ('epm_simbolos', '(d) EPM Sensor 4 convertido a símbolos 1, 2, 3 (original)', 'k'),
           ('epm_markov', '(e) Sustituto por bootstrap de Markov del EPM en símbolos (para el p-valor de la TE)', 'tab:green')]
for a, (c, t, col) in zip(ax, paneles):
    estilo = dict(drawstyle='steps-mid') if 'epm' in c else {}
    a.plot(v['t'], v[c], color=col, lw=1, **estilo)
    a.set_title(t, fontsize=11, loc='left')
    if 'epm' in c:
        a.set_yticks([1, 2, 3])
ax[-1].set_xlabel('posición en la serie (cada paso = 6 h); se muestran las primeras 120 de 880')
fig.savefig('figuras/sustitutos_ejemplo.png', dpi=170)
print('ok')
