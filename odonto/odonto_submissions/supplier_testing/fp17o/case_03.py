import datetime
from odonto.odonto_submissions.serializers import translate_to_bdcs1
from fp17 import treatments, exemptions


def annotate(bcds1):
    bcds1.patient.surname = "IBSTOCK"
    bcds1.patient.forename = "WILLIAM"
    bcds1.patient.address = ["35 HIGH STREET"]
    bcds1.patient.sex = 'M'
    bcds1.patient.date_of_birth = datetime.date(2005, 1, 24)

    bcds1.date_of_acceptance = datetime.date(2019, 10, 12)
    bcds1.date_of_completion = datetime.date(2019, 10, 12)

    bcds1.exemption_remission = {
        'code': exemptions.PATIENT_UNDER_18.EVIDENCE_SEEN,
    }

    bcds1.treatments = [
        treatments.ETHNIC_ORIGIN_PATIENT_DECLINED,
        treatments.TREATMENT_ABANDONED,
        treatments.PATIENT_FAILED_TO_RETURN,
        treatments.RADIOGRAPHS(1),
        treatments.FIXED_UPPER_APPLIANCE,
        treatments.IOTN(0),
        treatments.DAY_OF_REFERRAL(9),
        treatments.MONTH_OF_REFERRAL(10),
        treatments.YEAR_OF_REFERRAL(19),
        treatments.ASSESS_AND_REVIEW
    ]

    return bcds1


def from_model(bcds1, patient, episode):
    demographics = patient.demographics()
    demographics.surname = "IBSTOCK"
    demographics.first_name = "WILLIAM"
    demographics.house_number_or_name = "35"
    demographics.street = "HIGH STREET"
    demographics.sex = "Male"
    demographics.ethnicity = "Patient declined"
    demographics.date_of_birth = datetime.date(2005, 1, 24)
    demographics.save()

    episode.fp17exemptions_set.update(
        patient_under_18=True,
        evidence_of_exception_or_remission_seen=True
    )

    episode.orthodonticassessment_set.update(
        assessment_and_review=True,
        date_of_referral=datetime.date(2019, 10, 9),
        date_of_assessment=datetime.date(2019, 10, 12),
    )
    episode.orthodonticdataset_set.update(
        fixed_upper_appliance=True,
        radiograph=1
    )

    episode.orthodontictreatment_set.update(
        patient_failed_to_return=True,
        date_of_completion=datetime.date(2019, 10, 12),
        iotn_not_applicable=True
    )

    translate_to_bdcs1(bcds1, episode)
