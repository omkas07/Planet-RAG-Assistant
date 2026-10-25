from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from label import test_dataset
from ingest import Ingest
import os

load_dotenv()

class Judge(BaseModel):
    score: float = Field("...")

judge_llm = ChatOpenAI(
    model = "openai/gpt-4o-mini",
    base_url = "https://openrouter.ai/api/v1",
    api_key = os.getenv("OPENROUTER_API_KEY")
).with_structured_output(Judge)


def precision_recall(results, expected_ids, k):
    top = results[:k]
    hits = sum(1 for doc in top if doc.id in expected_ids)
    precision = hits/k
    recall = hits/len(expected_ids)
    return precision, recall

def test(search_method: str, k: int = 3):
    ingest = Ingest()
    ingest.indexing()
    precisions = 0
    recalls = 0
    count = 0

    for item in test_dataset:
        q = item["question"]
        exp_ans = item["answer"]
        ids = set(item["relevant_ids"])

        if search_method == 's': results = ingest.semantic_search(q)
        elif search_method == 'k': results = ingest.keyword_search(q)
        else: results = ingest.rrf(q)

        p, r= precision_recall(results, ids, k)
        precisions+=p
        recalls+=r
        count+=1

        print("Question:", q)
        print("Expected Answer:", exp_ans)
        print("Chunk ids: ", [doc.id for doc in results][:k])
        print(f"Precision: {p:.2f}, Recall: {r:.2f}")
        print("="*139)

    print("Search Method:", search_method)
    print(f"Average Precision: {(precisions/count):.2f}")
    print(f"Average Recall: {(recalls/count):.2f}")

if __name__ == "__main__":
    test('s', 5)