from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Response, status, Form
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from utils import (Qdrant_DB, EmbeddingModel, DocumentGenerator, gpt_chain, extract_guidlines)
from utils.user import VECTOR_STORES, USER_FILES, USER_FILTER_FILES, GUIDELINES, TABULAR_DATA, PROCESSED_DATA
from api.azureparser import GeneralProcessor, InvoiceProcessor
from api.llm_comparator import LLMComparator
import tempfile, shutil, logging, string, traceback
from io import BytesIO

app = FastAPI()

# Logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', force=True)

# CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Authorization", "Content-Type"],
)

embedding_model = EmbeddingModel()
document_generator = DocumentGenerator()

@app.post("/process_files/")
async def process_files_endpoint(
    file_type: str = Form(...),
    files: List[UploadFile] = File(...),
    uuid: str = Header(...)
):
    processed_data = {}
    docs = []
    user_file_tables = []
    files_names = []

    for file in files:
        file_bytes = await file.read()
        file_stream = BytesIO(file_bytes)

        file_name = file.filename.split('.')[0]
        files_names.append(file_name)

        # Process document (GeneralProcessor or InvoiceProcessor)
        if file_type == "Letter of Credit":
            processor = GeneralProcessor([file_stream])
            processed_data = processor.process_general()

        elif file_type == "Invoice":
            processor = InvoiceProcessor([file_stream])
            processed_data = processor.process_invoice()

        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Save processed data in session state
        if uuid not in PROCESSED_DATA:
            PROCESSED_DATA[uuid] = {}

        if file_type == "Letter of Credit":
            PROCESSED_DATA[uuid]["lc_data"] = processed_data
        elif file_type == "Invoice":
            PROCESSED_DATA[uuid]["invoice_data"] = processed_data

        # Generate documents and prepare for vector storage
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(file_bytes)
            temp_file.flush()

            splitted_docs, tables_in_file = document_generator.generate_documents(
                file=str(temp_file.name), file_name=file_name
            )

            docs.extend(splitted_docs)
            user_file_tables.extend(tables_in_file)

    collection_name = f"temp_{uuid}"

    if uuid in VECTOR_STORES:
        existing_qdrant = VECTOR_STORES[uuid]
        existing_docs = getattr(existing_qdrant, "documents", [])
        combined_docs = existing_docs + docs

        qdrant = Qdrant_DB(embedding_model, collection_name)
        qdrant.upload_vectors(combined_docs)
        VECTOR_STORES[uuid] = qdrant

        USER_FILES[uuid] = USER_FILES.get(uuid, []) + files_names
        TABULAR_DATA[uuid] = TABULAR_DATA.get(uuid, []) + user_file_tables
    else:
        qdrant = Qdrant_DB(embedding_model, collection_name)
        qdrant.upload_vectors(docs)
        VECTOR_STORES[uuid] = qdrant
        USER_FILES[uuid] = files_names
        TABULAR_DATA[uuid] = user_file_tables

    return processed_data

@app.post("/compare_documents/")
async def compare_documents_endpoint(uuid: str = Header(...)):
    user_data = PROCESSED_DATA.get(uuid)

    if not user_data or "lc_data" not in user_data or "invoice_data" not in user_data:
        raise HTTPException(status_code=400, detail="Both Letter of Credit and Invoice must be processed before comparison.")

    lc_data = user_data["lc_data"]
    invoice_data = user_data["invoice_data"]

    comparator = LLMComparator()
    result = comparator.compare_documents(lc_data, invoice_data)

    return result

@app.post("/query/")
async def query_endpoint(query: str, uuid: str = Header(...)):
    vector_store = VECTOR_STORES.get(uuid)

    if vector_store:
        query = query.lower().translate(str.maketrans({key: f" {key} " for key in string.punctuation}))
        result = gpt_chain(vector_store.vector_store, query, vector_store.documents, uuid)
        return result

    raise HTTPException(status_code=404, detail="User session not found.")

@app.post("/clean_db/")
async def clean_db_endpoint(uuid: str = Header(...)):
    if uuid in VECTOR_STORES:
        del VECTOR_STORES[uuid]
        return Response("User Deleted", status_code=200)

    raise HTTPException(status_code=404, detail="User not found.")

@app.post("/upload_guideline/")
async def gpt_guidelines(file: Optional[UploadFile] = File(None), text: Optional[str] = Form(None)):
    if not file and not text:
        raise HTTPException(status_code=422, detail="No guidelines provided")

    guidelines = ""

    if file:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            file_type = file.filename.split('.')[-1]
            guidelines = extract_guidlines(temp_file.name, file_type)

    if text:
        guidelines += f"\n{text}"

    GUIDELINES["guidelines"] = guidelines
    return Response("Guidelines Updated Successfully", status_code=200)

@app.post("/clear_guidelines/")
def clear_guidelines_endpoint():
    GUIDELINES.clear()
    return Response("Guidelines Cleared Successfully", status_code=200)

@app.get("/get_files_names/")
def get_files_name_endpoint(uuid: str = Header(...)):
    files = USER_FILES.get(uuid)

    if files:
        return files

    raise HTTPException(status_code=404, detail="No files found for user.")

@app.post("/choose_file_filter/")
def choose_file_endpoint(files_selected: Optional[List[str]] = None, uuid: str = Header(...)):
    if uuid not in USER_FILES:
        raise HTTPException(status_code=404, detail="User files not found.")

    if files_selected:
        for file in files_selected:
            if file not in USER_FILES[uuid]:
                raise HTTPException(status_code=400, detail=f"Invalid file: {file}")

    USER_FILTER_FILES[uuid] = files_selected
    return Response("Filter Applied Successfully", status_code=200)

@app.get("/")
def health_check_endpoint():
    return Response("Hi, I am Healthy RAG", status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
