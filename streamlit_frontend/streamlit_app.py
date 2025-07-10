import os
import streamlit as st
from streamlit_chat import message
import requests, json, uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

# Utility function to get file names from backend
def get_files_name(uuid):
    url = f"{BASE_URL}/get_files_names/"
    headers = {"uuid": uuid}
    response = requests.get(url, headers=headers)
    return response.json()

# Utility function to apply file filter (future use)
def apply_filter(files, uuid):
    url = f"{BASE_URL}/choose_file_filter/"
    headers = {'accept': 'application/json', 'uuid': uuid, 'Content-Type': 'application/json'}
    requests.post(url, headers=headers, data=json.dumps(files))

# Utility function to generate responses (RAG query)
def generate_response(user_input):
    url = f"{BASE_URL}/query/"
    headers = {'accept': 'application/json', 'uuid': st.session_state['uuid'], 'content-type': 'application/x-www-form-urlencoded'}
    params = {'query': user_input}
    response = requests.post(url, params=params, headers=headers)
    return response.json()

# Process and upload files via backend (combined in one step)
def process_files_on_backend(files, file_type):
    url = f"{BASE_URL}/process_files/"
    headers = {"uuid": st.session_state['uuid']}
    
    file_data = [("files", (f.name, f)) for f in files]
    response = requests.post(url, headers=headers, files=file_data, data={"file_type": file_type})

    if response.status_code == 200:
        refresh_and_cache_files()  # Refresh files list immediately after processing
        return response.json()
    else:
        st.error(f"Failed to process {file_type}. Please check the file format and try again.")
        return None

# Refresh file list from backend
def refresh_and_cache_files():
    backend_files = get_files_name(st.session_state['uuid'])
    st.session_state["file_names"] = backend_files

# Fetch text from chat input
def get_text(state, value):
    st.chat_input("Please Enter your Query Here", key=f"input-{value}", disabled=state)
    if st.session_state.get(f"input-{value}"):
        return st.session_state[f"input-{value}"].strip()
    return None

# Apply custom styles
def get_styles(parameters):
    style = f"""
        <style>
            .stTextInput {{ position: fixed; bottom: 3rem; }}
            .stMultiSelect > label {{ font-size:105%; font-weight:bold; }}
            div[data-testid=stToast] {{ background-color: green; }}
            div[data-testid=stSidebarUserContent] {{ user-select: {parameters}; pointer-events: {parameters}; }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)

# Initialize Streamlit app & session state
st.set_page_config(page_title="Entropy")
st.sidebar.title("SmartDocx")

if "uploaded_file_names" not in st.session_state:
    st.session_state['uploaded_file_names'] = []

if "disable" not in st.session_state:
    st.session_state['disable'] = False

if "file_names" not in st.session_state:
    st.session_state["file_names"] = []

if "filter_flag" not in st.session_state:
    st.session_state["filter_flag"] = False

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'uuid' not in st.session_state:
    st.session_state['uuid'] = str(uuid.uuid4())

# Sidebar upload - Letter of Credit
st.sidebar.subheader("Upload Letter of Credit")
with st.sidebar.form("lc-upload-form", clear_on_submit=True):
    lc_files = st.file_uploader("Upload Letter of Credit", accept_multiple_files=True, type=["pdf"], key="lc_files")
    lc_submitted = st.form_submit_button("Upload Letter of Credit")

if lc_submitted and lc_files:
    lc_data = process_files_on_backend(lc_files, "Letter of Credit")
    if lc_data:
        st.session_state["lc_data"] = lc_data

# Sidebar upload - Invoice
st.sidebar.subheader("Upload Invoice")
with st.sidebar.form("invoice-upload-form", clear_on_submit=True):
    invoice_files = st.file_uploader("Upload Invoice", accept_multiple_files=True, type=["pdf"], key="invoice_files")
    invoice_submitted = st.form_submit_button("Upload Invoice")

if invoice_submitted and invoice_files:
    invoice_data = process_files_on_backend(invoice_files, "Invoice")
    if invoice_data:
        st.session_state["invoice_data"] = invoice_data

# Sidebar - Show list of uploaded files
st.sidebar.title("Uploaded Files")
for file_name in st.session_state["file_names"]:
    st.sidebar.markdown(file_name)

# Main page - Title and Description
st.markdown("")
st.title("📑 Letter of Credit and Invoice Comparison Tool")
st.markdown("Upload your PDFs (Letter of Credit or Invoice), then click 'Compare Documents' to find discrepancies. You can also chat with me.")

# Compare Documents Button with Styling
st.markdown("""
<style>
div.stButton > button {
    background-color: #ff9100;
    color: #FFFFFF;
    padding: 1rem;
    font-size: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

compare_documents_button = st.button("Compare Documents")

# Compare action calls backend directly
if compare_documents_button:
    url = f"{BASE_URL}/compare_documents/"
    headers = {"uuid": st.session_state['uuid']}

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        comparison_result = response.json()
        st.subheader("🔍 Comparison Results")
        st.write(comparison_result)
    else:
        st.error("Failed to compare documents. Please ensure both are uploaded and processed correctly.")

# Chat Input and Display Logic
input_container = st.container()
user_input = ""

if st.session_state['disable']:
    with input_container:
        user_input = get_text(st.session_state['disable'], "disabled")
else:
    with input_container:
        user_input = get_text(st.session_state['disable'], "enabled")

response_container = st.container()
with response_container:
    if user_input:
        if not st.session_state["file_names"]:
            st.warning('Please upload a PDF first.')
        else:
            get_styles("none")
            response = generate_response(user_input)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)
            get_styles("auto")

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=f"{i}_user")
            message(st.session_state["generated"][i], key=f"{i}")
