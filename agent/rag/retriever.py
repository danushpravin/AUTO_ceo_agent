from .loader import load_knowledge_docs
from .embedder import build_vector_store

class KnowledgeRetriever:

    def __init__(self, knowledge_path="agent/rag/knowledge"):
        chunks = load_knowledge_docs(knowledge_path)
        self.vector_store = build_vector_store(chunks)
        
    def retrieve(self, query: str, k: int=3):
        docs = self.vector_store.similarity_search(query, k=k)
        return "\n\n".join([d.page_content for d in docs])