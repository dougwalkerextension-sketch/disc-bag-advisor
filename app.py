from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from typing import Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from catalog import CATALOG, get_disc
from agent import run_agent

ROOT=Path(__file__).parent
app=FastAPI(title='Disc Bag Advisor')

class Search(BaseModel):
    query:str=Field(min_length=1,max_length=300)
    brands:list[Literal['Innova','Latitude 64','MVP','Axiom']]=Field(default_factory=list,max_length=4)
    sort:Literal['match','popularity','speed','name']='match'
    bag:list[str]=Field(default_factory=list,max_length=100)

@app.middleware('http')
async def local_only(request:Request,call_next):
    host=request.headers.get('host','').split(':')[0]
    if host not in ['127.0.0.1','localhost','testserver']:
        return JSONResponse({'message':'Local access only'},status_code=403)
    if request.method=='POST' and request.headers.get('origin') not in [None,'http://127.0.0.1:8010','http://localhost:8010']:
        return JSONResponse({'message':'Origin not allowed'},status_code=403)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['Content-Security-Policy']="default-src 'self'; img-src 'self' https:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'"
    return response

@app.get('/')
def index(): return FileResponse(ROOT/'static/index.html')

@app.get('/api/catalog')
def catalog(): return {'discs':CATALOG}

@app.post('/api/recommend')
async def recommend(body:Search):
    result=await run_agent(**body.model_dump())
    return JSONResponse(result,status_code=503 if result.get('failed') else 200)

@app.post('/api/discs/{disc_id}')
async def detail(disc_id:str):
    if not get_disc(disc_id): raise HTTPException(404,'Disc not found')
    result=await run_agent(disc_id=disc_id)
    return JSONResponse(result,status_code=503 if result.get('failed') else 200)

app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8010)
