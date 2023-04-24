from apis_ontology.models import *
from apis_core.apis_relations.models import Property, TempTriple, Triple

alltt = TempTriple.objects.all()
print(f"Converting {len(alltt)} temptriples")
converted = 0
# person_has_living_place -> PersonHasLivingPlace



prop = Property.objects.get(name="bewohnt", name_reverse="Bewohner von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person bewohnt place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonHasLivingPlace.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person bewohnt")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "bewohnt place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_owns_place -> PersonOwnsPlace



prop = Property.objects.get(name="besitzt", name_reverse="Besitzer von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person besitzt place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonOwnsPlace.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person besitzt")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "besitzt place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_is_working_in_place -> PersonIsWorkingInPlace



prop = Property.objects.get(name="ist tätig in", name_reverse="ist Tätigkeitsort von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person ist tätig in place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonIsWorkingInPlace.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person ist tätig in")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist tätig in place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_place_of_residence -> PersonPlaceOfResidence



prop = Property.objects.get(name="hält sich auf in", name_reverse="ist Aufenthaltsort von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person hält sich auf in place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonPlaceOfResidence.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person hält sich auf in")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "hält sich auf in place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_has_correspondance_with -> PersonHasCorrespondanceWith



prop = Property.objects.get(name="hat Korrespondenz mit", name_reverse="hat Korrespondenz mit")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person hat Korrespondenz mit person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonHasCorrespondanceWith.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person hat Korrespondenz mit")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "hat Korrespondenz mit person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_has_family_relation_with -> PersonHasFamilyRelationWith



prop = Property.objects.get(name="hat Familienbeziehung zu", name_reverse="hat Familienbeziehung zu")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person hat Familienbeziehung zu person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonHasFamilyRelationWith.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person hat Familienbeziehung zu")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "hat Familienbeziehung zu person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_is_father_of -> PersonIsFatherOf



prop = Property.objects.get(name="ist Elternteil von", name_reverse="ist Kind von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person ist Elternteil von person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonIsFatherOf.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person ist Elternteil von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist Elternteil von person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_is_brother_of -> PersonIsBrotherOf



prop = Property.objects.get(name="ist Bruder/Schwester von", name_reverse="ist Bruder/Schwester von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person ist Bruder/Schwester von person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonIsBrotherOf.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person ist Bruder/Schwester von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist Bruder/Schwester von person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_is_son_of -> PersonIsSonOf



prop = Property.objects.get(name="ist Kind von", name_reverse="ist Elternteil von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person ist Kind von person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonIsSonOf.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person ist Kind von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist Kind von person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_has_marrige_with -> PersonHasMarrigeWith



prop = Property.objects.get(name="hat Ehe mit", name_reverse="hat Ehe mit")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person hat Ehe mit person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonHasMarrigeWith.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person hat Ehe mit")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "hat Ehe mit person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_was_present_at_court -> PersonWasPresentAtCourt



prop = Property.objects.get(name="war anwesend bei", name_reverse="hatte anwesende Person")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Court")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person war anwesend bei court: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonWasPresentAtCourt.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person war anwesend bei")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "war anwesend bei court")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_recommended_person_for_court -> PersonRecommendedPersonForCourt



prop = Property.objects.get(name="empfahl", name_reverse="wurde empfohlen von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person empfahl person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonRecommendedPersonForCourt.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person empfahl")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "empfahl person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_had_business_realtionship_with_person -> PersonHadBusinessRealtionshipWithPerson



prop = Property.objects.get(name="hat Geschäftsbeziehung zu", name_reverse="hat Geschäftsbeziehung zu")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person hat Geschäftsbeziehung zu person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonHadBusinessRealtionshipWithPerson.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person hat Geschäftsbeziehung zu")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "hat Geschäftsbeziehung zu person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_is_custodian_of_person -> PersonIsCustodianOfPerson



prop = Property.objects.get(name="ist Vormund von", name_reverse="ist Mündel von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person ist Vormund von person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonIsCustodianOfPerson.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person ist Vormund von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist Vormund von person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_was_member_of_institution -> PersonWasMemberOfInstitution



prop = Property.objects.get(name="Mitglied von", name_reverse="hatte Mitglied")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Institution")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person Mitglied von institution: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonWasMemberOfInstitution.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person Mitglied von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "Mitglied von institution")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_was_active_in_institution -> PersonWasActiveInInstitution



prop = Property.objects.get(name="war tätig an", name_reverse="hatte tätige Person")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Institution")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person war tätig an institution: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonWasActiveInInstitution.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person war tätig an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "war tätig an institution")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_gets_pension_from_institution -> PersonGetsPensionFromInstitution



prop = Property.objects.get(name="ist Pfründner von", name_reverse="hat Pfründner")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Institution")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person ist Pfründner von institution: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonGetsPensionFromInstitution.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person ist Pfründner von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist Pfründner von institution")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_took_part_in_event -> PersonTookPartInEvent



prop = Property.objects.get(name="nahm teil an", name_reverse="hatte teilnehmende Person")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Event")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person nahm teil an event: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonTookPartInEvent.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person nahm teil an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "nahm teil an event")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_recieved_salary -> PersonRecievedSalary



prop = Property.objects.get(name="erhielt Gehalt", name_reverse="wurde ausbezahlt an")
subj = ContentType.objects.get(model="Salary")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"salary erhielt Gehalt person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonRecievedSalary.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "salary erhielt Gehalt")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "erhielt Gehalt person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_authorized_salary -> PersonAuthorizedSalary



prop = Property.objects.get(name="weist an", name_reverse="auf Anweisung von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Salary")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person weist an salary: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonAuthorizedSalary.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person weist an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "weist an salary")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_born_in -> PersonBornIn



prop = Property.objects.get(name="geboren in", name_reverse="Geburtsort von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person geboren in place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonBornIn.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person geboren in")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "geboren in place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_died_in -> PersonDiedIn



prop = Property.objects.get(name="gestorben in", name_reverse="Sterbeort von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person gestorben in place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonDiedIn.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person gestorben in")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "gestorben in place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_is_servant_of_person -> PersonIsServantOfPerson



prop = Property.objects.get(name="ist im Dienst von", name_reverse="hat Diener")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person ist im Dienst von person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonIsServantOfPerson.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person ist im Dienst von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist im Dienst von person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_has_hometown -> PersonHasHometown



prop = Property.objects.get(name="hat Heimatort in", name_reverse="Heimatort von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person hat Heimatort in place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonHasHometown.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person hat Heimatort in")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "hat Heimatort in place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_sells_property_to -> PersonSellsPropertyTo



prop = Property.objects.get(name="verkauft Besitz an", name_reverse="kauft Besitz von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person verkauft Besitz an person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonSellsPropertyTo.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person verkauft Besitz an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "verkauft Besitz an person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_has_dispute_with -> PersonHasDisputeWith



prop = Property.objects.get(name="hat Streit mit", name_reverse="hat Streit mit")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person hat Streit mit person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonHasDisputeWith.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person hat Streit mit")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "hat Streit mit person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_or_function_executes_salary -> PersonOrFunctionExecutesSalary



prop = Property.objects.get(name="führt durch", name_reverse="wird durchgeführt von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Salary")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person führt durch salary: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonOrFunctionExecutesSalary.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person führt durch")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "führt durch salary")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")



prop = Property.objects.get(name="führt durch", name_reverse="wird durchgeführt von")
subj = ContentType.objects.get(model="Function")
obj = ContentType.objects.get(model="Salary")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"function führt durch salary: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonOrFunctionExecutesSalary.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "function führt durch")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "führt durch salary")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_or_function_takes_salary -> PersonOrFunctionTakesSalary



prop = Property.objects.get(name="nimmt entgegen", name_reverse="wird entgegengenommen von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Salary")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person nimmt entgegen salary: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonOrFunctionTakesSalary.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person nimmt entgegen")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "nimmt entgegen salary")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")



prop = Property.objects.get(name="nimmt entgegen", name_reverse="wird entgegengenommen von")
subj = ContentType.objects.get(model="Function")
obj = ContentType.objects.get(model="Salary")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"function nimmt entgegen salary: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonOrFunctionTakesSalary.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "function nimmt entgegen")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "nimmt entgegen salary")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# person_vouchers_for_person -> PersonVouchersForPerson



prop = Property.objects.get(name="bürgt für", name_reverse="wird gebürgt von")
subj = ContentType.objects.get(model="Person")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"person bürgt für person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PersonVouchersForPerson.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "person bürgt für")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "bürgt für person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# function_is_located_at_institution -> FunctionIsLocatedAtInstitution



prop = Property.objects.get(name="ist an", name_reverse="hat Funktion")
subj = ContentType.objects.get(model="Function")
obj = ContentType.objects.get(model="Institution")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"function ist an institution: {len(temptriples)} occurences")
for tt in temptriples:
	reification = FunctionIsLocatedAtInstitution.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "function ist an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist an institution")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")

prop = Property.objects.get(name="ist an", name_reverse="hat Funktion")
subj = ContentType.objects.get(model="Function")
obj = ContentType.objects.get(model="Court")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"function ist an court: {len(temptriples)} occurences")
for tt in temptriples:
	reification = FunctionIsLocatedAtInstitution.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "function ist an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist an court")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# function_is_hold_by -> FunctionIsHoldBy



prop = Property.objects.get(name="wird bekleidet von", name_reverse="hat Funktion inne")
subj = ContentType.objects.get(model="Function")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"function wird bekleidet von person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = FunctionIsHoldBy.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "function wird bekleidet von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "wird bekleidet von person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# function_ging_hervor_aus -> FunctionGingHervorAus



prop = Property.objects.get(name="ging hervor aus", name_reverse="war Vorgänger von")
subj = ContentType.objects.get(model="Function")
obj = ContentType.objects.get(model="Function")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"function ging hervor aus function: {len(temptriples)} occurences")
for tt in temptriples:
	reification = FunctionGingHervorAus.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "function ging hervor aus")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ging hervor aus function")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# function_is_subordinary_of -> FunctionIsSubordinaryOf



prop = Property.objects.get(name="ist untergeordnet", name_reverse="hat untergeordnete Funktion")
subj = ContentType.objects.get(model="Function")
obj = ContentType.objects.get(model="Function")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"function ist untergeordnet function: {len(temptriples)} occurences")
for tt in temptriples:
	reification = FunctionIsSubordinaryOf.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "function ist untergeordnet")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist untergeordnet function")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# function_was_located_in -> FunctionWasLocatedIn



prop = Property.objects.get(name="ausgeübt in", name_reverse="war Ausübungsort von")
subj = ContentType.objects.get(model="Function")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"function ausgeübt in place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = FunctionWasLocatedIn.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "function ausgeübt in")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ausgeübt in place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# place_located_in_place -> PlaceLocatedInPlace



prop = Property.objects.get(name="Teil von", name_reverse="hat Teil")
subj = ContentType.objects.get(model="Place")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"place Teil von place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = PlaceLocatedInPlace.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "place Teil von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "Teil von place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# institution_paid_salary -> InstitutionPaidSalary



prop = Property.objects.get(name="zahlte aus", name_reverse="wurde ausbezahlt von")
subj = ContentType.objects.get(model="Institution")
obj = ContentType.objects.get(model="Salary")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"institution zahlte aus salary: {len(temptriples)} occurences")
for tt in temptriples:
	reification = InstitutionPaidSalary.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "institution zahlte aus")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "zahlte aus salary")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# institutionlocated_in -> InstitutionlocatedIn



prop = Property.objects.get(name="ist gelegen in", name_reverse="inkludiert")
subj = ContentType.objects.get(model="Institution")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"institution ist gelegen in place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = InstitutionlocatedIn.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "institution ist gelegen in")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist gelegen in place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# institution_given_in_mortage_to -> InstitutionGivenInMortageTo



prop = Property.objects.get(name="ist verpfändet an", name_reverse="hat als Pfand")
subj = ContentType.objects.get(model="Institution")
obj = ContentType.objects.get(model="Person")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"institution ist verpfändet an person: {len(temptriples)} occurences")
for tt in temptriples:
	reification = InstitutionGivenInMortageTo.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "institution ist verpfändet an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "ist verpfändet an person")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# institution_belongs_to_institution -> InstitutionBelongsToInstitution



prop = Property.objects.get(name="gehört zu", name_reverse="zuständig für")
subj = ContentType.objects.get(model="Institution")
obj = ContentType.objects.get(model="Institution")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"institution gehört zu institution: {len(temptriples)} occurences")
for tt in temptriples:
	reification = InstitutionBelongsToInstitution.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "institution gehört zu")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "gehört zu institution")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# institution_orders_salary -> InstitutionOrdersSalary



prop = Property.objects.get(name="weist an", name_reverse="angewiesen von")
subj = ContentType.objects.get(model="Institution")
obj = ContentType.objects.get(model="Salary")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"institution weist an salary: {len(temptriples)} occurences")
for tt in temptriples:
	reification = InstitutionOrdersSalary.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "institution weist an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "weist an salary")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# event_took_place_at -> EventTookPlaceAt



prop = Property.objects.get(name="fand statt in", name_reverse="inkludierte")
subj = ContentType.objects.get(model="Event")
obj = ContentType.objects.get(model="Place")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"event fand statt in place: {len(temptriples)} occurences")
for tt in temptriples:
	reification = EventTookPlaceAt.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "event fand statt in")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "fand statt in place")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# salary_paid_to -> SalaryPaidTo



prop = Property.objects.get(name="wurde ausbezahlt an", name_reverse="erhielt")
subj = ContentType.objects.get(model="Salary")
obj = ContentType.objects.get(model="Function")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"salary wurde ausbezahlt an function: {len(temptriples)} occurences")
for tt in temptriples:
	reification = SalaryPaidTo.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "salary wurde ausbezahlt an")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "wurde ausbezahlt an function")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")


# salary_ordered_by -> SalaryOrderedBy



prop = Property.objects.get(name="auf Anweisung von", name_reverse="wies an")
subj = ContentType.objects.get(model="Salary")
obj = ContentType.objects.get(model="Function")
temptriples = TempTriple.objects.filter(subj__self_contenttype=subj, obj__self_contenttype=obj, prop=prop)
print(f"salary auf Anweisung von function: {len(temptriples)} occurences")
for tt in temptriples:
	reification = SalaryOrderedBy.objects.create(
				start_date = tt.start_date,
				start_start_date = tt.start_start_date,
				start_end_date = tt.start_end_date,
				start_date_written = tt.start_date_written,
				end_date = tt.end_date,
				end_start_date = tt.end_start_date,
				end_end_date = tt.end_end_date,
				end_date_written = tt.end_date_written)
	propin = Property.objects.get(name = "salary auf Anweisung von")
	triple_in = Triple.objects.create(subj = tt.subj, obj = reification, prop = propin)
	propout = Property.objects.get(name = "auf Anweisung von function")
	triple_out = Triple.objects.create(subj = reification, obj = tt.obj, prop = propout)
converted += len(temptriples)
percentage = 100 * float(converted) / float(len(alltt))
print(f"{percentage:.4f}%")



