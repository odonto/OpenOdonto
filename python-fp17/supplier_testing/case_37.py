import datetime

from fp17 import treatments


def annotate(bcds1):
    bcds1.patient.surname = "ASTON"
    bcds1.patient.forename = "ZARA"
    bcds1.patient.address = ["33 HIGH STREET"]
    bcds1.patient.sex = 'F'
    bcds1.patient.date_of_birth = datetime.date(1960, 6, 26)

    bcds1.date_of_acceptance = datetime.date(2017, 4, 1)
    bcds1.date_of_completion = datetime.date(2017, 4, 1)

    bcds1.patient_charge_pence = 5630

    # Treatments: "Extraction x 1, Ethnic Origin 99"
    bcds1.treatments = [
        treatments.TREATMENT_CATEGORY(2),
        treatments.EXTRACTION(1),
        treatments.ETHNIC_ORIGIN_PATIENT_DECLINED,
    ]

    return bcds1
