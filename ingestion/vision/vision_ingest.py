import os
import fitz
import tempfile
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ingestion.vision.vision_extractor import extract_page
from ingestion.vision.pseudo_mapper import generate_synthetic_layout
from ingestion.vision.knowledge_normalizer import normalize_page
from ingestion.text.hierarchy.hierarchy_builder import build_hierarchy
from ingestion.shared.rule_chunker import create_chunks
from ingestion.shared.metadata_builder import build_metadata
from ingestion.shared.store import save_chunk
from ingestion.shared.document_store import (
    create_document,
    update_document_status
)

logger = logging.getLogger(__name__)

# ==============================================================================
# DEBUG MODE: Add specific page numbers here to only process those pages.
# To process the entire PDF, leave it empty: DEBUG_PAGES = set()
# ==============================================================================
DEBUG_PAGES = {11, 12} 
# ==============================================================================

def process_page_safe(pdf_path: str, page_num: int):
    """Renders a single page, crops it, calls the VLM, and immediately deletes the image."""
    temp_img_path = None
    try:
        print(f"\n[PAGE {page_num}] ⚙️ Starting render and crop...")
        logger.debug(f"Rendering and cropping page {page_num}...")
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        
        rect = page.rect
        crop_box = fitz.Rect(rect.x0, rect.y0 + (rect.height * 0.08), rect.x1, rect.y1 - (rect.height * 0.08))
        pix = page.get_pixmap(clip=crop_box, matrix=fitz.Matrix(2, 2))
        
        fd, temp_img_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        pix.save(temp_img_path)
        
        print(f"[PAGE {page_num}] 🖼️ Image saved to {temp_img_path}. Sending to VLM...")
        logger.debug(f"Saved cropped page {page_num} to {temp_img_path}. Extracting semantic layout...")
        response_json = extract_page(temp_img_path) 
        
        print(f"[PAGE {page_num}] ✅ VLM Extraction complete!")
        return {"page": page_num, "data": response_json}
        
    except Exception as e:
        print(f"\n[PAGE {page_num}] ❌ ERROR during processing: {e}")
        logger.error(f"Failed processing page {page_num}: {e}", exc_info=True)
        return {"page": page_num, "data": {"paragraphs": []}}
        
    finally:
        if temp_img_path and os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
                print(f"[PAGE {page_num}] 🧹 Cleaned up temp image.")
                logger.debug(f"Cleaned up temp image: {temp_img_path}")
            except OSError as cleanup_err:
                print(f"[PAGE {page_num}] ⚠️ Warning: Failed to delete temp file: {cleanup_err}")
                logger.warning(f"Failed to delete temp file {temp_img_path}: {cleanup_err}")

def ingest_pdf_vision(pdf_path, filename, user_id=None):
    print("\n" + "=" * 80)
    print(f"🚀 STARTING PRODUCTION VISION PIPELINE: {filename}")
    print("=" * 80)
    
    logger.info("=" * 80)
    logger.info(f"STARTING PRODUCTION VISION PIPELINE: {filename}")
    logger.info("=" * 80)
    
    print(f"📁 Creating document record for {filename}...")
    document_id = create_document(filename=filename, pdf_path=pdf_path, document_type="VISION", user_id=user_id)
    print(f"✅ Document ID created: {document_id}")
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    print(f"📄 Total pages in PDF: {total_pages}")

    # Apply Debug Filter
    if DEBUG_PAGES:
        pages_to_process = [p for p in range(1, total_pages + 1) if p in DEBUG_PAGES]
        print(f"🐛 DEBUG MODE ACTIVE: Only processing {len(pages_to_process)} pages -> {pages_to_process}")
        logger.info(f"DEBUG MODE ACTIVE: Only processing {len(pages_to_process)} pages -> {pages_to_process}")
    else:
        pages_to_process = range(1, total_pages + 1)

    vision_responses = []
    print(f"\n🔥 Dispatching {len(pages_to_process)} pages to ThreadPoolExecutor (max_workers=5)...")
    logger.info(f"Dispatching {len(pages_to_process)} pages to VLM ThreadPoolExecutor...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Only submit the pages defined in our pages_to_process list
        futures = {executor.submit(process_page_safe, pdf_path, p): p for p in pages_to_process}
        for future in as_completed(futures):
            vision_responses.append(future.result())
            
    vision_responses = sorted(vision_responses, key=lambda x: x["page"])
    print(f"✅ All {len(vision_responses)} pages processed and sorted.")

    print("\n🏗️ Generating synthetic spatial layouts...")
    synthetic_layout = generate_synthetic_layout(vision_responses)
    print(f"✅ Synthetic layout generated for {len(synthetic_layout)} pages.")

    print("\n🧠 Routing generated pseudo-layout through Shared Text Hierarchy Engine...")
    logger.info("Routing generated pseudo-layout through Shared Text Hierarchy Engine...")
    structured_pages = build_hierarchy(synthetic_layout)
    print("✅ Hierarchy building complete.")

    total_chunks = 0
    print("\n🔪 Normalizing and chunking verified page hierarchies...")
    logger.info("Normalizing and chunking verified page hierarchies...")
    
    for page in structured_pages:
        page_number = page["page"]
        elements = page.get("elements", [])
        
        if not elements: 
            print(f"⏭️  [PAGE {page_number}] Skipped: No valid elements generated.")
            logger.debug(f"Skipping page {page_number}: No valid elements generated.")
            continue
            
        print(f"\n[PAGE {page_number}] 📦 Formatting data for chunking... Elements found: {len(elements)}")
        sample = elements[0]
        original_data = next((resp["data"] for resp in vision_responses if resp["page"] == page_number), {})
        
        page_json = {
            **original_data,
            "chapter": sample.get("chapter", ""),
            "section": sample.get("section", ""),
            "subsection": sample.get("subsection", ""),
            "subsubsection": sample.get("subsubsection", ""),
            "paragraphs": [e["text"] for e in elements if e.get("font_size") == 11.0]
        }

        units = normalize_page(page_json, page_number)
        chunks = create_chunks(units)

        print(f"[PAGE {page_number}] 🧩 Yielded {len(chunks)} chunks. Saving to database...")
        logger.debug(f"Page {page_number} chunked successfully. Yielded {len(chunks)} chunks.")

        for chunk in chunks:
            metadata = build_metadata(chunk, document_id)
            save_chunk(chunk, filename, metadata)
            total_chunks += 1

    print("\n" + "=" * 80)
    print(f"🎉 VISION PIPELINE COMPLETE! Total chunks saved: {total_chunks}")
    print("=" * 80)
    
    logger.info(f"VISION PIPELINE COMPLETE. Total chunks saved: {total_chunks}")

    # ---------------------------------------------------------
    # MARK AS READY ONCE ALL CHUNKS ARE SUCCESSFULLY SAVED
    # ---------------------------------------------------------
    update_document_status(document_id, "READY")
    print(f"✅ Document {document_id} marked as READY.")

    return total_chunks