import io
import requests
import os
from dotenv import load_dotenv
load_dotenv()


class InvoiceProcessor:
    def __init__(self, invoice_file):
        self.invoice_file = invoice_file
        self.fastapi_url =  os.getenv("INVOICE_PARSER")

    def load_file_as_stream(self) -> io.BytesIO:
        file_obj = self.invoice_file
        if isinstance(file_obj, list):
            if file_obj:
                file_obj = file_obj[0]
            else:
                raise ValueError("No file provided in general_file list.")
        return io.BytesIO(file_obj.getvalue())


    def process_invoice(self):
        file_stream = self.load_file_as_stream()
        try:
            files = {
                "file": ("document.pdf", file_stream, "application/pdf")  
            }
            response = requests.post(self.fastapi_url, files=files)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"An error occurred: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            return None



class GeneralProcessor:
    def __init__(self, general_file):
        self.general_file = general_file
        self.fastapi_url = os.getenv("GENERAL_PARSER") 

    def load_file_as_stream(self) -> io.BytesIO:
        file_obj = self.general_file
        if isinstance(file_obj, list):
            if file_obj:
                file_obj = file_obj[0]
            else:
                raise ValueError("No file provided in general_file list.")
        return io.BytesIO(file_obj.getvalue())


    def process_general(self):
        file_stream = self.load_file_as_stream()
        try:
            files = {
                "file": ("document.pdf", file_stream, "application/pdf")  
            }
            response = requests.post(self.fastapi_url, files=files)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"An error occurred: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            return None