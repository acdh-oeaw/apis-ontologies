import reversion
from django.db import models
from apis_core.apis_entities.models import AbstractEntity


@reversion.register(follow=["tempentityclass_ptr"])
class Race(AbstractEntity):

    allied_with_sauron = models.BooleanField(blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Hero(AbstractEntity):

    corruptable = models.BooleanField(blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Land(AbstractEntity):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class City(AbstractEntity):

    pass


