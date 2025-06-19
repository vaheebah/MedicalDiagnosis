from BayesianNetwork import create_bayesian_network
from neo4j import GraphDatabase
from pgmpy.inference import VariableElimination
import re

DISEASES = [
    'Flu', 'COVID-19', 'Common Cold', 'Malaria', 'Tuberculosis',
    'Dengue', 'Pneumonia', 'Typhoid', 'Asthma', 'Bronchitis',
    'Measles', 'Sinusitis', 'Meningitis', 'Chickenpox', 'Allergy'
]


class MedicalSystem:
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "neo4j12345")
        )
        self.bn_model, _ = create_bayesian_network()
        self.inference = VariableElimination(self.bn_model)
        self.inference.LOG_PROGRESS = False

        self.symptom_mappings = {
            'high fever': 'Fever',
            'stiff neck': 'Neck Stiffness',
            'runny nose': 'Runny Nose',
            'shortness of breath': 'Difficulty Breathing',
            'sore throat': 'Throat Pain',
            'body ache': 'Muscle Pain',
            'stomach pain': 'Abdominal Pain',
            'throwing up': 'Vomiting'
        }

        self.valid_symptoms = self._load_all_symptoms()
        print(f" System initialized with {len(self.valid_symptoms)} symptoms")

    def _load_all_symptoms(self):
        with self.neo4j_driver.session() as session:
            result = session.run("MATCH (s:Symptom) RETURN s.name AS symptom")
            base_symptoms = [record["symptom"] for record in result]

        return list(set(base_symptoms + [
            'Fever',
            'Neck Stiffness',
            'Runny Nose',
            'Difficulty Breathing',
            'Throat Pain',
            'Muscle Pain',
            'Abdominal Pain',
            'Vomiting'
        ]))

    def validate_symptoms(self, symptoms):
        valid = []
        for s in symptoms:
            s_lower = s.strip().lower()
            if s_lower in self.symptom_mappings:
                valid.append(self.symptom_mappings[s_lower])
            elif s.strip().capitalize() in self.valid_symptoms:
                valid.append(s.strip().capitalize())
            else:
                print(f"⚠️ Ignoring unrecognized symptom: {s}")
        return valid

    def parse_complex_sentence(self, sentence):
        sentence = sentence.lower().replace("with", "has").replace("and", ",")

        patient = re.search(r"^(child|adult|elderly|\w+)", sentence)
        patient = patient.group(1).capitalize() if patient else "Patient"

        symptom_text = re.search(r"has\s+(.*?)(?:,|therefore|$)", sentence)
        symptoms = self.validate_symptoms(
            re.split(r"\s*,\s*|\s+and\s+", symptom_text.group(1).strip())
            if symptom_text else []
        )

        return {
            'patient': patient,
            'symptoms': symptoms,
            'suspected_diseases': []
        }

    def get_neo4j_severity(self, symptoms):
        with self.neo4j_driver.session() as session:
            query = """
            MATCH (d:Disease)-[r:HAS_SYMPTOM]->(s:Symptom)
            WHERE s.name IN $symptoms
            RETURN d.name AS disease, 
                   SUM(CASE r.severity
                       WHEN 'low' THEN 1
                       WHEN 'medium' THEN 2
                       WHEN 'high' THEN 3
                       ELSE 1 END) AS severity_score
            ORDER BY severity_score DESC
            """
            return {r['disease']: r['severity_score']
                    for r in session.run(query, symptoms=symptoms)}

    def get_bayesian_probabilities(self, symptoms, age='adult', location='urban'):
        """Get probabilities from Bayesian Network"""
        evidence = {s: 'yes' for s in symptoms}
        evidence.update({
            'AgeGroup': age.lower(),
            'Location': location.lower()
        })

        probabilities = {}
        for disease in DISEASES:
            try:
                query = self.inference.query(
                    variables=[disease],
                    evidence=evidence
                )
                probabilities[disease] = query.get_value(**{disease: 'yes'})
            except Exception as e:
                probabilities[disease] = 0
        return probabilities

    def run_diagnosis(self, symptoms, age='adult', location='urban'):
        """Combined diagnosis with enhanced output"""
        if not symptoms:
            print(" No valid symptoms provided!")
            return

        print(f"\n Analyzing {len(symptoms)} symptoms...")

        neo4j_scores = self.get_neo4j_severity(symptoms)
        bayesian_probs = self.get_bayesian_probabilities(symptoms, age, location)

        results = []
        for disease in set(neo4j_scores.keys()).union(bayesian_probs.keys()):
            results.append({
                'disease': disease,
                'severity': neo4j_scores.get(disease, 0),
                'probability': bayesian_probs.get(disease, 0),
                'combined_score': neo4j_scores.get(disease, 0) * bayesian_probs.get(disease, 0)
            })
        results.sort(key=lambda x: x['combined_score'], reverse=True)

        print("\n🏥 Diagnosis Results:")
        for idx, result in enumerate(results[:2], 1):
            print(f"{idx}. {result['disease']}:")
            print(f"   - Probability: {result['probability'] * 100:.1f}%")
            print(f"   - Severity: {'★' * int(result['severity'])}")
            print(f"   - Key Symptoms: {', '.join(symptoms[:3])}")

    def interactive_diagnosis(self):
        """Enhanced interactive interface"""
        print("\n Interactive Medical Diagnosis")
        while True:
            print("\nOptions:")
            print("1. Enter symptoms (comma-separated)")
            print("2. Parse complex sentence")
            print("3. Exit")

            choice = input("Select: ").strip()

            if choice == '1':
                symptoms = self.validate_symptoms(input("Symptoms: ").split(','))
                self.run_diagnosis(symptoms)
            elif choice == '2':
                parsed = self.parse_complex_sentence(input("Enter sentence: "))
                print(f"\nParsed: {parsed['patient']} | Symptoms: {', '.join(parsed['symptoms'])}")
                if parsed['suspected_diseases']:
                    print(f"Suspected: {', '.join(parsed['suspected_diseases'])}")
                self.run_diagnosis(parsed['symptoms'])
            elif choice == '3':
                break
            else:
                print(" Invalid choice")


if __name__ == "__main__":
    try:
        system = MedicalSystem()
        print("\nLoaded Symptoms:", ', '.join(system.valid_symptoms))
        system.interactive_diagnosis()
    except Exception as e:
        print(f" System initialization failed: {e}")
