

"""
Task 7: Advanced Query Engine
- Queries Neo4j for symptom matches AND uses Bayesian Network for probabilities
- Ranks diseases by combined evidence (symptom severity + Bayesian probabilities)
"""

from neo4j import GraphDatabase
from BayesianNetwork import create_bayesian_network, DISEASES  # Import your BN
from pgmpy.inference import VariableElimination


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "neo4j12345"


class DiagnosisEngine:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        self.bn_model, _ = create_bayesian_network()
        self.inference = VariableElimination(self.bn_model)
        self.inference.LOG_PROGRESS = False

    def query_neo4j(self, symptoms):

        with self.driver.session() as session:
            query = """
            MATCH (d:Disease)-[r:HAS_SYMPTOM]->(s:Symptom)
            WHERE s.name IN $symptoms
            RETURN d.name AS disease, 
                   COUNT(*) AS matches,
                   SUM(CASE r.severity
                       WHEN 'low' THEN 1
                       WHEN 'medium' THEN 2
                       WHEN 'high' THEN 3
                       ELSE 1 END) AS severity_score
            ORDER BY severity_score DESC
            """
            return session.run(query, symptoms=symptoms).data()

    def query_bayesian_network(self, evidence):

        return {
            disease: self.inference.query(
                variables=[disease],
                evidence=evidence
            ).get_value(**{disease: 'yes'})
            for disease in DISEASES[:10]  # Top 10 diseases
        }

    def combined_diagnosis(self, symptoms, age='adult', location='urban'):
        """Combine Neo4j and Bayesian results"""

        neo4j_results = self.query_neo4j(symptoms)

        evidence = {s: 'yes' for s in symptoms}
        evidence.update({'AgeGroup': age, 'Location': location})


        bn_probs = self.query_bayesian_network(evidence)

        combined = []
        for record in neo4j_results:
            disease = record['disease']
            if disease in bn_probs:
                combined.append({
                    'disease': disease,
                    'neo4j_score': record['severity_score'],
                    'bayesian_prob': bn_probs[disease],
                    'combined_score': record['severity_score'] * bn_probs[disease]
                })

        return sorted(combined, key=lambda x: x['combined_score'], reverse=True)


if __name__ == "__main__":
    engine = DiagnosisEngine()
    test_symptoms = ['Fever', 'Cough', 'Fatigue']

    print("Running Combined Diagnosis...")
    results = engine.combined_diagnosis(test_symptoms)

    print("\nTop Diagnoses:")
    for idx, result in enumerate(results[:10], 1):
        print(f"{idx}. {result['disease']}:")
        print(f"   - Neo4j Severity Score: {result['neo4j_score']}")
        print(f"   - Bayesian Probability: {result['bayesian_prob'] * 100:.1f}%")
        print(f"   - Combined Score: {result['combined_score']:.2f}")