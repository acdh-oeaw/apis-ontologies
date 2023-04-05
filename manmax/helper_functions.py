import re
from typing import Iterable

from django.contrib.contenttypes.models import ContentType

from apis_core.helper_functions import caching


# Regex and function for removing double spaces
EXTRA_SPACE_REGEX = re.compile(r"\s+")


def remove_extra_spaces(string):
    return re.sub(EXTRA_SPACE_REGEX, " ", string)


class PropertyDeclaration:
    instances = {}

    def __init__(self, name_reverse: str, object_classes: Iterable[str]):

        self.name_reverse = name_reverse
        self.object_classes = object_classes

    def __set_name__(self, subject_class, subject_attribute_name):
        self.name = subject_attribute_name.replace("_", " ")
        self.subject_class = subject_class

        if (self.name, self.name_reverse) not in self.__class__.instances:
            self.__class__.instances[(self.name, self.name_reverse)] = {
                "subj_classes": set([subject_class]),
                "obj_classes": set(self.object_classes),
            }
        else:
            self.__class__.instances[(self.name, self.name_reverse)][
                "subj_classes"
            ].add(subject_class)
            self.__class__.instances[(self.name, self.name_reverse)][
                "obj_classes"
            ].union(self.object_classes)

        delattr(subject_class, subject_attribute_name)

    @classmethod
    def create_relationships(cls):
        from apis_core.apis_relations.models import Property

        for prop_name, prop_classes in cls.instances.items():

            subj_classes = set(prop_classes["subj_classes"])
            obj_classes_names = prop_classes["obj_classes"]

            for subj_class in prop_classes["subj_classes"]:
                if "Mixin" in subj_class.__name__:
                    subj_classes.remove(subj_class)
                    subj_classes.update(subj_class.__subclasses__())

            name, name_reverse = prop_name

            prop = Property.objects.get_or_create(
                name=name,
                name_reverse=name_reverse,
            )[0]
            prop.subj_class.clear()
            for subj in subj_classes:
                prop.subj_class.add(ContentType.objects.get(model=subj))
            prop.obj_class.clear()

            for obj in obj_classes:
                prop.obj_class.add(ContentType.objects.get(model=obj))
