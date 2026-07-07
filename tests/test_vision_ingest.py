from pathlib import Path
from ingestion.vision.vision_ingest import ingest_pdf_vision

pdf_path = "BBAB_BAN_501__resource__Digital_Study_Guide__merged_webp.pdf"

ingest_pdf_vision(
    pdf_path,
    Path(pdf_path).name,
)