import datetime

from fp17 import treatments, exemptions


def annotate(bcds1):
    bcds1.patient.surname = "BARROW"
    bcds1.patient.forename = "CHARLIE"
    bcds1.patient.address = ["3 HIGH STREET"]
    bcds1.patient.sex = 'M'
    bcds1.patient.date_of_birth = datetime.date(2001, 1, 24)

    bcds1.date_of_acceptance = datetime.date(2017, 4, 1)
    bcds1.date_of_completion = datetime.date(2017, 5, 1)

    # "Under 18"
    bcds1.exemption_remission = {
        'code': exemptions.PATIENT_UNDER_18.EVIDENCE_SEEN,
    }

    # Treatments: "Radiographs x 2, Crown x 1, Filled Deciduous 2, Ethnic Origin 3"
    bcds1.treatments = [
        treatments.TREATMENT_CATEGORY(3),
        treatments.RADIOGRAPHS(2),
        treatments.CROWN(1),
        treatments.FILLED_TEETH_DECIDUOUS(2),
        treatments.ETHNIC_ORIGIN_3_WHITE_OTHER,
    ]

    return bcds1

