"""
Iguana (c) by Marc Ammon, Moritz Fickenscher, Lukas Fridolin,
Michael Gunselmann, Katrin Raab, Christian Strate

Iguana is licensed under a
Creative Commons Attribution-ShareAlike 4.0 International License.

You should have received a copy of the license along with this
work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
"""
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from project.models import Project
from issue.models import Issue
from kanbancol.models import KanbanColumn
from timelog.validators import date_is_present_or_past, logged_time_is_positive
from django.contrib.auth import get_user_model


class ValidatorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # NOTE: if you modify those element they need to be created in setUp, instead of here
        cls.user = get_user_model().objects.create_user('test', 'test@testing.com', 'test1234')
        cls.project = Project(creator=cls.user, name_short='PRJ')
        cls.project.save()
        cls.project.developer.add(cls.user)
        cls.kanbancol = KanbanColumn(project=cls.project, position=4, name='test')
        cls.kanbancol.save()

    def setUp(self):
        self.client.force_login(self.user)
        # NOTE: this element gets modified by some of those tests, so this shall NOT be created in setUpTestData()
        self.issue = Issue(project=self.project, due_date='2016-12-16', kanbancol=self.kanbancol, storypoints='3')
        self.issue.save()
        self.time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    def test_date_is_present_or_past(self):
        valid_testobjs = {
            'datetime-today': timezone.now(),
            'datetime-past': timezone.now() - timedelta(days=1),
        }

        for obj in valid_testobjs:
            date_is_present_or_past(valid_testobjs[obj])

        invalid_testobjs = {
            'datetime-future': timezone.now() + timedelta(days=1),
            'invalid-object': self,
        }

        for obj in invalid_testobjs:
            self.assertRaises(ValidationError, date_is_present_or_past, invalid_testobjs[obj])

    def test_logged_time_is_positive(self):
        valid_testobjs = {
            'timedelta-positive': timedelta(days=1),
            'timedelta-positive2': timedelta(minutes=1)
                    }
        for obj in valid_testobjs:
            logged_time_is_positive(valid_testobjs[obj])

        invalid_testobjs = {
            'timedelta-negative': timedelta(),
            'timedelta-negative2': timedelta(minutes=-1),
            'invalid-object': self
        }

        for obj in invalid_testobjs:
            self.assertRaises(ValidationError, logged_time_is_positive, invalid_testobjs[obj])

    def test_logtime_time_syntax(self):
        valid = ['1d3h5m', '1d3h', '1d5m', '1d',
                 '2h15m', '3h', '10m',
                 '1d 3h 5m', '1d 3h', '1d 5m',
                 '2h 15m', '0d0h1m']

        invalid = ['asd', '12', '3h5', '1d  5h',
                   '3h1d5m', '5m1h', '3h 1d 5m',
                   '5m 1h', '3hm']
        invalid_not_positive = ['0d', '0h', '0m',
                                '0d0h0m', '0h0m', '0d0m']

        for v in valid:
            response = self.client.post(reverse('timelog:loginfo'),
                                        {'time': v, 'created_at': self.time, 'issue': self.issue.id},
                                        follow=True)
            self.assertNotContains(response, "Invalid time syntax" or "The logged time must be at least one minute")

        for v in invalid:
            response = self.client.post(reverse('timelog:loginfo'),
                                        {'time': v, 'created_at': self.time, 'issue': self.issue.id},
                                        follow=True)
            self.assertContains(response, "Invalid time syntax")

        for v in invalid_not_positive:
            response = self.client.post(reverse('timelog:loginfo'),
                                        {'time': v, 'created_at': self.time, 'issue': self.issue.id},
                                        follow=True)
            self.assertContains(response, "The logged time must be at least one minute")
