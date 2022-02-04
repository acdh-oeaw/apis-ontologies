import django
import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
# from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_relations.models import Property
from apis_core.apis_metainfo.models import RootObject


@reversion.register(follow=["tempentityclass_ptr"])
class Contribution(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Contribution"


@reversion.register(follow=["tempentityclass_ptr"])
class Identifier(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Identifier"


@reversion.register(follow=["tempentityclass_ptr"])
class Instance(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Instance"


@reversion.register(follow=["tempentityclass_ptr"])
class Item(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Item"


@reversion.register(follow=["tempentityclass_ptr"])
class Person(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Person"


@reversion.register(follow=["tempentityclass_ptr"])
class Role(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Role"


@reversion.register(follow=["tempentityclass_ptr"])
class Work(TempEntityClass):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Work"


def construct_properties():

    list_valid_properties = []

    instanceOf = Property.objects.get_or_create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/instanceOf",
    )[0]
    instanceOf.name = "Instance of"
    instanceOf.name_reverse = "Instance of Work"
    instanceOf.subj_class.clear()
    instanceOf.obj_class.clear()
    instanceOf.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    instanceOf.obj_class.add(ContentType.objects.get(model=Work.__name__))
    instanceOf.save()
    list_valid_properties.append(instanceOf)

    itemOf = Property.objects.get_or_create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/itemOf",
    )[0]
    itemOf.name="Holding for"
    itemOf.name_reverse="Has Holding"
    itemOf.subj_class.clear()
    itemOf.obj_class.clear()
    itemOf.subj_class.add(ContentType.objects.get(model=Item.__name__))
    itemOf.obj_class.add(ContentType.objects.get(model=Instance.__name__))
    itemOf.save()
    list_valid_properties.append(itemOf)

    contribution = Property.objects.get_or_create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/contribution",
    )[0]
    contribution.name="Contributor and role"
    contribution.name_reverse="Contribution of"
    contribution.subj_class.clear()
    contribution.obj_class.clear()
    contribution.subj_class.add(ContentType.objects.get(model=Work.__name__))
    contribution.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    contribution.subj_class.add(ContentType.objects.get(model=Item.__name__))
    contribution.obj_class.add(ContentType.objects.get(model=Contribution.__name__))
    contribution.save()
    list_valid_properties.append(contribution)

    role = Property.objects.get_or_create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/role",
    )[0]
    role.name="Contributor role"
    role.name_reverse="Contributor role"
    role.subj_class.clear()
    role.obj_class.clear()
    role.subj_class.add(ContentType.objects.get(model=Contribution.__name__))
    role.obj_class.add(ContentType.objects.get(model=Role.__name__))
    role.save()
    list_valid_properties.append(role)

    agent = Property.objects.get_or_create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/agent",
    )[0]
    agent.name="Associated agent"
    agent.name_reverse="Associated agent of"
    agent.subj_class.clear()
    agent.obj_class.clear()
    agent.subj_class.add(ContentType.objects.get(model=Work.__name__))
    agent.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    agent.subj_class.add(ContentType.objects.get(model=Item.__name__))
    agent.obj_class.add(ContentType.objects.get(model=Person.__name__))
    agent.save()
    list_valid_properties.append(agent)

    derivativeOf = Property.objects.get_or_create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/derivativeOf",
    )[0]
    derivativeOf.name="Is derivative of"
    derivativeOf.name_reverse="Has derivative"
    derivativeOf.subj_class.clear()
    derivativeOf.obj_class.clear()
    derivativeOf.subj_class.add(ContentType.objects.get(model=Work.__name__))
    derivativeOf.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    derivativeOf.obj_class.add(ContentType.objects.get(model=Work.__name__))
    derivativeOf.obj_class.add(ContentType.objects.get(model=Instance.__name__))
    derivativeOf.save()
    list_valid_properties.append(derivativeOf)

    absorbed = Property.objects.get_or_create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/absorbed",
    )[0]
    absorbed.name="Absorption of"
    absorbed.name_reverse="Absorbed by"
    absorbed.subj_class.clear()
    absorbed.obj_class.clear()
    absorbed.subj_class.add(ContentType.objects.get(model=Work.__name__))
    absorbed.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    absorbed.obj_class.add(ContentType.objects.get(model=Work.__name__))
    absorbed.obj_class.add(ContentType.objects.get(model=Instance.__name__))
    absorbed.save()
    list_valid_properties.append(absorbed)

    for p in Property.objects.all():

        if p not in list_valid_properties:

            p.delete()
