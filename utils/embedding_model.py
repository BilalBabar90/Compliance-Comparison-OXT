from langchain_huggingface import HuggingFaceEmbeddings
import logging
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = os.getenv("parallel_token")

class EmbeddingModel():
    """
    A singleton class that instantiates and provides access to a BAAI embedding model.
    This class ensures that only one instance of the HuggingFaceBgeEmbeddings model.
    
    Attributes:
    - model_instance: Stores the single instance of the embedding model.
    """
    model_instance = None 

    def __new__(cls,*args,**kwargs):

        if cls.model_instance is None:
            logging.info("Embedding Model Loading")
            model_name = "BAAI/bge-large-en-v1.5"
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            cls.model_instance = HuggingFaceEmbeddings(model_name=model_name,model_kwargs=model_kwargs,encode_kwargs=encode_kwargs)
        return cls.model_instance