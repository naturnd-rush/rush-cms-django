import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from ..models.helpers import create_test_layer


@pytest.fixture
def admin_client(client):
    User.objects.create_superuser(
        username="editor", email="editor@example.com", password="password"
    )
    client.login(username="editor", password="password")
    return client


def _searched_layer_names(admin_client, search_term: str) -> list[str]:
    response = admin_client.get(
        reverse("admin:rush_layer_changelist"), {"q": search_term, "channel": "all"}
    )
    assert response.status_code == 200
    return [layer.name for layer in response.context["cl"].result_list]


@pytest.mark.django_db
def test_layer_search_is_fuzzy_and_lists_best_matches_first(admin_client):
    create_test_layer(name="Grassland Health")
    create_test_layer(name="Tree Protection Score")
    create_test_layer(name="Tree Canopy Cover")

    # a typo still finds the layer, and layers scoring below the cutoff are hidden
    assert _searched_layer_names(admin_client, "canopee") == ["Tree Canopy Cover"]
    # the best match is listed first
    assert _searched_layer_names(admin_client, "tree canopy") == [
        "Tree Canopy Cover",
        "Tree Protection Score",
    ]


@pytest.mark.django_db
def test_layer_search_without_a_term_lists_every_layer(admin_client):
    create_test_layer(name="Grassland Health")
    create_test_layer(name="Tree Canopy Cover")
    assert sorted(_searched_layer_names(admin_client, "")) == [
        "Grassland Health",
        "Tree Canopy Cover",
    ]
