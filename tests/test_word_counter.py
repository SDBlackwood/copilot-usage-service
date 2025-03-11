from app.main import _count_words_by_length


def test_count_words_by_length():
    # Looking at the 2nd usage message
    # "Are there any restrictions on alterations or improvements?"
    # - char count: 41 * 0.05 = 2.05
    # - 8 words: 4 short, 1 medium, 3 long
    # - short: 4 * 0.02 = 0.08
    # - medium: 1 * 0.03 = 0.03
    # - long: 3 * 0.04 = 0.12
    # - Total cost is 2.28 credits
    # Test the calculation of credits for a message
    # Let's verify the calculation for the second message:
    # "Are there any restrictions on alterations or improvements?"
    short, medium, long = _count_words_by_length(
        "Are there any restrictions on alterations or improvements?"
    )
    assert short == 4
    assert medium == 1
    assert long == 3
