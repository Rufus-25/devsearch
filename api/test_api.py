"""Tests for the REST API: public reads, privacy, voting and JWT tokens.

Put this file in the `api/` folder (next to views.py).
Run with:  python manage.py test api
"""
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from projects.models import Project, Review

PASSWORD = 'Sup3r-Secret-Pass!'


def make_user(username):
    """Create a user. The post_save signal creates the matching Profile."""
    return User.objects.create_user(
        username=username, password=PASSWORD, email=f'{username}@example.com'
    )


class ProjectReadTests(APITestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.project = Project.objects.create(
            owner=self.owner.profile, title='Demo Project'
        )

    def test_project_list_is_public(self):
        response = self.client.get('/api/projects/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Demo Project')

    def test_single_project_is_public(self):
        response = self.client.get(f'/api/projects/{self.project.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Demo Project')

    def test_owner_email_is_not_exposed(self):
        response = self.client.get('/api/projects/')

        owner = response.data[0]['owner']
        self.assertEqual(
            set(owner.keys()), {'id', 'name', 'headline', 'profile_image'}
        )
        self.assertNotIn('email', owner)


class VoteTests(APITestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.voter = make_user('voter')
        self.second_voter = make_user('voter2')
        self.project = Project.objects.create(
            owner=self.owner.profile, title='Demo Project'
        )
        self.url = f'/api/projects/{self.project.id}/vote/'

    def test_voting_requires_authentication(self):
        response = self.client.post(self.url, {'value': 'up'}, format='json')

        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(Review.objects.count(), 0)

    def test_vote_updates_the_project_totals(self):
        self.client.force_authenticate(user=self.voter)
        response = self.client.post(self.url, {'value': 'up'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.total_vote, 1)
        self.assertEqual(self.project.vote_ratio, 100)

        self.client.force_authenticate(user=self.second_voter)
        self.client.post(self.url, {'value': 'down'}, format='json')

        self.project.refresh_from_db()
        self.assertEqual(self.project.total_vote, 2)
        self.assertEqual(self.project.vote_ratio, 50)

    def test_voting_twice_changes_the_vote_instead_of_adding_another(self):
        self.client.force_authenticate(user=self.voter)

        self.client.post(self.url, {'value': 'up'}, format='json')
        self.client.post(self.url, {'value': 'down'}, format='json')

        self.assertEqual(Review.objects.filter(project=self.project).count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.total_vote, 1)
        self.assertEqual(self.project.vote_ratio, 0)


class TokenTests(APITestCase):
    def setUp(self):
        make_user('alice')

    def test_token_endpoint_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            '/api/users/token/',
            {'username': 'alice', 'password': PASSWORD},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_endpoint_rejects_a_wrong_password(self):
        response = self.client.post(
            '/api/users/token/',
            {'username': 'alice', 'password': 'wrong-password'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn('access', response.data)
