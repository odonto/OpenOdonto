import datetime

from fp17 import treatments, exemptions


def annotate(bcds1):
    bcds1.patient.surname = "CARSTAIRS"
    bcds1.patient.forename = "EMMA"
    bcds1.patient.address = ["38 HIGH STREET"]
    bcds1.patient.sex = 'F'
    bcds1.patient.date_of_birth = datetime.date(1990, 6, 21)

    bcds1.date_of_acceptance = datetime.date(2017, 4, 1)
    bcds1.date_of_completion = datetime.date(2017, 4, 1)

    # "Prisoner"
    bcds1.exemption_remission = {
        'code': exemptions.PRISONER,
    }

    # Treatments: "None"
    bcds1.treatments = [
        treatments.TREATMENT_CATEGORY(1),
    ]

    return bcds1
