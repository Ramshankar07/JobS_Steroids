from langchain_community.graphs import Neo4jGraph
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = OllamaLLM(model="llama2")

neo4j_url = os.getenv("NEO4J_URI")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

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

def create_skills_graph(job_description, resume):
    if not neo4j_available:
        return None, None

    try:
        extract_skills_template = PromptTemplate(
            input_variables=["text", "source"],
            template="Extract all skills mentioned in the following {source}. Return as a comma-separated list:\n\n{text}\n\nSkills:"
        )
        extract_skills_chain = extract_skills_template | llm

        job_skills = extract_skills_chain.invoke({"text": job_description, "source": "job description"})
        resume_skills = extract_skills_chain.invoke({"text": resume, "source": "resume"})

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

        matching_skills = graph.query("""
        MATCH (s:Skill)-[:REQUIRED_FOR]->(j:Job)
        MATCH (s)-[:PRESENT_IN]->(r:Resume)
        RETURN s.name as skill
        """)

        skills_gap = graph.query("""
        MATCH (s:Skill)-[:REQUIRED_FOR]->(j:Job)
        WHERE NOT (s)-[:PRESENT_IN]->(:Resume)
        RETURN s.name as skill
        """)

        return matching_skills, skills_gap
    except Exception as e:
        print(f"Error during graph analysis: {e}")
        return None, None