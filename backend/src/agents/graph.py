from src.agents.state import AgentState
from src.agents.nodes import agent_1_extract_symptoms, medical_docs_retriever ,agent_3_synthesize_diagnose
from langgraph.graph import StateGraph, END

def route_after_agent_1(state: AgentState) -> str:
    """
    Funzione di routing per determinare il prossimo nodo dopo l'Agente 1.
    Se ci sono sintomi estratti, si passa al nodo Medical_docs_retriever.
    Altrimenti, si termina il grafo.
    """
    if state['symptoms']:
        return "success"
    else:
        return "failure"

def compile_graph():
    """
    Funzione per compilare il grafo degli agenti medici. 
    Definisce i nodi, le transizioni e il punto d'ingresso del grafo.
    """
    # Creazione del grafo e definizione dello stato iniziale
    graph = StateGraph(AgentState)

    # Definizione dei nodi del grafo
    graph.add_node("Agent_1_extract_symptoms", agent_1_extract_symptoms)
    graph.add_node("Medical_docs_retriever", medical_docs_retriever)
    graph.add_node("Agent_3_synthesize_diagnose", agent_3_synthesize_diagnose)

    # Definizione del punto d'ingresso del grafo (input del paziente)
    graph.set_entry_point("Agent_1_extract_symptoms")

    # Definizione delle transizioni del grafo
    graph.add_conditional_edges("Agent_1_extract_symptoms", route_after_agent_1, {"success": "Medical_docs_retriever", "failure": END})
    graph.add_edge("Medical_docs_retriever", "Agent_3_synthesize_diagnose")
    graph.add_edge("Agent_3_synthesize_diagnose", END)

    # Compilazione del grafo
    compiled_graph = graph.compile()
    return compiled_graph
    
GRAPH = compile_graph()