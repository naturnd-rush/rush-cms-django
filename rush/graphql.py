import graphene
from graphene_django.types import DjangoObjectType

from .models import Question

"""
GraphQL Schema for RUSH models. This file defines what data GraphQL
is allowed to query and communicate to the frontend.
"""


class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        fields = ("id", "title", "content")


class Query(graphene.ObjectType):
    all_questions = graphene.List(QuestionType)
    question = graphene.Field(QuestionType, id=graphene.Int(required=True))

    def resolve_all_questions(root, info):
        return Question.objects.all()

    def resolve_question(root, info, id):
        return Question.objects.get(pk=id)


def get_schema() -> graphene.Schema:
    return graphene.Schema(query=Query)
