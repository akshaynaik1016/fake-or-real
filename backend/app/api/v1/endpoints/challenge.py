"""Judge challenge: fixed synthetic inputs, real persisted investigation outputs."""
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.access import current_actor
from app.evaluation.runner import dataset,run_scenario
router=APIRouter(prefix='/challenge',tags=['Evidence Challenge'])

@router.get('/scenarios')
def scenarios():
    return {'synthetic':True,'scenarios':[s for s in dataset()['scenarios'] if s.get('challenge')]}

@router.post('/run/{scenario_id}')
async def run(scenario_id:str,db:Session=Depends(get_db),actor=Depends(current_actor)):
    scenario=next((s for s in dataset()['scenarios'] if s['id']==scenario_id and s.get('challenge')),None)
    if not scenario:raise HTTPException(404,'Unknown evidence challenge')
    return await run_scenario(db,scenario,actor)
