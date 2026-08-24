from pathlib import Path
from prepare_documents import load_documents
from langchain_text_splitters import RecursiveCharacterTextSplitter

documents = load_documents()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

chunks = splitter.split_documents(documents)

for i, chunk in enumerate(chunks):
    chunk.metadata["chunk_id"] = f"strategy_a_{i}"

if __name__ == "__main__":
    print(f"Loaded documents: {len(documents)}")
    print(f"Total Strategy A chunks: {len(chunks)}")
    print()

    for i, chunk in enumerate(chunks[:5]):
        print("=" * 60)
        print(f"Chunk ID: {chunk.metadata['chunk_id']}")
        print(f"Article ID: {chunk.metadata['article_id']}")
        print(f"Source File: {chunk.metadata['source_file']}")
        print(f"Product Area: {chunk.metadata['product_area']}")
        print(f"Last Updated: {chunk.metadata['last_updated']}")
        print(f"Characters: {len(chunk.page_content)}")
        print()
        print(chunk.page_content[:300])