from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..core import carry_score, fit_pair
from .models import Principal, Role
from .service import EnterpriseRuntime, principal_dependency, request_id_header

class AnalyzeRequest(BaseModel):
    x:list[float]; y:list[float]; x_now:float; y_now:float; expected_carry_bps:float=0; volatility:float=.1; corr_hedge:float=1.0

def build_product_router(runtime:EnterpriseRuntime)->APIRouter:
    router=APIRouter(prefix="/enterprise/v1/relative-value",tags=["enterprise-relative-value"])
    @router.post("/analyze")
    async def analyze(req:AnalyzeRequest, principal:Principal=Depends(principal_dependency(runtime,{Role.RESEARCHER,Role.TRADER})), request_id:str=Depends(request_id_header)):
        model=fit_pair(req.x,req.y);z=model.zscore(req.x_now,req.y_now);carry=carry_score(req.expected_carry_bps,req.volatility,req.corr_hedge)
        runtime.record(principal,action="relative_value.analyze",request_id=request_id,payload={"zscore":z,"beta":model.beta,"carry_score":carry})
        return {"request_id":request_id,"alpha":model.alpha,"beta":model.beta,"zscore":z,"carry_score":carry}
    return router
