import datetime
from unittest import mock
from django.utils import timezone
from opal.core.test import OpalTestCase
from odonto.odonto_submissions.models import Submission
from odonto.episode_categories import FP17Episode


class FP17EpisodeTestCase(OpalTestCase):
    def setUp(self):
        self.yesterday = timezone.now() - datetime.timedelta(1)

    def get_episode(self):
        _, episode = self.new_patient_and_episode_please()
        episode.category_name = FP17Episode.display_name
        episode.stage = FP17Episode.SUBMITTED
        episode.save()
        return episode

    def get_submission(self, episode, state):
        mock_str = "odonto.odonto_submissions.models.serializers.\
translate_episode_to_xml"
        with mock.patch(mock_str) as m:
            m.return_value = ""
            submission = Submission.create(episode)
        submission.state = state
        submission.save()
        return submission

    def test_submission_none(self):
        episode = self.get_episode()
        self.assertIsNone(episode.category.submission())

    def test_submission_simple_success(self):
        episode = self.get_episode()
        submission = self.get_submission(episode, Submission.SUCCESS)
        self.assertEqual(episode.category.submission(), submission)

    def test_submission_correct_rejection(self):
        episode = self.get_episode()
        submission = self.get_submission(episode, Submission.REJECTED_BY_COMPASS)
        self.assertEqual(episode.category.submission(), submission)

    def test_submission_success_even_when_rejected(self):
        episode = self.get_episode()
        successful_submission = self.get_submission(episode, Submission.SUCCESS)
        successful_submission.created = self.yesterday
        successful_submission.save()

        self.get_submission(
            episode, Submission.REJECTED_BY_COMPASS
        )

        self.assertEqual(episode.category.submission(), successful_submission)

    def test_get_successful_episodes(self):
        successful_episode = self.get_episode()
        self.get_submission(successful_episode, Submission.SUCCESS)
        rejected_episode = self.get_episode()
        self.get_submission(rejected_episode, Submission.REJECTED_BY_COMPASS)
        self.assertEqual(
            FP17Episode.get_successful_episodes().get(), successful_episode
        )

    def test_get_successful_episodes_previously_rejected(self):
        episode = self.get_episode()
        rejected = self.get_submission(episode, Submission.REJECTED_BY_COMPASS)
        rejected.created = self.yesterday
        rejected.save()

        self.get_submission(episode, Submission.SUCCESS)
        self.assertEqual(FP17Episode.get_successful_episodes().get(), episode)

    def test_get_rejected_episodes(self):
        """
        Should ignore those have been rejected but have subsequently been
        successful
        """
        successful_episode = self.get_episode()
        self.get_submission(successful_episode, Submission.REJECTED_BY_COMPASS)
        self.get_submission(successful_episode, Submission.SUCCESS)

        rejected_episode = self.get_episode()
        self.get_submission(rejected_episode, Submission.REJECTED_BY_COMPASS)

        self.assertEqual(FP17Episode.get_rejected_episodes().get(), rejected_episode)

    def test_get_episodes_by_rejection_uses_last_rejection(self):
        rejected_episode = self.get_episode()
        rejected_submission = self.get_submission(
            rejected_episode, Submission.REJECTED_BY_COMPASS
        )
        rejected_submission.created = self.yesterday
        rejected_submission.rejection = "not this"
        rejected_submission.save()

        rejected_submission = self.get_submission(
            rejected_episode, Submission.REJECTED_BY_COMPASS
        )
        rejected_submission.rejection = "yes this"
        rejected_submission.save()

        rejection_to_episode = FP17Episode.get_episodes_by_rejection()

        self.assertEqual(len(rejection_to_episode.keys()), 1)

        self.assertEqual(rejection_to_episode["yes this"].get(), rejected_episode)

    def test_get_episodes_by_rejection_ignores_successful(self):
        rejected_episode = self.get_episode()
        rejected_submission = self.get_submission(
            rejected_episode, Submission.REJECTED_BY_COMPASS
        )
        rejected_submission.rejection = "boom"
        rejected_submission.save()

        successful_episode = self.get_episode()
        self.get_submission(
            successful_episode, Submission.SUCCESS
        )
        rejection_to_episode = FP17Episode.get_episodes_by_rejection()
        self.assertEqual(len(rejection_to_episode.keys()), 1)
        self.assertEqual(rejection_to_episode["boom"].get(), rejected_episode)

    def test_get_episodes_by_rejection_none(self):
        rejection_to_episode = FP17Episode.get_episodes_by_rejection()
        self.assertEqual(len(rejection_to_episode.keys()), 0)