import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
# from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_relations.models import Property
from apis_core.apis_metainfo.models import RootObject


@reversion.register(follow=["tempentityclass_ptr"])
class Resource(TempEntityClass):

    class_uri = "https://www.w3.org/2000/01/rdf-schema#Resource"


@reversion.register(follow=["tempentityclass_ptr"])
class Agent(Resource):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Agent"


@reversion.register(follow=["tempentityclass_ptr"])
class Contribution(Resource):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Contribution"


@reversion.register(follow=["tempentityclass_ptr"])
class Identifier(Resource):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Identifier"


@reversion.register(follow=["tempentityclass_ptr"])
class Instance(Resource):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Instance"


@reversion.register(follow=["tempentityclass_ptr"])
class Item(Resource):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Item"


@reversion.register(follow=["tempentityclass_ptr"])
class Person(Agent):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Person"


@reversion.register(follow=["tempentityclass_ptr"])
class Role(Resource):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Role"


@reversion.register(follow=["tempentityclass_ptr"])
class Work(Resource):

    class_uri = "http://id.loc.gov/ontologies/bibframe/Work"


def construct_properties():

    Property.objects.all().delete()

    instanceOf = Property.objects.create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/instanceOf",
        name="Instance of",
        name_reverse="Instance of Work",
    )
    instanceOf.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    instanceOf.obj_class.add(ContentType.objects.get(model=Work.__name__))

    itemOf = Property.objects.create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/itemOf",
        name="Holding for",
        name_reverse="Has Holding",
    )
    itemOf.subj_class.add(ContentType.objects.get(model=Item.__name__))
    itemOf.obj_class.add(ContentType.objects.get(model=Instance.__name__))

    contribution = Property.objects.create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/contribution",
        name="Contributor and role",
        name_reverse="Contribution of",
    )
    contribution.subj_class.add(ContentType.objects.get(model=Work.__name__))
    contribution.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    contribution.subj_class.add(ContentType.objects.get(model=Item.__name__))
    contribution.obj_class.add(ContentType.objects.get(model=Contribution.__name__))

    role = Property.objects.create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/role",
        name="Contributor role",
        name_reverse="Contributor role",
    )
    role.subj_class.add(ContentType.objects.get(model=Contribution.__name__))
    role.obj_class.add(ContentType.objects.get(model=Role.__name__))

    agent = Property.objects.create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/agent",
        name="Associated agent",
        name_reverse="Associated agent of",
    )
    agent.subj_class.add(ContentType.objects.get(model=Resource.__name__))
    agent.obj_class.add(ContentType.objects.get(model=Agent.__name__))

    derivativeOf = Property.objects.create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/derivativeOf",
        name="Is derivative of",
        name_reverse="Has derivative",
    )
    derivativeOf.subj_class.add(ContentType.objects.get(model=Work.__name__))
    derivativeOf.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    derivativeOf.obj_class.add(ContentType.objects.get(model=Work.__name__))
    derivativeOf.obj_class.add(ContentType.objects.get(model=Instance.__name__))

    absorbed = Property.objects.create(
        property_class_uri="http://id.loc.gov/ontologies/bibframe/absorbed",
        name="Absorption of",
        name_reverse="Absorbed by",
    )
    absorbed.subj_class.add(ContentType.objects.get(model=Work.__name__))
    absorbed.subj_class.add(ContentType.objects.get(model=Instance.__name__))
    absorbed.obj_class.add(ContentType.objects.get(model=Work.__name__))
    absorbed.obj_class.add(ContentType.objects.get(model=Instance.__name__))