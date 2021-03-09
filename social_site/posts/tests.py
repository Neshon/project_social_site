from unittest import TestCase

from django.test import Client

from .models import Group, User, Post


class TestClientMixin:
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create(username='test_user', email='q@q.com')
        self.user.set_password('123')
        self.user.save()

    def tearDown(self) -> None:
        Group.objects.filter(slug='first_group').delete()
        User.objects.filter(username='test_user').delete()


class TestIndexPage(TestClientMixin, TestCase):
    def test_index_available(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class TestGroups(TestClientMixin, TestCase):
    def test_page_not_found(self):
        response = self.client.get('/group/not_exist/')
        self.assertEqual(response.status_code, 404)

    def test_exists_group(self):
        Group.objects.create(
            title='test',
            slug='first_group',
            description='empty'
        )
        response = self.client.get('/group/first_group')
        self.assertEqual(response.status_code, 200)


class TestPosts(TestClientMixin, TestCase):
    def test_valid(self):
        group = Group.objects.create(
            title='test',
            slug='first_group',
            description='empty'
        )
        group_id = group.id
        self.client.login(username='test_user', password='123')
        self.client.post('/new/', data={
            'text': 'text',
            'group': group_id
        })
        self.assertTrue(Post.objects.filter(text='text', group=group_id).exists())
