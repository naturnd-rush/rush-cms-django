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
        fields = ["id", "title", "content"]


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


class Query(graphene.ObjectType):
    all_questions = graphene.List(QuestionType)
    question = graphene.Field(QuestionType, id=graphene.UUID(required=True))

    all_map_datas = graphene.List(MapDataType)
    map_data = graphene.Field(MapDataType, id=graphene.UUID(required=True))

    def resolve_all_questions(root, info):
        return models.Question.objects.all()

    def resolve_question(root, info, id):
        return models.Question.objects.get(pk=id)

    def resolve_all_map_datas(root, info):
        return models.MapData.objects.all()

    def resolve_map_data(root, info, id):
        return models.MapData.objects.get(pk=id)


def get_schema() -> graphene.Schema:
    return graphene.Schema(query=Query)
