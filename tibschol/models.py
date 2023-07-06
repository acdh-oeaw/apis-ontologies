import reversion
from apis_core.apis_entities.models import TempEntityClass
from django.db import models


@reversion.register(follow=["tempentityclass_ptr"])
class Instance(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Instance"
    citation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="citation",
    )


@reversion.register(follow=["tempentityclass_ptr"])
class Person(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Person"


@reversion.register(follow=["tempentityclass_ptr"])
class Role(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Role"


@reversion.register(follow=["tempentityclass_ptr"])
class Work(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Work"
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="subject",
    )  # should be a controlled vocabulary field


@reversion.register(follow=["tempentityclass_ptr"])
class Place(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Place"
    longitude = models.DecimalField(max_digits=22,
                                    decimal_places=16,
                                    blank=True,
                                    null=True)
    latitude = models.DecimalField(max_digits=22,
                                   decimal_places=16,
                                   blank=True,
                                   null=True)
