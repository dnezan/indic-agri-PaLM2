import streamlit as st
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import config
from config import call_open_api_key
import PyPDF2
from docx import Document
 
def extract_text_from_pdf(file):

    pdf_reader = PyPDF2.PdfReader(file)

    text = ""

    for page in pdf_reader.pages:

        text += page.extract_text()

    return text

 

def extract_text_from_docx(file):

    doc = Document(file)

    text = ""

    for paragraph in doc.paragraphs:

        text += paragraph.text + "\n"

    return text

 

def generate_response(uploaded_files, openai_api_key, query_text):

    # Load documents if files are uploaded

    if uploaded_files is not None:

        documents = []

        for file in uploaded_files:

            file_type = file.type.split('/')[1]

            if file_type == 'pdf':

                # Handle PDF files

                text = extract_text_from_pdf(file)

                documents.append(text)

            elif file_type == 'txt':

                # Handle text files

                documents.append(file.read().decode())

            elif file_type in ['doc', 'docx']:

                # Handle document files (e.g., .doc, .docx)

                text = extract_text_from_docx(file)

                documents.append(text)

 

        # Split documents into chunks

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

        texts = text_splitter.create_documents(documents)

        # Select embeddings

        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

        # Create a vectorstore from documents

        db = Chroma.from_documents(texts, embeddings)

        # Create retriever interface

        retriever = db.as_retriever()

        # Create QA chain

        qa = RetrievalQA.from_chain_type(llm=OpenAI(openai_api_key=openai_api_key), chain_type='stuff', retriever=retriever)

        response = qa.run(query_text)

        # Save response as PDF file

        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(PyPDF2.PageObject.create_text_page(response))
        pdf_filename = "response.pdf"

        with open(pdf_filename, "wb") as pdf_file:
            pdf_writer.write(pdf_file)

        return response, pdf_filename

 

# Page title

st.set_page_config(page_title='🦜🔗 Ask me anything from the Doc App')

st.title('🦜🔗 Ask me anything from the Doc App')

 

# File upload

uploaded_files = st.file_uploader('Upload articles', type=['pdf', 'txt', 'doc', 'docx'], accept_multiple_files=True)

# Query text

query_text = st.text_input('Enter your question:', placeholder='Please provide a short summary.', disabled=not uploaded_files)

 

# Form input and query

result = []

openai_api_key = call_open_api_key()
if openai_api_key.startswith('sk-'):
    if query_text:
        with st.spinner('Generating...'):
            response, pdf_filename = generate_response(uploaded_files, openai_api_key, query_text)
            result.append(response)
            st.write(response)
            st.download_button("Download Response as PDF", pdf_filename)
