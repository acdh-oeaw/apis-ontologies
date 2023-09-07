from apis_ontology.models import Instance, Work
from apis_core.apis_vocabularies.models import LabelType
from apis_core.apis_labels.models import Label


def run():
    label_types = ["Sanskrit title", "sDe dge ref", "Ref Nr"]
    for lt in label_types:
        labels = Label.objects.filter(label_type=LabelType.objects.get(name=lt))
        for label_object in labels:
            entity = label_object.temp_entity
            print(lt)
            if lt == "Sanskrit title":
                work = Work.objects.get(id=entity.id)
                work.alternative_names = (
                    (work.alternative_names if work.alternative_names else "")
                    + "\n"
                    + label_object.label
                ).strip()
                work.save()
                label_object.delete()
            elif lt == "sDe dge ref":
                work = Work.objects.get(id=entity.id)
                work.sde_dge_ref = label_object.label
                work.save()
                label_object.delete()
            elif lt == "Ref Nr":
                instance = Instance.objects.get(id=entity.id)
                instance.tibschol_ref = label_object.label
                instance.save()
                label_object.delete()
