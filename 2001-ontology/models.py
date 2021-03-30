import reversion
from django.db import models
from apis_core.apis_entities.models import AbstractEntity


@reversion.register(follow=["tempentityclass_ptr"])
class Human(AbstractEntity):

    iq = models.IntegerField(blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Robot(AbstractEntity):

    has_gone_rogue = models.BooleanField(blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Spaceship(AbstractEntity):

    weight = models.IntegerField(blank=True, null=True)

