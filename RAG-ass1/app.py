# =====================================================
# 1. IMPORTS
# =====================================================
import os
import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =====================================================
# 2. LOAD .env
# =====================================================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found. Please add it to .env file.")
    st.stop()

# =====================================================
# 3. STREAMLIT CONFIG
# =====================================================
st.set_page_config(page_title="PDF Chunking App", layout="wide")
st.title("📄 PDF Chunking Example (Using .env)")

# =====================================================
# 4. FILE UPLOAD
# =====================================================
uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_pdf:
    st.success("PDF uploaded successfully!")

    # =================================================
    # 5. LOAD PDF
    # =================================================
    loader = PyPDFLoader(uploaded_pdf)
    pages = loader.load()

    full_text = "\n".join([page.page_content for page in pages])

    st.write(f"📄 Total Pages: {len(pages)}")
    st.write(f"🧾 Total Characters: {len(full_text)}")

    # =================================================
    # 6. CHUNKING
    # =================================================
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
        separators=["\n\n", "\n", " "]
    )

    chunks = text_splitter.create_documents([full_text])

    st.success(f"✅ Total Chunks Created: {len(chunks)}")

    # =================================================
    # 7. DISPLAY CHUNKS
    # =================================================
    st.subheader("🔍 Sample Chunks")

    for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
        st.markdown(f"### Chunk {i+1}")
        st.text(chunk.page_content)
        st.divider()
