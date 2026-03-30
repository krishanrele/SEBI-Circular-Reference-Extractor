import re
import json
import pytest
from agent.extractor import extract_references

def load_ground_truth():
    with open("evals/ground_truth.json") as f:
        return json.load(f)

def normalise_for_matching(title: str) -> str:
    """
    Strips punctuation, extra whitespace, and common leading words
    so that slightly different title formats can still be matched.
    e.g. 'SEBI Master Circular for AIFs' and 'Master Circular for AIFs'
    will both normalise to 'master circular for aifs'.
    """
    title = title.lower().strip()
    title = re.sub(r'[^\w\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title)
    for prefix in ["sebi ", "the ", "a "]:
        if title.startswith(prefix):
            title = title[len(prefix):]
    return title.strip()

def titles_match(found: str, expected: str) -> bool:
    """
    Returns True if two document titles refer to the same document.
    Checks exact match after normalisation, substring match,
    and significant word overlap (75% threshold).
    """
    found_n = normalise_for_matching(found)
    expected_n = normalise_for_matching(expected)

    if found_n == expected_n:
        return True

    if expected_n in found_n or found_n in expected_n:
        return True

    stop_words = {'of', 'for', 'the', 'and', 'by', 'in', 'to', 'a', 'an', 'dated'}
    found_words = set(found_n.split()) - stop_words
    expected_words = set(expected_n.split()) - stop_words

    if not expected_words:
        return False

    overlap = len(found_words & expected_words) / len(expected_words)
    return overlap >= 0.75

def score_result(result: dict, expected: list) -> dict:
    """
    Scores the agent's output against expected references.

    - Recall:    Did the agent find everything it should have? (no misses)
    - Precision: Did the agent avoid making things up? (no hallucinations)
    - F1 Score:  A single combined score balancing both (higher is better)
    """
    found_titles = [r["document_title"] for r in result["references"]]
    true_positives = 0
    false_negatives = []

    for expected_ref in expected:
        expected_title = expected_ref["document_title"]
        aliases = expected_ref.get("aliases", [])
        all_titles_to_check = [expected_title] + aliases

        match = any(
            titles_match(found, candidate)
            for found in found_titles
            for candidate in all_titles_to_check
        )

        if match:
            true_positives += 1
        else:
            false_negatives.append(expected_title)

    recall = true_positives / len(expected) if expected else 1.0
    precision = true_positives / len(found_titles) if found_titles else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1_score": round(f1, 2),
        "missed_references": false_negatives,
        "total_found": len(found_titles),
        "total_expected": len(expected)
    }

def get_all_test_cases():
    """Returns all test cases from ground truth as a list of (pdf_file, expected) tuples."""
    ground_truth = load_ground_truth()
    return [
        (case["pdf_file"], case["expected_references"])
        for case in ground_truth["test_cases"]
    ]

@pytest.fixture(scope="module", params=get_all_test_cases(), ids=lambda x: x[0])
def agent_result(request):
    """Runs the agent once per test case and returns the result alongside expected references."""
    pdf_file, expected = request.param
    result = extract_references(pdf_file)
    return result, expected

class TestReferenceExtraction:

    def test_output_structure(self, agent_result):
        """Output must have the correct JSON structure."""
        result, _ = agent_result
        assert "circular_title" in result, "Missing 'circular_title' key"
        assert "references" in result, "Missing 'references' key"
        assert isinstance(result["references"], list), "'references' must be a list"

    def test_no_hallucinations(self, agent_result):
        """Agent should not invent references that do not exist."""
        result, expected = agent_result
        scores = score_result(result, expected)
        print(f"\n  Precision: {scores['precision']} | Recall: {scores['recall']} | F1: {scores['f1_score']}")
        assert scores["precision"] >= 0.85, (
            f"Too many hallucinated references. Precision: {scores['precision']}. "
            f"Found {scores['total_found']} references, expected {scores['total_expected']}."
        )

    def test_high_recall(self, agent_result):
        """Agent should find at least 90% of real references."""
        result, expected = agent_result
        scores = score_result(result, expected)
        print(f"\n  Precision: {scores['precision']} | Recall: {scores['recall']} | F1: {scores['f1_score']}")
        assert scores["recall"] >= 0.90, (
            f"Too many missed references. Recall: {scores['recall']}. "
            f"Missed: {scores['missed_references']}"
        )

    def test_page_numbers_present(self, agent_result):
        """Every reference must have at least one page number."""
        result, _ = agent_result
        for ref in result["references"]:
            assert len(ref["pages"]) > 0, (
                f"No page numbers recorded for: {ref['document_title']}"
            )

    def test_document_types_valid(self, agent_result):
        """Document types must be from the allowed list.
        'master circular' is included as a valid type — Gemini correctly
        distinguishes master circulars from regular circulars and this
        distinction is preserved rather than flattened.
        """
        result, _ = agent_result
        valid_types = {"circular", "master circular", "regulation", "act", "guideline", "other"}
        for ref in result["references"]:
            assert ref["document_type"] in valid_types, (
                f"Invalid type '{ref['document_type']}' for '{ref['document_title']}'"
            )