# database.py
import chromadb

class ResumeDatabase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./knowledge_base")
        self.collection = self.client.get_or_create_collection("resumes")

    def delete_by_resume_id(self, resume_id):
        ids = self.collection.get()["ids"]
        delete_ids = [i for i in ids if i.startswith(resume_id)]
        if delete_ids:
            self.collection.delete(ids=delete_ids)

    def list_resumes(self):
        metas = self.collection.get()["metadatas"]
        resumes = {}
        if metas:
            for m in metas:
                rid = m["resume_id"]
                resumes.setdefault(rid, m)
        return resumes
