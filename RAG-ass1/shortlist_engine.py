# shortlist_engine.py
import re
from groq import Groq

class ShortlistEngine:
    def __init__(self, db, embedder, groq_api_key):
        self.db = db
        self.embedder = embedder
        self.client = Groq(api_key=groq_api_key)

    def shortlist(self, job_desc, top_k):
        jd_embedding = self.embedder.embed([job_desc])[0]
        results = self.db.collection.query(
            query_embeddings=[jd_embedding],
            n_results=top_k
        )
        return list({m["resume_id"] for m in results["metadatas"][0]})

    def extract_info(self, text):
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        name = lines[0] if lines else "N/A"

        phone = re.search(r"\+?\d[\d\s\-]{7,}\d", text)
        email = re.search(r"[\w\.-]+@[\w\.-]+", text)

        contact = " | ".join(filter(None, [
            phone.group() if phone else "",
            email.group() if email else ""
        ])) or "N/A"

        exp = re.search(r"(\d+\+?\s*(years|yrs))", text, re.I)
        experience = exp.group(1) if exp else "N/A"

        return name, contact, experience

    def explain_selection_ai(self, job_desc, resume_text):
        prompt = f"""
You are an expert HR recruiter.

Explain clearly and professionally why this candidate was shortlisted.

Job Description:
{job_desc}

Candidate Resume:
{resume_text}

Use bullet points focusing on:
• Skill match
• Experience relevance
• Role suitability
"""

        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300
        )

        return response.choices[0].message.content
