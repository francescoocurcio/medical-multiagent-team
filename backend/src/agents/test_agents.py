from state import AgentState
from nodes import agent_1_extract_symptoms, agent_3_synthesize_diagnose
import logging
logging.basicConfig(level=logging.INFO)
from rich.console import Console
from rich.markdown import Markdown

def initialize_console_logger():
    console = Console()
    return console

def main():
    console = initialize_console_logger()
    # Creazione di uno stato immutabile fittizio
    mock_state = AgentState(
        patient_input = "I've been experiencing sharp chest pain radiating to my left arm for the past 3 hours, accompanied by profuse sweating, shortness of breath, and nausea. I also feel a sense of impending doom."
    )
    try: 
        console.print("[AGENT 1 TEST] Starting the test for agent_1_extract_symptoms.")
        symptoms_output = agent_1_extract_symptoms(mock_state)['symptoms']
        markdown_info = Markdown(f"**Extracted Symptoms:** {symptoms_output}")
        console.print(markdown_info)
        mock_state.update(symptoms = symptoms_output)

        mock_state.update(retrieved_docs = ["Acute myocardial infarction (AMI) is characterized by ischemic chest discomfort often radiating to the left arm or jaw, associated with diaphoresis and dyspnea.", "The 12-lead ECG is the cornerstone of AMI diagnosis. ST-elevation in leads II, III, aVF suggests inferior MI. Troponin levels confirm myocardial necrosis.", "Differential diagnosis for chest pain includes STEMI, NSTEMI, unstable angina, aortic dissection, and pulmonary embolism."])
        console.print("[AGENT 3 TEST] Starting the test for agent_3_synthesize_diagnose.")
        report_output = agent_3_synthesize_diagnose(mock_state)['final_report']
        markdown_info = Markdown(report_output)
        console.print(markdown_info)
    except Exception as e:
        console.print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()