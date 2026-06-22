from typing import TypedDict

class AgentState(TypedDict):
    """
    Rappresenta lo stato immutabile che viene passato
    tra i nodi del grafo. Ogni agente legge dallo stato e restituisce 
    un dizionario con i valori aggiornati
    """
    patient_input : str
    symptoms : list[str] # Lista di sintomi estratti dall'Agente 1
    retrieved_docs : list[str] # Lista di documenti recuperati da ChromaDB
    final_report : str # Report finale generato dall'Agente 3
    error : str # Messaggio di errore, da assegnare per indicare eventuali problemi durante l'elaborazione dello stato