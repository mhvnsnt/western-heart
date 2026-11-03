import json,sys,numpy as np,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'.'); from fit_proxies import load_template, TEMPLATES
assets=sys.argv[2:]; out=sys.argv[1]
fig,ax=plt.subplots(2,len(TEMPLATES),figsize=(3*len(TEMPLATES),6.4))
cols={'hair':'#8b4513','eyebrows':'#000','eyelashes':'#0055ff','beard':'#d00'}
for c,n in enumerate(TEMPLATES):
  t=load_template(n); m=t['headw']>0.3; H=t['Hinv']
  P=(H[:3,:3]@t['P'][m].T).T+H[:3,3]
  for r,(i,j) in enumerate([(0,1),(2,1)]):
    a=ax[r,c]; a.scatter(P[:,i],P[:,j],s=0.3,c='#ccc'); a.set_aspect('equal'); a.axis('off')
    for aid in assets:
      J=json.load(open(f'fit/{aid}/{n}.json')); Q=np.array(J['pos']).reshape(-1,3)
      a.scatter(Q[:,i],Q[:,j],s=0.3,c=cols[J['kind']])
  ax[0,c].set_title(n,fontsize=8)
plt.tight_layout(); plt.savefig(out,dpi=70)
