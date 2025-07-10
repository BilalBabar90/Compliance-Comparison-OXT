import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()


openai_api_type = os.getenv("api_type")
openai_api_base =os.getenv("api_base")
openai_api_version = os.getenv("api_version")
openai_api_key = os.getenv("openai_api_key")
deployment_name = os.getenv("deployment_name")
model_name = os.getenv("model_name")
model_version = os.getenv("deployment_version")



azure_openai = AzureChatOpenAI(deployment_name=deployment_name,
                            model=model_name,              
                            openai_api_key=openai_api_key,
                            openai_api_version=openai_api_version,
                            azure_endpoint=openai_api_base,
                            openai_api_type=openai_api_type,
                            temperature=0.1
                            )