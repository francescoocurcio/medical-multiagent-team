#Il browser blocca le richieste SSE dal frontend (localhost:3000) verso il backend (localhost:8000)
# perché sono su origini diverse — questo è il meccanismo CORS (Cross-Origin Resource Sharing).
# Senza CORS middleware, EventSource nel browser riceverà un errore bloccante prima ancora di ricevere un evento.
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.api.routes import router

def create_app() -> FastAPI:
    """
    Funzione per creare e configurare l'app FastAPI.
    """
    app = FastAPI(title= "Medical Triage API",
                  description= "Triage medico per la redazione di report specifici basati sui sintomi del paziente e i documenti della knowledge base.",
                  version = "1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Permette richieste da localhost:3000
        allow_credentials=True,
        allow_methods=["GET"],  # Permette solo il metodo GET
        allow_headers=["*"],  # Permette tutti gli header
    )

    # Includiamo il router con i percorsi definiti in src/api/routes.py
    app.include_router(router, prefix="/api")

    return app

app = create_app()