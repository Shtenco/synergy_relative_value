from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from .core import fit_pair,synthetic_rate
app=FastAPI(title='SYNERGY Relative Value',version='2.0.0')
class PairReq(BaseModel):x:list[float];y:list[float];x_now:float;y_now:float
@app.get('/health')
def health():return {'ok':True,'service':'relative-value'}
@app.post('/v1/pair')
def pair(req:PairReq):
    m=fit_pair(req.x,req.y);return {'alpha':m.alpha,'beta':m.beta,'zscore':m.zscore(req.x_now,req.y_now)}

# Enterprise v2 control/data plane
from .enterprise.service import EnterpriseRuntime, build_enterprise_router, install_observability
from .enterprise.product import build_product_router
enterprise_runtime=EnterpriseRuntime.from_env(service_name='synergy-relative-value')
install_observability(app,enterprise_runtime)
app.include_router(build_enterprise_router(enterprise_runtime))
app.include_router(build_product_router(enterprise_runtime))

if __name__=='__main__':uvicorn.run(app,host='0.0.0.0',port=8000)
