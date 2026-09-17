import pytest

from rush.models.layer.layer_group_on_question import LayerGroupOnQuestion

is_empty = LayerGroupOnQuestion._is_group_description_empty


@pytest.mark.parametrize(
    "desc",
    [
        "",
        "   ",
        "\n\t  \n",
        "<p></p>",
        "<br>",
        "</br>",
        "<p><br></p>",  # what summernote leaves behind on a cleared editor
        "<p><br></p><p><br></p>",
        "<p> </p>",
        "<p>\n  <br>\n</p>",
    ],
)
def test_empty_descriptions(desc):
    assert is_empty(desc) is True


    "desc",
    [
        "hello",
        "<p>hello</p>",
        "<p><br>hello<br></p>",
        "<p>&nbsp;</p>",  # an entity is real content as far as this check goes
        "<div></div>",  # only <br>/<p> are stripped, so this is not empty
        "<p>.</p>",
        "0",
    ],
)
def test_non_empty_descriptions(desc):
    assert is_empty(desc) is False


