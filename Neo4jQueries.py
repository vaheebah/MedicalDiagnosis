
"""
Task 5: Neo4j Query Generator
- Populates Neo4j with parsed disease-symptom-severity data.
- Uses MERGE to avoid duplicates.
"""

from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "neo4j12345"

MEDICAL_KNOWLEDGE = [
    {
        'disease': 'Flu',
        'symptoms': [
            {'name': 'Fever', 'severity': 'medium'},
            {'name': 'Cough', 'severity': 'low'},
            {'name': 'Fatigue', 'severity': 'high'},
            {'name': 'Headache', 'severity': 'low'}
        ]
    },
    {
        'disease': 'COVID-19',
        'symptoms': [
            {'name': 'Fever', 'severity': 'medium'},
            {'name': 'Cough', 'severity': 'low'},
            {'name': 'Fatigue', 'severity': 'medium'},
            {'name': 'Loss of Smell', 'severity': 'medium'},
            {'name': 'Shortness of Breath', 'severity': 'high'}
        ]
    },
    {
        'disease': 'Common Cold',
        'symptoms': [
            {'name': 'Cough', 'severity': 'medium'},
            {'name': 'Sneezing', 'severity': 'low'},
            {'name': 'Runny Nose', 'severity': 'high'}
        ]
    },
    {
        'disease': 'Malaria',
        'symptoms': [
            {'name': 'Fever', 'severity': 'medium'},
            {'name': 'Chills', 'severity': 'low'},
            {'name': 'Sweating', 'severity': 'medium'},
            {'name': 'Headache', 'severity': 'medium'}
        ]
    },
    {
        'disease': 'Tuberculosis',
        'symptoms': [
            {'name': 'Cough', 'severity': 'low'},
            {'name': 'Fever', 'severity': 'low'},
            {'name': 'Weight Loss', 'severity': 'high'},
            {'name': 'Night Sweats', 'severity': 'high'}
        ]
    },
    {
        'disease': 'Dengue',
        'symptoms': [
            {'name': 'Fever', 'severity': 'high'},
            {'name': 'Joint Pain', 'severity': 'medium'},
            {'name': 'Headache', 'severity': 'high'},
            {'name': 'Rash', 'severity': 'high'}
        ]
    },
    {
        'disease': 'Pneumonia',
        'symptoms': [
            {'name': 'Fever', 'severity': 'high'},
            {'name': 'Cough', 'severity': 'high'},
            {'name': 'Chest Pain', 'severity': 'low'},
            {'name': 'Shortness of Breath', 'severity': 'low'}
        ]
    },
    {
        'disease': 'Typhoid',
        'symptoms': [
            {'name': 'Fever', 'severity': 'medium'},
            {'name': 'Abdominal Pain', 'severity': 'low'},
            {'name': 'Weakness', 'severity': 'low'},
            {'name': 'Headache', 'severity': 'high'}
        ]
    },
    {
        'disease': 'Asthma',
        'symptoms': [
            {'name': 'Cough', 'severity': 'medium'},
            {'name': 'Shortness of Breath', 'severity': 'low'},
            {'name': 'Wheezing', 'severity': 'medium'}
        ]
    },
    {
        'disease': 'Bronchitis',
        'symptoms': [
            {'name': 'Cough', 'severity': 'high'},
            {'name': 'Fatigue', 'severity': 'high'},
            {'name': 'Chest Discomfort', 'severity': 'low'}
        ]
    },
    {
        'disease': 'Measles',
        'symptoms': [
            {'name': 'Fever', 'severity': 'medium'},
            {'name': 'Rash', 'severity': 'low'},
            {'name': 'Cough', 'severity': 'low'},
            {'name': 'Runny Nose', 'severity': 'low'}
        ]
    },
    {
        'disease': 'Sinusitis',
        'symptoms': [
            {'name': 'Headache', 'severity': 'high'},
            {'name': 'Runny Nose', 'severity': 'low'},
            {'name': 'Facial Pain', 'severity': 'high'}
        ]
    },
    {
        'disease': 'Meningitis',
        'symptoms': [
            {'name': 'Fever', 'severity': 'high'},
            {'name': 'Headache', 'severity': 'high'},
            {'name': 'Neck Stiffness', 'severity': 'high'}
        ]
    },
    {
        'disease': 'Chickenpox',
        'symptoms': [
            {'name': 'Fever', 'severity': 'low'},
            {'name': 'Rash', 'severity': 'medium'},
            {'name': 'Fatigue', 'severity': 'medium'}
        ]
    },
    {
        'disease': 'Allergy',
        'symptoms': [
            {'name': 'Sneezing', 'severity': 'low'},
            {'name': 'Runny Nose', 'severity': 'high'},
            {'name': 'Cough', 'severity': 'high'}
        ]
    }
]

def populate_neo4j(knowledge):

    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    with driver.session() as session:
        for entry in knowledge:
            disease = entry['disease']
            session.run("MERGE (d:Disease {name: $disease})", disease=disease)

            for symptom_data in entry['symptoms']:
                symptom = symptom_data['name']
                severity = symptom_data['severity']
                session.run("MERGE (s:Symptom {name: $symptom})", symptom=symptom)
                session.run("""
                    MATCH (d:Disease {name: $disease})
                    MATCH (s:Symptom {name: $symptom})
                    MERGE (d)-[r:HAS_SYMPTOM]->(s)
                    SET r.severity = $severity
                """, disease=disease, symptom=symptom, severity=severity)

    print("Neo4j populated successfully.")
    driver.close()


if __name__ == "__main__":
    populate_neo4j(MEDICAL_KNOWLEDGE)