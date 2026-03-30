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

For the circular title, capture BOTH the reference number 
(e.g. HO/19/28/(1)2026-AFD-SEC3/I/6176/2026) AND the descriptive title 
(e.g. Regulatory Reporting by AIFs), formatted as:
"[Reference Number] — [Descriptive Title]"

INCLUDE only these document types:
- SEBI Circulars — whether referenced by full title, short title, or number alone
- SEBI Master Circulars — always use the full title including the date
  e.g. "Master Circular for Alternative Investment Funds (AIFs) dated May 07, 2024"
  NOT "Master Circular for AIFs dated May 07, 2024" (too short)
- SEBI Regulations — always include the full name and year
  e.g. "SEBI (Alternative Investment Funds) Regulations, 2012"
- Acts of Parliament (e.g. "Securities and Exchange Board of India Act, 1992")
- RBI Guidelines or Master Circulars
- Stock Exchange Rules or Bye-laws
- Any other formal statutory or regulatory instrument

CRITICAL RULES FOR TITLES:
- For Master Circulars, always spell out the full subject area in the title.
  CORRECT: "Master Circular for Alternative Investment Funds (AIFs) dated May 07, 2024"
  WRONG:   "Master Circular for AIFs dated May 07, 2024"
- For circulars referenced by number only, capture the full reference number exactly 
  as it appears in the document, including all slashes, digits, and suffixes.
  e.g. "Circular No. HO/47/11/11(3)2025-MRD-POD2/I/2765/2026 dated January 16, 2026"
- If the same document appears under slightly different names, always use the longest 
  and most complete version of the name.
- If a document is referenced multiple times, return it as ONE entry with all page 
  numbers combined in the pages array.

EXCLUDE the following entirely:
- Website URLs or web addresses
- SEBI committees, working groups, or advisory panels
- Industry bodies, forums, or associations
- Internal SEBI departments or divisions
- Names of people or organisations that are not documents

SELF-CHECK INSTRUCTIONS:
Before returning your final JSON, perform these checks:
1. Re-read every paragraph of the circular and verify you have not missed any 
   formal document reference.
2. Check every footnote, header, and annexure separately.
3. For each Master Circular in your list, confirm you have used the full subject 
   name, not an abbreviation.
4. For each circular referenced by number, confirm you have captured the complete 
   reference number exactly as written.
5. Check for duplicate entries — if the same document appears twice under different 
   names, merge them into one entry using the longer title.
6. Remove any entry that is a website, committee, forum, or working group.

Only return your answer after completing all six checks.

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