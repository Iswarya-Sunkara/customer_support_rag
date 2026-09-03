import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from src.dynamic_rag import DynamicRAGEngine

def test_bustlespot_pdf_qa():
    print("Testing Question-Aware Answer Extraction for BustleSpot PDF...", flush=True)

    pdf_text_sample = (
        "--- Page 1 ---\n"
        "BustleSpot\n"
        "Organization\n"
        "Date\n"
        "User\n"
        "Total Hours\n"
        "Total Idle Hours\n"
        "Total Working Hours\n"
        "Total Activity\n"
        "Projects\n"
        "Days Worked\n"
        ": SoftSuave - Bangalore\n"
        ": 2026-08-31 to 2026-08-31\n"
        ": Sunkara Iswarya\n"
        ": 09 : 19 hrs\n"
        ": 01 : 16 hrs\n"
        ": 08 : 03 hrs\n"
        ": 46%\n"
        ": 1\n"
        ": 1\n"
        "31/08\n"
        "Mon\n"
        "Total Hours 09 : 19 hrs\n"
        "Working Hours 08 : 03 hrs\n"
        "Idle Hours 01 : 16 hrs\n"
        "Activity % 46%\n"
        "No of projects 1\n"
    )

    engine = DynamicRAGEngine()
    engine.add_document("Bustlespot(2026-08-31 to 2026-08-31).pdf", pdf_text_sample.encode("utf-8"))

    questions = [
        "what the file giving info",
        "what is the activity percentage",
        "what is the Total Activity in that pdf",
        "what is the project name",
        "who is the user",
        "what is total working hours"
    ]

    for q in questions:
        print("\n" + "="*60, flush=True)
        print(f"QUESTION: {q}", flush=True)
        print("="*60, flush=True)
        res = engine.query(q)
        print(f"ANSWER:\n{res['answer']}\n", flush=True)

if __name__ == "__main__":
    test_bustlespot_pdf_qa()
