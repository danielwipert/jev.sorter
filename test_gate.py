"""Tests for gate.py. Run with: python test_gate.py"""

import gate

CATEGORIES = {"card_arrival": "card arrival", "lost_or_stolen_card": "lost or stolen card"}
KEYWORDS = {"card_arrival": ["card", "arrival", "delivery"], "lost_or_stolen_card": ["lost", "stolen"]}
MESSAGE = "Where is my card? It hasn't arrived."


def check(predicted, confidence=90, message=MESSAGE, threshold=None):
    return gate.gate(message, predicted, confidence, CATEGORIES, KEYWORDS, threshold)


def test_invalid_category():
    assert check("card_arrivals") == ("review", "invalid_category", None)  # near miss
    assert check("Card_Arrival") == ("review", "invalid_category", None)  # must be exact
    assert check("") == ("review", "invalid_category", None)


def test_invalid_category_beats_high_confidence():
    # The point of the gate: 100% confident but broken is still rejected.
    assert check("made_up_label", confidence=100, threshold=0) == ("review", "invalid_category", None)


def test_empty_input():
    assert check("card_arrival", message="   \n") == ("review", "empty_input", False)


def test_keyword_flag_only():
    # "Where is my card" has no keyword for lost_or_stolen_card: flagged but not blocked.
    assert check("lost_or_stolen_card") == ("auto_accept", "", True)
    assert check("card_arrival") == ("auto_accept", "", False)


def test_keyword_blocking():
    gate.KEYWORD_CHECK_BLOCKS = True
    try:
        assert check("lost_or_stolen_card") == ("review", "keyword_miss", True)
    finally:
        gate.KEYWORD_CHECK_BLOCKS = False


def test_keyword_whole_words_only():
    # "cards" is not "card": keywords match whole words, case-insensitive.
    assert check("card_arrival", message="My CARD, please") == ("auto_accept", "", False)
    assert check("card_arrival", message="My cards please") == ("auto_accept", "", True)


def test_confidence_threshold():
    assert check("card_arrival", confidence=69.9, threshold=70) == ("review", "low_confidence", False)
    assert check("card_arrival", confidence=70, threshold=70) == ("auto_accept", "", False)  # at threshold passes
    assert check("card_arrival", confidence=5) == ("auto_accept", "", False)  # no threshold: check 4 skipped


if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"All {len(tests)} tests passed.")
