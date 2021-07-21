import django_filters
import reversion
import copy
from django.contrib.contenttypes.models import ContentType
from django.db import models
# from apis_core.apis_entities.models import AbstractEntity
from django.db.models import Q

from apis_core.apis_entities.models import TempEntityClass


@reversion.register(follow=["tempentityclass_ptr"])
class Race(TempEntityClass):

    allied_with_sauron = models.BooleanField(blank=True, null=True)

    entity_settings = copy.deepcopy(TempEntityClass.entity_settings)
    entity_settings["list_filters"] = entity_settings["list_filters"] + ["allied_with_sauron"]


@reversion.register(follow=["tempentityclass_ptr"])
class Hero(TempEntityClass):

    corruptible = models.BooleanField(blank=True, null=True)

    entity_settings = copy.deepcopy(TempEntityClass.entity_settings)
    entity_settings["list_filters"] = entity_settings["list_filters"] + ["filter_corruptible"]

    @classmethod
    def get_entity_list_filter(cls):

        from apis_core.apis_entities.filters import GenericEntityListFilter

        class HeroListFilter(GenericEntityListFilter):

            filter_corruptible = django_filters.BooleanFilter(method="filter_corruptible_method", label="is corruptible?")

            class Meta(GenericEntityListFilter.Meta):

                model = cls

            def filter_corruptible_method(self, queryset, name, value):

                if value is False:

                    return queryset.filter(name="Sam")

                else:

                    return queryset.filter(~Q(name="Sam"))

        return HeroListFilter



@reversion.register(follow=["tempentityclass_ptr"])
class Land(TempEntityClass):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class City(TempEntityClass):

    pass


# TODO RDF : Make this proper
# Either find a way to integrate this function and its produced instances into migrations
# Or change the property class from needing to produce instances to use the classes themselves (and their contenttypes)
def construct_properties():

    from apis_core.apis_relations.models import Property, TempTriple
    from apis_core.apis_metainfo.models import Text, RootObject
    from apis_core.apis_vocabularies.models import TextType, VocabsBaseClass

    TempTriple.objects.all().delete()
    Property.objects.all().delete()
    Race.objects.all().delete()
    Hero.objects.all().delete()
    Land.objects.all().delete()
    City.objects.all().delete()

    man = Race.objects.create(name="man", allied_with_sauron=False)
    hobbits = Race.objects.create(name="hobbits", allied_with_sauron=False)
    elves = Race.objects.create(name="elves", allied_with_sauron=False)
    orcs = Race.objects.create(name="orcs", allied_with_sauron=True)

    frodo = Hero.objects.create(name="Frodo", corruptible=True)
    sam = Hero.objects.create(name="Sam", corruptible=False)
    aragorn = Hero.objects.create(name="Aragorn", corruptible=True)
    gandalf = Hero.objects.create(name="Gandalf", corruptible=None)
    legolas = Hero.objects.create(name="Legolas", corruptible=True)

    the_shire = Land.objects.create(name="The Shire")
    mordor = Land.objects.create(name="Mordor")

    minas_tirith = City.objects.create(name="Minas Tirith")
    moria = City.objects.create(name="Moria")

    is_master_of = Property.objects.create(name="is master of", name_reverse="is servant of master")
    is_master_of.subj_class.add(ContentType.objects.get(model="Hero"))
    is_master_of.obj_class.add(ContentType.objects.get(model="Hero"))
    is_master_of.save()

    is_member_of = Property.objects.create(name="is member of", name_reverse="has member")
    is_member_of.subj_class.add(ContentType.objects.get(model="Hero"))
    is_member_of.obj_class.add(ContentType.objects.get(model="Race"))
    is_member_of.save()

    TempTriple.objects.create(subj=frodo, prop=is_member_of, obj=hobbits)
    TempTriple.objects.create(subj=sam, prop=is_member_of, obj=hobbits)
    TempTriple.objects.create(subj=aragorn, prop=is_member_of, obj=man)
    TempTriple.objects.create(subj=legolas, prop=is_member_of, obj=elves)

    was_birthplace_of = Property.objects.create(name="was birthplace of", name_reverse="was born in")
    was_birthplace_of.obj_class.add(ContentType.objects.get(model="Hero"))
    was_birthplace_of.subj_class.add(ContentType.objects.get(model="Land"))
    was_birthplace_of.subj_class.add(ContentType.objects.get(model="City"))
    was_birthplace_of.save()

    TempTriple.objects.create(subj=the_shire, prop=was_birthplace_of, obj=frodo)
    TempTriple.objects.create(subj=the_shire, prop=was_birthplace_of, obj=sam)

    fights_in = Property.objects.create(name="fights in", name_reverse="was fighting ground of")
    fights_in.subj_class.add(ContentType.objects.get(model="Hero"))
    fights_in.obj_class.add(ContentType.objects.get(model="Land"))
    fights_in.obj_class.add(ContentType.objects.get(model="City"))
    fights_in.save()

    TempTriple.objects.create(subj=frodo, prop=fights_in, obj=the_shire)
    TempTriple.objects.create(subj=frodo, prop=fights_in, obj=mordor)
    TempTriple.objects.create(subj=frodo, prop=fights_in, obj=moria)
    TempTriple.objects.create(subj=sam, prop=fights_in, obj=the_shire)
    TempTriple.objects.create(subj=sam, prop=fights_in, obj=mordor)
    TempTriple.objects.create(subj=sam, prop=fights_in, obj=moria)
    TempTriple.objects.create(subj=gandalf, prop=fights_in, obj=moria)
    TempTriple.objects.create(subj=gandalf, prop=fights_in, obj=minas_tirith)

