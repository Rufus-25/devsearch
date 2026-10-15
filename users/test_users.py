"""Tests for the users app: profiles, authentication, skills and messages.

Put this file in the `users/` folder (next to models.py).
Run with:  python manage.py test users
"""
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Message, Profile, Skill

PASSWORD = 'Sup3r-Secret-Pass!'


def make_user(username, email=None):
    """Create a user. The post_save signal creates the matching Profile."""
    return User.objects.create_user(
        username=username,
        password=PASSWORD,
        email=email or f'{username}@example.com',
    )


class ProfileSignalTests(TestCase):
    def test_creating_a_user_creates_a_matching_profile(self):
        user = make_user('alice')

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.username, 'alice')
        self.assertEqual(profile.email, 'alice@example.com')

    def test_welcome_email_is_sent_on_signup(self):
        make_user('alice')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Welcome to DevSearch!')

    def test_profile_without_photo_uses_default_image(self):
        profile = make_user('alice').profile

        self.assertIn('images/user-default.png', profile.imageURL)


class LoginTests(TestCase):
    def setUp(self):
        make_user('alice')

    def test_wrong_password_shows_an_error_instead_of_crashing(self):
        response = self.client.post(
            reverse('login'), {'username': 'alice', 'password': 'wrong-password'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        flashed = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertIn('Username or password is incorrect', flashed)

    def test_successful_login_goes_to_account_page(self):
        # Usernames are lower-cased by the view, so mixed case still works.
        response = self.client.post(
            reverse('login'), {'username': 'ALICE', 'password': PASSWORD}
        )

        self.assertRedirects(
            response, reverse('account'), fetch_redirect_response=False
        )
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_follows_a_safe_next_url(self):
        url = reverse('login') + '?next=' + reverse('projects')

        response = self.client.post(url, {'username': 'alice', 'password': PASSWORD})

        self.assertRedirects(
            response, reverse('projects'), fetch_redirect_response=False
        )

    def test_login_ignores_an_external_next_url(self):
        url = reverse('login') + '?next=https://evil.example/steal'

        response = self.client.post(url, {'username': 'alice', 'password': PASSWORD})

        self.assertRedirects(
            response, reverse('account'), fetch_redirect_response=False
        )

    def test_account_page_requires_login(self):
        response = self.client.get(reverse('account'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('account')}",
            fetch_redirect_response=False,
        )


class SignUpTests(TestCase):
    def test_sign_up_creates_user_lowercases_username_and_logs_in(self):
        response = self.client.post(
            reverse('sign-up'),
            {
                'first_name': 'alice',
                'username': 'AliceDev',
                'email': 'alice@example.com',
                'password1': PASSWORD,
                'password2': PASSWORD,
            },
        )

        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
        user = User.objects.get(username='alicedev')
        self.assertEqual(user.first_name, 'Alice')
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_sign_up_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse('sign-up'),
            {
                'first_name': 'bob',
                'username': 'bob',
                'email': 'bob@example.com',
                'password1': PASSWORD,
                'password2': 'something-else-entirely',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='bob').exists())


class SkillOwnershipTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.other = make_user('other')
        self.skill = Skill.objects.create(owner=self.owner.profile, name='Django')

    def test_owner_can_delete_their_skill(self):
        self.client.login(username='owner', password=PASSWORD)

        response = self.client.post(reverse('delete-skill', args=[self.skill.id]))

        self.assertRedirects(
            response, reverse('account'), fetch_redirect_response=False
        )
        self.assertFalse(Skill.objects.filter(id=self.skill.id).exists())

    def test_other_user_cannot_delete_the_skill(self):
        self.client.login(username='other', password=PASSWORD)

        response = self.client.post(reverse('delete-skill', args=[self.skill.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Skill.objects.filter(id=self.skill.id).exists())

    def test_other_user_cannot_edit_the_skill(self):
        self.client.login(username='other', password=PASSWORD)

        response = self.client.post(
            reverse('update-skill', args=[self.skill.id]),
            {'name': 'Hacked', 'description': ''},
        )

        self.assertEqual(response.status_code, 404)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, 'Django')


class MessageAccessTests(TestCase):
    def setUp(self):
        self.sender = make_user('sender')
        self.recipient = make_user('recipient')
        self.stranger = make_user('stranger')
        self.message = Message.objects.create(
            sender=self.sender.profile,
            recipient=self.recipient.profile,
            name='Sender',
            email='sender@example.com',
            subject='Hello',
            body='Hi there',
        )

    def test_recipient_can_read_message_and_it_is_marked_read(self):
        self.client.login(username='recipient', password=PASSWORD)

        response = self.client.get(reverse('message', args=[self.message.id]))

        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)

    def test_sender_can_read_message_without_marking_it_read(self):
        self.client.login(username='sender', password=PASSWORD)

        response = self.client.get(reverse('message', args=[self.message.id]))

        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_read)

    def test_stranger_cannot_read_the_message(self):
        self.client.login(username='stranger', password=PASSWORD)

        response = self.client.get(reverse('message', args=[self.message.id]))

        self.assertEqual(response.status_code, 404)
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_read)

    def test_inbox_requires_login(self):
        response = self.client.get(reverse('inbox'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('inbox')}",
            fetch_redirect_response=False,
        )
