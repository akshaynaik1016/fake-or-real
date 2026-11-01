import io
import re
from datetime import datetime
from typing import Dict, Any, List
from pypdf import PdfReader

def analyze_pdf_document(pdf_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
    """
    Extracts text, metadata (producer, creation/mod dates), URLs, emails,
    and inspects for possible document manipulation indicators.
    """
    text_content = ""
    metadata = {}
    flags = []
    urls_found = []
    emails_found = []
    phones_found = []
    
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        
        # 1. Extract text across pages
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text_content += f"\n--- Page {page_idx + 1} ---\n" + page_text
            
        # 2. Extract Document Metadata
        raw_meta = reader.metadata
        if raw_meta:
            metadata = {
                "author": str(raw_meta.get("/Author", "")),
                "creator": str(raw_meta.get("/Creator", "")),
                "producer": str(raw_meta.get("/Producer", "")),
                "creation_date": str(raw_meta.get("/CreationDate", "")),
                "mod_date": str(raw_meta.get("/ModDate", ""))
            }
            
        # 3. Detect suspicious producer or toolkits (e.g. Canva, iLovePDF, Word templates vs enterprise ERP)
        producer_str = metadata.get("producer", "").lower()
        creator_str = metadata.get("creator", "").lower()
        
        if any(tool in producer_str or tool in creator_str for tool in ["ilovepdf", "canva", "camscanner", "smallpdf", "pdfescape"]):
            flags.append({
                "code": "CONSUMER_PDF_TOOLKIT",
                "severity": "moderate",
                "message": f"Document generated using consumer web editing tool ('{producer_str or creator_str}').",
                "detail": "Legitimate enterprise offer letters are typically issued from corporate HR systems (e.g., Workday, SuccessFactors, SAP) rather than consumer PDF generators."
            })
            
        # 4. Inconsistent Creation vs Modification Date Check
        if metadata.get("creation_date") and metadata.get("mod_date"):
            if metadata["creation_date"] != metadata["mod_date"]:
                flags.append({
                    "code": "DOCUMENT_MODIFICATION_DETECTED",
                    "severity": "moderate",
                    "message": "Document modification date differs from original creation date.",
                    "detail": "Possible document manipulation indicators detected. Content may have been altered after initial compilation."
                })
                
        # 5. Extract URLs, Emails, Phones
        urls_found = list(set(re.findall(r"https?://[^\s<>\"']+", text_content)))
        emails_found = list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text_content)))
        phones_found = list(set(re.findall(r"\+?[1-9]\d{1,2}[-.\s]?\d{3,5}[-.\s]?\d{4,6}", text_content)))
        
        return {
            "num_pages": num_pages,
            "text": text_content.strip(),
            "metadata": metadata,
            "urls_found": urls_found,
            "emails_found": emails_found,
            "phones_found": phones_found,
            "flags": flags,
            "has_manipulation_indicators": len(flags) > 0
        }
    except Exception as e:
        return {
            "num_pages": 0,
            "text": f"Error parsing PDF document: {str(e)}",
            "metadata": {},
            "urls_found": [],
            "emails_found": [],
            "phones_found": [],
            "flags": [
                {
                    "code": "PDF_CORRUPT_OR_ENCRYPTED",
                    "severity": "high",
                    "message": f"Could not read PDF stream: {str(e)}",
                    "detail": "File may be encrypted or improperly formatted."
                }
            ],
            "has_manipulation_indicators": True
        }
