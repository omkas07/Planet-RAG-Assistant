import pymupdf
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os

# DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
# FILES = ["mars.pdf", "jupiter.pdf", "saturn.pdf", "venus.pdf"]

class Retrieval:

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap = 80
        )
        self.DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.FILES = ["mars.pdf", "jupiter.pdf", "saturn.pdf", "venus.pdf"]

    @staticmethod
    def extract(path: str):
        paragraphs = []
        with pymupdf.open(path) as pdf:
            for page in pdf:
                for block in page.get_text("blocks"):
                    if block[6] == 0:                                   # 0 = текстовый блок
                        paragraphs.append(" ".join(block[4].split()))   # убрать переносы внутри абзаца

        text = "\n\n".join(paragraphs)
        return Document(page_content=text, metadata={"source": os.path.basename(path)})

    def chunking(self):
        chunks = []
        for name in self.FILES:
            converted = self.extract(os.path.join(self.DATA_DIR, name))
            chunks.extend(self.splitter.split_documents([converted]))

        return chunks