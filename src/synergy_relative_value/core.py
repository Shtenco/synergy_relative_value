from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class PairModel:
    alpha:float; beta:float; spread_mean:float; spread_std:float
    def zscore(self,x:float,y:float)->float:
        s=y-(self.alpha+self.beta*x)
        return 0.0 if self.spread_std<=0 else (s-self.spread_mean)/self.spread_std

def fit_pair(x,y)->PairModel:
    x=np.asarray(x,float);y=np.asarray(y,float)
    if len(x)!=len(y) or len(x)<10:raise ValueError('need aligned history >=10')
    X=np.column_stack([np.ones(len(x)),x]); alpha,beta=np.linalg.lstsq(X,y,rcond=None)[0]
    spread=y-(alpha+beta*x)
    return PairModel(float(alpha),float(beta),float(spread.mean()),float(spread.std(ddof=1)))

def carry_score(expected_carry_bps:float,volatility:float,corr_hedge:float=1.0)->float:
    if volatility<=0:return 0.0
    return expected_carry_bps/10000.0/max(volatility,1e-12)*max(0.0,min(1.0,corr_hedge))

def synthetic_rate(path_rates:list[float])->float:
    r=1.0
    for x in path_rates:
        if x<=0:raise ValueError('rates must be positive')
        r*=x
    return r
