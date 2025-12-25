
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


pdf_path = "/Users/surajkale/Downloads/fake-resumes/resume-001.pdf"  

loader = PyPDFLoader(pdf_path)
pages = loader.load()  


full_text = "\n".join([p.page_content for p in pages])
print(f"Total pages loaded: {len(pages)}")
print(f"Total characters in text: {len(full_text)}")



text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,       
    chunk_overlap=20,     
    separators=["\n\n", "\n", " "]
)

chunks = text_splitter.create_documents([full_text])

print(f"Total chunks created: {len(chunks)}\n")


for i, chunk in enumerate(chunks[:5]):  
    print(f"--- Chunk {i+1} ---")
    print(chunk.page_content)
    print()
