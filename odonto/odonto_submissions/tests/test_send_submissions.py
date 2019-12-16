import datetime
from unittest.mock import patch
from django.test import override_settings
from opal.core.test import OpalTestCase
from opal.models import Episode
from odonto.episode_categories import FP17Episode, FP17OEpisode
from odonto.odonto_submissions.management.commands import send_submissions

BASE_STR = "odonto.odonto_submissions.management.commands.send_submissions"


@patch(BASE_STR + ".send_mail")
@patch(BASE_STR + ".models.Submission.send")
@patch(BASE_STR + ".render_to_string")
@patch(BASE_STR + ".logger")
class SendSubmissionEmailTestCase(OpalTestCase):
    """
    Tests the summary email that get's sent out of everything that
    has been sent downstream
    """
    def setUp(self):
        self.cmd = send_submissions.Command()
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.episode.stage = "Submitted"
        self.episode.save()
        self.today = datetime.date.today()
        self.yesterday = self.today - datetime.timedelta(1)

    def test_success_fp17(self, logger, render_to_string, send_submission, send_email):
        Episode.objects.update(category_name=FP17Episode.display_name)
        self.cmd.handle()
        ctx = render_to_string.call_args[0][1]
        self.assertFalse(ctx["threshold_breached"])
        self.assertEqual(ctx["total_success"], 1)
        self.assertEqual(ctx["total_failure"], 0)
        self.assertEqual(ctx["fp17_success_count"], 1)
        self.assertEqual(ctx["fp17_failure_count"], 0)
        self.assertEqual(ctx["fp17o_success_count"], 0)
        self.assertEqual(ctx["fp17o_failure_count"], 0)
        self.assertFalse(ctx["title"].startswith("Urgent"))

    def test_fail_fp17(self, logger, render_to_string, send_submission, send_email):
        send_submission.side_effect = ValueError("boom")
        Episode.objects.update(category_name=FP17Episode.display_name)
        self.cmd.handle()
        ctx = render_to_string.call_args[0][1]
        self.assertFalse(ctx["threshold_breached"])
        self.assertEqual(ctx["total_success"], 0)
        self.assertEqual(ctx["total_failure"], 1)
        self.assertEqual(ctx["fp17_success_count"], 0)
        self.assertEqual(ctx["fp17_failure_count"], 1)
        self.assertEqual(ctx["fp17o_success_count"], 0)
        self.assertEqual(ctx["fp17o_failure_count"], 0)

    def test_success_fp17o(self, logger, render_to_string, send_submission, send_email):
        self.episode.category_name = FP17OEpisode.display_name
        self.episode.save()
        self.patient.demographics_set.update(ethnicity_fk_id=1)
        self.episode.orthodonticassessment_set.update(
            date_of_referral=self.yesterday, date_of_assessment=self.today
        )
        Episode.objects.update(category_name=FP17OEpisode.display_name)
        self.cmd.handle()
        ctx = render_to_string.call_args[0][1]
        self.assertFalse(ctx["threshold_breached"])
        self.assertEqual(ctx["total_success"], 1)
        self.assertEqual(ctx["total_failure"], 0)
        self.assertEqual(ctx["fp17_success_count"], 0)
        self.assertEqual(ctx["fp17_failure_count"], 0)
        self.assertEqual(ctx["fp17o_success_count"], 1)
        self.assertEqual(ctx["fp17o_failure_count"], 0)

    def test_fail_fp17o(self, logger, render_to_string, send_submission, send_email):
        send_submission.side_effect = ValueError("boom")
        self.episode.category_name = FP17OEpisode.display_name
        self.episode.save()
        self.patient.demographics_set.update(ethnicity_fk_id=1)
        self.episode.orthodonticassessment_set.update(
            date_of_referral=self.yesterday, date_of_assessment=self.today
        )
        Episode.objects.update(category_name=FP17OEpisode.display_name)
        self.cmd.handle()
        ctx = render_to_string.call_args[0][1]
        self.assertFalse(ctx["threshold_breached"])
        self.assertEqual(ctx["total_success"], 0)
        self.assertEqual(ctx["total_failure"], 1)
        self.assertEqual(ctx["fp17_success_count"], 0)
        self.assertEqual(ctx["fp17_failure_count"], 0)
        self.assertEqual(ctx["fp17o_success_count"], 0)
        self.assertEqual(ctx["fp17o_failure_count"], 1)

    def test_ignores_some_fp17o(
        self, logger, render_to_string, send_submission, send_email
    ):
        send_submission.side_effect = ValueError("boom")
        self.episode.category_name = FP17OEpisode.display_name
        self.episode.save()
        self.patient.demographics_set.update(ethnicity_fk_id=1)
        Episode.objects.update(category_name=FP17OEpisode.display_name)
        extract_chart = self.episode.extractionchart_set.get()
        extract_chart.ur_1 = True
        extract_chart.save()
        self.cmd.handle()
        ctx = render_to_string.call_args[0][1]
        self.assertFalse(ctx["threshold_breached"])
        self.assertEqual(ctx["total_success"], 0)
        self.assertEqual(ctx["total_failure"], 0)
        self.assertEqual(ctx["fp17_success_count"], 0)
        self.assertEqual(ctx["fp17_failure_count"], 0)
        self.assertEqual(ctx["fp17o_success_count"], 0)
        self.assertEqual(ctx["fp17o_failure_count"], 0)

    @override_settings(FAILED_TO_SEND_WARNING_THRESHOLD=0)
    def test_threshold_breached(
        self, logger, render_to_string, send_submission, send_email
    ):
        send_submission.side_effect = ValueError("boom")
        Episode.objects.update(category_name=FP17Episode.display_name)
        self.cmd.handle()
        ctx = render_to_string.call_args[0][1]
        self.assertTrue(ctx["threshold_breached"])
        self.assertEqual(ctx["total_success"], 0)
        self.assertEqual(ctx["total_failure"], 1)
        self.assertEqual(ctx["fp17_success_count"], 0)
        self.assertEqual(ctx["fp17_failure_count"], 1)
        self.assertEqual(ctx["fp17o_success_count"], 0)
        self.assertEqual(ctx["fp17o_failure_count"], 0)
        self.assertTrue(ctx["title"].startswith("URGENT"))

    def test_none(self, logger, render_to_string, send_submission, send_email):
        Episode.objects.all().delete()
        self.assertIsNone(render_to_string.call_args)


class SendSubmissionGetQSTestCase(OpalTestCase):
    """
    Tests that the correct episodes are being sent downstream
    """
    def setUp(self):
        self.cmd = send_submissions.Command()
        self.patient, self.fp17_episode = self.new_patient_and_episode_please()
        today = datetime.date.today()

        # an fp17 episode ready to be submitted
        self.fp17_episode.stage = FP17Episode.SUBMITTED
        self.fp17_episode.category_name = FP17Episode.display_name
        self.fp17_episode.save()

        # an fp17o episode ready to be submitted
        self.fp17o_episode = self.patient.create_episode()
        self.fp17o_episode.stage = FP17OEpisode.SUBMITTED
        self.fp17o_episode.category_name = FP17OEpisode.display_name
        self.fp17o_episode.save()
        self.fp17o_episode.patient.demographics_set.update(
            ethnicity_fk_id=1
        )
        self.fp17o_episode.orthodonticassessment_set.update(
            date_of_assessment=today,
            date_of_referral=today
        )
        self.fp17o_episode.orthodontictreatment_set.update(
            date_of_completion=None
        )

    def test_get_fp17os_success(self):
        self.assertEqual(
            self.cmd.get_fp17os()[0],
            self.fp17o_episode
        )

    def test_get_fp17os_category(self):
        self.fp17o_episode.category_name = FP17Episode.display_name
        self.fp17o_episode.save()
        self.assertEqual(len(self.cmd.get_fp17os()), False)

    def test_get_fp17os_submitted(self):
        self.fp17o_episode.stage = FP17OEpisode.OPEN
        self.fp17o_episode.save()
        self.assertEqual(len(self.cmd.get_fp17os()), False)

    def test_get_fp17oswith_submissions(self):
        self.fp17o_episode.submission_set.create()
        self.assertEqual(len(self.cmd.get_fp17os()), False)

    def test_get_fp17os_with_extractions(self):
        extract_chart = self.fp17o_episode.extractionchart_set.get()
        extract_chart.ur_1 = True
        extract_chart.save()

        self.assertEqual(len(self.cmd.get_fp17os()), False)

    def test_get_fp17_qs_success(self):
        self.assertEqual(
            self.cmd.get_fp17_qs().get(),
            self.fp17_episode
        )

    def test_get_fp17_qs_category(self):
        self.fp17_episode.category_name = FP17OEpisode.display_name
        self.fp17_episode.save()
        self.assertFalse(self.cmd.get_fp17_qs().exists())

    def test_get_fp17_qs_submitted(self):
        self.fp17_episode.stage = FP17OEpisode.OPEN
        self.fp17_episode.save()
        self.assertFalse(self.cmd.get_fp17_qs().exists())

    def test_get_fp17_qs_with_submissions(self):
        self.fp17_episode.submission_set.create()
        self.assertFalse(self.cmd.get_fp17_qs().exists())

