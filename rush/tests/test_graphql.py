from pytest import mark

from rush.graphql import PublishedStateGraphQLView
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
