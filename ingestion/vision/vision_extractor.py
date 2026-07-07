import json
import re
import logging
from ollama import chat

logger = logging.getLogger(__name__)

PROMPT = """
Analyze this cropped page image carefully. Extract ONLY information visible on the page.

HEADING DETECTION RULES:
- Identify headings strictly based on visual prominence: larger font size, bold text, centering, distinct padding, and numbering patterns (e.g., 'CHAPTER 1', '1.1', 'A.').
- REJECT and DO NOT extract as headings: Table rows, figure descriptions, bullet points, exercises, quiz questions, or bold terms embedded inside standard paragraphs.
- Ignore running headers or page fragments near the edges.

CONFIDENCE VALUES:
- Provide a heading confidence value between 0.0 and 1.0 for each level. 1.0 means an explicitly visual, standalone heading. 0.0 means completely missing.

Return ONLY valid JSON. Do not explain or include markdown wrappers.

{
"chapter":"", "chapter_confidence": 0.0,
"section":"", "section_confidence": 0.0,
"subsection":"", "subsection_confidence": 0.0,
"subsubsection":"", "subsubsection_confidence": 0.0,
"paragraphs":[], "definitions":[], "examples":[], "tables":[], "figures":[],
"formulas":[], "workflows":[], "decision_trees":[], "business_rules":[],
"relationships":[], "database_mappings":[], "key_points":[]
}
"""

def extract_page(image_path):
    logger.debug(f"Sending image to Vision Model: {image_path}")
    try:
        response = chat(
            model="qwen2.5vl",
            messages=[{"role": "user", "content": PROMPT, "images": [image_path]}],
            options={"num_ctx": 8192, "temperature": 0.0}
        )
        
        text = response["message"]["content"].replace("```json", "").replace("```", "").strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        
        if match:
            logger.debug(f"Successfully extracted valid JSON from {image_path}")
            return json.loads(match.group(0))
        else:
            logger.warning(f"Regex failed to find JSON block in VLM response for {image_path}")
            
    except Exception as e:
        logger.error(f"Vision extraction failed for {image_path}: {e}", exc_info=True)
        
    return {"paragraphs": []}