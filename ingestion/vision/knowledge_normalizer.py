import json
import logging

logger = logging.getLogger(__name__)

def _ensure_list(data):
    """Safety wrapper: VLMs sometimes return strings/dicts instead of lists."""
    if not data:
        return []
    if isinstance(data, list):
        return data
    
    logger.debug(f"VLM returned non-list type ({type(data).__name__}). Wrapping in list.")
    return [data]

def normalize_value(value, chunk_type):
    if isinstance(value, str):
        return value

    if not isinstance(value, dict):
        logger.debug(f"Normalizing non-dict/non-string value for {chunk_type}: {value}")
        return str(value)

    if chunk_type == "definition":
        return value.get("definition") or value.get("term") or json.dumps(value)

    if chunk_type == "learning_outcome":
        return value.get("outcome", json.dumps(value))

    if chunk_type == "key_point":
        return value.get("text", json.dumps(value))

    if chunk_type == "relationship":
        source = value.get("source", "")
        relation = value.get("relation", "")
        target = value.get("target", "")
        return f"{source} {relation} {target}".strip()

    if chunk_type in ["figure", "table"]:
        return value.get("title", value.get("name", json.dumps(value)))

    if chunk_type == "example":
        return value.get("example") or value.get("description") or json.dumps(value)

    return json.dumps(value)

def normalize_page(page_json, page_number):
    logger.debug(f"Starting normalization for page {page_number}")
    units = []

    chapter = page_json.get("chapter", "")
    section = page_json.get("section", "")
    subsection = page_json.get("subsection", "")
    subsubsection = page_json.get("subsubsection", "")

    mappings = {
        "definitions": "definition",
        "examples": "example",
        "tables": "table",
        "figures": "figure",
        "formulas": "formula",
        "decision_trees": "decision_tree",
        "business_rules": "business_rule",
        "relationships": "relationship",
        "database_mappings": "database_mapping",
        "learning_outcomes": "learning_outcome",
        "key_points": "key_point",
        "paragraphs": "content",
    }

    # 1. Process standard mapped fields
    for field, chunk_type in mappings.items():
        values = _ensure_list(page_json.get(field, []))
        
        if values:
            logger.debug(f"Found {len(values)} items for field '{field}' on page {page_number}")

        for value in values:
            content = normalize_value(value, chunk_type).strip()
            if not content:
                logger.debug(f"Skipping empty content for chunk_type '{chunk_type}'")
                continue
                
            units.append({
                "page": page_number,
                "chapter": chapter,
                "section": section,
                "subsection": subsection,
                "subsubsection": subsubsection,
                "type": chunk_type,
                "content": content,
            })

    # 2. Process workflows separately due to specific joining logic
    workflows = _ensure_list(page_json.get("workflows", []))
    if workflows:
        logger.debug(f"Found {len(workflows)} workflows on page {page_number}")

    for workflow in workflows:
        if isinstance(workflow, list):
            workflow_text = " -> ".join([str(step) for step in workflow])
        else:
            workflow_text = str(workflow)
            
        workflow_text = workflow_text.strip()
        if not workflow_text:
            continue

        units.append({
            "page": page_number,
            "chapter": chapter,
            "section": section,
            "subsection": subsection,
            "subsubsection": subsubsection,
            "type": "workflow",
            "content": workflow_text,
        })

    logger.debug(f"Finished normalization for page {page_number}. Generated {len(units)} units.")
    return units