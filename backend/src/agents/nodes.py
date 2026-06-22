from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from state import AgentState
import json
import os

def check_for_env_variables():
    load_dotenv()
    api_key = os.getenv("GROQ_API")
    model_name = os.getenv("MODEL_NAME")

    if not api_key:
        raise ValueError("GROQ_API environment variable is not set.")
    if not model_name:
        raise ValueError("MODEL_NAME environment variable is not set.")
    
    return api_key, model_name

def build_llm(json_output: bool) -> ChatGroq:
    api_key, model_name = check_for_env_variables()

    llm = ChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=0 if json_output else 0.5, # Temperature più bassa per output JSON più coerente, più alta per output testuale più creativo
        model_kwargs={"response_format": {"type": "json_object"}} if json_output else {}
    )
    return llm

LLM_JSON = build_llm(json_output=True)
LLM_TEXT = build_llm(json_output=False)

# Paradigma base di LangGraph: ogni nodo è una funzione Python pura con firma fissa. 
# Riceve lo stato e restituisce un dizionario con i valori aggiornati sulle chiavi.
# N.B: lo stato NON è IMMUTABILE in senso assoluto, è IMMUTABILE all'interno di un singolo nodo, ma evolve tra un nodo e l'altro.

def agent_1_extract_symptoms(state: AgentState) -> dict:
    """
    Agente 1: Estrazione dei sintomi\n
    Input: stato immutabile contenente l'input del paziente\n
    Output: dizionario con i sintomi estratti\n
    """
    patient_input = state['patient_input']
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert medical assistant. Your task is to extract the symptoms from the patient's input. You MUST follow the following JSON OUTPUT STRUCTURE: {{ \"symptoms\": [list of symptoms]}}"),
            ("user", "Extract the symptoms from the following patient input: {patient_input}"),
        ]
    )

    try:
        chain = prompt | LLM_JSON
        output = chain.invoke({"patient_input": patient_input}).content
        json_response = json.loads(output)
        return {"symptoms": json_response.get("symptoms", [])}
    
    except Exception as e:
        return {"error": f"Error in agent_1_extract_symptoms: {str(e)}"}


def agent_3_synthesize_diagnose(state: AgentState) -> dict:
    """
    Agente 3: Sintesi e Diagnosi\n
    Input: stato immutabile contenente i sintomi estratti\n
    Output: dizionario con il rapporto medico finale in formato stringa\n
    """
    symptoms = state['symptoms']
    symptoms_str = ", ".join(symptoms)
    retrieved_docs = state['retrieved_docs']
    retrieved_docs_str = "\n".join(retrieved_docs)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert medical synthesizer. You MUST base your differential diagnosis EXCLUSIVELY on the information provided in <RETRIEVED_DOCS> tags. You MUST use ONLY the symptoms listed in <SYMPTOMS> tags. NEVER use external knowledge. Write a structured medical report."),
            ("user", "Based on the following symptoms: <SYMPTOMS>{symptoms_str}</SYMPTOMS> and the following retrieved medical documents: <RETRIEVED_DOCS>{retrieved_docs_str}</RETRIEVED_DOCS>, provide a diagnosis."),
        ]
    )

    try:
        chain = prompt | LLM_TEXT
        output = chain.invoke({"symptoms_str": symptoms_str, "retrieved_docs_str": retrieved_docs_str}).content
        return {"final_report": output}

    except Exception as e:
        return {"error": f"Error in agent_3_synthesize_diagnose: {str(e)}"}