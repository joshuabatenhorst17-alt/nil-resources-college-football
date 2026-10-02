"""Auditable NIL QC rerun. Python >=3.11, NumPy and SciPy; no hidden inputs.
Run from this directory: python analysis.py. Output results/ is regenerated.
OLS HC3 uses normal Wald inference, matching the archived analysis.
Dyadic meat explicitly sums score outer products for pairs sharing either team,
including self-pairs once. This handles repeated matchups correctly.
"""
import csv, io, json, hashlib, platform
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit
from scipy.stats import norm, binomtest, chi2_contingency, fisher_exact, kruskal, ttest_ind, mannwhitneyu, chi2

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
SEED=20260930
def read(name):
    return list(csv.DictReader(io.StringIO((ROOT/'data'/name).read_text())))
def write(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def number(r,k): return float(r[k]) if r[k] else np.nan
def arrays(rows,resources=None):
    a=np.array([number(r,'Team A Score') for r in rows]); b=np.array([number(r,'Team B Score') for r in rows])
    ra=np.array([resources[r['Team A']] if resources else number(r,'Team A Resource Mid ($M)') for r in rows])
    rb=np.array([resources[r['Team B']] if resources else number(r,'Team B Resource Mid ($M)') for r in rows])
    side=np.sign(ra-rb); gap=np.abs(ra-rb)/np.minimum(ra,rb)
    fav=np.array([1 if r['Market Favorite']==r['Team A'] else -1 for r in rows])
    spread=np.array([number(r,'Closing Spread') for r in rows]); total=np.array([number(r,'Closing Total') for r in rows])
    margin=(a-b)*side; market=spread*fav*side; residual=margin-market
    return dict(margin=margin,market=market,residual=residual,gap=gap,win=(margin>0).astype(float),resolved=(side!=0)&np.isfinite(a+b),
                binary=(side!=0)&np.isfinite(a+b)&(a!=b),spread=np.abs((a-b)*fav-spread),
                signed_spread=(a-b)*fav-spread,signed_total=a+b-total,absolute_total=np.abs(a+b-total))
def fit(y,X,rows,logit=False):
    mask=np.isfinite(y)&np.all(np.isfinite(X),axis=1); y=y[mask]; X=X[mask]; rows=[r for r,m in zip(rows,mask) if m]
    if logit:
        beta=np.zeros(X.shape[1]); converged=False
        for _ in range(100):
            p=expit(X@beta); H=X.T@((p*(1-p))[:,None]*X); step=np.linalg.solve(H,X.T@(y-p)); beta+=step
            if np.max(np.abs(step))<1e-10: converged=True; break
        if not converged: raise RuntimeError('Logit did not converge')
        p=expit(X@beta); bread=np.linalg.inv(X.T@((p*(1-p))[:,None]*X)); scores=X*(y-p)[:,None]; hc=bread@scores.T@scores@bread
    else:
        beta=np.linalg.lstsq(X,y,rcond=None)[0]; bread=np.linalg.inv(X.T@X); resid=y-X@beta
        scores=X*resid[:,None]; h=np.einsum('ij,jk,ik->i',X,bread,X)
        adj=scores/(1-h)[:,None]; hc=bread@adj.T@adj@bread
    teams=defaultdict(lambda:np.zeros(X.shape[1])); pairs=defaultdict(lambda:np.zeros(X.shape[1]))
    for r,s in zip(rows,scores):
        teams[r['Team A']]+=s; teams[r['Team B']]+=s; pairs[tuple(sorted((r['Team A'],r['Team B'])))]+=s
    meat=sum(np.outer(s,s) for s in teams.values())-sum(np.outer(s,s) for s in pairs.values())
    dy=(len(y)/(len(y)-X.shape[1]))*(bread@meat@bread)
    return beta,hc,dy,len(y)
def stat(beta,cov,j):
    variance=cov[j,j]
    if variance<0: return dict(coef=float(beta[j]),se=None,p=None,ci_low=None,ci_high=None,warning='negative dyadic variance')
    se=np.sqrt(variance); return dict(coef=float(beta[j]),se=float(se),p=float(2*norm.sf(abs(beta[j]/se))),ci_low=float(beta[j]-norm.ppf(.975)*se),ci_high=float(beta[j]+norm.ppf(.975)*se))
def models(rows,label,resources=None,quadratic=False):
    d=arrays(rows,resources); out=[]
    for name in ['margin','residual','win','spread','signed_total','absolute_total']:
        mask=d['binary'] if name=='win' else (d['resolved'] if name in ['margin','residual'] else np.isfinite(d[name]))
        rr=[r for r,m in zip(rows,mask) if m]; y=d[name][mask]; g=d['gap'][mask]
        cols=[np.ones(len(y))]
        if name in ['margin','win']: cols.append(d['market'][mask])
        cols.append(g)
        if quadratic: cols.append(g*g)
        beta,hc,dy,n=fit(y,np.column_stack(cols),rr,name=='win')
        for typ,cov in [('HC3' if name!='win' else 'sandwich',hc),('dyadic',dy)]:
            out.append(dict(dataset=label,model=name,term='gap_squared' if quadratic else 'gap',covariance=typ,n=n,**stat(beta,cov,len(cols)-1)))
    return out
def descriptions(rows,label):
    d=arrays(rows); out=[]
    for tier in ['Overall']+sorted({r['Frozen Tier'] for r in rows}):
        m=np.array([tier=='Overall' or r['Frozen Tier']==tier for r in rows]); resolved=m&d['binary']; valid=m&np.isfinite(d['signed_total']); errors=d['signed_total'][valid]
        out.append(dict(dataset=label,tier=tier,rows=int(m.sum()),resolved=int(resolved.sum()),wins=int(d['win'][resolved].sum()),win_rate=float(d['win'][resolved].mean()),spread_mae=float(np.nanmean(d['spread'][m])),total_mae=float(np.mean(np.abs(errors))),signed_total=float(np.mean(errors)),over=int((errors>0).sum()),under=int((errors<0).sum()),push=int((errors==0).sum())))
    return out
def seasonal(rows,label):
    rr=[r for r in rows if r['Week'].isdigit()]; d=arrays(rr); w=np.array([float(r['Week']) for r in rr]); out=[]
    for name in ['spread','signed_spread','absolute_total','signed_total']:
        b,h,c,n=fit(d[name],np.column_stack([np.ones(len(w)),w]),rr)
        out.append(dict(dataset=label,model=name,term='week',covariance='dyadic',n=n,**stat(b,c,1)))
    for name in ['residual','spread','signed_total','absolute_total']:
        mask=d['resolved'] if name=='residual' else np.isfinite(d[name]); y=d[name][mask]; ww=w[mask]; g=d['gap'][mask]; sub=[r for r,m in zip(rr,mask) if m]
        b,h,c,n=fit(y,np.column_stack([np.ones(len(y)),ww,g,ww*g]),sub)
        out.append(dict(dataset=label,model=name,term='week_gap',covariance='dyadic',n=n,**stat(b,c,3)))
    return out
def phases(rows,label):
    out=[]; tests=[]
    for tier in sorted({r['Frozen Tier'] for r in rows}):
        groups=[]
        for name,lo,hi in [('early',0,4),('mid',5,8),('late',9,14),('postseason',15,16)]:
            rr=[r for r in rows if r['Frozen Tier']==tier and r['Week'].isdigit() and lo<=int(r['Week'])<=hi and r['Team A Score']]
            e=arrays(rr)['signed_total'] if rr else np.array([])
            if len(e): out.append(dict(dataset=label,tier=tier,phase=name,n=len(e),mae=float(np.mean(abs(e))),signed=float(np.mean(e)),over_rate=float(np.mean(e>0))))
            if name!='postseason': groups.append(abs(e))
        tests.append(dict(dataset=label,tier=tier,kruskal_p=float(kruskal(*groups).pvalue),mid_late_welch_p=float(ttest_ind(groups[1],groups[2],equal_var=False).pvalue),mid_late_mannwhitney_p=float(mannwhitneyu(groups[1],groups[2],alternative='two-sided').pvalue)))
    return out,tests
def validate(rows):
    assert len(rows)==347
    keys=[(r['Date'],tuple(sorted([r['Team A'],r['Team B']]))) for r in rows]; assert len(set(keys))==len(keys)
    checks=[]
    for r in rows:
        if not r['Team A Score']: continue
        a=number(r,'Team A Score'); b=number(r,'Team B Score'); fav=1 if r['Market Favorite']==r['Team A'] else -1
        expected={'Winner':r['Team A'] if a>b else r['Team B'] if b>a else 'Tie','Favorite Margin':(a-b)*fav,'Spread Error (pts)':abs((a-b)*fav-number(r,'Closing Spread')),'Combined Score':a+b,'Total Error Signed (pts)':a+b-number(r,'Closing Total'),'Total Error Abs (pts)':abs(a+b-number(r,'Closing Total'))}
        for k,v in expected.items():
            assert (r[k]==v if isinstance(v,str) else abs(float(r[k])-v)<1e-7),(r['Date'],r['Team A'],k)
    checks.append({'check':'game keys and derived score fields','result':'pass','rows':len(rows)})
    return checks
def main():
    before=read('games_original.csv'); after=read('games_corrected.csv'); resources=read('resources.csv')
    checks=validate(before)+validate(after); diffs=[]
    for a,b in zip(before,after):
        for k in a:
            if a[k]!=b[k]: diffs.append({'game':b['Date']+' '+b['Team A']+' vs '+b['Team B'],'field':k,'before':a[k],'after':b[k]})
    assert len({x['game'] for x in diffs})==2
    write('correction_diff.csv',diffs)
    result=models(before,'original')+models(after,'QC-v3'); write('primary.csv',result)
    expected=[-1.2561409,-.076442,-.2129396,-.1339036,4.2576374,2.8183133]
    hc=[r for r in result if r['dataset']=='original' and r['covariance']!='dyadic']; assert all(abs(r['coef']-v)<1e-6 for r,v in zip(hc,expected))
    expected_dy=[3.606079,3.220501,.498031,2.107585,3.190669,2.673111]
    dy=[r for r in result if r['dataset']=='original' and r['covariance']=='dyadic']; checks.append({'check':'archived dyadic SE reproduction','result':'pass' if all(abs(r['se']-v)<2e-6 for r,v in zip(dy,expected_dy)) else 'FAIL','rows':len(dy)})
    assert all(x['result']=='pass' for x in checks), checks
    write('descriptive.csv',descriptions(before,'original')+descriptions(after,'QC-v3'))
    write('nonlinear.csv',models(before,'original',quadratic=True)+models(after,'QC-v3',quadratic=True))
    write('archive_only.csv',models([r for r in before if 'CFP' not in r['Source/Notes']],'original-primary')+models([r for r in after if 'CFP' not in r['Source/Notes']],'QC-v3-primary'))
    write('seasonal.csv',seasonal(before,'original')+seasonal(after,'QC-v3'))
    phase=[]; pt=[]
    for rows,label in [(before,'original'),(after,'QC-v3')]:
        p,t=phases(rows,label); phase+=p;pt+=t
    write('phases.csv',phase);write('phase_tests.csv',pt)
    tier=descriptions(after,'QC-v3')[1:]; matrix=[[r['over'],r['under']] for r in tier]
    tests={'tier_OU_chisquare':float(chi2_contingency(matrix).pvalue),'binomial_descriptive_only':float(binomtest(201,308,.5).pvalue)}
    (OUT/'tests.json').write_text(json.dumps(tests,indent=2))
    dis=[]
    for rows,label in [(before,'original'),(after,'QC-v3')]:
        d=arrays(rows)
        for group,mask in [('underdog',d['market']<0),('favorite',d['market']>0)]:
            mask &= d['resolved']; dis.append(dict(dataset=label,group=group,n=int(mask.sum()),win_rate=float(d['win'][mask].mean()),ats_cover_rate=float((d['residual'][mask]>0).mean()),spread_mae=float(d['spread'][mask].mean()),mean_residual=float(d['residual'][mask].mean()),mean_gap=float(d['gap'][mask].mean())))
    write('disagreement.csv',dis)
    rng=np.random.default_rng(SEED); draws=[]
    for i in range(500):
        sampled={r['Program']:rng.uniform(float(r['Payroll Low ($M)']),float(r['Payroll High ($M)'])) for r in resources}
        # Matched draws permit an exact comparison of score correction under this new seed.
        for rows,label in [(before,'original-new-seed'),(after,'QC-v3-new-seed')]:
            d=arrays(rows,sampled); m=d['binary']; draws.append(dict(draw=i,dataset=label,model='win_rate',coef=float(d['win'][m].mean()),p=None))
            for r in models(rows,label,sampled):
                if r['covariance']!='dyadic' and r['model']!='residual': draws.append(dict(draw=i,dataset=label,model=r['model'],coef=r['coef'],p=r['p']))
    write('range_draws.csv',draws); summary=[]
    for label in ['original-new-seed','QC-v3-new-seed']:
        for model in ['win_rate','margin','win','spread','signed_total','absolute_total']:
            rr=[r for r in draws if r['dataset']==label and r['model']==model]; vals=[r['coef'] for r in rr]
            q=np.quantile(vals,[.025,.5,.975]); summary.append(dict(dataset=label,model=model,seed=SEED,draws=500,q025=float(q[0]),median=float(q[1]),q975=float(q[2]),fraction_p_lt_05=None if model=='win_rate' else float(np.mean([r['p']<.05 for r in rr]))))
    write('range_summary.csv',summary);write('checks.csv',checks)
    (OUT/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__,'seed':SEED,'old_seed':'not recovered; fresh rerun explicitly versioned'},indent=2))
    print(json.dumps({'checks':checks,'corrected_primary':[r for r in result if r['dataset']=='QC-v3'],'tests':tests},indent=2))
if __name__=='__main__': main()
