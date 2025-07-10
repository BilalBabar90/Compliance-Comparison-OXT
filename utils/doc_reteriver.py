from .user import USER_FILES, USER_FILTER_FILES
from qdrant_client.http import models as qdrant_models
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
import logging, traceback


def vector_store_retriever(file, vector_store):
    """
    Create a retriever for a specific file from a vector store.

    Parameters:
    - file (str): The name of the file for which the retriever is to be created.
    - vector_store (Qdrant Model Object): The vector store object from Qdrant models.

    Returns:
    - A retriever object configured for the specified file.
    """
    try:
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            ef_construct=500,
            search_kwargs=dict(
                filter=qdrant_models.Filter(must=[
                    qdrant_models.FieldCondition(
                        key="metadata.file_name",
                        match=qdrant_models.MatchValue(value=file)
                    )
                ]),
                score_threshold=0.5,
                k=6
            )
        )
        return retriever
    except Exception as e:
        error_msg = "Error in vector_store_retriever:"
        logging.error(f"{error_msg}{e} trace_back:{traceback.format_exc()}")
        raise Exception(f"{error_msg} {e}")


def bm25_retriever(file, documents):
    """
    Initializes a BM25 Retriever for documents related to a specific file.

    Parameters:
    - file (str): The name of the file to filter documents by.
    - documents (list): A list of document objects, each with a 'metadata' attribute containing a 'file_name' key.

    Returns:
    - BM25Retriever: An instance of BM25Retriever initialized with documents related to the specified file.
    """
    try:
        filtered_docs = [doc for doc in documents if doc.metadata.get("file_name") == file]
        retriever = BM25Retriever.from_documents(filtered_docs)
        retriever.k = 6
        return retriever
    except Exception as e:
        error_msg = "Error in bm25_retriever:"
        logging.error(f"{error_msg}{e} trace_back:{traceback.format_exc()}")
        raise Exception(f"{error_msg} {e}")


def ensemble_retriever(vector_store, documents, uuid, query):
    """
    Retrieves relevant documents based on a given query using an ensemble approach
    that combines vector-based and BM25 retrievers.

    Parameters:
    - vector_store: The storage for vector embeddings of documents.
    - documents: A collection of documents to be searched.
    - uuid: A unique identifier for the user, used to select specific files for retrieval.
    - query: The search query for retrieving relevant documents.

    Returns:
    - context: A list of documents relevant to the query, based on the combined
      results of the vector-based and BM25 retrievers.
    """
    try:
        selected_files = USER_FILTER_FILES.get(uuid, [])
        if not selected_files:
            selected_files = USER_FILES.get(uuid, [])

        context = []
        for file in selected_files:
            vector_retriever = vector_store_retriever(file, vector_store)
            bm25 = bm25_retriever(file, documents)
            ensemble = EnsembleRetriever(retrievers=[vector_retriever, bm25], weights=[0.5, 0.5])

            # This is the main change: use `invoke()` instead of `get_relevant_documents()`
            data = ensemble.invoke(query)

            context.extend(data)

        return context
    except Exception as e:
        error_msg = "Error in ensemble_retriever:"
        logging.error(f"{error_msg}{e} trace_back:{traceback.format_exc()}")
        raise Exception(f"{error_msg} {e}")
