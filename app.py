from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Initialize Ollama LLM
llm = Ollama(model="llama2")  # You can change the model as needed

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

cover_letter_chain = LLMChain(llm=llm, prompt=cover_letter_template)

# 2. Skills Analysis
skills_analysis_template = PromptTemplate(
    input_variables=["job_description", "resume"],
    template="Analyze the following job description and resume. List the skills needed for the job that are not present in the resume:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nNeeded Skills:"
)

skills_analysis_chain = LLMChain(llm=llm, prompt=skills_analysis_template)

# 3. Message to Hiring Manager
hiring_manager_message_template = PromptTemplate(
    input_variables=["job_description", "resume"],
    template="Draft a short, curated message to the hiring manager based on the following job description and resume:\n\nJob Description: {job_description}\n\nResume: {resume}\n\nMessage to Hiring Manager:"
)

hiring_manager_message_chain = LLMChain(llm=llm, prompt=hiring_manager_message_template)

# Main function to run all tasks
def run_job_application_tasks(job_description_path, resume_path):
    job_description = read_pdf(job_description_path)
    resume = read_pdf(resume_path)

    # Generate cover letter
    cover_letter = cover_letter_chain.run(job_description=job_description, resume=resume)
    create_pdf(cover_letter, "cover_letter.pdf")
    print("Cover Letter has been saved as 'cover_letter.pdf'")

    # Analyze needed skills
    needed_skills = skills_analysis_chain.run(job_description=job_description, resume=resume)
    print("\nNeeded Skills:\n", needed_skills)

    # Draft message to hiring manager
    hiring_manager_message = hiring_manager_message_chain.run(job_description=job_description, resume=resume)
    print("\nMessage to Hiring Manager:\n", hiring_manager_message)

# Example usage
if __name__ == "__main__":
    job_description_path = "path/to/job_description.pdf"
    resume_path = "path/to/resume.pdf"
    run_job_application_tasks(job_description_path, resume_path)