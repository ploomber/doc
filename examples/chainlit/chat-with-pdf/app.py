import PyPDF2
from pathlib import Path
from typing import List
import shutil

import lancedb

from openai import OpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import LanceDB
from langchain.chains import (
    ConversationalRetrievalChain,
)
from langchain.chat_models import ChatOpenAI

from langchain.docstore.document import Document
from langchain.memory import ChatMessageHistory, ConversationBufferMemory

import chainlit as cl

from ploomber_cloud import functions

client = OpenAI()
embeddings = OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


@cl.on_chat_start
async def on_chat_start():

    files = None

    # Wait for the user to upload a file
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload a PDF file to begin!",
            accept=["application/pdf"],
            max_size_mb=100,
            timeout=180,
        ).send()

    file = files[0]

    msg = cl.Message(content=f"Processing `{file.name}`...", disable_feedback=True)
    await msg.send()

    # result = None
    # jobid = functions.pdf_to_text(file.path, block=False)
    # while not isinstance(result, list):
    #     try:
    #         result = functions.get_result(jobid)
    #     except Exception:
    #         pass
    # print(result)
    # pdf_text = "".join(result)

    # Read the PDF file
    pdf = PyPDF2.PdfReader(file.path)
    pdf_text = ""
    for page in pdf.pages:
        pdf_text += page.extract_text()

    page_count = int(0.1 * len(pdf.pages))

    # Split the text into chunks
    texts = text_splitter.split_text(pdf_text)
    # Create a metadata for each chunk
    metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]

    directory_path = Path(file.path).parent
    path_to_vector_db = Path(directory_path, "vector-db")

    if path_to_vector_db.exists():
        shutil.rmtree(path_to_vector_db)

    db = lancedb.connect(path_to_vector_db)
    table = db.create_table(
        "pdf",
        data=[
            {"vector": embeddings.embed_query(texts[0]), "text": texts[0], "id": "1"}
        ],
        mode="overwrite",
    )

    docsearch = LanceDB.from_texts(
        texts[1:], embeddings, metadatas=metadatas, connection=table
    )

    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, streaming=True),
        chain_type="stuff",
        retriever=docsearch.as_retriever(search_kwargs={"k": min(page_count, 5)}),
        memory=memory,
        return_source_documents=True,
    )

    # Let the user know that the system is ready
    msg.content = f"Processing `{file.name}` done. You can now ask questions!"
    await msg.update()

    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler()

    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["answer"]
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source {source_idx+1}"
            # Create the text element referenced in the message
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    await cl.Message(content=answer, elements=text_elements).send()