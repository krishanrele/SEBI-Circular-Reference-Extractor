# SEBI Circular Reference Extractor

> An AI-powered compliance agent for Indian banking — automatically maps every regulatory cross-reference inside a SEBI circular, so your team spends less time hunting through PDFs and more time acting on what they find.

---

## The Problem

SEBI circulars rarely stand alone. A single circular may reference five other circulars, two regulations, and an Act of Parliament — each of which references further documents. For a compliance team responsible for tracking and responding to SEBI's evolving guidelines, manually tracing these cross-references across hundreds of PDFs is slow, error-prone, and impossible to scale.

This agent solves that problem. Feed it a circular, and it tells you exactly which documents it references, where, and in what context.

---

## What It Does

- Accepts any SEBI circular in PDF format as input
- Identifies every reference to an external regulatory document — circulars, regulations, Acts of Parliament, RBI guidelines, and more
- Returns the full title of each referenced document, the page numbers where it appears, and the exact phrase in which it was referenced
- Filters out noise — websites, internal committees, working groups — so results contain only formal legal instruments
- Deduplicates references so each document appears once, with all its mentions consolidated
- Outputs results as a formatted terminal table and a saved JSON file

---

## Approach

### Model & Tools

| Component | Choice | Reason |
|---|---|---|
| AI Model | Google Gemini 2.5 Flash | Native PDF understanding — reads layout, footnotes, and tables directly without text extraction |
| PDF Reading | pdfplumber | Page count and metadata extraction |
| Output | rich + JSON | Human-readable terminal table and machine-readable file |
| Evaluations | pytest | Automated precision, recall, and F1 scoring across multiple circulars |

### Why Gemini 2.5 Flash

Unlike a regex-based approach, Gemini reads the PDF the same way a human would — understanding context, following sentence structure, and catching references that are phrased unusually, abbreviated, or buried in footnotes. Critically, it accepts PDFs natively, meaning it sees the actual document layout rather than raw extracted text.

### Evaluation-Driven Development

The agent was improved iteratively using a structured evaluation framework:

1. A ground truth file was created by manually reading circulars and listing every formal reference
2. Five automated tests measure output quality on every run: structure validity, precision, recall, page number completeness, and document type correctness
3. Each test run produces a score — failures point directly to what needs fixing in the prompt
4. Changes are logged in `CHANGELOG.md` with before and after scores

This means every change to the agent is measurable, not subjective.

---

## Evaluation Results

| Version | Change | Failures | Successes | Number of Documents |
|---|---|---|---|---|
| v1.0 | Initial release | 0 Failures | 5 Successes | 1 |
| v1.1 | Added 3 more documents to test agent further | 10 Failures | 10 Successes | 4 |
| v1.2 | Ground Truth Adjustment | 4 Failures | 16 Successes | 4 |
| v1.3 | Improved Reference Capture and Reduced Hallucinations | 3 Failures | 17 Successes | 4 |
| v1.4 | Document Type Fix and Alias Matching | 5 Failures | 15 Successes | 4 |
| v1.5 | Type Validation Fix and Ground Truth Completion | 0 Failures | 20 Successes | 4 |


See [CHANGELOG.md](CHANGELOG.md) for the full improvement log.

---

## Prerequisites

- Python 3.11 or higher
- A free Google Gemini API key — get one at [aistudio.google.com](https://aistudio.google.com)

> **Free tier limits for Gemini 2.5 Flash:** 250 requests per day, 15 requests per minute — sufficient for daily compliance workflows at no cost.

---

## Installation

**Step 1 — Clone the repository:**
```bash
git clone https://github.com/YOUR-USERNAME/sebi-circular-agent.git
cd sebi-circular-agent
```

**Step 2 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 3 — Set up your API key:**
```bash
cp .env.example .env
```
Open `.env` and replace the placeholder with your Gemini API key.

---

## Usage
```bash
python main.py path/to/sebi_circular.pdf
```

**Example:**
```bash
python main.py evals/sample_circulars/SEBI_Circular_1774433908492.pdf
```

The agent will print a formatted table in your terminal and save a JSON file to `outputs/`.

**Example output:**
```
Circular: HO/19/28/(1)2026-AFD-SEC3/I/6176/2026 — Regulatory Reporting by AIFs
Total references found: 3

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Document Title                           ┃ Type       ┃ Pages ┃ Context                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ SEBI (Alternative Investment Funds)      │ regulation │ 1, 2  │ [1] In terms of          │
│ Regulations, 2012                        │            │       │ Regulation 28...          │
│                                          │            │       │                          │
│                                          │            │       │ [2] read with Regulation  │
│                                          │            │       │ 28 and Regulation 36...   │
├──────────────────────────────────────────┼────────────┼───────┼──────────────────────────┤
│ Master Circular for AIFs dated           │ circular   │ 1, 2  │ [1] read with Clause      │
│ May 07, 2024                             │            │       │ 15.1.1...                 │
├──────────────────────────────────────────┼────────────┼───────┼──────────────────────────┤
│ Securities and Exchange Board of         │ act        │ 2     │ [1] under Section 11(1)   │
│ India Act, 1992                          │            │       │ of the SEBI Act, 1992     │
└──────────────────────────────────────────┴────────────┴───────┴──────────────────────────┘
```

---

## Output Format

Results are saved as JSON in `outputs/`:
```json
{
  "circular_title": "HO/19/28/(1)2026-AFD-SEC3/I/6176/2026 — Regulatory Reporting by AIFs",
  "references": [
    {
      "document_title": "SEBI (Alternative Investment Funds) Regulations, 2012",
      "document_type": "regulation",
      "pages": [1, 2],
      "context": "In terms of Regulation 28 of SEBI (Alternative Investment Funds) Regulations, 2012"
    }
  ]
}
```

---

## Running Evaluations
```bash
pytest evals/ -v
```

To see precision, recall, and F1 scores printed for each circular:
```bash
pytest evals/ -v -s
```

Evaluations run against every circular listed in `evals/ground_truth.json`. To add a new circular to the test suite, add its PDF to `evals/sample_circulars/` and add its expected references to `ground_truth.json`.

---

## Project Structure
```
sebi-circular-agent/
├── agent/
│   ├── extractor.py        ← uploads PDF to Gemini, parses response
│   └── pdf_reader.py       ← reads page count and metadata
├── evals/
│   ├── test_extraction.py  ← pytest evaluation suite
│   ├── ground_truth.json   ← manually verified reference lists
│   └── sample_circulars/   ← test PDFs
├── outputs/                ← saved JSON results
├── main.py                 ← entry point
├── conftest.py             ← pytest path configuration
├── CHANGELOG.md            ← improvement log with scores
├── requirements.txt
├── .env.example
└── README.md
```

---

## Known Limitations (v1)

**Scope of ground truth** — Evaluations are only as good as the ground truth they test against. Ground truth was created manually for a small number of circulars; edge cases in unusual circulars may not yet be covered.

**Near-duplicate titles** — When Gemini returns the same document under two slightly different names (e.g. with and without the "SEBI" prefix), the agent consolidates them using normalisation logic. Highly unusual variations may still slip through.

**Scanned PDFs** — Gemini handles most PDFs natively, but very old circulars that are pure image scans with no text layer may produce incomplete results.

**Single circular input** — The agent processes one circular at a time. It does not yet follow references to retrieve and analyse the documents it finds.

**No persistent storage** — Each run produces a standalone JSON file. References are not yet stored in a database or linked across circulars.

---

## Ideas for v2 — Scaling to a Knowledge Graph

The natural next step is to move from extracting references to building a connected graph of the entire SEBI regulatory universe. Here is how that could work:

**1. Bulk ingestion pipeline**
Write a script that downloads all SEBI circulars from [sebi.gov.in](https://www.sebi.gov.in) and runs each one through the agent automatically, storing results in a structured database (PostgreSQL or a graph database like Neo4j).

**2. Graph construction**
Each circular becomes a node. Each reference becomes a directed edge pointing from the citing circular to the cited document. This makes it immediately visible which documents are most heavily cited, which circulars have been superseded, and how regulatory themes connect over time.

**3. Recursive reference following**
When the agent finds a referenced circular, automatically retrieve and process that circular too — building the graph outward from any starting point.

**4. Clause-level granularity**
Rather than referencing a whole document, identify the specific clause or section being cited and link at that level — enabling precise compliance tracking per clause.

**5. Natural language query interface**
Add a conversational layer so compliance officers can ask questions like "which circulars reference Regulation 28 of the AIF Regulations?" or "what are all the documents I need to read to understand our obligations on reporting?" and get instant, traceable answers.

**6. Change tracking**
Monitor SEBI's website for new circulars, automatically process them on publication, and alert the compliance team when a new circular references documents they are already tracking.

---

## Acknowledgements

Built as part of a compliance automation exercise for an Indian bank. Powered by [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/) via the [Google GenAI Python SDK](https://github.com/google-gemini/generative-ai-python).

---

## License

MIT License — see [LICENSE](LICENSE) for details.