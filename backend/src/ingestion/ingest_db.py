"""
Modulo per l'ingestion dei dati medici all'interno del database.

Il modulo si occupa di leggere i dati medici di tipo JSONL presenti nella cartella 
backend/data/processed e di estrarre le informazioni rilevanti da ogni riga di ognuno dei file 
tramite le parole chiave 'title' e 'content' e crea una lista Python con oggetti di tipo Document.
Gli oggetti di tipo Document vengono poi inseriti all'interno di ChromaDB, 
un database vettoriale, simile a FAISS, che permette di effettuare ricerche semantiche sui dati.
Per la definizione della pipeline ETL (Extract, Transform, Load) di ingestion si utilizza il principio 
di Separation of Concerns.
Modello di embedding: all-MiniLM-L6-v2.
"""

import os
import glob
import json
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def parse_jsonl_to_documents(filepath : str):
    with open(filepath, 'r', encoding='utf-8') as f:
        documents = []
        for line in f:
            data = json.loads(line)
            doc_id = data.get('id', '')
            title = data.get('title', '')
            content = data.get('content', '')
            if title and content:
                document = Document(page_content=content, metadata={'id': doc_id, 'title': title})
                documents.append(document)

    return documents


def ingest_documents(chroma_instance, documents, batch_size=10):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        chroma_instance.add_documents(batch)

def main ():
    # Path per i dati processati e per il database persistente
    batch_size = 20
    data_path = "backend/data/processed"
    persisted_dir = "backend/chroma_vector_db"

    # Embedding model
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    chroma_instance = Chroma(collection_name="medical_data", embedding_function=embedding_model, persist_directory=persisted_dir)

    # Processing dei file JSONL e ingestion dei documenti
    # Il ciclo for scorre tutti i file con estensione .jsonl presenti nella cartella data_path,
    # e per ognuno di essi chiama la funzione parse_jsonl_to_documents per estrarre i documenti.
    # Una volta ottenuta la lista complessiva con tutti i document, voglio iterare a step di 10 documenti
    # per volta e chiamare la funzione ingest_documents per inserire i documenti all'interno di ChromaDB.
    for filepath in glob.glob(os.path.join(data_path, "*.jsonl")):
        documents = parse_jsonl_to_documents(filepath)
        ingest_documents(chroma_instance, documents, batch_size=batch_size)

if __name__ == "__main__":
    main()