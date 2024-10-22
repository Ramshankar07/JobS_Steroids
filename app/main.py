from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import job_analysis

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_analysis.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Job Analysis API"}