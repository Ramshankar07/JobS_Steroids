from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from services import job_analysis_service
import io

app = FastAPI()

class AnalysisRequest(BaseModel):
    job_description: str

@app.post("/analyze")
async def analyze_job_application(job_description: AnalysisRequest, resume: UploadFile = File(...)):
    try:
        resume_content = await resume.read()
        resume_text = job_analysis_service.pdf_to_text(io.BytesIO(resume_content))
        
        analysis_result = job_analysis_service.run_job_application_tasks(
            job_description.job_description, 
            resume_text
        )
        
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)