# 🦜️🔗 ChatLangChain with own Data

This repo is an implementation of a locally hosted chatbot specifically focused on question answering over the [LangChain documentation](https://langchain.readthedocs.io/en/latest/).
Built with [LangChain](https://github.com/hwchase17/langchain/), [FastAPI](https://fastapi.tiangolo.com/), [Pinecone](https://www.pinecone.io/).

Currently the page goes inactive after a few minutes of no interaction.

## 📝 Prompt engineering
If you want to make changes to the prompt, change the prompt_template in query_data.py. 

## ✅ Running locally
1. Install dependencies: `pip install -r requirements.txt -U`
2. Run `ingest.py` to ingest LangChain docs data into the Pinecone vectorstore (only needs to be done once).
3. Run the app: `make start`
4. Open [localhost:9000](http://localhost:9000) in your browser.


## 📚 Technical description
There are two components: ingestion and question-answering.

Ingestion has the following steps:

1. Pull html from documentation site
2. Load html with LangChain's [ReadTheDocs Loader](https://langchain.readthedocs.io/en/latest/modules/document_loaders/examples/readthedocs_documentation.html)
3. Split documents with LangChain's [TextSplitter](https://langchain.readthedocs.io/en/latest/reference/modules/text_splitter.html)
4. Create a vectorstore of embeddings, using LangChain's [vectorstore wrapper](https://langchain.readthedocs.io/en/latest/reference/modules/vectorstore.html) (with OpenAI's embeddings and Pinecone vectorstore).

Question-Answering has the following steps, all handled by [ChatVectorDBChain](https://langchain.readthedocs.io/en/latest/modules/indexes/chain_examples/chat_vector_db.html):

1. Given the chat history and new user input, determine what a standalone question would be (using GPT-3).
2. Given that standalone question, look up relevant documents from the vectorstore.
3. Pass the standalone question and relevant documents to GPT-3 to generate a final answer.
