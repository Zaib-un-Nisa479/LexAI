from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL
import PIL.Image
import json, os

client = genai.Client(api_key=GEMINI_API_KEY)

def extract_text_from_image(image_path: str) -> dict:
    """
    Extract all text from an image file.
    Works on scanned PDFs, photos of documents, handwritten notes.
    Returns extracted text + document type classification.
    WHY: Lawyers often have physical documents — this makes them searchable.
    """
    img = PIL.Image.open(image_path)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(temperature=0.0),
        contents=[
            img,
            """You are a legal document OCR specialist.
Extract ALL text from this image exactly as written.
Then classify the document type.

Return as JSON only:
{
  "extracted_text": "complete verbatim text from the image",
  "document_type": "one of: contract|court_order|invoice|nda|letter|handwritten_note|signature_page|unknown",
  "language": "detected language",
  "has_signatures": true/false,
  "has_stamps": true/false,
  "key_dates": ["any dates found"],
  "parties_mentioned": ["names of people or organizations"]
}"""
        ]
    )
    try:
        clean = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        return result
    except:
        return {
            "extracted_text": response.text,
            "document_type": "unknown",
            "language": "unknown",
            "has_signatures": False,
            "has_stamps": False
        }

def analyze_document_image(image_path: str, question: str) -> str:
    """
    Answer a specific question about an image of a document.
    Used when user uploads a photo and asks a targeted question.
    WHY: Faster than full OCR when user just needs one specific thing.
    """
    img = PIL.Image.open(image_path)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(temperature=0.1),
        contents=[
            img,
            f"""You are a legal document analyst.
Analyze this document image and answer the question.
Be precise and cite what you see in the image.
If the answer is not visible in the image, say so.

Question: {question}"""
        ]
    )
    return response.text

def compare_documents_visually(image_path1: str, image_path2: str) -> str:
    """
    Compare two document images side by side.
    WHY: Lawyers often need to compare signed vs unsigned versions,
    or spot differences between contract versions.
    """
    img1 = PIL.Image.open(image_path1)
    img2 = PIL.Image.open(image_path2)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(temperature=0.0),
        contents=[
            img1, img2,
            """Compare these two legal documents.
Identify:
1. Key differences in content or clauses
2. Missing sections in either document
3. Different signatures, dates, or stamps
4. Any concerning discrepancies
Be specific about which document has what."""
        ]
    )
    return response.text

def detect_risk_from_image(image_path: str) -> dict:
    """
    Scan a contract image for red-flag clauses.
    Returns structured risk assessment.
    WHY: The most impressive legal AI feature — instant risk detection.
    """
    img = PIL.Image.open(image_path)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(temperature=0.0),
        contents=[
            img,
            """You are a senior legal risk analyst.
Scan this contract for risk clauses.

Return as JSON only:
{
  "risk_level": "low|medium|high|critical",
  "risks_found": [
    {"clause": "exact quote", "risk": "explanation", "severity": "low|medium|high"}
  ],
  "missing_protections": ["protections not present"],
  "favorable_clauses": ["clauses that protect the client"],
  "recommendation": "overall recommendation"
}"""
        ]
    )
    try:
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"risk_level": "unknown", "risks_found": [], "recommendation": response.text}