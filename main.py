"""Main entrypoint for the app."""
import logging
import pickle
from pathlib import Path
from typing import Optional
import pinecone


from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from langchain.embeddings import OpenAIEmbeddings
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from langchain.vectorstores import VectorStore, Pinecone

from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from query_data import get_chain
from schemas import ChatResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
vectorstore: Optional[VectorStore] = None

index_name = "redbullchat2"

import os
os.environ["LANGCHAIN_HANDLER"] = "langchain"	
os.environ.get('OPENAI_API_KEY')

#vstore = "vectorstore.pkl"

@app.on_event("startup")
async def startup_event():
    logging.info("loading vectorstore")
    global vectorstore
    #vectorstore = ingest_docs()


    pinecone.init(
        api_key=os.environ.get('PINECONE_API'),  # find at app.pinecone.io
        environment="eu-west1-gcp",  # find at app.pinecone.io
    )

    vectorstore = Pinecone.from_existing_index(index_name=index_name, embedding=OpenAIEmbeddings())


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)

    chat_history = []

    qa_chain = get_chain(vectorstore, question_handler, stream_handler, tracing=False)


    while True:
        try:
            # Receive and send back the client message
            question = await websocket.receive_text()
            resp = ChatResponse(sender="you", message=question, type="stream")
            await websocket.send_json(resp.dict())

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())
            logging.info(f"start_resp={start_resp.dict()}")


            result = await qa_chain.acall(
                {"question": question, "chat_history": chat_history}
            )
            chat_history.append((question, result["answer"]))

            end_resp = ChatResponse(sender="bot", message="", type="end")
            logging.info(f"end_resp={end_resp.dict()}")


            await websocket.send_json(end_resp.dict())
        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender="bot",
                message="Sorry, something went wrong. Try again.",
                type="error",
            )
            raise e
            await websocket.send_json(resp.dict())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
