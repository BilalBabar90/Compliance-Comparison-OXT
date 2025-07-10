import json
from dotenv import load_dotenv
from langchain.schema import SystemMessage, HumanMessage
from utils.prompts import DISCREPANCY_DETECTION_PROMPT
from utils.azure_model import azure_openai

load_dotenv()

class LLMComparator:
    def __init__(self):
        self.llm = azure_openai

    def clean_data(self, data):
        if isinstance(data, dict):
        
            for key in ["spans", "confidence", "mean_confidence", "min_confidence"]:
                data.pop(key, None)

            if 'boundingRegions' in data:
                regions = data.pop('boundingRegions')
                if isinstance(regions, list):
                    page_numbers = [region.get('pageNumber') for region in regions if isinstance(region, dict) and 'pageNumber' in region]
                    if page_numbers:
                        data['pageNumber'] = page_numbers[0] if len(page_numbers) == 1 else page_numbers
                elif isinstance(regions, dict) and 'pageNumber' in regions:
                    data['pageNumber'] = regions['pageNumber']

            if 'currencyCode' in data and data['currencyCode'] == "USD":
                del data['currencyCode']
            
            if 'valueCurrency' in data and isinstance(data['valueCurrency'], dict):
                if data['valueCurrency'].get('currencyCode') == "USD":
                    del data['valueCurrency']['currencyCode']

            for key in list(data.keys()):
                data[key] = self.clean_data(data[key])  
            
            return data
        
        elif isinstance(data, list):
            return [self.clean_data(item) for item in data]  
        
        else:
            return data


    def compare_documents(self, lc_response, invoice_response):
        
        cleaned_invoice_response = self.clean_data(invoice_response)
        cleaned_lc_response = self.clean_data(lc_response)
        
        prompt = DISCREPANCY_DETECTION_PROMPT.format(
            lc_response=json.dumps(cleaned_lc_response, indent=2),
            invoice_response=json.dumps(cleaned_invoice_response, indent=2)
        )

        response = self.llm.invoke([
            SystemMessage(content="You are expert in reviewing financial documents, You have the compare letter of credit with the invoice"),
            HumanMessage(content=prompt)
        ])
        
        try:
            return response.content
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from llm"}