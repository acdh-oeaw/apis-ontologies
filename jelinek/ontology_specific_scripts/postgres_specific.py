from django.contrib.contenttypes.models import ContentType
import django.apps


def postgres_workaround_for_case_sensitive_contenttypes():
    all_classes = [c.__name__ for c in django.apps.apps.get_models()]
    for contenttype in ContentType.objects.all():
        related_class_name = [c for c in all_classes if str.lower(c) == contenttype.model]
        if (len(related_class_name) == 1):
            if (len(ContentType.objects.filter(model=related_class_name[0], app_label=contenttype.app_label)) <= 0): 
                contenttype.model = related_class_name[0]
                contenttype.save()
                print(contenttype.model, related_class_name)
            else:
                print(contenttype, " already exists")
        else:
            print("No model found for ", contenttype.model)

def run(*args, **options):
  
    def main_run():

        postgres_workaround_for_case_sensitive_contenttypes()

    main_run()