import graphene
from graphene_django.types import DjangoObjectType

from rush import models

"""
GraphQL Schema for RUSH models. This file defines what data GraphQL
is allowed to query and communicate to the frontend.
"""


class QuestionType(DjangoObjectType):
    class Meta:
        model = models.Question
        fields = ["id", "title"]


class MapDataType(DjangoObjectType):
    class Meta:
        model = models.MapData
        fields = [
            "id",
            "name",
            "provider",
            "geojson",
            "ogm_map_id",
            "feature_url_template",
            "icon_url_template",
            "image_url_template",
        ]


class StylesOnLayersType(DjangoObjectType):
    class Meta:
        model = models.StylesOnLayer
        fields = [
            "id",
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


class Query(graphene.ObjectType):
    all_questions = graphene.List(QuestionType)
    question = graphene.Field(QuestionType, id=graphene.UUID(required=True))

    all_map_datas = graphene.List(MapDataType)
    map_data = graphene.Field(MapDataType, id=graphene.UUID(required=True))
    map_data_by_name = graphene.Field(MapDataType, name=graphene.String(required=True))

    all_styles_on_layers = graphene.List(StylesOnLayersType)
    styles_on_layer = graphene.Field(
        StylesOnLayersType, id=graphene.UUID(required=True)
    )

    all_styles = graphene.List(StyleType)
    style = graphene.Field(StyleType, id=graphene.UUID(required=True))

    def resolve_all_questions(self, info):
        return models.Question.objects.all()

    def resolve_question(self, info, id):
        return models.Question.objects.get(pk=id)

    def resolve_all_map_datas(self, info):
        return models.MapData.objects.all()

    def resolve_map_data(self, info, id):
        return models.MapData.objects.get(pk=id)

    def resolve_map_data_by_name(self, info, name: str):
        return models.MapData.objects.get(name=name)

    def resolve_all_styles_on_layers(self, info):
        return models.StylesOnLayer.objects.all()

    def resolve_styles_on_layer(self, info, id):
        return models.StylesOnLayer.objects.get(pk=id)

    def resolve_all_styles(self, info):
        return models.Style.objects.all()

    def resolve_style(self, info, id):
        return models.Style.objects.get(pk=id)


def get_schema() -> graphene.Schema:
    return graphene.Schema(query=Query)
