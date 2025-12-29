# pdf_utils.py
from langchain_community.document_loaders import PyPDFLoader

class PDFLoaderUtil:
    @staticmethod
    def load_pdf(path):
        loader = PyPDFLoader(path)
        pages = loader.load()
        text = "\n".join(p.page_content for p in pages)
        return text, len(pages)
