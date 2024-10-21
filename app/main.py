from fastapi import FastAPI
from routers import job_analysis

app = FastAPI()

app.include_router(job_analysis.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Job Analysis API"}