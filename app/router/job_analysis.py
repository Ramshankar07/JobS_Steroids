from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from app.services import job_analysis_service
import io

router = APIRouter()

class JobDescription(BaseModel):
    content: str

class AnalysisResult(BaseModel):
    cover_letter: str
    skills_analysis: dict
    hiring_manager_message: str

class JobAnalyzer:
    @staticmethod
    async def analyze(job_description: str, resume_file: UploadFile) -> AnalysisResult:
        try:
            resume_content = await resume_file.read()
            resume_text = job_analysis_service.pdf_to_text(io.BytesIO(resume_content))
            
            analysis_result = job_analysis_service.run_job_application_tasks(
                job_description, 
                resume_text
            )
            
            return AnalysisResult(**analysis_result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_job_application(job_description: JobDescription, resume: UploadFile = File(...)):
    return await JobAnalyzer.analyze(job_description.content, resume)