FROM python:3.10.7

# For better caching we list the packages
RUN pip install \
    fastapi==0.92.0 \
    black \
    isort \
    websockets==10.4 \
    pydantic \
    langchain==0.0.105 \
    uvicorn==0.20.0 \
    jinja2 \
    faiss-cpu==1.7.3 \
    bs4 \
    unstructured==0.5.2 \
    libmagic==1.0
 

WORKDIR /code
COPY . /code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--forwarded-allow-ips=*"]