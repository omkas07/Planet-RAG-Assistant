from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from dotenv import load_dotenv
from collections import defaultdict
import os
import re

from retrieval import Retrieval

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Ingest:

    def __init__(self):

        self.retrieval = Retrieval()
        self.embeddings = OpenAIEmbeddings(
            model="openai/text-embedding-3-small",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            check_embedding_ctx_length=False
            )

        self.vectorstore = Chroma(
            collection_name="planets",
            embedding_function=self.embeddings,
            persist_directory=os.path.join(BASE_DIR, "chroma_db"),
            collection_metadata={"hnsw:space" : "cosine"}
        )

        self.bm25 = None

    @staticmethod
    def preprocess(text: str):
        return re.findall(r"\w+", text.lower())

    def bm25_build(self, k: int = 10):
        data = self.vectorstore.get()

        chunks = [
            Document(id=doc_id, page_content=text, metadata=meta) for doc_id, text, meta in zip(data["ids"], data["documents"], data["metadatas"])
        ]

        self.bm25 = BM25Retriever.from_documents(chunks, k=k, preprocess_func=self.preprocess)

    def keyword_search(self, query: str, k: int = 10):
        if self.bm25 is None:
            self.bm25_build()
        self.bm25.k = k
        return self.bm25.invoke(query)

    def indexing(self):
        if self.vectorstore._collection.count() > 0:
            print("DB is already full")
            return
        
        chunks = self.retrieval.chunking()
        counter = defaultdict(int)
        ids = []
        for c in chunks:
            src = c.metadata["source"]
            ids.append(f"{src}_{counter[src]}")
            counter[src] +=1

        self.vectorstore.add_documents(chunks, ids=ids)

    def semantic_search(self, query: str, k: int = 10):
        return self.vectorstore.similarity_search(query, k=k)

    def rrf(self, query: str, k: int = 5):
        semantic = self.semantic_search(query, 15)
        keyword = self.keyword_search(query, 15)

        scores = {}
        docs = {}

        for results in (semantic, keyword):
            for rank, doc in enumerate(results, start = 1):
                scores[doc.id] = scores.get(doc.id, 0) + (1/(60+rank))
                docs[doc.id] = doc

        best_ids = sorted(scores, key=scores.get, reverse = True)[:k]
        return [docs[doc_id] for doc_id in best_ids]
