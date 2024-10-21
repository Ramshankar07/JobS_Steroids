from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
from .neo4j_service import create_skills_graph, neo4j_available
from .llm_service import (
    generate_cover_letter,
    analyze_skills_gap,
    analyze_resume_skills,
    analyze_relevant_skills,
    draft_hiring_manager_message,
    fallback_skills_analysis
)

load_dotenv()

llm = OllamaLLM(model="llama2")

def pdf_to_text(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

def run_job_application_tasks(job_description, resume):
    # Generate cover letter
    cover_letter = generate_cover_letter(job_description, resume)

    # Chain-based Skills Analysis
    skills_gap = analyze_skills_gap(job_description, resume)
    resume_skills = analyze_resume_skills(resume)
    relevant_skills = analyze_relevant_skills(job_description, resume)

    # Knowledge Graph-based or Fallback Skills Analysis
    if neo4j_available:
        matching_skills, graph_skills_gap = create_skills_graph(job_description, resume)
    else:
        matching_skills, graph_skills_gap = fallback_skills_analysis(job_description, resume)

    # Draft message to hiring manager
    hiring_manager_message = draft_hiring_manager_message(job_description, resume)

    return {
        "cover_letter": cover_letter,
        "skills_analysis": {
            "chain_based": {
                "skills_gap": skills_gap,
                "resume_skills": resume_skills,
                "relevant_skills": relevant_skills
            },
            "graph_based": {
                "matching_skills": [skill["skill"] for skill in matching_skills],
                "skills_gap": [skill["skill"] for skill in graph_skills_gap]
            }
        },
        "hiring_manager_message": hiring_manager_message
    }