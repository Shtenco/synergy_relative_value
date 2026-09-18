from synergy_relative_value.core import *

def test_pair_fit():
    x=list(range(20));y=[2+3*v for v in x]
    m=fit_pair(x,y)
    assert abs(m.beta-3)<1e-10

def test_synthetic():assert abs(synthetic_rate([2,.5])-1)<1e-12
