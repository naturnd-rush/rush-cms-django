# questions/models.py

from django.db import models
from simple_history.models import HistoricalRecords


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    history = HistoricalRecords()

    def __str__(self):
        return f"<Question: {self.title}>"
