# =====================================================
# 1. IMPORTS
# =====================================================
import streamlit as st
import os
import tempfile
import re
import chromadb

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import init_embeddings

# =====================================================
# 2. STREAMLIT PAGE CONFIG
# =====================================================
st.set_page_config(page_title="AI Resume Shortlisting", layout="wide")
st.title("AI Enabled Resume Shortlisting System (Upload/Shortlist)")

# =====================================================
# 3. EMBEDDING MODEL
# =====================================================
embed_model = init_embeddings(
    model="text-embedding-nomic-embed-text-v1.5",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed",
    check_embedding_ctx_length=False
)

# =====================================================
# 4. TEXT SPLITTER
# =====================================================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
    separators=[" ", "\n", "\n\n"]
)

# =====================================================
# 5. CHROMA DB SETUP
# =====================================================
db = chromadb.PersistentClient(path="./knowledge_base")
collection = db.get_or_create_collection(name="resumes")

# =====================================================
# 6. PDF LOADER FUNCTION
# =====================================================
def load_pdf_resume(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    full_text = "\n".join([p.page_content for p in pages])
    return full_text, len(pages)

# =====================================================
# 7. STORE/UPDATE RESUME
# =====================================================
def store_or_update_resume(pdf_path, resume_id):
    # Delete existing chunks with same ID
    all_ids = collection.get()["ids"]
    delete_ids = [i for i in all_ids if i.startswith(resume_id)]
    if delete_ids:
        collection.delete(ids=delete_ids)

    # Load PDF text
    text, page_count = load_pdf_resume(pdf_path)
    file_name = os.path.basename(pdf_path)

    # Create chunks
    docs = text_splitter.create_documents(
        texts=[text],
        metadatas=[{"resume_id": resume_id, "file_name": file_name, "page_count": page_count}]
    )

    texts, metadatas, ids = [], [], []
    for i, doc in enumerate(docs):
        texts.append(doc.page_content)
        metadatas.append(doc.metadata)
        ids.append(f"{resume_id}_chunk_{i}")

    embeddings = embed_model.embed_documents(texts)
    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

# =====================================================
# 8. DELETE RESUME
# =====================================================
def delete_resume(resume_id):
    all_ids = collection.get()["ids"]
    delete_ids = [i for i in all_ids if i.startswith(resume_id)]
    if delete_ids:
        collection.delete(ids=delete_ids)

# =====================================================
# 9. LIST RESUMES
# =====================================================
def list_resumes():
    metadatas = collection.get()["metadatas"]
    if not metadatas:
        return {}
    unique = {}
    for meta in metadatas:
        rid = meta["resume_id"]
        if rid not in unique:
            unique[rid] = {"file_name": meta["file_name"], "page_count": meta["page_count"]}
    return unique

# =====================================================
# 10. SHORTLIST RESUMES
# =====================================================
def shortlist_resumes(job_desc, top_k):
    jd_embedding = embed_model.embed_documents([job_desc])[0]
    results = collection.query(query_embeddings=[jd_embedding], n_results=top_k)
    shortlisted = list({meta["resume_id"] for meta in results["metadatas"][0]})
    return shortlisted

# =====================================================
# 11. EXTRACT INFO FROM PDF TEXT
# =====================================================
def extract_candidate_info(pdf_text):
    # Name: assume first non-empty line
    lines = [l.strip() for l in pdf_text.split("\n") if l.strip()]
    name = lines[0] if lines else "N/A"

    # Contact: phone/email regex
    phone_match = re.search(r"\+?\d[\d\s\-]{7,}\d", pdf_text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", pdf_text)
    contact = ""
    if phone_match: contact += phone_match.group()
    if email_match: contact += f" | {email_match.group()}" if contact else email_match.group()
    if not contact: contact = "N/A"

    # Skills: simple heuristic (look for "Skills" section)
    skills = "N/A"
    skills_match = re.search(r"(Skills|Technical Skills|Expertise)[:\n](.*)", pdf_text, re.I)
    if skills_match:
        skills = skills_match.group(2).strip().split("\n")[0]

    # Experience: look for X years or experience keyword
    exp_match = re.search(r"(\d+\+?\s*(years|yrs))", pdf_text, re.I)
    experience = exp_match.group(1) if exp_match else "N/A"

    return name, contact, skills, experience

# =====================================================
# 12. STREAMLIT UI
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["Upload Resume", "List Resumes", "Delete Resume", "Shortlist"]
)

# Upload
with tab1:
    resume_id = st.text_input("Enter Resume ID (e.g., 001, JohnDoe)")
    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

    if uploaded_file and resume_id:
        if st.button("Upload Resume"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                pdf_path = tmp.name

            store_or_update_resume(pdf_path, resume_id)
            st.success(f"Resume uploaded successfully with ID = {resume_id}")

# List
with tab2:
    resumes = list_resumes()
    if resumes:
        st.subheader("Resumes in Database")
        for r_id, meta in resumes.items():
            st.write(f"{r_id} | {meta['file_name']} | Pages: {meta['page_count']}")
    else:
        st.info("No resumes found")

# Delete
with tab3:
    resumes = list_resumes()
    if resumes:
        selected = st.selectbox("Select resume to delete", list(resumes.keys()))
        if st.button("Delete Resume"):
            delete_resume(selected)
            st.success("Resume deleted successfully")
    else:
        st.info("No resumes available to delete")

# Shortlist
with tab4:
    job_desc = st.text_area("Enter Job Description")
    top_k = st.number_input("Number of resumes to shortlist", 1, 10, 3)

    if st.button("Shortlist Resumes"):
        shortlisted_ids = shortlist_resumes(job_desc, top_k)
        st.subheader("Shortlisted Resumes")

        if shortlisted_ids:
            for r_id in shortlisted_ids:
                # Get first chunk text
                doc_ids = [i for i in collection.get()["ids"] if i.startswith(r_id)]
                if doc_ids:
                    pdf_text = " ".join(collection.get(ids=[doc_ids[0]])["documents"])
                    name, contact, skills, experience = extract_candidate_info(pdf_text)
                    st.write(f"ID: {r_id}")
                    st.write(f"Name: {name}")
                    st.write(f"Contact: {contact}")
                    st.write(f"Experience: {experience}")
                    st.write("---")
        else:
            st.info("No resumes matched the job description")
