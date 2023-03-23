"""Create a ChatVectorDBChain for question/answering."""

from langchain.callbacks.base import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import ChatVectorDBChain
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

from langchain.llms import OpenAI
from langchain.vectorstores.base import VectorStore

from langchain.prompts.prompt import PromptTemplate


prompt_template_stoeckl = """You are an AI assistant for the webblog of Andreas Stöckl. The website is located at https://stoeckl.ai
You are given the following extracted parts of a long document and a question. Provide a conversational answer with a hyperlink to the source.
You can construct the hyperlink by using the href and section fields in the context and the base url https://stoeckl.ai/.
You should only use hyperlinks that are explicitly listed as a source in the context. Do NOT make up a hyperlink that is not listed.
You should only give answers that are explicitly listed in the webpage.  Do not make up answers.
If the question includes a request for code, provide a fenced code block directly from the documentation.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
If the question is not related to the content of the website, politely inform them that you are tuned to only answer questions about Andreas Stöckls blog.
No matter the input language, you should always answer in German.

Question: {question}

Documents:
=========
{context}
=========

Answer in Markdown:"""

prompt_template = """You are an AI assistant for the webpage of voestalpine. The website is located at https://voestalpine.com/
You are given the following extracted parts of a long document and a question. Provide a conversational answer with a hyperlink to the source.
You can construct the hyperlink by using the href and section fields in the context and the base url https://voestalpine.com/.
You should only use hyperlinks that are explicitly listed as a source in the context. Do NOT make up a hyperlink that is not listed.
You should only give answers that are explicitly listed in the webpage.  Do not make up answers.
If the question includes a request for code, provide a fenced code block directly from the documentation.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
If the question is not related to the content of the website, politely inform them that you are tuned to only answer questions about voestalpine.
No matter the input language, you should always answer in German.

Question: {question}

Documents:
=========
{context}
=========

Answer in Markdown:"""

QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

def get_chain(
    vectorstore: VectorStore, question_handler, stream_handler, tracing: bool = False
) -> ChatVectorDBChain:
    """Create a ChatVectorDBChain for question/answering."""
    # Construct a ChatVectorDBChain with a streaming llm for combine docs
    # and a separate, non-streaming llm for question generation
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])
    if tracing:
        tracer = LangChainTracer()
        tracer.load_default_session()
        manager.add_handler(tracer)
        question_manager.add_handler(tracer)
        stream_manager.add_handler(tracer)

    question_gen_llm = OpenAI(
        temperature=0,
        verbose=True,
        callback_manager=question_manager,
    )
    streaming_llm = OpenAI(
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        temperature=0,
    )

    question_generator = LLMChain(
        llm=question_gen_llm, prompt=CONDENSE_QUESTION_PROMPT, callback_manager=manager
    )

    #doc_chain = load_qa_chain_wi(
    #    streaming_llm, chain_type="stuff", prompt=QA_PROMPT, callback_manager=manager
    #)

    doc_chain = load_qa_with_sources_chain(streaming_llm, chain_type="stuff")#, prompt=QA_PROMPT, callback_manager=manager)
    

    qa = ChatVectorDBChain(
        vectorstore=vectorstore,
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        callback_manager=manager,
        #return_source_documents=True,

    )
    return qa
