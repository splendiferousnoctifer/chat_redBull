"""Load html from files, clean up, split, ingest into Weaviate."""
import math
import re
import requests
from bs4 import BeautifulSoup
import json

from langchain.document_loaders import ReadTheDocsLoader, DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.vectorstores import Pinecone
import pinecone


import os
os.environ.get('OPENAI_API_KEY')

def return_url(url):
    # send HTTP request to the webpage and get the response content
    response = requests.get(url)
    html_content = response.content

    # parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    pattern = r'(?<="videoUrl":")[^"]+' 
    matches = re.findall(pattern, str(soup))


    return(matches[0])


def ingest_docs():
    pinecone.init(
        api_key=os.environ.get('PINECONE_API'),  # find at app.pinecone.io
        environment="eu-west1-gcp",  # find at app.pinecone.io
    )

    index_name = "redbullchat2"

    """Get documents from web pages."""
    
    print("Loading documents...")
    #loader = DirectoryLoader('www.voestalpine.com/', glob="**/*.html")
    #loader = DirectoryLoader('www.stoeckl.ai/', glob="**/*.html")
    loader = DirectoryLoader('data-bull/', glob="**/*.txt")



    raw_documents = loader.load()

    for i in range(len(raw_documents)):
        source = raw_documents[i].metadata['source']
        pattern = r'CP-[SVT]-\d{3,6}'
        matches = re.findall(pattern, source)

        if (matches[0][3] == 'V'):   
            pattern = r"(\d{0,9})\.txt"
            match = re.search(pattern, source)
            if match[0]:
                raw_documents[i].metadata['source'] = (return_url("https://editor.redbullcontentpool.com/api/v1/assets?sort=-firstPublishedAt&include=offers.licenseOffer&format=contentExpo&filter%5bassetModel%5d=video&filter%5bchannel%5d=communication&filter%5bproductId%5d=" + str(matches[0])) + "&time=" + str(int((int(match[0][:-4])/25)))).replace('https:', 'video:')
        elif(matches[0][3] == 'P'):   
            raw_documents[i].metadata['source'] = return_url("https://editor.redbullcontentpool.com/api/v1/assets?sort=-firstPublishedAt&include=offers.licenseOffer&format=contentExpo&filter%5bassetModel%5d=photo&filter%5bchannel%5d=communication&filter%5bproductId%5d=" + str(matches[0])).replace('https:', 'image:')
        elif(matches[0][3] == 'S'):   
            raw_documents[i].metadata['source'] = "https://www.redbullcontentpool.com/international/" + str(matches[0])
        else:
            raw_documents[i].metadata['source'] = raw_documents[i].metadata['source']


    #region embedding & save    
    #"""
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
   # """
    #endregion


if __name__ == "__main__":
    ingest_docs()
