from pytest import mark


@mark.parametrize(
    "value, decimal",
    [
        (1, Decimal("1")),
        (12.45, Decimal("12.45")),
        ("foo", Decimal("0")),
        (float("1"), Decimal("1")),
    ],
)
def test (value: Any, decimal: Decimal):
    assert get_decimal(value) == decimal
