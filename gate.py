"""The gate: deterministic checks first, model confidence last (spec Section 6).

Checks, in order. The first failure sends the message to review.
  1. invalid_category  predicted label is not exactly one of the category names
  2. empty_input       message is empty after stripping whitespace
  3. keyword_miss      message has none of the predicted category's keywords
                       (flag only until step 2.1: logged, does not block)
  4. low_confidence    confidence (0-100) is below the threshold

threshold=None runs checks 1-3 only. run.py logs that; analyze.py re-runs the gate with
each model's thresholds (Section 8).
"""

import re

KEYWORD_CHECK_BLOCKS = False  # step 2.1 decides whether to switch this on


def words(text):
    """Lowercase whole words. The rule for matching keywords."""
    return set(re.findall(r"[a-z]+", text.lower()))


def gate(message, predicted, confidence, categories, keywords, threshold=None):
    """Return (gate_result, gate_reason, keyword_miss).

    gate_result is "auto_accept" or "review". gate_reason is "" when accepted.
    keyword_miss is True/False, or None when check 1 failed (no valid category to check).
    """
    if predicted not in categories:
        return "review", "invalid_category", None
    if not message.strip():
        return "review", "empty_input", False
    keyword_miss = not (words(message) & set(keywords[predicted]))
    if keyword_miss and KEYWORD_CHECK_BLOCKS:
        return "review", "keyword_miss", True
    if threshold is not None and confidence < threshold:
        return "review", "low_confidence", keyword_miss
    return "auto_accept", "", keyword_miss
