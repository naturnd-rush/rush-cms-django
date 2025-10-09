import pytest

from rush.models.question import Question


@pytest.mark.django_db
@pytest.mark.parametrize(
    "instance_slug, db_slug, raises",
    [
        ("different-slug-one", "different-slug-two", False),
        ("same-slug", "same-slug", True),
    ],
)
def test_clean_slug(instance_slug, db_slug, raises):
    db_question = Question.objects.create(title="Test Question", subtitle="Test Subtitle", slug=db_slug)
    instance_question = Question(title="Test Question", subtitle="Test Subtitle", slug=instance_slug)
    if raises:
        match = 'Question with id "{}" has the same slug as this question "{}"!'.format(
            db_question.id,
            instance_question.id,
        )
        with pytest.raises(Question.DuplicateSlug, match=match):
            instance_question.clean_slug()
    else:
        instance_question.clean_slug()
