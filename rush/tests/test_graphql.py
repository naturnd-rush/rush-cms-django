from pytest import mark

from rush.graphql import PublishedStateGraphQLView, convert_relative_images_to_absolute
from rush.models import PublishedState


@mark.parametrize(
    "params, expected",
    [
        # PUBLISHED is the default query visibility when unspecified
        (None, [PublishedState.PUBLISHED]),
        ({}, [PublishedState.PUBLISHED]),
        ({"visibility": "foobar"}, [PublishedState.PUBLISHED]),
        ({"foo": "barbaz"}, [PublishedState.PUBLISHED]),
        # the published-state returned corresponds to the visibility param, when it matches a published-state value
        ({"visibility": "published"}, [PublishedState.PUBLISHED]),
        ({"visibility": "draft"}, [PublishedState.DRAFT]),
        ({"visibility": "all"}, [PublishedState.PUBLISHED, PublishedState.DRAFT]),
    ],
)
def test_get_published_state_from_request_params(params: dict | None, expected: PublishedState):
    assert PublishedStateGraphQLView.get_published_state_from_request_params(params) == expected


@mark.django_db
@mark.parametrize(
    "relative, expected",
    [
        ############ Same as BASE_MEDIA_URL ####################
        (
            # HTTPS image URL remains unchanged
            '<img src="https://www.kagi.com/example.png"/>',
            '<img src="https://www.kagi.com/example.png"/>',
        ),
        (
            # HTTP image URL changes to HTTPS
            '<img src="http://www.kagi.com/example.png"/>',
            '<img src="https://www.kagi.com/example.png"/>',
        ),
        (
            # protocol agnostic URL changes to HTTPS. See: https://stackoverflow.com/questions/28446314.
            '<img src="//example.png"/>',
            '<img src="https://www.kagi.com/example.png"/>',
        ),
        (
            # protocol agnostic URL changes to HTTPS (even when double forward-slash present in url)
            '<img src="//something//example.png"/>',
            '<img src="https://www.kagi.com/something//example.png"/>',
        ),
        (
            # HTTPS is appended if missing
            '<img src="www.kagi.com/example.png"/>',
            '<img src="https://www.kagi.com/example.png"/>',
        ),
        (
            # HTTPS and www are appended if missing
            '<img src="kagi.com/example.png"/>',
            '<img src="https://www.kagi.com/example.png"/>',
        ),
        (
            # HTTPS, www, and base media url are appended if missing
            '<img src="example.png"/>',
            '<img src="https://www.kagi.com/example.png"/>',
        ),
        (
            # HTTPS, www, and base media url are appended if missing (even when resource is prefixed by a
            # forward-slash)
            '<img src="/example.png"/>',
            '<img src="https://www.kagi.com/example.png"/>',
        ),
        ############### DIFFERENT DOMAIN ####################
        (
            # HTTPS image URL remains unchanged
            '<img src="https://www.google.com/example.png"/>',
            '<img src="https://www.google.com/example.png"/>',
        ),
        (
            # HTTP image URL changes to HTTPS
            '<img src="http://www.google.com/example.png"/>',
            '<img src="https://www.google.com/example.png"/>',
        ),
        (
            # HTTPS is appended if missing
            '<img src="www.google.com/example.png"/>',
            '<img src="https://www.google.com/example.png"/>',
        ),
        (
            # HTTPS and www are appended if missing
            '<img src="google.com/example.png"/>',
            '<img src="https://www.google.com/example.png"/>',
        ),
    ],
)
def test_convert_relative_images_to_absolute(relative, expected):
    base_media_url = "https://www.kagi.com/"
    absolute = convert_relative_images_to_absolute(relative, base_media_url=base_media_url)
    assert expected == absolute
