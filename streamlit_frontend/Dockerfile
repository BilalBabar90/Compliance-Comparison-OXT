FROM python:3.9-slim-bullseye


WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8008:8008

CMD ["streamlit" ,"run" ,"streamlit_app.py", "--server.port=8008", "--server.address=0.0.0.0"]
