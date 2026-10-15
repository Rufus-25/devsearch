"""Tests for the projects app: voting, pages, ownership, tags and link validation.

Put this file in the `projects/` folder (next to models.py).
Run with:  python manage.py test projects
"""
import json
import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ProjectForm
from .models import Project, Review, Tag

PASSWORD = 'Sup3r-Secret-Pass!'


def make_user(username):
    """Create a user. The post_save signal creates the matching Profile."""
    return User.objects.create_user(
        username=username, password=PASSWORD, email=f'{username}@example.com'
    )


class VoteCalculationTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.project = Project.objects.create(
            owner=self.owner.profile, title='Demo Project'
        )

    def test_update_vote_counts_votes_and_calculates_the_ratio(self):
        for index, vote in enumerate(['up', 'up', 'up', 'down']):
            reviewer = make_user(f'reviewer{index}')
            Review.objects.create(
                project=self.project, reviewer=reviewer.profile, vote_type=vote
            )

        self.project.updateVote()

        self.project.refresh_from_db()
        self.assertEqual(self.project.total_vote, 4)
        self.assertEqual(self.project.vote_ratio, 75)

    def test_project_with_no_votes_has_a_zero_ratio(self):
        self.project.updateVote()

        self.project.refresh_from_db()
        self.assertEqual(self.project.total_vote, 0)
        self.assertEqual(self.project.vote_ratio, 0)

    def test_project_without_image_uses_default_image(self):
        self.assertIn('images/default.jpg', self.project.imageURL)


class ProjectPageTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.project = Project.objects.create(
            owner=self.owner.profile, title='Demo Project', description='A demo'
        )

    def test_projects_list_page_loads(self):
        response = self.client.get(reverse('projects'))

        self.assertEqual(response.status_code, 200)

    def test_project_page_loads_for_anonymous_visitors(self):
        response = self.client.get(reverse('project', args=[self.project.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Demo Project')

    def test_unknown_project_returns_404(self):
        response = self.client.get(reverse('project', args=[uuid.uuid4()]))

        self.assertEqual(response.status_code, 404)

    def test_malformed_project_id_returns_404(self):
        response = self.client.get('/projects/project/not-a-uuid/')

        self.assertEqual(response.status_code, 404)


class CreateAndUpdateProjectTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')

    def test_create_project_requires_login(self):
        response = self.client.get(reverse('create-project'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('create-project')}",
            fetch_redirect_response=False,
        )

    def test_logged_in_user_can_create_a_project_with_tags(self):
        self.client.login(username='owner', password=PASSWORD)

        response = self.client.post(
            reverse('create-project'),
            {
                'title': 'My App',
                'description': 'Something cool',
                'demo_link': '',
                'github_link': '',
                'newtags': 'django, python',
            },
        )

        self.assertRedirects(
            response, reverse('account'), fetch_redirect_response=False
        )
        project = Project.objects.get(title='My App')
        self.assertEqual(project.owner, self.owner.profile)
        self.assertEqual(
            sorted(project.tags.values_list('name', flat=True)), ['django', 'python']
        )

    def test_invalid_form_shows_the_page_again_instead_of_crashing(self):
        self.client.login(username='owner', password=PASSWORD)

        response = self.client.post(
            reverse('create-project'),
            {
                'title': 'Bad link',
                'demo_link': 'javascript:alert(1)',
                'newtags': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(title='Bad link').exists())


class ProjectOwnershipTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.other = make_user('other')
        self.project = Project.objects.create(
            owner=self.owner.profile, title='Original'
        )

    def test_owner_can_update_their_project(self):
        self.client.login(username='owner', password=PASSWORD)

        response = self.client.post(
            reverse('update-project', args=[self.project.id]),
            {'title': 'Renamed', 'newtags': ''},
        )

        self.assertRedirects(
            response,
            reverse('project', args=[self.project.id]),
            fetch_redirect_response=False,
        )
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Renamed')

    def test_other_user_cannot_update_the_project(self):
        self.client.login(username='other', password=PASSWORD)

        response = self.client.post(
            reverse('update-project', args=[self.project.id]),
            {'title': 'Hacked', 'newtags': ''},
        )

        self.assertTemplateUsed(response, 'unauthorized.html')
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Original')

    def test_other_user_cannot_delete_the_project(self):
        self.client.login(username='other', password=PASSWORD)

        self.client.post(reverse('delete-project', args=[self.project.id]))

        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_owner_can_delete_their_project(self):
        self.client.login(username='owner', password=PASSWORD)

        response = self.client.post(reverse('delete-project', args=[self.project.id]))

        self.assertRedirects(
            response, reverse('account'), fetch_redirect_response=False
        )
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())


class RemoveTagTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.other = make_user('other')
        self.project = Project.objects.create(
            owner=self.owner.profile, title='Tagged'
        )
        self.tag = Tag.objects.create(name='django')
        self.project.tags.add(self.tag)

    def post_remove(self):
        return self.client.post(
            reverse('remove-tag'),
            data=json.dumps(
                {'project': str(self.project.id), 'tag': str(self.tag.id)}
            ),
            content_type='application/json',
        )

    def test_owner_can_remove_a_tag(self):
        self.client.login(username='owner', password=PASSWORD)

        response = self.post_remove()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'removed': True})
        self.assertEqual(self.project.tags.count(), 0)

    def test_other_user_cannot_remove_a_tag(self):
        self.client.login(username='other', password=PASSWORD)

        response = self.post_remove()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.project.tags.count(), 1)

    def test_anonymous_user_is_sent_to_login(self):
        response = self.post_remove()

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])
        self.assertEqual(self.project.tags.count(), 1)


class ProjectFormLinkTests(TestCase):
    def test_link_without_a_scheme_is_accepted_and_made_absolute(self):
        form = ProjectForm(
            data={'title': 'T', 'demo_link': 'example.com', 'github_link': ''}
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(
            form.cleaned_data['demo_link'].startswith(('http://', 'https://'))
        )

    def test_javascript_links_are_rejected(self):
        form = ProjectForm(
            data={'title': 'T', 'demo_link': 'javascript:alert(1)', 'github_link': ''}
        )

        self.assertFalse(form.is_valid())
        self.assertIn('demo_link', form.errors)

    def test_empty_links_are_allowed(self):
        form = ProjectForm(data={'title': 'T', 'demo_link': '', 'github_link': ''})

        self.assertTrue(form.is_valid(), form.errors)
