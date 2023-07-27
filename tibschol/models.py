import reversion
from apis_core.apis_entities.models import TempEntityClass
from django.db import models
import logging

logger = logging.getLogger(__name__)


@reversion.register(follow=["tempentityclass_ptr"])
class Instance(TempEntityClass):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Instance"
    SETS = [
        ("Set 1", "Set 1"),
        ("Set 2", "Set 2"),
        ("Set 3", "Set 3"),
        ("Set 4", "Set 4"),
    ]
    set_num = models.CharField(
        max_length=5, choices=SETS, null=True, blank=True, verbose_name="Set"
    )
    volume = models.CharField(max_length=255, blank=True, null=True)
    sb_text_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Number ascribed to item by Tibschol",
    )
    pp_kdsb = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Page numbers in print",
    )
    num_folios = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Number of folios"
    )

    signature_letter = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Signature letter (category)",
    )
    signature_number = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Signature number"
    )
    drepung_number = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Drepung catalogue number"
    )
    provenance = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Provenance"
    )
    comments = models.TextField(blank=True, null=True)
    external_link = models.CharField(max_length=255, blank=True, null=True)

    @property
    def citation(self):
        if self.set_num == "Set 1":
            return f"bKa' gdams gsung ‘bum phyogs bsgrigs theng dang po, vol. {self.volume}, dPal brtsegs bod yig dpe rnying zhib 'jug khang [dPe sgrig 'gan 'khur ba: dByang can lha mo et al.], Chengdu [khreng tu’u]: Si khron mi rigs dpe skrun khang, 2006, pp. {self.pp_kdsb}."

        if self.set_num == "Set 2":
            return f"bKa' gdams gsung ‘bum phyogs bsgrigs theng gnyis pa, vol. {self.volume}, dPal brtsegs bod yig dpe rnying zhib 'jug khang [dPe sgrig 'gan 'khur ba: dByang can lha mo et al.], Chengdu [khreng tu’u]: Si khron mi rigs dpe skrun khang, 2007, pp. {self.pp_kdsb}."

        if self.set_num == "Set 3":
            return f"bKa' gdams gsung ‘bum phyogs bsgrigs theng gsum pa, vol. {self.volume}, dPal brtsegs bod yig dpe rnying zhib 'jug khang [dPe sgrig 'gan 'khur ba: dByang can lha mo et al.], Chengdu [khreng tu’u]: Si khron mi rigs dpe skrun khang, 2009, pp. {self.pp_kdsb}."

        if self.set_num == "Set 4":
            return f"bKa' gdams gsung ‘bum phyogs bsgrigs thengs bzhi pa, vol. {self.volume}, dPal brtsegs bod yig dpe rnying zhib 'jug khang [dPe sgrig 'gan 'khur ba: dByang can lha mo et al.], Chengdu [khreng tu’u]: Si khron mi rigs dpe skrun khang, 2015, pp. {self.pp_kdsb}."

        logger.warn(f"Unknown {self.set_num}. Cannot build citation.")
        return f"Unknown {self.set_num}. Cannot build citation."


@reversion.register(follow=["tempentityclass_ptr"])
class Person(TempEntityClass):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Person"
    GENDERS = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    gender = models.CharField(max_length=6, choices=GENDERS, default="male")
    comments = models.TextField(blank=True, null=True)
    external_link = models.CharField(max_length=255, blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Work(TempEntityClass):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Work"
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="subject",
    )  # should be a controlled vocabulary field
    comments = models.TextField(blank=True, null=True)
    external_link = models.CharField(max_length=255, blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Place(TempEntityClass):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Place"
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )
    external_link = models.CharField(max_length=255, blank=True, null=True)
