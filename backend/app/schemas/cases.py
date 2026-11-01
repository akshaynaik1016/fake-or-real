from typing import Literal
from pydantic import BaseModel,Field

class CaseCreate(BaseModel):
    title:str=Field(min_length=3,max_length=200)

class CaseMutation(BaseModel):
    expected_revision:int=Field(ge=1)

class CaseSourceCreate(CaseMutation):
    input_type:Literal['text','url','email','phone']
    content:str=Field(min_length=1,max_length=50000)
    title:str|None=Field(default=None,max_length=200)

class CaseSourceReview(CaseMutation):
    content:str=Field(min_length=1,max_length=50000)

class CaseRename(CaseCreate,CaseMutation):
    pass
