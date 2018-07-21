import datetime

from fp17 import treatments


def annotate(bcds1):
    bcds1.patient.surname = "BROMSGROVE"
    bcds1.patient.forename = "GARY"
    bcds1.patient.address = ["15 HIGH STREET"]
    bcds1.patient.sex = 'M'
    bcds1.patient.date_of_birth = datetime.date(1970, 5, 27)

    bcds1.date_of_acceptance = datetime.date(2017, 4, 1)
    bcds1.date_of_completion = datetime.date(2017, 5, 1)

    bcds1.patient_charge_pence = 24430

    # Treatments: "Extraction x 2, Upper Denture Acrylic 2 teeth, Recall
    # Interval 8, Ethnic Origin 15"
    bcds1.treatments = [
        treatments.TREATMENT_CATEGORY(3),
        treatments.EXTRACTION(2),
        treatments.UPPER_DENTURE_ACRYLIC(2),
        treatments.RECALL_INTERVAL(8),
        treatments.ETHNIC_ORIGIN_15_CHINESE,
        treatments.SEDATION_SERVICES,
    ]

    return bcds1
