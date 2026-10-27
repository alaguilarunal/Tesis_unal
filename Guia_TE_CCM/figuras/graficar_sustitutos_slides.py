"""Tres figuras (real arriba, sustituto abajo) para las diapositivas. Mismos datos que sustitutos_ejemplo.png."""
import random
import matplotlib.pyplot as plt
import pandas as pd
import pyEDM

d = pd.read_csv('figuras/sustitutos_ejemplo.csv')
random.seed(2026)
d['tpm_ebisuzaki'] = pyEDM.SurrogateData(dataFrame=pd.DataFrame({'Time': d['t'], 'X': d['tpm']}),
                                         column='X', method='ebisuzaki', numSurrogates=1).iloc[:, 1]
v = d.iloc[:120]
casos = {
    'barajado':  ('tpm', 'tpm_barajado', 'TPM Tilt(5) real', 'Sustituto barajado (100 por par)', 'tab:orange', False),
    'markov':    ('epm_simbolos', 'epm_markov', 'EPM Sensor 4 real, en símbolos 1-2-3',
                  'Sustituto por bootstrap de Markov (300 por par)', 'tab:green', True),
    'ebisuzaki': ('tpm', 'tpm_ebisuzaki', 'TPM Tilt(5) real', 'Sustituto de fase aleatoria (1000 por par)', 'tab:purple', False),
}
for nombre, (c_real, c_sust, t_real, t_sust, col, simb) in casos.items():
    fig, ax = plt.subplots(2, 1, figsize=(6.4, 4.6), sharex=True, constrained_layout=True)
    for a, c, t, k in ((ax[0], c_real, t_real, 'k'), (ax[1], c_sust, t_sust, col)):
        a.plot(v['t'], v[c], color=k, lw=1, **({'drawstyle': 'steps-mid'} if simb else {}))
        a.set_title(t, fontsize=11, loc='left')
        if simb:
            a.set_yticks([1, 2, 3])
    if not simb:
        lim = max(abs(v[c_real]).max(), abs(v[c_sust]).max()) * 1.05
        for a in ax:
            a.set_ylim(-lim, lim)
    ax[1].set_xlabel('posición (cada paso = 6 h); primeras 120 de 880')
    fig.savefig(f'figuras/sustituto_{nombre}.png', dpi=200)
print('ok')
