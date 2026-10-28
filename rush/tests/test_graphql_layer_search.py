from django.test import Client
from pytest import mark

from rush.models import Channel

from .models.helpers import (
    create_test_layer,
    create_test_layer_group,
    create_test_layer_on_layer_group,
    create_test_question,
)


def _query(client: Client, query: str) -> dict:
    response = client.post("/graphql/", {"query": query}, content_type="application/json")
    body = response.json()
    assert "errors" not in body, body
    return body["data"]


@mark.django_db
def test_questions_by_layer_returns_only_questions_the_layer_is_on(client: Client):
    layer = create_test_layer(name="Tree Canopy Cover")
    on_question = create_test_question(title="On question", layer_groups=[])
    on_question.channels.set([Channel.objects.published()])
    group = create_test_layer_group(on_question, layers_on_layer_group=[])
    create_test_layer_on_layer_group(group, layer=layer)

    # this question uses other layers only
    other_question = create_test_question(title="Other question")
    other_question.channels.set([Channel.objects.published()])

    data = _query(client, '{ questionsByLayer(layerId: "%s") { title } }' % layer.id)
    assert data["questionsByLayer"] == [{"title": "On question"}]


@mark.django_db
def test_questions_by_layer_is_scoped_to_the_requested_channels(client: Client):
    layer = create_test_layer()
    draft_question = create_test_question(title="Draft question", layer_groups=[])
    draft_question.channels.set([Channel.objects.draft()])
    group = create_test_layer_group(draft_question, layers_on_layer_group=[])
    create_test_layer_on_layer_group(group, layer=layer)

    # the published channel is served by default, so the draft question is hidden
    data = _query(client, '{ questionsByLayer(layerId: "%s") { title } }' % layer.id)
    assert data["questionsByLayer"] == []

    data = _query(
        client,
        '{ questionsByLayer(layerId: "%s", channels: ["%s"]) { title } }'
        % (layer.id, Channel.DRAFT_NAME),
    )
    assert data["questionsByLayer"] == [{"title": "Draft question"}]
