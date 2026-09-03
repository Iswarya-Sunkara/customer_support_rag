from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent))
from prepare_documents import load_documents
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

documents = load_documents()

def build_structure_aware_chunks(documents):
    final_chunks = []

    for doc in documents:
        lines = doc.page_content.splitlines()
        current_header = doc.metadata.get("title", "")
        prose_lines = []

        def flush_prose(lines_to_flush, section_title):
            if not lines_to_flush:
                return
            text = "\n".join(lines_to_flush).strip()
            if not text:
                return
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
            )
            sub_chunks = splitter.split_text(text)
            for sc in sub_chunks:
                meta = doc.metadata.copy()
                meta["section_header"] = section_title
                final_chunks.append(Document(page_content=sc, metadata=meta))

        i = 0
        while i < len(lines):
            line = lines[i]

            # Track section headers
            if line.startswith("#"):
                flush_prose(prose_lines, current_header)
                prose_lines = [line]
                current_header = line.lstrip("#").strip()
                i += 1
                continue

            # Detect markdown table: header row + divider row starting with '|'
            if (
                line.strip().startswith("|")
                and (i + 1 < len(lines))
                and lines[i + 1].strip().startswith("|")
                and "---" in lines[i + 1]
            ):
                # Flush prior prose
                flush_prose(prose_lines, current_header)
                prose_lines = []

                header_row = lines[i].strip()
                divider_row = lines[i + 1].strip()
                i += 2

                # Process table data rows
                table_rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_rows.append(lines[i].strip())
                    i += 1

                # Group rows (1-3 rows per chunk) ensuring table headers are NEVER separated
                row_group_size = 2
                for r_idx in range(0, len(table_rows), row_group_size):
                    group = table_rows[r_idx : r_idx + row_group_size]
                    table_chunk_content = (
                        f"Section: {current_header}\n"
                        f"{header_row}\n"
                        f"{divider_row}\n" + "\n".join(group)
                    )
                    meta = doc.metadata.copy()
                    meta["section_header"] = current_header
                    meta["is_table_chunk"] = "true"
                    final_chunks.append(
                        Document(page_content=table_chunk_content, metadata=meta)
                    )
                continue

            prose_lines.append(line)
            i += 1

        flush_prose(prose_lines, current_header)

    # Assign unique chunk_ids
    for idx, chunk in enumerate(final_chunks):
        chunk.metadata["chunk_id"] = f"strategy_b_{idx}"

    return final_chunks

chunks = build_structure_aware_chunks(documents)

if __name__ == "__main__":
    print(f"Loaded documents: {len(documents)}")
    print(f"Final Strategy B structure-aware chunks: {len(chunks)}")
    print()

    for i, chunk in enumerate(chunks[:5]):
        print("=" * 70)
        print(f"Chunk ID:     {chunk.metadata['chunk_id']}")
        print(f"Article ID:   {chunk.metadata['article_id']}")
        print(f"Source File:  {chunk.metadata['source_file']}")
        print(f"Product Area: {chunk.metadata['product_area']}")
        print(f"Header:       {chunk.metadata.get('section_header', '')}")
        print(f"Characters:   {len(chunk.page_content)}")
        print()
        print(chunk.page_content)