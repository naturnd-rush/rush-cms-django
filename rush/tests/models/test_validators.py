from django.test import TestCase


class TestHelloWorld(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.foo = "bar"

    def test_hello_world(self):
        print("Hello world!")
