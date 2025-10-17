import graphene
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

    def resolve_geojson(self, info):
        if self.has_geojson_data():  # type: ignore
            return self.get_raw_geojson_data()  # type: ignore
        return None

    geotiff_link = graphene.String()

    def resolve_geotiff_link(self, info):
        if isinstance(self, models.MapData):
            if self.geotiff:
                return self.geotiff.url
            return None
        raise ValueError("Expected API object to be an instance of MapData!")


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
            "legend_order",
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
        fields = ["id", "name", "map_data", "description", "styles_on_layer", "serialized_leaflet_json"]

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


class LayerGroupType(DjangoObjectType):
    class Meta:
        model = models.LayerGroup
        fields = ["id", "group_name", "group_description", "layers"]

    layers = graphene.List(LayerTypeWithoutSerializedLeafletJSON)

    def resolve_layers(self, info):
        if isinstance(self, models.LayerGroup):
            return models.Layer.objects.filter(layeronquestion__layer_group=self).distinct()
        raise ValueError("Expected LayerGroup object while resolving query!")


class LayerOnQuestionType(DjangoObjectType):
    class Meta:
        model = models.LayerOnQuestion
        fields = ["layer", "question", "active_by_default", "layer_group"]


class QuestionTabType(DjangoObjectType):
    class Meta:
        model = models.QuestionTab
        fields = ["id", "title", "content"]


class InitiativeTagType(DjangoObjectType):
    class Meta:
        model = models.InitiativeTag
        fields = ["id", "name"]


class InitiativeType(DjangoObjectType):
    class Meta:
        model = models.Initiative
        fields = ["id", "title", "link", "image", "content", "tags"]


class QuestionType(DjangoObjectType):
    class Meta:
        model = models.Question
        fields = ["id", "title", "subtitle", "image", "initiatives", "tabs", "slug"]

    # Link one half of the many-to-many through table in the graphql schema
    layers_on_question = graphene.List(LayerOnQuestionType)

    def resolve_layers_on_question(self, info):
        return models.LayerOnQuestion.objects.filter(question=self)


class PageType(DjangoObjectType):
    class Meta:
        model = models.Page
        fields = ["id", "title", "content", "background_image"]


class Query(graphene.ObjectType):

    all_layers = graphene.List(LayerTypeWithoutSerializedLeafletJSON)
    layer = graphene.Field(LayerType, id=graphene.UUID(required=True))

    layer_group = graphene.List(LayerGroupType, question_id=graphene.UUID(required=True))

    all_questions = graphene.List(QuestionType)
    question = graphene.Field(QuestionType, id=graphene.UUID(required=True))
    question_by_slug = graphene.Field(QuestionType, slug=graphene.String(required=True))
    question_tab_by_id = graphene.Field(QuestionTabType, id=graphene.UUID(required=True))

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
        return models.Layer.objects.all()

    def resolve_layer(self, info, id):
        return models.Layer.objects.get(pk=id)

    def resolve_layer_group(self, info, question_id):
        return models.LayerGroup.objects.filter(layeronquestion__question__id=question_id).distinct()

    def resolve_all_questions(self, info):
        return models.Question.objects.all()

    def resolve_question(self, info, id):
        return models.Question.objects.get(pk=id)

    def resolve_question_by_slug(self, info, slug: str):
        return models.Question.objects.get(slug=slug)

    def resolve_question_tab_by_id(self, info, id):
        return models.QuestionTab.objects.get(pk=id)

    def resolve_all_map_datas(self, info):
        return models.MapData.objects.all()

    def resolve_map_data(self, info, id):
        return models.MapData.objects.get(pk=id)

    def resolve_map_data_by_dropdown_name(self, info, dropdownName: str):
        return models.MapData.objects.get(name=dropdownName.split("(")[0].strip())

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
