
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .pdf_reader import get_pdf_metadata

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are a specialist in Indian securities law and SEBI regulations.
Your task is to analyze SEBI circulars and identify references to formal legal and 
regulatory documents only.

For the circular title, capture BOTH the reference number (e.g. HO/19/28/(1)2026-AFD-SEC3/I/6176/2026) 
AND the descriptive title (e.g. Regulatory Reporting by AIFs), formatted as:
"[Reference Number] — [Descriptive Title]"

INCLUDE only these document types:
- SEBI Circulars (e.g. "SEBI Master Circular for AIFs dated May 07, 2024")
- SEBI Regulations (e.g. "SEBI (Alternative Investment Funds) Regulations, 2012")
- Acts of Parliament (e.g. "Securities and Exchange Board of India Act, 1992")
- RBI Guidelines or Master Circulars
- Stock Exchange Rules or Bye-laws
- Any other formal statutory or regulatory instrument

EXCLUDE the following — do not include these even if mentioned in the circular:
- Website URLs or web addresses
- SEBI committees, working groups, or advisory panels
- Industry bodies, forums, or associations (e.g. IVCA, Standards Forum)
- Internal SEBI departments or divisions
- Names of people or organisations that are not documents

For each reference found, extract:
1. The full title or identifier of the referenced document.
   When the same document is referred to by slightly different names,
   always use the longest and most complete version of the name.
2. The exact page number(s) where this reference appears.
3. If the same document is referenced multiple times throughout the circular, return it as a SINGLE entry with all page numbers combined into the pages array and all context phrases combined into a single context string separated by " | "
4. Never merge two genuinely different documents.

Return your response as a valid JSON object only, with this structure:
{
  "circular_title": "Reference Number — Descriptive Title",
  "references": [
    {
      "document_title": "Full name/identifier of the referenced document",
      "document_type": "circular / regulation / act / guideline / other",
      "pages": [1, 3, 5],
      "context": "Brief phrase showing how it was referenced"
    }
  ]
}

Be thorough. Include every reference to a formal document, even passing mentions.
Pay special attention to footnotes, headers, and annexures.
Output ONLY the JSON — no explanation, no markdown, no preamble."""

def extract_references(pdf_path: str) -> dict:
    metadata = get_pdf_metadata(pdf_path)
    print(f"Reading PDF: {pdf_path}")
    print(f"  → {metadata['page_count']} pages found")
    print("Uploading to Gemini 2.5 Flash...")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            types.Part.from_text(text=SYSTEM_PROMPT)
        ]
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    return json.loads(raw)

def save_results(result: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {output_path}")