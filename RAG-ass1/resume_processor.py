# resume_processor.py
import os
from pdf_utils import PDFLoaderUtil

class ResumeProcessor:
    def __init__(self, db, embedder):
        self.db = db
        self.embedder = embedder

    def store_or_update(self, pdf_path, resume_id):
        self.db.delete_by_resume_id(resume_id)

        text, pages = PDFLoaderUtil.load_pdf(pdf_path)
        embedding = self.embedder.embed([text])[0]

        self.db.collection.add(
            ids=[f"{resume_id}_full"],
            documents=[text],
            metadatas=[{
                "resume_id": resume_id,
                "file_name": os.path.basename(pdf_path),
                "page_count": pages
            }],
            embeddings=[embedding]
        )
