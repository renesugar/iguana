"""
Iguana (c) by Marc Ammon, Moritz Fickenscher, Lukas Fridolin,
Michael Gunselmann, Katrin Raab, Christian Strate

Iguana is licensed under a
Creative Commons Attribution-ShareAlike 4.0 International License.

You should have received a copy of the license along with this
work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
"""
from lib.selenium_test_case import StaticSeleniumTestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

username = 'django'
email = 'django@example.com'
pw = 'unchained'


class LoginTest(StaticSeleniumTestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username, email, pw)

    def test_login(self):
        self.selenium.get('{}{}'.format(self.live_server_url, reverse('login')))
        login_form = self.selenium.find_element_by_id("id_login_form")

        login_form.find_element_by_id("id_username").send_keys(username)
        login_form.find_element_by_id("id_password").send_keys(pw)
        login_form.find_element_by_id('id_submit_login').click()
        self.assertEqual(self.selenium.title, 'Dashboard')

    def test_login_as_user_with_email(self):
        self.selenium.get('{}{}'.format(self.live_server_url, reverse('login')))
        login_form = self.selenium.find_element_by_id("id_login_form")

        login_form.find_element_by_id("id_username").send_keys(email)
        login_form.find_element_by_id("id_password").send_keys(pw)
        login_form.find_element_by_id('id_submit_login').click()
        self.assertEqual(self.selenium.title, 'Dashboard')

    def test_redirect_to_home_from_login_while_already_logged_in(self):
        self.selenium.get('{}{}'.format(self.live_server_url, reverse('login')))
        login_form = self.selenium.find_element_by_id("id_login_form")
        login_form.find_element_by_id("id_username").send_keys(email)
        login_form.find_element_by_id("id_password").send_keys(pw)
        self.selenium.find_element_by_id('id_login_form').find_element_by_id('id_submit_login').click()
        self.assertEqual(self.selenium.title, 'Dashboard')

        self.selenium.get('{}{}'.format(self.live_server_url, reverse('login')))
        self.assertEqual(self.selenium.title, 'Home')

    def test_buttons(self):
        self.selenium.get('{}{}'.format(self.live_server_url, reverse('login')))
        self.selenium.find_element_by_id("id_lost_password_ref").click()
        self.assertEqual(self.selenium.title, 'Password Reset')

        self.selenium.get('{}{}'.format(self.live_server_url, reverse('login')))
        self.selenium.find_element_by_id("id_not_yet_a_member_ref").click()
        self.assertEqual(self.selenium.title, 'Sign Up')
