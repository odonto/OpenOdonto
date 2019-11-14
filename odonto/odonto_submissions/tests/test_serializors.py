from opal.core.test import OpalTestCase
import datetime
from django.utils import timezone
from django.utils.module_loading import import_string
from fp17 import bcds1 as message
from fp17 import treatments as t
from fp17.envelope import Envelope
from odonto.odonto_submissions import serializers
from odonto import episode_categories
from opal import models as opal_models
from lxml import etree


BASE_CASE_PATH = "odonto.odonto_submissions.supplier_testing.{}.case_{:02d}"
FROM_MESSAGE = "{}.annotate".format(BASE_CASE_PATH)
FROM_MODEL = "{}.from_model".format(BASE_CASE_PATH)


def generate_bcds1():
    contract_number = 1000000000
    performer_number = 100000
    location_id = 4
    pin = "100000"
    start_claim_number = 7

    bcds1 = message.BCDS1()
    bcds1.message_reference_number = start_claim_number
    bcds1.performer_number = performer_number
    bcds1.dpb_pin = pin
    bcds1.contract_number = contract_number
    bcds1.location = location_id
    bcds1.patient = message.Patient()
    return bcds1


def generate_envelope():
    site_number = "site_number"
    serial_number = 1

    envelope = Envelope()
    envelope.origin = site_number
    envelope.destination = "1234"
    envelope.approval_number = 1
    envelope.release_timestamp = datetime.datetime(2019, 1, 2, 10, 30)
    envelope.test = True
    envelope.serial_number = serial_number
    return envelope


def get_from_message_method(category_name, number):
    category_name = category_name.lower()
    return import_string(FROM_MESSAGE.format(category_name, number))


def get_from_model_method(category_name, number):
    category_name = category_name.lower()
    return import_string(FROM_MODEL.format(category_name, number))


def from_message(number, category_name):
    bcds1 = generate_bcds1()
    envelope = generate_envelope()
    from_message_method = get_from_message_method(category_name, number)
    from_message_method(bcds1)
    envelope.add_message(bcds1)
    assert not bcds1.get_errors(), bcds1.get_errors()
    assert not envelope.get_errors(), envelope.get_errors()
    root = envelope.generate_xml()
    Envelope.validate_xml(root)
    return etree.tostring(root, encoding="unicode", pretty_print=True).strip()


def from_model(number, category_name):
    patient = opal_models.Patient.objects.create()
    episode = patient.create_episode()
    episode.fp17dentalcareprovider_set.update(provider_location_number="site_number")
    episode.category_name = category_name
    bcds1 = generate_bcds1()
    envelope = generate_envelope()
    from_model_method = get_from_model_method(category_name, number)
    from_model_method(bcds1, patient, episode)
    envelope.add_message(bcds1)
    assert not bcds1.get_errors(), bcds1.get_errors()
    assert not envelope.get_errors(), envelope.get_errors()
    root = envelope.generate_xml()
    Envelope.validate_xml(root)
    return etree.tostring(root, encoding="unicode", pretty_print=True).strip()


def get_treatments(some_xml):
    return set([etree.tostring(y).strip() for y in some_xml.findall(".//reptrtty")])


def equalise_treatments(old_xml, new_xml):
    new_treatments = get_treatments(new_xml)
    old_treatments = get_treatments(old_xml)
    if not new_treatments == old_treatments:
        new_difference = new_treatments.difference(old_treatments)
        print("Only in new {}".format(new_difference))
        old_difference = old_treatments.difference(new_treatments)
        print("Only in old {}".format(old_difference))
        return False
    return True


def equal(old, new):
    old_xml = etree.fromstring(old)
    new_xml = etree.fromstring(new)
    treatments_equal = equalise_treatments(old_xml, new_xml)
    if not treatments_equal:
        print("Old method")
        print(old_xml)
        print("=" * 20)
        print("New method")
        print(new_xml)
        print("=" * 20)
        return False
    old_xml.find(".//bcds1").remove(old_xml.find(".//tst"))
    new_xml.find(".//bcds1").remove(new_xml.find(".//tst"))
    result = etree.tostring(old_xml) == etree.tostring(new_xml)
    if not result:
        print("Old method")
        print(old)
        print("=" * 20)
        print("New method")
        print(new)
        print("=" * 20)
        # print("Equivalent {}".format(is_equal))
    return result


class SerializerTestCase(OpalTestCase):
    def test_cases(self):
        fp17_category = episode_categories.FP17Episode.display_name
        fp17o_category = episode_categories.FP17OEpisode.display_name
        for case_number in range(1, 46):
            new = from_model(case_number, fp17_category)
            old = from_message(case_number, fp17_category)
            self.assertTrue(equal(old, new))

        for case_number in range(1, 5):
            new = from_model(case_number, fp17o_category)
            old = from_message(case_number, fp17o_category)
            self.assertTrue(equal(old, new))

    def test_clean_non_alphanumeric(self):
        name = "Mc'Wilson-Smith-jones"
        self.assertEqual(serializers.clean_non_alphanumeric(name), "McWilsonSmithjones")


class OrthodonticAssessmentTranslatorTestCase(OpalTestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.yesterday = (timezone.now() - datetime.timedelta(1)).date()
        self.two_days_ago = (timezone.now() - datetime.timedelta(2)).date()

    def test_validate_no_exception(self):
        _, self.episode = self.new_patient_and_episode_please()
        orthodontic_assessment = self.episode.orthodonticassessment_set.get()

        orthodontic_assessment.assessment_and_review = True
        orthodontic_assessment.iotn = 4
        orthodontic_assessment.date_of_referral = self.two_days_ago
        orthodontic_assessment.date_of_assessment = self.yesterday
        orthodontic_assessment.date_of_appliance_fitted = self.today
        orthodontic_assessment.save()
        translator = serializers.OrthodonticAssessmentTranslator(self.episode)
        translator.validate()

    def test_validate_date_of_assessment_exception(self):
        _, self.episode = self.new_patient_and_episode_please()
        orthodontic_assessment = self.episode.orthodonticassessment_set.get()

        orthodontic_assessment.assessment_and_review = True
        orthodontic_assessment.iotn = 4
        orthodontic_assessment.date_of_referral = self.two_days_ago
        orthodontic_assessment.date_of_assessment = self.today
        orthodontic_assessment.date_of_appliance_fitted = self.yesterday
        orthodontic_assessment.save()
        translator = serializers.OrthodonticAssessmentTranslator(self.episode)
        with self.assertRaises(serializers.SerializerValidationError) as v:
            translator.validate()

        self.assertEqual(
            str(v.exception), "Date appliance fitted prior to date of assessment"
        )


class GetIotnTestCase(OpalTestCase):
    def setUp(self):
        _, self.episode = self.new_patient_and_episode_please()
        self.treatment = self.episode.orthodontictreatment_set.get()
        self.assessment = self.episode.orthodonticassessment_set.get()

    def test_get_iotn_the_same(self):
        self.treatment.iotn = 2
        self.treatment.save()
        self.assessment.iotn = 2
        self.assessment.save()
        result = serializers.get_iotn_treatment(self.episode)
        self.assertEqual(result, t.IOTN(2))

    def test_get_iotn_treatment_set(self):
        self.treatment.iotn = 2
        self.treatment.save()
        result = serializers.get_iotn_treatment(self.episode)
        self.assertEqual(result, t.IOTN(2))

    def test_get_iotn_assessment_set(self):
        self.assessment.iotn = 2
        self.assessment.save()
        result = serializers.get_iotn_treatment(self.episode)
        self.assertEqual(result, t.IOTN(2))

    def test_get_iotn_both_na(self):
        self.assessment.iotn_not_applicable = True
        self.assessment.save()
        self.treatment.iotn_not_applicable = True
        self.treatment.save()
        result = serializers.get_iotn_treatment(self.episode)
        self.assertEqual(result, t.IOTN(0))

    def test_get_iotn_one_na(self):
        self.assessment.iotn_not_applicable = True
        self.assessment.save()
        result = serializers.get_iotn_treatment(self.episode)
        self.assertEqual(result, t.IOTN(0))

    def test_get_iotn_different(self):
        self.treatment.iotn = 2
        self.treatment.save()
        self.assessment.iotn = 4
        self.assessment.save()
        with self.assertRaises(serializers.SerializerValidationError) as v:
            serializers.get_iotn_treatment(self.episode)
        self.assertEqual(
            str(v.exception), "Treatmeant IOTN does not equal Assessment IOTN"
        )

    def test_get_iotn_one_na_one_populated(self):
        self.treatment.iotn = 2
        self.treatment.save()
        self.assessment.iotn_not_applicable = True
        self.assessment.save()
        with self.assertRaises(serializers.SerializerValidationError) as v:
            serializers.get_iotn_treatment(self.episode)
        self.assertEqual(str(v.exception), "We should not have an IOTN and IOTN NA")

    def test_get_iotn_not_set(self):
        self.assertIsNone(serializers.get_iotn_treatment(self.episode))

    def test_iotn_3_and_no_aesthetic_component(self):
        self.treatment.iotn = 2
        self.treatment.aesthetic_component = 4
        self.treatment.save()
        with self.assertRaises(serializers.SerializerValidationError) as v:
            serializers.get_iotn_treatment(self.episode)
        self.assertEqual(
            str(v.exception),
            "If a value of 3 is present then the aesthetic component must be present",
        )


class GetAestheticComponentTestCase(OpalTestCase):
    def setUp(self):
        _, self.episode = self.new_patient_and_episode_please()
        self.treatment = self.episode.orthodontictreatment_set.get()
        self.assessment = self.episode.orthodonticassessment_set.get()

    def test_component_differs(self):
        self.treatment.aesthetic_component = 4
        self.treatment.save()

        self.assessment.aesthetic_component = 3
        self.assessment.save()

        with self.assertRaises(serializers.SerializerValidationError) as v:
            serializers.get_aesthetic_component(self.episode)
        self.assertEqual(
            str(v.exception),
            "treatment aesthetic component differs from assessment aesthetic component",
        )

    def test_component_same(self):
        self.treatment.aesthetic_component = 4
        self.treatment.save()

        self.assessment.aesthetic_component = 4
        self.assessment.save()
        self.assertEqual(
            serializers.get_aesthetic_component(self.episode),
            t.AESTHETIC_COMPONENT(4)
        )

    def test_component_only_set_on_one(self):
        self.treatment.aesthetic_component = 4
        self.treatment.save()
        self.assertEqual(
            serializers.get_aesthetic_component(self.episode),
            t.AESTHETIC_COMPONENT(4)
        )

    def test_component_not_set(self):
        self.assertIsNone(serializers.get_aesthetic_component(self.episode))
