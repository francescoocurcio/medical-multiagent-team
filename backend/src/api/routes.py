from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from src.agents.graph import GRAPH
from src.agents.state import AgentState
import json

router = APIRouter()

@router.get("/triage/stream")
async def stream_triage(patient_input : str = Query(..., description="Input del paziente per il triage medico")):
    """
    Endpoint per avviare il processo di triage medico. Viene usato per inviare aggiornamenti in tempo reale al client.
    Input: input del paziente 
    Output: restituisce uno stream SSE (Server-Sent Events) di aggiornamenti sullo stato del processo.
    """
    async def event_generator():

        initial_state: AgentState = {
            "patient_input": patient_input
        }

        async for event in GRAPH.astream_events(initial_state, version="v2"):
            # È necessario filtrare gli eventi che descrivono il lifecycle del grafo,
            # in modo da inviare solo gli eventi di tipo on_chat_model_stream (è l'unico evento
            # che trasporta progressivamente i singoli frammenti di testo generati dal modello.
            if event["event"] == "on_chat_model_stream":
                chunk_content = event["data"]["chunk"].content

                # Usiamo langgraph_node dai metadati per distinguere i nodi del grafo
                node_name = event.get("metadata", {}).get("langgraph_node", event.get("name", "unknown_node"))

                if chunk_content:
                    # Serializzazione JSON per prevenire la rottura del protocollo SSE
                    # a causa di newline presenti all'interno di chunk_content.
                    payload = json.dumps({
                        "node": node_name,
                        "text": chunk_content
                    })
                    
                    # La sintassi corretta per SSE: "data: <payload>\n\n"
                    yield f"data: {payload}\n\n"

        yield 'data: {"type": "done"}\n\n'

    return StreamingResponse(event_generator(), 
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
                            )