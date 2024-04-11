import shutil
import asyncio
import pyarrow as pa
from pathlib import Path
from typing import List

import lancedb
import chainlit as cl
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import LanceDB

from ploomber_cloud.functions import pdf_to_text, pdf_scanned_to_text, get_result

embeddings = OpenAIEmbeddings()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)


async def process_pdf(file, pdf_to_text_func):
    """Function for extracting text from PDF"""
    jobid = pdf_to_text_func(file.path, block=False)
    result = None
    while not isinstance(result, list):
        try:
            result = get_result(jobid)
        except Exception:
            await asyncio.sleep(1)
    result = [text.strip() for text in result if text.strip() != ""]
    return result


@cl.on_chat_start
async def on_chat_start():
    files = None

    # Wait for the user to upload a file
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload a PDF file to begin!\n"
            "The processing of the file may require a few moments or minutes to complete.",
            accept=["application/pdf"],
            max_size_mb=100,
            timeout=180,
        ).send()

    file = files[0]

    msg = cl.Message(content=f"Processing `{file.name}`...", disable_feedback=True)
    await msg.send()

    pdf_text = await process_pdf(file, pdf_to_text)

    if len(pdf_text) == 0:
        msg.content = (
            f"This looks like a scanned document. Reprocessing `{file.name}`..."
        )
        await msg.update()
        pdf_text = await process_pdf(file, pdf_scanned_to_text)

    # Convert each page into a Document object with metadata
    documents = [
        Document(page_content=text, metadata={"source": file.path, "page": ind})
        for ind, text in enumerate(pdf_text)
    ]

    # Split the text into chunks
    documents = text_splitter.split_documents(documents)

    if not documents:
        msg.content = (
            f"Couldn't find any text in `{file.name}`. "
            f"Click on `New Chat` for uploading another file."
        )
        await msg.update()

    else:
        directory_path = Path(file.path).parent
        path_to_vector_db = Path(directory_path, "vector-db")

        if path_to_vector_db.exists():
            shutil.rmtree(path_to_vector_db)

        db = lancedb.connect(path_to_vector_db)

        schema = pa.schema(
            [
                pa.field("vector", pa.list_(pa.float32(), list_size=1536)),
                pa.field("text", pa.string()),
                pa.field("id", pa.string()),
            ]
        )

        table = db.create_table("embeddings", schema=schema, mode="overwrite")

        docsearch = LanceDB.from_documents(documents, embeddings, connection=table)

        chain = RetrievalQA.from_chain_type(
            llm=OpenAI(),
            chain_type="stuff",
            retriever=docsearch.as_retriever(
                search_type="similarity", search_kwargs={"k": 2}
            ),
            return_source_documents=True,
            verbose=True,
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

    answer = res["result"]
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
