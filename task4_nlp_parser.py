"""
Task 4: NLP-Based Sentence Parser
- Uses spaCy to extract disease-symptom-severity triplets from sentences.
- Processes each line in `Knowledge.txt` to structured data.
"""
import spacy

nlp = spacy.load("en_core_web_sm")


def extract_disease_symptoms_severity(sentence):
    doc = nlp(sentence)
    disease = None
    symptoms = []
    current_symptom = []
    current_severity = "moderate"  # default severity

    if "has symptoms" in sentence:
        disease = sentence.split("has symptoms")[0].strip()

    in_symptoms_section = False
    for token in doc:

        if token.text.lower() == "symptoms":
            in_symptoms_section = True
            continue

        if not in_symptoms_section:
            continue

        if token.text in [".", ","]:
            if current_symptom:
                symptom_text = " ".join(current_symptom).strip()
                if symptom_text:
                    symptoms.append((symptom_text, current_severity))
                current_symptom = []
                current_severity = "moderate"
            continue

        if token.text == "(" and token.i + 1 < len(doc):
            severity_token = doc[token.i + 1]
            if severity_token.text in ["high", "mild", "severe", "moderate"]:
                current_severity = severity_token.text
                continue

        if token.text == ")" or token.text in ["high", "mild", "severe", "moderate"]:
            continue

        current_symptom.append(token.text)

    if current_symptom:
        symptom_text = " ".join(current_symptom).strip()
        if symptom_text:
            symptoms.append((symptom_text, current_severity))

    return disease, symptoms


if __name__ == "__main__":
    test_sentences = [
        "Flu has symptoms fever (high), cough, fatigue (mild).",
        "Migraine has symptoms headache (severe), nausea.",
        "Common cold has symptoms runny nose, sneezing (moderate)."
    ]

    for sentence in test_sentences:
        print(f"\nProcessing: {sentence}")
        disease, symptoms = extract_disease_symptoms_severity(sentence)
        if disease:
            print(f"Disease: {disease}")
            for symptom, severity in symptoms:
                print(f"  Symptom: {symptom}, Severity: {severity}")
        else:
            print("[!] Could not parse disease")