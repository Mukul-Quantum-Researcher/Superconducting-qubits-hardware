"""Reanalyse saved simulated populations; does not rerun trajectory dynamics."""
from pathlib import Path
import ast
import csv
import json
import os
import re
import numpy as np
from scipy.optimize import curve_fit
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]
notebook=json.loads((root/'notebooks/qubit_spectroscopy.ipynb').read_text(encoding='utf-8'))
def recorded(index):
    return ''.join(''.join(o.get('text',[])) for o in notebook['cells'][index].get('outputs',[]) if o.get('output_type')=='stream')
namespace={'np':np,'curve_fit':curve_fit}
module=ast.parse(''.join(notebook['cells'][1]['source']))
functions=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in {'chevron_model','fit_chevron','sin_squared'}]
exec(compile(ast.Module(body=functions,type_ignores=[]),'<supplied-fit-functions>','exec'),namespace)
rows=[ast.literal_eval(x) for x in re.findall(r'p1_values:\s*(\[[^\n]+\])',recorded(15))]
assert len(rows)==9 and all(len(row)==20 for row in rows)
probabilities=np.asarray(rows);freq=np.arange(5000,5020);times=np.arange(100,501,50)*.0012
assert np.all((probabilities>=0)&(probabilities<=1))
fit=namespace['fit_chevron'](freq,times,probabilities,[5011,5,0,1,0])
F,T=np.meshgrid(freq,times)
pred=namespace['chevron_model']((F,T),*fit.values())
rmse=float(np.sqrt(np.mean((pred-probabilities)**2)))
assert abs(fit['f01_MHz']-5011)<.2 and abs(fit['fRabi_MHz']-5)<.2
fig,axes=plt.subplots(1,3,figsize=(13,3.6),layout='constrained')
for ax,data,title in zip(axes,[probabilities,pred,probabilities-pred],['Simulated populations','Chevron fit','Simulation − fit']):
    im=ax.pcolormesh(F,T,data,shading='auto',cmap='RdBu_r' if title.startswith('Simulation') else 'viridis')
    ax.set(xlabel='Drive frequency (MHz)',ylabel='Pulse duration (µs)',title=title);fig.colorbar(im,ax=ax,label='P₁' if title!='Simulation − fit' else 'Residual')
(root/'figures').mkdir(exist_ok=True);fig.savefig(root/'figures/spectroscopy-chevron.png',dpi=150)

values=re.findall(r't_end:\s*([\d.eE+-]+) us, flat_duration:\s*([\d.eE+-]+) us, P\(\|1>\):\s*([\d.eE+-]+)',recorded(22))
rabi=np.array(values,dtype=float);assert rabi.shape[0]>=30
model=namespace['sin_squared'];solutions=[]
for initial_frequency in [2.5,4,5,6,8]:
    p,_=curve_fit(model,rabi[:,0],rabi[:,2],p0=[1,initial_frequency,0],bounds=([0,.1,-np.pi],[1.2,15,np.pi]),maxfev=10000)
    solutions.append((float(np.mean((model(rabi[:,0],*p)-rabi[:,2])**2)),p))
rabi_error,parameters=min(solutions,key=lambda x:x[0])
fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
ax.plot(rabi[:,0],rabi[:,2],'o',ms=4,label='Saved simulated populations')
grid=np.linspace(rabi[:,0].min(),rabi[:,0].max(),500)
ax.plot(grid,model(grid,*parameters),label='Recomputed sine-squared fit')
ax.set(xlabel='Pulse duration (µs)',ylabel='Excited-state population',title='Rabi oscillations in the simulated transmon');ax.legend();ax.grid(alpha=.2)
fig.savefig(root/'figures/spectroscopy-rabi.png',dpi=150)
out=root/'results';out.mkdir(exist_ok=True)
with (out/'spectroscopy-chevron.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['duration_us','frequency_MHz','simulated_P1'])
    for i,t in enumerate(times):
        for j,frequency in enumerate(freq):w.writerow([t,frequency,probabilities[i,j]])
summary={'scope':'Fits recomputed from recorded simulation output; no new trajectory integration.','chevron_points':int(probabilities.size),'chevron_fit':{k:float(v) for k,v in fit.items()},'chevron_rmse':rmse,'rabi_points':len(rabi),'rabi_refit_frequency_MHz':float(parameters[1]),'rabi_rmse':float(np.sqrt(rabi_error)),'limits':['The coarse 10 MHz Lorentzian fit is under-resolved and its phase argument is unused.','The original Rabi fit output is inconsistent with the recorded oscillations; the separate refit uses multiple starting points.','Quasi-static Gaussian offsets are not a full 1/f noise spectrum.','The voltage-to-drive conversion is assumed, not an experimental calibration.']}
(out/'spectroscopy-analysis.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
