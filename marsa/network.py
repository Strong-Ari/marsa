"""Synthetic network and traffic model. Topology, capacities and demands are illustrative, not operator data."""
from dataclasses import dataclass
import numpy as np
@dataclass
class Path:
    id:str; capacity:float; latency:int; hops:tuple; up:bool=True
CLASSES=[("emergency",40),("clinical",90),("government",160),("payments",120),("enterprise",520),("consumer",1400)]
RANK={c:i for i,(c,_) in enumerate(CLASSES)}
def default_paths():
    return {"EAST":Path("EAST",1100,95,("UAE","INT-WATERS")),
            "WEST":Path("WEST",900,120,("UAE","INT-WATERS")),
            "NORTH":Path("NORTH",260,70,("UAE","NEIGHBOUR-A")),
            "SAT":Path("SAT",35,580,("UAE","SPACE"))}
def allocate(paths, protected=(), available=None):
    """Share of each traffic class served. Protected classes are filled first, in rank order."""
    cap=available if available is not None else sum(p.capacity for p in paths.values() if p.up)
    if not protected:
        share=min(1,cap/sum(d for _,d in CLASSES))
        return {c:round(share,3) for c,_ in CLASSES},cap
    floor=0.15*cap  # 15 percent stays open to unprotected traffic, so a crisis measure never switches a class off
    rest=[c for c in CLASSES if c[0] not in protected]; left=cap-floor; served={}
    for c,d in sorted(CLASSES,key=lambda c:(0 if c[0] in protected else 1,RANK[c[0]])):
        if c not in protected: continue
        g=min(left,d); served[c]=round(g/d,3); left-=g
    pool=left+floor; demand=sum(d for _,d in rest)
    for c,d in rest: served[c]=round(min(1,pool/demand),3)
    return served,cap
def forecast_model(seed=7):
    """Y.3172 M node: 30-minute-ahead utilisation forecast trained on synthetic series."""
    from sklearn.ensemble import GradientBoostingRegressor
    r=np.random.default_rng(seed); n=3000; t=np.arange(n)
    u=.55+.2*np.sin(2*np.pi*t/96)+r.normal(0,.03,n)
    X=np.c_[u[3:-6],u[2:-7],u[:-9],np.sin(2*np.pi*t[3:-6]/96),np.cos(2*np.pi*t[3:-6]/96)]; y=u[9:]
    m=GradientBoostingRegressor(n_estimators=120,max_depth=3,random_state=seed).fit(X[:2400],y[:2400])
    return m,float(np.abs(m.predict(X[2400:])-y[2400:]).mean())
