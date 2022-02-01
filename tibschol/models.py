import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
# from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_entities.models import TempEntityClass


class Work(TempEntityClass):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class Instance(TempEntityClass):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class Item(TempEntityClass):

    pass


def construct_properties():

    pass