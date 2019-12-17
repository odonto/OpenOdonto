import datetime
from odonto import models
from odonto.odonto_submissions.serializers import translate_to_bdcs1
from fp17 import treatments


def annotate(bcds1):
    bcds1.patient.surname = "BURTON"
    bcds1.patient.forename = "TANIA"
    bcds1.patient.address = ["19 HIGH STREET"]
    bcds1.patient.sex = 'F'
    bcds1.patient.date_of_birth = datetime.date(1950, 8, 16)

    bcds1.date_of_acceptance = datetime.date(2017, 4, 1)
    bcds1.date_of_completion = datetime.date(2017, 4, 1)

    # Treatments: "Ethnic Origin 2"
    bcds1.treatments = [
        treatments.DENTURE_REPAIRS,
        treatments.ETHNIC_ORIGIN_2_WHITE_IRISH,
    ]

    return bcds1


def from_model(bcds1, patient, episode):
    demographics = patient.demographics()
    demographics.surname = "BURTON"
    demographics.first_name = "TANIA"
    demographics.house_number_or_name = "19"
    demographics.street = "HIGH STREET"
    demographics.sex = "Female"
    demographics.date_of_birth = datetime.date(1950, 8, 16)
    demographics.ethnicity = "White irish"
    demographics.save()

    episode.fp17treatmentcategory_set.update(
        treatment_category=models.Fp17TreatmentCategory.DENTURE_REPAIRS
    )

    episode.fp17incompletetreatment_set.update(
        date_of_acceptance=datetime.date(2017, 4, 1),
        completion_or_last_visit=datetime.date(2017, 4, 1)
    )

    translate_to_bdcs1(bcds1, episode)
