from django.db.models import Q


def name_filter(queryset, name, value):
    return queryset.filter(
        Q(id__icontains=value)
        | Q(name__icontains=value)
        | Q(alternative_names__icontains=value)
        | Q(external_link__endswith=value)
    )


def instance_name_filter(queryset, name, value):
    print("Name: %s, Value: %s", name, value)
    return queryset.filter(
        Q(id__icontains=value)
        | Q(name__icontains=value)
        | Q(alternative_names__icontains=value)
        | Q(tibschol_ref__icontains=value)
        | Q(external_link__endswith=value)
    )


def work_name_filter(queryset, name, value):
    return queryset.filter(
        Q(id__icontains=value)
        | Q(name__icontains=value)
        | Q(alternative_names__icontains=value)
        | Q(sde_dge_ref__icontains=value)
        | Q(external_link__endswith=value)
    )
