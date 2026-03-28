# SEBI Circular Reference Extractor

An AI-powered agent that reads SEBI circulars (PDF format) and automatically 
extracts all references to other regulatory documents, along with the page 
numbers where each reference appears.

Powered by **Google Gemini 2.5 Flash** (free tier).

## Prerequisites

- Python 3.11 or higher
- A free Google Gemini API key — get one at [aistudio.google.com](https://aistudio.google.com)

## Installation

Clone the repository and move into the folder:

    git clone https://github.com/YOUR-USERNAME/sebi-circular-agent.git
    cd sebi-circular-agent

Install dependencies:

    pip install -r requirements.txt

Set up your API key:

    cp .env.example .env
    # Open .env and paste your Gemini API key

## Usage

    python main.py path/to/sebi_circular.pdf

## Running Evaluations

    pytest evals/ -v

## Output Format

Results are printed as a table in the terminal and saved as a JSON file in `outputs/`:

    {
      "circular_title": "SEBI Circular on ...",
      "references": [
        {
          "document_title": "Securities Contracts (Regulation) Act, 1956",
          "document_type": "act",
          "pages": [1, 4],
          "context": "as defined under Section 2(h) of..."
        }
      ]
    }

## Improvement History

See [CHANGELOG.md](CHANGELOG.md) for evaluation scores across all versions.

## License

MIT License