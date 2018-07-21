import datetime

from fp17 import treatments, exemptions


def annotate(bcds1):
    bcds1.patient.surname = "CAMPBELL"
    bcds1.patient.forename = "PAUL"
    bcds1.patient.address = ["39 HIGH STREET"]
    bcds1.patient.sex = 'M'
    bcds1.patient.date_of_birth = datetime.date(1970, 9, 1)

    bcds1.date_of_acceptance = datetime.date(2017, 4, 1)
    bcds1.date_of_completion = datetime.date(2017, 4, 1)

    # "Employment Support Allowance"
    bcds1.exemption_remission = {
        'code': exemptions.INCOME_RELATED_EMPLOYMENT_AND_SUPPORT_ALLOWANCE.EVIDENCE_SEEN,
    }

    # Treatments: "Extraction 1"
    bcds1.treatments = [
        treatments.TREATMENT_CATEGORY(2),
    ]

    return bcds1
