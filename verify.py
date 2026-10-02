"""Independent arithmetic and invariance checks. Run after analysis.py."""
import csv,io,json
from pathlib import Path
import numpy as np
import analysis as a
r=a.read('games_corrected.csv'); d=a.arrays(r)
resources=a.read('resources.csv');res={x['Program']:float(x['Midpoint ($M)']) for x in resources}
assert len(res)==len(resources)==68
for x in resources:
    lo,hi,mid=[float(x[k]) for k in ['Payroll Low ($M)','Payroll High ($M)','Midpoint ($M)']]
    assert 0<lo<=hi and abs(mid-(lo+hi)/2)<1e-10
for x in r:
    ra,rb=res[x['Team A']],res[x['Team B']]
    assert abs(float(x['Team A Resource Mid ($M)'])-ra)<1e-10
    assert abs(float(x['Team B Resource Mid ($M)'])-rb)<1e-10
    assert abs(float(x['Resource Gap ($M)'])-abs(ra-rb))<1e-10
    assert abs(float(x['Resource Gap %'])-abs(ra-rb)/min(ra,rb))<1e-8
before=a.read('games_original.csv')
changes=[(x['Date'],x['Team A'],x['Team B'],k) for x,y in zip(before,r) for k in x if x[k]!=y[k]]
assert len(changes)==12 and len({x[:3] for x in changes})==2
assert len(r)==347 and int(d['resolved'].sum())==308 and int(d['win'][d['resolved']].sum())==201
assert int(np.isnan(d['signed_total']).sum())==1
q=r[267]; assert q['Winner']=='Northwestern' and float(q['Spread Error (pts)'])==.5 and float(q['Total Error Abs (pts)'])==32.5
assert sum(x['Team A Resource Mid ($M)']==x['Team B Resource Mid ($M)'] for x in r)==38
mask=d['resolved']; rr=[x for x,m in zip(r,mask) if m]; X=np.column_stack([np.ones(mask.sum()),d['market'][mask],d['gap'][mask]]); y=d['margin'][mask]
b,h,c,n=a.fit(y,X,rr)
# Independent normal-equation fit, distinct from lstsq implementation.
assert np.allclose(b,np.linalg.solve(X.T@X,X.T@y),atol=1e-10)
assert np.allclose(X.T@(y-X@b),0,atol=1e-8)
# Source row orientation and order must not alter shared-team uncertainty.
reverse=[dict(x,**{'Team A':x['Team B'],'Team B':x['Team A']}) for x in rr[::-1]]
bb,hh,cc,nn=a.fit(y[::-1],X[::-1],reverse)
assert np.allclose(c,cc,rtol=1e-9,atol=1e-9)
# Independent explicit dyadic-pair covariance; catches group subtraction errors.
bread=np.linalg.inv(X.T@X); s=X*(y-X@b)[:,None]; meat=np.zeros((3,3))
for i,x in enumerate(rr):
    tx={x['Team A'],x['Team B']}
    for j,z in enumerate(rr):
        if tx.intersection((z['Team A'],z['Team B'])):meat+=np.outer(s[i],s[j])
assert np.allclose(c,n/(n-3)*bread@meat@bread,rtol=1e-9,atol=1e-9)
checks=list(csv.DictReader((a.OUT/'checks.csv').open()))
assert all(x['result']=='pass' for x in checks),checks
report={'game_count':347,'resolved':308,'wins':201,'missing_score_games':1,'resource_ties':38,'normal_equation_check':'pass','row_orientation_and_order':'pass','independent_pair_covariance':'pass','archive_reproduction':'pass'}
report.update({'resource_join_consistency':'pass for all 347 rows','resource_range_midpoints':'pass for all 68 programs','correction_field_entries':12,'corrected_games':2})
(a.OUT/'independent_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
