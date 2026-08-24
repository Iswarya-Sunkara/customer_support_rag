from pathlib import Path
from langchain_core.documents import Document

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Predefined dates for last_updated metadata per article drop
LAST_UPDATED_MAP = {
    "article_01": "2026-08-15",
    "article_02": "2026-08-18",
    "article_03": "2026-08-20",
    "article_04": "2026-08-10",
    "article_05": "2026-08-12",
    "article_06": "2026-08-22",
}

def load_documents():
    documents = []

    for file in sorted(DATA_DIR.glob("*.md")):
        content = file.read_text(encoding="utf-8")
        lines = content.splitlines()

        title = lines[0].replace("# ", "").strip()
        
        # Extract article_id from filename e.g. article_01
        parts = file.stem.split("_")
        article_id = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else file.stem

        metadata = {
            "source_file": file.name,
            "article_id": article_id,
            "title": title,
            "last_updated": LAST_UPDATED_MAP.get(article_id, "2026-08-01"),
        }

        for line in lines:
            if line.startswith("Source:"):
                metadata["source"] = line.replace("Source:", "").strip()
            elif line.startswith("URL:"):
                metadata["url"] = line.replace("URL:", "").strip()
            elif line.startswith("Category:"):
                cat = line.replace("Category:", "").strip()
                metadata["category"] = cat
                metadata["product_area"] = cat

        documents.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    return documents

if __name__ == "__main__":
    documents = load_documents()
    print(f"Loaded {len(documents)} documents.\n")

    for document in documents:
        print("=" * 60)
        print(f"Article ID:   {document.metadata.get('article_id')}")
        print(f"Source File:  {document.metadata.get('source_file')}")
        print(f"Product Area: {document.metadata.get('product_area')}")
        print(f"Last Updated: {document.metadata.get('last_updated')}")
        print(f"Title:        {document.metadata.get('title')}")