# test_rag.py  — run with: python test_rag.py
from rag.retriever import KnowledgeRetriever

retriever = KnowledgeRetriever()

queries = [
    "ROAS threshold marketing efficiency",
    "stockout days inventory risk",
    "fake growth loss making products",
    "channel revenue concentration risk",
    "product portfolio classification star cash cow",
]

for q in queries:
    print(f"\n{'='*60}")
    print(f"QUERY: {q}")
    print(f"{'='*60}")
    result = retriever.retrieve(q, k=2)
    print(result)