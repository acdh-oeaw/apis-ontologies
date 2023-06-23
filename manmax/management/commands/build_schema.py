import json

from django.core.management.base import BaseCommand, CommandError
from apis_core.apis_entities.models import TempEntityClass


def build_hierarchy(cls):

    return [{subclass.__name__: build_hierarchy(subclass)} for subclass in cls.__subclasses__()]

class Command(BaseCommand):
    help = "Writes schema to a file"
    def handle(self, *args, **options):

        with open("schema.json", "w") as f:
            f.write(json.dumps(build_hierarchy(TempEntityClass)))


    
    
