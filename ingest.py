"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle

from langchain.document_loaders import ReadTheDocsLoader, DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.vectorstores import Pinecone
import pinecone


import os
os.environ.get('OPENAI_API_KEY')

def ingest_docs():
    pinecone.init(
        api_key=os.environ.get('PINECONE_API'),  # find at app.pinecone.io
        environment="us-central1-gcp",  # find at app.pinecone.io
    )

    index_name = "voestchat"

    """Get documents from web pages."""
    
    print("Loading documents...")
    loader = DirectoryLoader('www.voestalpine.com/', glob="**/*.html")
    #loader = DirectoryLoader('www.stoeckl.ai/', glob="**/*.html")


    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    
    print("Splitting documents...")
    documents = text_splitter.split_documents(raw_documents)

    print("Embedding documents...")
    embeddings = OpenAIEmbeddings()

  

    print("Ingesting documents...")
    vectorstore = Pinecone.from_documents(documents, embeddings, index_name=index_name)



if __name__ == "__main__":
    ingest_docs()
