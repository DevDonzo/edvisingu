import chromadb

client = chromadb.PersistentClient(path="./chroma-data")
col = client.get_or_create_collection("test")
col.add(
    documents=[
        "EdVisingU teaches students to earn while learning",
        "HireEd Nexus Labs connects students to real projects",
        "CrediVersity offers AI micro-credentials",
    ],
    ids=["1", "2", "3"],
)
result = col.query(query_texts=["student income opportunities"], n_results=2)
print("ChromaDB working! Top results:", result["documents"])
