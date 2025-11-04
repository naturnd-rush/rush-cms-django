from typing import List

import graphene
from django.conf import settings
from django.db.models import Prefetch, QuerySet
from graphene.types import ResolveInfo
from graphene_django.types import DjangoObjectType

from rush import models

"""
GraphQL Schema for RUSH models. This file defines what data GraphQL
is allowed to query and communicate to the frontend.
"""


class MapDataType(DjangoObjectType):
    class Meta:
        model = models.MapData
        fields = [
            "id",
            "name",
            "provider_state",
            "geojson",
            "map_link",
            "campaign_link",
            "geotiff_link",
        ]

    geojson = graphene.String()
    geotiff_link = graphene.String()

    def resolve_geojson(self, info):
        if not isinstance(self, models.MapData):
            raise ValueError("Expected object to be of type MapData when resolving query.")
        return self.geojson

    def resolve_geotiff_link(self, info):
        if not isinstance(self, models.MapData):
            return None
        if not self.geotiff.name:
            # .geotiff.name doesn't make a file-existance check, unlike .geotiff.
            return None
        return self.geotiff.url


class MapDataWithoutGeoJsonType(DjangoObjectType):
    class Meta:  # type: ignore
        model = models.MapData
        fields = [x for x in MapDataType._meta.fields if x != "geojson"]

    # Still need this resolved and filed definition here because inheritance of
    # mapDataType in this class keeps geojson accessible for some reason...
    geotiff_link = graphene.String()

    def resolve_geotiff_link(self, info):
        if isinstance(self, models.MapData):
            if self.geotiff:
                return self.geotiff.url
            return None
        raise ValueError("Expected API object to be an instance of MapData!")


class StylesOnLayersType(DjangoObjectType):
    class Meta:
        model = models.StylesOnLayer
        fields = [
            "id",
            "legend_description",
            "display_order",
            "style",
            "layer",
        ]


class StyleType(DjangoObjectType):
    class Meta:
        model = models.Style
        fields = [
            "id",
            "draw_stroke",
            "stroke_color",
            "stroke_weight",
            "stroke_opacity",
            "stroke_line_cap",
            "stroke_line_join",
            "stroke_dash_array",
            "stroke_dash_offset",
            "draw_fill",
            "fill_color",
            "fill_opacity",
            "draw_marker",
            "marker_icon",
            "marker_icon_opacity",
            "marker_background_color",
            "name",
        ]


class LayerType(DjangoObjectType):
    class Meta:
        model = models.Layer
        fields = [
            "id",
            "name",
            "map_data",
            "description",
            "styles_on_layer",
            "serialized_leaflet_json",
        ]

    styles_on_layer = graphene.List(StylesOnLayersType)

    def resolve_styles_on_layer(self, info):
        if isinstance(self, models.Layer):
            return models.StylesOnLayer.objects.filter(layer__id=self.id)
        raise ValueError("Expected Layer object while resolving query!")


class LayerTypeWithoutSerializedLeafletJSON(DjangoObjectType):
    """
    Defensive type to prevent people from querying serializedLeafletJSON from allLayers, which
    would be too computationally expensive and probably isn't needed by any API client.
    """

    map_data = graphene.Field(MapDataWithoutGeoJsonType)

    class Meta:  # type: ignore
        model = models.Layer
        fields = ["id", "name", "description", "map_data"]


class LayerOnLayerGroupType(DjangoObjectType):

    class Meta:
        model = models.LayerOnLayerGroup
        fields = [
            "active_by_default",
            "display_order",
        ]

    layer_id = graphene.String()

    def resolve_layer_id(self, info):
        if isinstance(self, models.LayerOnLayerGroup):
            return str(self.layer.id)
        raise ValueError("Expected LayerOnLayerGroup object while resolving query!")


class LayerGroupOnQuestionType(DjangoObjectType):
    class Meta:
        model = models.LayerGroupOnQuestion
        fields = [
            "group_name",
            "group_description",
            "display_order",
        ]

    layers_on_layer_group = graphene.List(LayerOnLayerGroupType)

    def resolve_layers_on_layer_group(self, info):
        if isinstance(self, models.LayerGroupOnQuestion):
            if prefetch_cache := getattr(self, "_prefetched_objects_cache", None):
                if "layers" in prefetch_cache:
                    # use prefetched layers if available
                    return self.layers.all()  # type: ignore
            return (
                models.LayerOnLayerGroup.objects.filter(layer_group_on_question=self)
                .distinct()
                .select_related("layer")
                .defer(
                    "layer__serialized_leaflet_json",
                )
            )
        raise ValueError("Expected LayerGroupOnQuestion object while resolving query!")


class QuestionTabType(DjangoObjectType):

    class Meta:
        model = models.QuestionTab
        fields = ["id", "title", "content", "display_order", "slug", "icon_url"]

    icon_url = graphene.String()

    def resolve_icon_url(self, info):
        if isinstance(self, models.QuestionTab):
            url = str(self.icon.file.url)
            if url.startswith(settings.MEDIA_URL):
                # HACK: For some reason that I cannot figure out, the media
                # url gets appended to the start of this file field, but not
                # any others that I have observed. This is a hacky fix.
                return url.removeprefix(settings.MEDIA_URL)
            return url
        raise ValueError("Expected QuestionTab object while resolving query!")


class InitiativeTagType(DjangoObjectType):
    class Meta:
        model = models.InitiativeTag
        fields = ["id", "name", "text_color", "background_color"]


class InitiativeType(DjangoObjectType):
    class Meta:
        model = models.Initiative
        fields = ["id", "title", "link", "image", "content", "tags"]


class QuestionType(DjangoObjectType):
    class Meta:
        model = models.Question
        fields = [
            "id",
            "title",
            "subtitle",
            "image",
            "initiatives",
            "tabs",
            "slug",
            "display_order",
        ]

    # Link one half of the many-to-many through table in the graphql schema
    layer_groups_on_question = graphene.List(LayerGroupOnQuestionType)

    def resolve_layer_groups_on_question(self, info):
        if prefetch_cache := getattr(self, "_prefetched_objects_cache"):
            if "layer_groups" in prefetch_cache:
                # use prefetched layer-groups if available
                return self.layer_groups.all()  # type: ignore
        return models.LayerGroupOnQuestion.objects.filter(question=self)


class PageType(DjangoObjectType):
    class Meta:
        model = models.Page
        fields = ["id", "title", "content", "background_image"]


def get_requested_fields(info: ResolveInfo) -> List[str]:
    """
    Get the graphene fields being resolved at this stage of the request.
    NOTE: Fields are returned in Graphql-style camelCase, e.g., "fieldName".
    """
    selection_set = info.field_nodes[0].selection_set
    if selection_set is None:
        return []
    requested_fields = []
    for field in selection_set.selections:
        print(field)
        name = getattr(field, "name", None)
        value = getattr(name, "value", None)
        if value is not None:
            requested_fields.append(value)
    return requested_fields


def optimized_map_data_resolve_qs(info: ResolveInfo) -> QuerySet[models.MapData]:
    """
    Defer expensive map-data fields when they're not requested to speed up loading times.
    """
    queryset = models.MapData.objects.all()
    requested_fields = get_requested_fields(info)
    if "geojson" not in requested_fields:
        queryset = queryset.defer("_geojson")
    return queryset.all()


def optimized_layer_resolve_qs(info: ResolveInfo) -> QuerySet[models.Layer]:
    """
    Defer expensive map-data fields when they're not requested to speed up loading times.
    """
    queryset = models.Layer.objects.all()
    requested_fields = get_requested_fields(info)
    if "serializedLeafletJson" not in requested_fields:
        # We know we won't be accessing serialized_leaflet_json
        queryset = queryset.defer("serialized_leaflet_json")
    # This will always send another request when accessing _geojson, but
    # it will speed up queries that don't access _geojson significantly.
    queryset = queryset.select_related("map_data").defer("map_data___geojson")
    return queryset.all()


def optimized_question_resolve_qs() -> QuerySet[models.Question]:
    """
    Defer the expensive `serialized_leaflet_json` field and prefetch layers + layer-groups.
    """
    return models.Question.objects.prefetch_related(
        Prefetch(
            # Prefetch layer groups on each question
            "layer_groups",
            queryset=models.LayerGroupOnQuestion.objects.prefetch_related(
                Prefetch(
                    # Prefetch layer ids on each layer group
                    "layers",
                    queryset=models.LayerOnLayerGroup.objects.select_related("layer")
                    .defer("layer__serialized_leaflet_json")
                    .order_by("display_order"),
                )
            ).order_by("display_order"),
        )
    )


class Query(graphene.ObjectType):

    all_layers = graphene.List(LayerTypeWithoutSerializedLeafletJSON)
    layer = graphene.Field(LayerType, id=graphene.UUID(required=True))

    all_questions = graphene.List(QuestionType)
    question = graphene.Field(QuestionType, id=graphene.UUID(required=True))
    question_by_slug = graphene.Field(QuestionType, slug=graphene.String(required=True))
    question_tab_by_id = graphene.Field(QuestionTabType, id=graphene.UUID(required=True))
    question_tab_by_slug = graphene.Field(
        QuestionTabType,
        question_slug=graphene.String(required=True),
        question_tab_slug=graphene.String(required=True),
    )

    all_map_datas = graphene.List(MapDataWithoutGeoJsonType)
    map_data = graphene.Field(MapDataType, id=graphene.UUID(required=True))
    map_data_by_dropdown_name = graphene.Field(MapDataType, dropdownName=graphene.String(required=True))

    all_styles_on_layers = graphene.List(StylesOnLayersType)
    styles_on_layer = graphene.Field(StylesOnLayersType, id=graphene.UUID(required=True))

    all_styles = graphene.List(StyleType)
    style = graphene.Field(StyleType, id=graphene.UUID(required=True))

    all_pages = graphene.List(PageType)
    page = graphene.Field(PageType, id=graphene.UUID(required=True))

    def resolve_all_layers(self, info):
        return optimized_layer_resolve_qs(info).all()

    def resolve_layer(self, info, id):
        return optimized_layer_resolve_qs(info).get(pk=id)

    def resolve_layer_group(self, info, question_id):
        return (
            models.LayerGroupOnQuestion.objects.filter(layeronquestion__question__id=question_id)
            .select_related("layer_on_layer_group")
            .distinct()
        )

    def resolve_all_questions(self, info):
        return optimized_question_resolve_qs().all()

    def resolve_question(self, info, id):
        return optimized_question_resolve_qs().get(pk=id)

    def resolve_question_by_slug(self, info, slug: str):
        return models.Question.objects.get(slug=slug)

    def resolve_question_tab_by_slug(self, info, question_slug: str, question_tab_slug: str):
        return models.QuestionTab.objects.filter(slug=question_tab_slug, question__slug=question_slug).first()

    def resolve_question_tab_by_id(self, info, id):
        return models.QuestionTab.objects.get(pk=id)

    def resolve_all_map_datas(self, info):
        return optimized_map_data_resolve_qs(info).all()

    def resolve_map_data(self, info, id):
        return optimized_map_data_resolve_qs(info).get(pk=id)

    def resolve_map_data_by_dropdown_name(self, info, dropdownName: str):
        optimized_map_data_resolve_qs(info).get(name=dropdownName.split("(")[0].strip())

    def resolve_all_styles_on_layers(self, info):
        return models.StylesOnLayer.objects.all()

    def resolve_styles_on_layer(self, info, id):
        return models.StylesOnLayer.objects.get(pk=id)

    def resolve_all_styles(self, info):
        return models.Style.objects.all()

    def resolve_style(self, info, id):
        return models.Style.objects.get(pk=id)

    def resolve_all_pages(self, info):
        return models.Page.objects.all()

    def resolve_page(self, info, id):
        return models.Page.objects.get(pk=id)


def get_schema() -> graphene.Schema:
    return graphene.Schema(query=Query)
