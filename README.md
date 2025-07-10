# Leter of credit and Invoice comparison tool 

This is a letter of credit and invoice comparison tool that also provides chatbot features. 

If you want to do it manually, create a virtual environment and install the requirements separately for the frontend and backend, and then run the commands as existing in the README.md.

## Features

- Can Upload Multiple PDF Files 
- Query to LLM from PDF
- Clean the Vector Stores
- Can select files to query from selected files
- Admin can set the Guidelines for LLM Response
- Admin can clear the Guidelines

## API Reference

#### Post the PDFs to create a vector Store against the UUID

```http
  POST /process_files/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `UUID` | `Header` | **Required**. UUID of the User|
| `Files` | `File` | **Required**. PDF files  |
#### Compares the respones from arzure document intelligence endpoints for Lc and invoice

```http
  POST /compare_documents/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `UUID` | `Header` | **Required**. UUID of the User|
| `Files` | `File` | **Required**. PDF files  |

#### Post the query and relative uuid in header

```http
  POST /query/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `UUID` | `Header` | **Required**. UUID of the User|
| `query`      | `String` | **Required**. Query from PDF|

#### Post uuid in header

```http
  POST /clean_db/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `UUID` | `Header` | **Required**. UUID of the User|

#### Post the Guidelines in PDF file or Text or Both from LLM

```http
  POST /upload_guideline/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `File` | `File` | **Optional**. PDF file of Guidelines from Admin to LLM|
| `Text`      | `String` | **Optional**. Guidelines from Admin to LLM|

#### Post Request to clear all the Guidelines

```http
  POST /clear_guidelines/
```

#### GET the names of All the files uploaded by USER

```http
  GET /get_files_names/
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `UUID` | `Header` | **Required**. UUID of the User|

#### POST the files names selected by the USER for filter 

```http
  POST /choose_file_filter/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `UUID` | `Header` | **Required**. UUID of the User|
| `Files` | `LIST` | **Required**. List files names|

## Environment Variables

To run this project, you will need to add the following environment variable to your .env file

`api_type`

`openai_api_key`

`api_base`

`api_version`

`deployment_name`

`model_name`

`deployment_version`

`parallel_token`

`BASE_URL`

`GENERAL_parser:http://coyote.entropy-x.com:9003/parse_general/`

`INVOICE_PARSER:http://coyote.entropy-x.com:9003/parse_invoice/`
## Docker-compose setup 
Just run the following command in your terminal to start the project
```bash
  docker-compose up
```
## Run Locally

#### Backend Setup

Clone the project

```bash
  git clone git@bitbucket.org:entropyx/rag.git
```

Go to the project directory

```bash
  cd RAG
```
Create a virtual enn
```bash
  conda create -n <name> python=3.9
```
Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup

Go to the Frontend directory

```bash
    cd streamlit_app.py
```

Set the BASE_URL in the env file which the backend URL

Start the server

```bash
  streamlit run streamlit_app.py
