from app.main import _calculate_third_vowels_or_uppercase_cost


def test_third_vowel_rule():
    text = "Are there any restrictions on alterations or improvements?"
    # Are there any restrictions on alterations or improvements?
    # !-! --!-- !-- |--|--|--!-- !- -|--|--!--| -- !--|--|--!---
    # 9 * 0.3 = 2.7
    assert _calculate_third_vowels_or_uppercase_cost(text) == 2.7
