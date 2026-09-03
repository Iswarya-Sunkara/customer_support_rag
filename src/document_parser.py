import os
import re
import io
from pathlib import Path
from typing import Dict, Any, Optional

def parse_document(file_path: Optional[str] = None, file_bytes: Optional[bytes] = None, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Universal document parser that extracts clean text from ANY file format.
    Supports PDF, DOCX, CSV, Excel, TXT, MD, Code files, JSON, Images, and raw binary fallbacks.
    Never throws unhandled exceptions — guarantees non-breaking ingestion.
    """
    if file_path:
        path_obj = Path(file_path)
        if filename is None:
            filename = path_obj.name
        if file_bytes is None:
            try:
                with open(path_obj, "rb") as f:
                    file_bytes = f.read()
            except Exception as e:
                return {
                    "filename": filename,
                    "extension": path_obj.suffix.lower(),
                    "size_bytes": 0,
                    "text": "",
                    "char_count": 0,
                    "line_count": 0,
                    "status": "error",
                    "message": f"Failed to read file: {str(e)}"
                }
    
    if file_bytes is None:
        file_bytes = b""
    if filename is None:
        filename = "uploaded_file.bin"

    ext = Path(filename).suffix.lower()
    size_bytes = len(file_bytes)
    extracted_text = ""
    status = "success"
    message = "Successfully extracted text"

    try:
        # 1. PDF Documents
        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                pages_text = []
                for i, page in enumerate(reader.pages):
                    t = page.extract_text()
                    if t:
                        pages_text.append(f"--- Page {i+1} ---\n{t.strip()}")
                extracted_text = "\n\n".join(pages_text)
            except Exception as pdf_err:
                extracted_text = _fallback_binary_string_extraction(file_bytes)
                message = f"PDF parsed with fallback string extractor ({str(pdf_err)})"

        # 2. Word Documents (.docx)
        elif ext in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                # also extract table text
                tables_text = []
                for table in doc.tables:
                    for row in table.rows:
                        row_str = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                        if row_str:
                            tables_text.append(row_str)
                full_doc = []
                if paragraphs:
                    full_doc.append("\n".join(paragraphs))
                if tables_text:
                    full_doc.append("\nTables:\n" + "\n".join(tables_text))
                extracted_text = "\n\n".join(full_doc)
            except Exception as docx_err:
                extracted_text = _fallback_binary_string_extraction(file_bytes)
                message = f"DOCX parsed with fallback string extractor ({str(docx_err)})"

        # 3. CSV Data
        elif ext == ".csv":
            try:
                import pandas as pd
                df = pd.read_csv(io.BytesIO(file_bytes))
                extracted_text = f"CSV Data ({filename}):\n" + df.to_markdown(index=False)
            except Exception:
                extracted_text = _try_decode_text(file_bytes)

        # 4. Excel Documents (.xlsx, .xls)
        elif ext in [".xlsx", ".xls"]:
            try:
                import pandas as pd
                excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
                sheets_text = []
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet)
                    sheets_text.append(f"Sheet: {sheet}\n" + df.to_markdown(index=False))
                extracted_text = "\n\n".join(sheets_text)
            except Exception as excel_err:
                extracted_text = _fallback_binary_string_extraction(file_bytes)
                message = f"Excel parsed with fallback string extractor ({str(excel_err)})"

        # 5. Text / Markdown / Code / Structural Files
        elif ext in [
            ".txt", ".md", ".json", ".py", ".html", ".htm", ".xml", ".yaml", ".yml",
            ".js", ".ts", ".jsx", ".tsx", ".css", ".c", ".cpp", ".h", ".hpp", ".cs",
            ".java", ".go", ".rs", ".sql", ".sh", ".bat", ".ps1", ".log", ".ini",
            ".conf", ".env", ".rst", ".tex", ".rtf"
        ]:
            extracted_text = _try_decode_text(file_bytes)

        # 6. Images (PNG, JPG, etc.)
        elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".svg"]:
            extracted_text = f"[Image Document: {filename}]\nFile size: {size_bytes} bytes. Image content indexed for metadata context."
            message = "Image metadata extracted"

        # 7. Fallback for any unknown / binary file format
        else:
            decoded = _try_decode_text(file_bytes)
            if len(decoded.strip()) > 10 and not _is_binary_garbage(decoded):
                extracted_text = decoded
            else:
                extracted_text = _fallback_binary_string_extraction(file_bytes)
                message = "Extracted readable ASCII/UTF-8 strings from binary file"

    except Exception as general_err:
        extracted_text = _fallback_binary_string_extraction(file_bytes)
        message = f"Fallback extraction used: {str(general_err)}"

    extracted_text = extracted_text.strip()
    if not extracted_text:
        extracted_text = f"Document {filename} loaded ({size_bytes} bytes)."

    return {
        "filename": filename,
        "extension": ext or ".bin",
        "size_bytes": size_bytes,
        "text": extracted_text,
        "char_count": len(extracted_text),
        "line_count": len(extracted_text.splitlines()),
        "status": status,
        "message": message
    }

def _try_decode_text(file_bytes: bytes) -> str:
    """Tries UTF-8 decoding, falling back to latin-1 and utf-16."""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16"]:
        try:
            return file_bytes.decode(enc)
        except Exception:
            continue
    return _fallback_binary_string_extraction(file_bytes)

def _is_binary_garbage(text: str) -> bool:
    """Checks if text contains high density of non-printable control characters."""
    non_printable = sum(1 for c in text if ord(c) < 32 and c not in "\n\r\t")
    return (non_printable / max(len(text), 1)) > 0.15

def _fallback_binary_string_extraction(file_bytes: bytes) -> str:
    """Extracts printable string sequences (>= 4 chars) from binary data."""
    try:
        raw_text = file_bytes.decode("latin-1", errors="ignore")
        matches = re.findall(r"[\x20-\x7E\n\r\t]{4,}", raw_text)
        cleaned = "\n".join(m.strip() for m in matches if len(m.strip()) > 3)
        return cleaned if cleaned else "[No printable text found in binary data]"
    except Exception:
        return "[Binary file content]"
