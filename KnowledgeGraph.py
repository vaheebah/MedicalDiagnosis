
"""
Task 2: Knowledge Graph
- Connects to Neo4j and creates a medical knowledge graph.
- Defines diseases and their symptoms as nodes with HAS_SYMPTOM relationships.
"""

from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "neo4j12345"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

MEDICAL_DATA = {
    "Flu": ["Fever", "Cough", "Fatigue", "Headache"],
    "COVID-19": ["Fever", "Cough", "Fatigue", "Loss of Smell", "Shortness of Breath"],
    "Common Cold": ["Cough", "Sneezing", "Runny Nose"],
    "Malaria": ["Fever", "Chills", "Sweating", "Headache"],
    "Tuberculosis": ["Cough", "Fever", "Weight Loss", "Night Sweats"],
    "Dengue": ["Fever", "Joint Pain", "Headache", "Rash"],
    "Pneumonia": ["Fever", "Cough", "Chest Pain", "Shortness of Breath"],
    "Typhoid": ["Fever", "Abdominal Pain", "Weakness", "Headache"],
    "Asthma": ["Cough", "Shortness of Breath", "Wheezing"],
    "Bronchitis": ["Cough", "Fatigue", "Chest Discomfort"],
    "Measles": ["Fever", "Rash", "Cough", "Runny Nose"],
    "Sinusitis": ["Headache", "Runny Nose", "Facial Pain"],
    "Meningitis": ["Fever", "Headache", "Neck Stiffness"],
    "Chickenpox": ["Fever", "Rash", "Fatigue"],
    "Allergy": ["Sneezing", "Runny Nose", "Cough"]
}


def create_knowledge_graph(data):

    with driver.session() as session:
        for disease, symptoms in data.items():
            session.run("MERGE (d:Disease {name: $disease})", disease=disease)

            for symptom in symptoms:
                session.run("MERGE (s:Symptom {name: $symptom})", symptom=symptom)
                # Link Disease to Symptom
                session.run("""
                    MATCH (d:Disease {name: $disease})
                    MATCH (s:Symptom {name: $symptom})
                    MERGE (d)-[:HAS_SYMPTOM]->(s)
                """, disease=disease, symptom=symptom)


if __name__ == "__main__":
    create_knowledge_graph(MEDICAL_DATA)
    print("Medical Knowledge Graph created.")
    driver.close()