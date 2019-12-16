import datetime
from odonto.odonto_submissions.serializers import translate_to_bdcs1
from odonto import models
from fp17 import treatments, exemptions


def annotate(bcds1):
    bcds1.patient.surname = "IBSTOCK"
    bcds1.patient.forename = "WILLIAM"
    bcds1.patient.address = ["35 HIGH STREET"]
    bcds1.patient.sex = 'M'
    bcds1.patient.date_of_birth = datetime.date(1974, 10, 15)

    bcds1.date_of_acceptance = datetime.date(2019, 10, 12)

    bcds1.exemption_remission = {
        'code': exemptions.EXPECTANT_MOTHER.EVIDENCE_SEEN,
    }

    bcds1.treatments = [
        treatments.ETHNIC_ORIGIN_PATIENT_DECLINED,
        treatments.ASSESS_AND_REVIEW,
        treatments.RADIOGRAPHS(3),
        treatments.ORTHODONTIC_EXTRACTIONS(54),
        treatments.ORTHODONTIC_EXTRACTIONS(45),
        treatments.DAY_OF_REFERRAL(11),
        treatments.MONTH_OF_REFERRAL(10),
        treatments.YEAR_OF_REFERRAL(19),
        treatments.IOTN(0),
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
    demographics.date_of_birth = datetime.date(1974, 10, 15)
    demographics.save()

    episode.fp17exemptions_set.update(
        expectant_mother=True,
        evidence_of_exception_or_remission_seen=True
    )

    episode.orthodonticdataset_set.update(
        radiograph=3
    )

    episode.extractionchart_set.update(
        ur_d=True,
        lr_5=True
    )

    date_of_referral = datetime.date(2019, 10, 11)
    date_of_assessment = datetime.date(2019, 10, 12)
    episode.orthodonticassessment_set.update(
        date_of_referral=date_of_referral,
        date_of_assessment=date_of_assessment,
        assessment=models.OrthodonticAssessment.ASSESSMENT_AND_REVIEW,
        iotn_not_applicable=True
    )

    translate_to_bdcs1(bcds1, episode)
