
"""
Task 6: Bayesian Network for Medical Diagnosis
"""
from itertools import product
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination


CORE_SYMPTOMS = ['Fever', 'Cough', 'Fatigue', 'Headache']
DEMOGRAPHICS = ['AgeGroup', 'Location']
DISEASES = [
    'Flu', 'COVID-19', 'Common Cold', 'Malaria', 'Tuberculosis',
    'Dengue', 'Pneumonia', 'Typhoid', 'Asthma', 'Bronchitis',
    'Measles', 'Sinusitis', 'Meningitis', 'Chickenpox', 'Allergy'
]


def create_bayesian_network():
    """Builds Bayesian Network"""

    edges = (
            [(symptom, disease) for symptom in CORE_SYMPTOMS for disease in DISEASES] +
            [(demographic, disease) for demographic in DEMOGRAPHICS for disease in DISEASES]
    )
    model = DiscreteBayesianNetwork(edges)

    symptom_cpds = [
        TabularCPD(
            variable=s,
            variable_card=2,
            values=[[0.8], [0.2]],
            state_names={s: ['no', 'yes']}
        ) for s in CORE_SYMPTOMS
    ]

    demographic_cpds = [
        TabularCPD(
            variable='AgeGroup',
            variable_card=3,
            values=[[0.2], [0.5], [0.3]],
            state_names={'AgeGroup': ['child', 'adult', 'elderly']}
        ),
        TabularCPD(
            variable='Location',
            variable_card=3,
            values=[[0.4], [0.3], [0.3]],
            state_names={'Location': ['urban', 'rural', 'tropical']}
        )
    ]

    disease_cpds = []
    for disease in DISEASES:
        evidence = CORE_SYMPTOMS + DEMOGRAPHICS
        evidence_card = [2, 2, 2, 2, 3, 3]
        values = [[], []]

        symptom_weights = {
            'Fever': 1.5, 'Cough': 1.3, 'Fatigue': 1.2, 'Headache': 1.1
        }
        age_weights = {'child': 1.2, 'adult': 1.0, 'elderly': 1.5}
        loc_weights = {'urban': 1.3, 'rural': 1.0, 'tropical': 1.4}

        for fever, cough, fatigue, headache in product([0, 1], repeat=4):
            for age in ['child', 'adult', 'elderly']:
                for loc in ['urban', 'rural', 'tropical']:
                    # Base probabilities
                    base_prob = {
    'Flu': 0.1,
    'COVID-19': 0.05,
    'Common Cold': 0.15,
    'Malaria': 0.07,
    'Tuberculosis': 0.08,
    'Dengue': 0.06,
    'Pneumonia': 0.07,
    'Typhoid': 0.06,
    'Asthma': 0.05,
    'Bronchitis': 0.06,
    'Measles': 0.05,
    'Sinusitis': 0.04,
    'Meningitis': 0.02,
    'Chickenpox': 0.07,
    'Allergy': 0.07
}.get(disease, 0.05)

                    if fever: base_prob *= symptom_weights['Fever']
                    if cough: base_prob *= symptom_weights['Cough']
                    if fatigue: base_prob *= symptom_weights['Fatigue']
                    if headache: base_prob *= symptom_weights['Headache']
                    base_prob *= age_weights[age] * loc_weights[loc]

                    prob = min(base_prob, 0.95)
                    values[0].append(1 - prob)
                    values[1].append(prob)

        disease_cpds.append(
            TabularCPD(
                variable=disease,
                variable_card=2,
                values=values,
                evidence=evidence,
                evidence_card=evidence_card,
                state_names={
                    **{disease: ['no', 'yes']},
                    **{s: ['no', 'yes'] for s in CORE_SYMPTOMS},
                    'AgeGroup': ['child', 'adult', 'elderly'],
                    'Location': ['urban', 'rural', 'tropical']
                }
            )
        )

    model.add_cpds(*symptom_cpds, *demographic_cpds, *disease_cpds)
    if model.check_model():
        print("Bayesian Network created successfully")
        return model, DISEASES
    raise ValueError("Model check failed")


if __name__ == "__main__":
    try:
        from pgmpy.inference import VariableElimination

        VariableElimination.LOG_PROGRESS = False

        print("Building reliable Bayesian Network...")
        bn_model, diseases = create_bayesian_network()
        inference = VariableElimination(bn_model)

        evidence = {'Fever': 'yes', 'Cough': 'yes', 'AgeGroup': 'child', 'Location': 'tropical'}
        print("\nRunning diagnosis...")

        for disease in ['Flu', 'COVID-19', 'Common Cold']:
            prob = inference.query(variables=[disease], evidence=evidence)
            print(f"- {disease}: {prob.get_value(**{disease: 'yes'}) * 100:.1f}%")

    except Exception as e:
        print(f" Error: {e}")
