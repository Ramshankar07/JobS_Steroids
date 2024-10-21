from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

llm = OllamaLLM(model="llama2")

def generate_cover_letter(job_description, resume):
    template = PromptTemplate(
        input_variables=["job_description", "resume"],
        template="Based on the following job description and resume, generate a tailored cover letter:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nCover Letter:"
    )
    chain = template | llm
    return chain.invoke({"job_description": job_description, "resume": resume})

def analyze_skills_gap(job_description, resume):
    template = PromptTemplate(
        input_variables=["job_description", "resume"],
        template="Analyze the following job description and resume. List the skills needed for the job that are not present in the resume:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nSkills Gap (skills needed but not in resume):"
    )
    chain = template | llm
    return chain.invoke({"job_description": job_description, "resume": resume})

def analyze_resume_skills(resume):
    template = PromptTemplate(
        input_variables=["resume"],
        template="Analyze the following resume and list all the skills mentioned or implied:\n\nResume: {resume}\n\nSkills in Resume:"
    )
    chain = template | llm
    return chain.invoke({"resume": resume})

def analyze_relevant_skills(job_description, resume):
    template = PromptTemplate(
        input_variables=["job_description", "resume"],
        template="Analyze the following job description and resume. List the skills from the resume that are most relevant to the job description, ordered by relevance:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nMost Relevant Skills:"
    )
    chain = template | llm
    return chain.invoke({"job_description": job_description, "resume": resume})

def draft_hiring_manager_message(job_description, resume):
    template = PromptTemplate(
        input_variables=["job_description", "resume"],
        template="Draft a short, curated message to the hiring manager based on the following job description and resume:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nMessage to Hiring Manager:"
    )
    chain = template | llm
    return chain.invoke({"job_description": job_description, "resume": resume})

def fallback_skills_analysis(job_description, resume):
    template = PromptTemplate(
        input_variables=["job_description", "resume"],
        template="Analyze the following job description and resume. Provide two lists:\n1) Skills present in both the job description and resume\n2) Skills needed for the job but not present in the resume\n\nJob Description: {job_description}\n\nResume: {resume}\n\nAnalysis:"
    )
    chain = template | llm
    analysis = chain.invoke({"job_description": job_description, "resume": resume})
    
    parts = analysis.split("1)")
    if len(parts) > 1:
        matching_skills = parts[1].split("2)")[0].strip().split("\n")
        skills_gap = parts[1].split("2)")[1].strip().split("\n")
    else:
        matching_skills = []
        skills_gap = []
    
    return [{"skill": skill.strip("- ")} for skill in matching_skills], [{"skill": skill.strip("- ")} for skill in skills_gap]