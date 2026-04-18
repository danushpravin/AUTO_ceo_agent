from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_knowledge_docs(knowledge_dir: str):
    docs=[]

    for file in Path(knowledge_dir).glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            docs.append(f.read())
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    chunks = []
    for doc in docs:
        chunks.extend(splitter.split_text(doc))

    return chunks