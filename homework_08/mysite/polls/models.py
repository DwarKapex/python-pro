import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField("Question", max_length=200)
    pub_date = models.DateTimeField("Date published")

    def __str__(self) -> str:
        return str(self.question_text)

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self) -> bool:
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choise_text = models.CharField("Choises", max_length=200)
    votes = models.IntegerField("Votes", default=0)

    def __str__(self):
        return str(self.choise_text)
