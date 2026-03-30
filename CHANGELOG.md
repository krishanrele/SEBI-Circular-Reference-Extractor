# Agent Improvement Log

## Version 1.0 — Initial Release
- Model: gemini-2.5-flash
- Circulars tested: SEBI_Circular_1772622793928
- Results: 5/5 tests passed
- Failures identified:
  - None

## Version 1.1 — Added 3 more circulars to test agent further
- Model: gemini-2.5-flash
- Circulars tested: SEBI_Circular_1772622793928; SEBI_Circular_1774433908492; SEBI_Circular_1773399435433; SEBI_Circular_1774433435925
- Results: 10/20 tests passed
- Failures identified:
  - Recall failures: agent missing master circulars referenced by short name
  - Precision failures: agent finding valid references not captured 
    in ground truth — ground truth updated to reflect these

## Version 1.2 — Ground Truth Adjustment
- Changes made:
  - Prompt now explicitly instructs agent to capture circulars 
    referenced by number only
  - Prompt now instructs agent never to skip a reference just because
    it has no descriptive title
  - Prompt reinforces always including the year in regulation names
- Ground truth updated for SEBI_Circular_1774433908492 after verifying agent's additional findings were correct
- Results: 16/20 tests passed

## Version 1.3 — Improved Reference Capture and Reduced Hallucinations
- Changes made:
  - Added self-checking instructions to the prompt
  - Prompt now instructs agent never to skip a reference just because
    it has no descriptive title
  - Prompt reinforces always including the year in regulation names
  - Updated the matching logic to ensure that in addition to matching on substrings to also match on key words
- Results: 17/20 tests passed

## Version 1.4 — Document Type Fix and Alias Matching
- Changes made:
  - Added alias support to ground_truth.json for titles Gemini returns under slightly longer names than ground truth
  - Extractor now checks aliases before marking a reference missed
- Results: 15/20 tests passed

## Version 1.5 — Type Validation Fix and Ground Truth Completion
- Changes made:
  - Added "master circular" to valid document types in test suite — Gemini correctly distinguishes master circulars from regular circulars and this should be reflected as a valid type rather than penalised
  - Updated ground truth for Circular 1774433908492 to include Master Circular for Research Analysts dated February 06, 2026, as an alias for Master Circular for Research Analysts, which the agent was correctly identifying but ground truth was missing as an alias
- Results: [fill in after running pytest]