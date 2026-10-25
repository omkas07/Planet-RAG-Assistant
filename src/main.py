from ingest import Ingest

ingest = Ingest()

results = ingest.rrf("Why does Mars look red?")
for doc in results:
    print(doc.page_content, "\n\n")