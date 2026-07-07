import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

ADAPTIVE_THRESHOLDS = {
    "chapter": 0.85,
    "section": 0.75,
    "subsection": 0.65,
    "subsubsection": 0.60
}

def is_valid_heading(text: str) -> bool:
    t = text.strip()
    if not t or len(t) > 130: return False
    if re.match(r"^(Figure|Fig\.|Table|Chart|Graph|Equation|Eq\.)\s*\d+", t, re.I): return False
    if re.match(r"^([•\-\*o]|\d+[\.\)]\s*$)", t): return False
    if re.search(r"https?://|www\.|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", t, re.I): return False
    if re.search(r"^\+?\d{10,14}$", t): return False
    if t.endswith(".") and len(t.split()) > 4 and not re.search(r"\b([A-Z]\.){2,}$", t): return False
    return True

def build_global_noise_map(vision_responses: list) -> set:
    frequency_map = Counter()
    total_pages = len(vision_responses)
    
    logger.debug(f"Building global noise map across {total_pages} pages...")
    
    for page in vision_responses:
        data = page.get("data", {})
        candidates = []
        for key in ["chapter", "section", "subsection", "subsubsection"]:
            if data.get(key): candidates.append(data[key].strip().lower())
        for para in data.get("paragraphs", []):
            if len(para.split()) < 15: candidates.append(para.strip().lower())
        for c in set(candidates):
            frequency_map[c] += 1
            
    noise_threshold = max(3, int(total_pages * 0.10))
    noise_set = {text for text, count in frequency_map.items() if count >= noise_threshold}
    
    logger.info(f"Identified {len(noise_set)} noisy repeated headers/footers (Threshold: {noise_threshold} pages)")
    if noise_set:
        logger.debug(f"Noise patterns detected: {noise_set}")
        
    return noise_set

def recover_latent_headings(paragraphs: list, global_noise: set) -> list:
    recovered = []
    for _ in range(min(3, len(paragraphs))):
        para = paragraphs[0].strip()
        if not para or para.lower() in global_noise or not is_valid_heading(para): 
            break
            
        word_count = len(para.split())
        is_numbered = bool(re.match(r"^[A-Z\d]+[\.\-]\s", para))
        
        if (word_count <= 8 and para.istitle()) or is_numbered or (word_count <= 10 and para.isupper()):
            promoted_text = paragraphs.pop(0)
            logger.debug(f"Recovered latent heading from paragraph text: '{promoted_text}'")
            recovered.append({"text": promoted_text})
        else:
            break
            
    return recovered

def calculate_page_quality(data: dict) -> dict:
    confidences = [data.get(f"{lvl}_confidence", 0) for lvl in ADAPTIVE_THRESHOLDS.keys() if data.get(lvl)]
    avg_conf = sum(confidences) / len(confidences) if confidences else 1.0
    content_words = sum(len(p.split()) for p in data.get("paragraphs", []))
    
    is_low = avg_conf < 0.50 and content_words < 20
    return {
        "heading_quality": avg_conf,
        "is_low_quality": is_low
    }

def generate_synthetic_layout(vision_responses: list) -> list:
    logger.info("Generating dynamic synthetic spatial layouts...")
    global_noise = build_global_noise_map(vision_responses)
    synthetic_pages = []
    
    PAGE_WIDTH, CENTER_X, LEFT_MARGIN = 612, 306, 72.0
    MOCK_FONTS = {"chapter": 24.0, "section": 20.0, "subsection": 16.0, "subsubsection": 14.0, "content": 11.0}

    for page in vision_responses:
        page_num = page.get("page", 0)
        data = page["data"]
        quality = calculate_page_quality(data)
        
        if quality["is_low_quality"]: 
            logger.warning(f"Skipping page {page_num} due to low quality score (Conf: {quality['heading_quality']:.2f})")
            continue
            
        elements = []
        current_y = 72.0 
        
        # 1. Inject Headings
        for level, base_threshold in ADAPTIVE_THRESHOLDS.items():
            text = data.get(level, "").strip()
            conf = data.get(f"{level}_confidence", 0.0)
            threshold = base_threshold * (0.9 if quality["heading_quality"] > 0.8 else 1.1)
            
            if text and conf >= threshold and text.lower() not in global_noise and is_valid_heading(text):
                font_size = MOCK_FONTS[level]
                is_centered = level == "chapter"
                x0 = CENTER_X - 100 if is_centered else LEFT_MARGIN
                x1 = CENTER_X + 100 if is_centered else PAGE_WIDTH - LEFT_MARGIN
                
                current_y += (font_size * 2) 
                elements.append({
                    "text": text, "font_size": font_size, "bold": True,
                    "bbox": [x0, current_y, x1, current_y + font_size], "page": page_num
                })
                current_y += font_size * 1.5 
                logger.debug(f"Page {page_num} - Injected {level}: '{text}' (Conf: {conf:.2f})")

        # 2. Recover Headings
        paragraphs = data.get("paragraphs", [])
        for rec in recover_latent_headings(paragraphs, global_noise):
            current_y += MOCK_FONTS["subsection"] * 2
            elements.append({
                "text": rec["text"], "font_size": MOCK_FONTS["subsection"], "bold": True,
                "bbox": [LEFT_MARGIN, current_y, PAGE_WIDTH - LEFT_MARGIN, current_y + MOCK_FONTS["subsection"]],
                "page": page_num
            })
            current_y += MOCK_FONTS["subsection"] * 1.5

        # 3. Inject Paragraphs
        for para in paragraphs:
            para_text = para.strip()
            if not para_text or para_text.lower() in global_noise: 
                continue
            para_height = ((len(para_text.split()) / 12) + 1) * MOCK_FONTS["content"] * 1.2
            elements.append({
                "text": para_text, "font_size": MOCK_FONTS["content"], "bold": False,
                "bbox": [LEFT_MARGIN, current_y, PAGE_WIDTH - LEFT_MARGIN, current_y + para_height],
                "page": page_num
            })
            current_y += para_height + 12.0

        if elements:
            synthetic_pages.append({"page": page_num, "elements": elements})

    logger.info(f"Synthetic layout generation complete. Rendered {len(synthetic_pages)} usable pages.")
    return synthetic_pages