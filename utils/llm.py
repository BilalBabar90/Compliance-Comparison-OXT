from langchain.chains import LLMChain
import logging
import traceback
from .azure_model import azure_openai
from .guidelines_function import guidelines_chain
from .doc_reteriver import ensemble_retriever
from .prompts import QUERY_PROMPT
from .user import TABULAR_DATA

try:
    llm = azure_openai
except Exception as e:
    error_msg = "Error while Initializing ChatOpenAi: "
    logging.error(f"{error_msg}{e} trace_back:{traceback.format_exc()}")
    raise Exception (f"{error_msg} {e}")

def get_files(context) -> dict:
    """
    Get the Context retrieved by the retrievers and extract the file names which has 
    tabular data 
    Parameters:
        - context(Documents): Documents retrieved by the retriever
    Return:
        Dict: Dictionary containing filename as key and their pages as values 

    """
    tabular_retrieved_files = {}
    for docs in context:
        
        if docs.metadata.get("has_table"):
            file_name = docs.metadata.get("file_name")
            page_number = docs.metadata.get("page_number")
        
            if tabular_retrieved_files.get(file_name):
                tabular_retrieved_files[file_name].add(page_number)
            else:
                tabular_retrieved_files[file_name] =  {page_number}
            
    return tabular_retrieved_files

def get_tables(files,uuid) ->  list:
    """
    Retrieves reference tables based on file names and page numbers.

    Parameters:
        - files (dict): A dictionary containing file names as keys and corresponding page numbers as values.
        - uuid (str): Unique identifier for the tabular data.

    Returns:
        -list: A list of reference tables found in the specified files and pages.

    """
    tabular_data = TABULAR_DATA.get(uuid)
    referance_table = []
    
    keys = list(files.keys())
    keys_item = -1
    tables = False
    table_found = True
    pages = {}
    try :

        while True:
        
            if not pages and not tables:

                keys_item +=1
                if keys_item<len(keys):
                    file_name = keys[keys_item]
                    pages = files[keys[keys_item]]
                else:
                    break 
            
            
            #  for founding tables of one file pages  
            if table_found:
                item = 0
                page_number = pages.pop()
                table_found = False

            if not pages:
                tables = True

            if (tabular_data[item].get("file_name")==file_name and tabular_data[item].get("page_number")==page_number):
                table_found = True
                referance_table.append(tabular_data[item])
                tables = False 
            
            item += 1

            if item == len(tabular_data):
                table_found = True

        return referance_table
    
    except Exception as e:
        error_msg =" Error while Retrieving Tables: "
        logging.error(f"{error_msg}{e} trace_back:{traceback.format_exc()}")
        raise Exception (f"{error_msg} {e}")

def gpt_chain(vector_store,question,documents,uuid) -> dict:
    
    """
    Executes a query-answering process using a LLM, supported by an ensemble of retrievers for context retrieval.

    An ensemble retriever, combining BM25 and a vector similarity-based retriever, to fetch relevant context from a provided document set.

    Parameters:
    - vector_store (VectorStore): A vectorized data store used for context retrieval based on similarity scores.
    - question (str): The question to be answered by the LLM.
    - documents (list): A list of documents that serve as a knowledge base for context retrieval.
    - uuid (str): A unique identifier used for filtering data in retrievers.

    Returns:
    - dict: A dictionary containing the generated answer.
    """

    try:        
        logging.info("Generating Q/A Chain")
        context = ensemble_retriever(vector_store,documents,uuid,question)
        files = get_files(context)
        referance_table = get_tables(files,uuid)
        if context:
            qa_chain = LLMChain(llm=llm,prompt=QUERY_PROMPT)
            gpt_response = qa_chain({"question":question,"context":context,"referance_table":referance_table})
            result = guidelines_chain(question,gpt_response["text"])
            logging.info("Q/A Chain Processed Successfully")

            return result
        
        return "No Data Found"
        
    except Exception as e:
        error_msg =" Error while Generating Chain:"
        logging.error(f"{error_msg}{e} trace_back:{traceback.format_exc()}")
        raise Exception (f"{error_msg} {e}")
