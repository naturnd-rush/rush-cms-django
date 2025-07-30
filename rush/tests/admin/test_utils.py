from unittest.mock import Mock

import pytest

from rush.admin.utils import *


class TestSliderAndTextboxNumberInput:

    @pytest.mark.parametrize(
        "type, min, max, step",
        [(InputType.NUMBER, 0, 1, 0.01), (InputType.SLIDER, 0, 100, 0.01)],
    )
    def test_create_input(
        self,
        type: InputType,
        min: int,
        max: int,
        step: float,
    ):
        instance = SliderAndTextboxNumberInput(min=min, max=max, step=step)
        input = instance._create_input(type)
        assert input.attrs["min"] == str(min)
        assert input.attrs["max"] == str(max)
        assert input.attrs["step"] == str(step)
        assert input.input_type == type.value

    @pytest.mark.parametrize(
        "value, decimal",
        [
            (1, Decimal("1")),
            (12.45, Decimal("12.45")),
            ("foo", Decimal("0")),
            (float("1"), Decimal("1")),
        ],
    )
    def test_get_decimal(self, value: Any, decimal: Decimal):
        instance = SliderAndTextboxNumberInput()
        assert instance._get_decimal(value) == decimal

    @pytest.mark.parametrize(
        "name, value, min, max, step",
        [
            ("test_widget", 12, 1, 100, 0.01),
            ("foobar", 10000, 0, 1, 0.7),  # No value-enforcement at render time
        ],
    )
    def test_render(self, name, value, min, max, step):

        instance = SliderAndTextboxNumberInput(min=min, max=max, step=step)
        assert instance.slider_input == None
        assert instance.textbox_input == None

        result = instance.render(name, value)

        assert isinstance(instance.slider_input, forms.NumberInput)
        assert isinstance(instance.textbox_input, forms.NumberInput)

        assert f'data-fieldname="{name}"' in result
        assert (
            f'<input type="range" name="{name}" value="{value}" min="{min}" max="{max}" step="{step}" id="slider_{name}">'
            in result
        )
        assert (
            f'<input type="number" name="{name}" value="{value}" min="{min}" max="{max}" step="{step}" id="id_{name}">'
            in result
        )
