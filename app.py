from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.graphs import Neo4jGraph
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Ollama LLM
llm = OllamaLLM(model="llama3.2")  # You can change the model as needed

# Initialize Neo4j connection
neo4j_url = "neo4j+s://6f8cd405.databases.neo4j.io"
neo4j_username = "neo4j"
neo4j_password = "QKR4L-neiyRBxGCNx7aj6BP5y-9a5Vmfu43pSHjDpV8"
try:
    graph = Neo4jGraph(
        url=neo4j_url,
        username=neo4j_username,
        password=neo4j_password
    )
    neo4j_available = True
except Exception as e:
    print(f"Error connecting to Neo4j: {e}")
    print("Falling back to non-graph-based analysis.")
    neo4j_available = False
# Function to read text file content
def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to read PDF file content
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to create PDF
def create_pdf(content, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = [Paragraph(line, styles['Normal']) for line in content.split('\n')]
    doc.build(flowables)

# 1. Cover Letter Generation
cover_letter_template = PromptTemplate(
    input_variables=["job_description", "resume"],
    template="Based on the following job description and resume, generate a tailored cover letter:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nCover Letter:"
)

cover_letter_chain = cover_letter_template | llm

# 2. Skills Analysis (Chain-based)
skills_gap_template = PromptTemplate(
    input_variables=["job_description", "resume"],
    template="Analyze the following job description and resume. List the skills needed for the job that are not present in the resume:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nSkills Gap (skills needed but not in resume):"
)

resume_skills_template = PromptTemplate(
    input_variables=["resume"],
    template="Analyze the following resume and list all the skills mentioned or implied:\n\nResume: {resume}\n\nSkills in Resume:"
)

relevant_skills_template = PromptTemplate(
    input_variables=["job_description", "resume"],
    template="Analyze the following job description and resume. List the skills from the resume that are most relevant to the job description, ordered by relevance:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nMost Relevant Skills:"
)

skills_gap_chain = skills_gap_template | llm
resume_skills_chain = resume_skills_template | llm
relevant_skills_chain = relevant_skills_template | llm

# 3. Message to Hiring Manager
hiring_manager_message_template = PromptTemplate(
    input_variables=["job_description", "resume"],
    template="Draft a short, curated message to the hiring manager based on the following job description and resume:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nMessage to Hiring Manager:"
)

hiring_manager_message_chain = hiring_manager_message_template | llm

# 4. Knowledge Graph Analysis
def create_skills_graph(job_description, resume):
    if not neo4j_available:
        print("Neo4j is not available. Using alternative analysis method.")
        return fallback_skills_analysis(job_description, resume)
    
    try:
        extract_skills_template = PromptTemplate(
            input_variables=["text", "source"],
            template="Extract all skills mentioned in the following {source}. Return as a comma-separated list:\n\n{text}\n\nSkills:"
        )
        extract_skills_chain = extract_skills_template | llm

        job_skills = extract_skills_chain.invoke({"text": job_description, "source": "job description"})
        resume_skills = extract_skills_chain.invoke({"text": resume, "source": "resume"})

        # Create nodes and relationships in Neo4j
        graph.query("MATCH (n) DETACH DELETE n")

        for skill in job_skills.split(','):
            graph.query(f"""
            MERGE (s:Skill {{name: "{skill.strip()}"}})
            MERGE (j:Job)
            MERGE (s)-[:REQUIRED_FOR]->(j)
            """)

        for skill in resume_skills.split(','):
            graph.query(f"""
            MERGE (s:Skill {{name: "{skill.strip()}"}})
            MERGE (r:Resume)
            MERGE (s)-[:PRESENT_IN]->(r)
            """)

        # Query to find matching skills
        matching_skills = graph.query("""
        MATCH (s:Skill)-[:REQUIRED_FOR]->(j:Job)
        MATCH (s)-[:PRESENT_IN]->(r:Resume)
        RETURN s.name as skill
        """)

        # Query to find skills gap
        skills_gap = graph.query("""
        MATCH (s:Skill)-[:REQUIRED_FOR]->(j:Job)
        WHERE NOT (s)-[:PRESENT_IN]->(:Resume)
        RETURN s.name as skill
        """)

        return matching_skills, skills_gap
    except Exception as e:
        print(f"Error during graph analysis: {e}")
        print("Falling back to alternative analysis method.")
        return fallback_skills_analysis(job_description, resume)
def fallback_skills_analysis(job_description, resume):
    fallback_template = PromptTemplate(
        input_variables=["job_description", "resume"],
        template="Analyze the following job description and resume. Provide two lists:\n1) Skills present in both the job description and resume\n2) Skills needed for the job but not present in the resume\n\nJob Description: {job_description}\n\nResume: {resume}\n\nAnalysis:"
    )
    fallback_chain = fallback_template | llm
    analysis = fallback_chain.invoke({"job_description": job_description, "resume": resume})
    
    # Parse the analysis to extract matching skills and skills gap
    # This is a simple parsing, you might need to adjust based on the actual output format
    parts = analysis.split("1)")
    if len(parts) > 1:
        matching_skills = parts[1].split("2)")[0].strip().split("\n")
        skills_gap = parts[1].split("2)")[1].strip().split("\n")
    else:
        matching_skills = []
        skills_gap = []
    
    return [{"skill": skill.strip("- ")} for skill in matching_skills], [{"skill": skill.strip("- ")} for skill in skills_gap]

# Main function to run all tasks
def run_job_application_tasks(job_description_path, resume_path):
    job_description = read_text_file(job_description_path)
    resume = read_pdf(resume_path)

    # Generate cover letter
    cover_letter = cover_letter_chain.invoke({"job_description": job_description, "resume": resume})
    create_pdf(cover_letter, "cover_letter.pdf")
    print("Cover Letter has been saved as 'cover_letter.pdf'")

    # Chain-based Skills Analysis
    skills_gap = skills_gap_chain.invoke({"job_description": job_description, "resume": resume})
    print("\nChain-based Skills Gap Analysis:\n", skills_gap)

    resume_skills = resume_skills_chain.invoke({"resume": resume})
    print("\nChain-based Resume Skills Analysis:\n", resume_skills)

    relevant_skills = relevant_skills_chain.invoke({"job_description": job_description, "resume": resume})
    print("\nChain-based Most Relevant Skills Analysis:\n", relevant_skills)

    # Knowledge Graph-based Skills Analysis
    matching_skills, graph_skills_gap = create_skills_graph(job_description, resume)

    print("\nKnowledge Graph-based Matching Skills (present in both job description and resume):")
    for skill in matching_skills:
        print(f"- {skill['skill']}")

    print("\nKnowledge Graph-based Skills Gap (required in job but not present in resume):")
    for skill in graph_skills_gap:
        print(f"- {skill['skill']}")

    # Draft message to hiring manager
    hiring_manager_message = hiring_manager_message_chain.invoke({"job_description": job_description, "resume": resume})
    print("\nMessage to Hiring Manager:\n", hiring_manager_message)

if __name__ == "__main__":
    job_description_path = "job_description.txt"
    resume_path = "Main-Resume.pdf"
    run_job_application_tasks(job_description_path, resume_path)