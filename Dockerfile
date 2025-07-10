FROM python:3.9-slim-bullseye


WORKDIR /app

RUN pip install --upgrade pip

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN apt-get install -y poppler-utils tesseract-ocr

RUN pip install "unstructured[pdf]"

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8009

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]
