from django.test import TestCase
from django.contrib.auth.models import User
from .models import Author, Article, Tag, Comment
from rest_framework.test import APIClient
import logging
from rest_framework.authtoken.models import Token



class ArticleCommentTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='George', email='george@example2.com', password='george123')
        self.user2 = User.objects.create_user(username='John', email='john@example1.com', password='john123')

        self.author1 = Author.objects.create(name='Author George', email='georgeauthor@example.com')
        self.author2 = Author.objects.create(name='Author John', email='johnauthor@example.com')

        self.tag1 = Tag.objects.create(name='Python')
        self.tag2 = Tag.objects.create(name='Java')

        self.article1 = Article.objects.create(
            title='Article Python',
            abstract='This is the first article',
            publication_date='2023-05-03',
            user_id=self.user1
        )
        self.article1.authors.set([self.author1])
        self.article1.tags.set([self.tag1])

        self.article2 = Article.objects.create(
            title='Article Java',
            abstract='This is the second article',
            publication_date='2020-05-05',
            user_id=self.user2
        )
        self.article2.authors.set([self.author2])
        self.article2.tags.set([self.tag2])

        self.comment1 = Comment.objects.create(
            article=self.article1,
            user_id=self.user1,
            text='This is a comment on Python Article'
        )

        self.comment2 = Comment.objects.create(
            article=self.article2,
            user_id=self.user2,
            text='This is a comment on Java Article'
        )
        self.token = Token.objects.create(user=self.user1)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_created(self):
        #creation check
        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(Comment.objects.count(), 2)

    def test_filter_by_year(self):
       # client = APIClient()
       # client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        # Test filtering articles by year
        response = self.client.get('/articles/?year=2020')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count'), 1)
        response = self.client.get('/articles/?year=2023')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count'), 1)

    def test_filter_by_month(self):
        # Test filtering articles by month
        response = self.client.get('/articles/?month=5')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count'), 2)

    def test_filter_by_author(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        # Test filtering articles by author name
        response = client.get('/articles/?authors=Author John')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(response.data.get('results')[0].get('title'), 'Article Java')

    def test_filter_by_tag(self):
        # Test filtering articles by tag name
        response = self.client.get('/articles/?tags=Python')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count') , 1)
        self.assertEqual(response.data.get('results')[0].get('title'), 'Article Python')

    def test_filter_by_keyword(self):
        response1 = self.client.get('/articles/?keywords=first')
        response2 = self.client.get('/articles/?keywords=Python')
        # check title keyword filtering
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data.get('count'), 1)
        self.assertEqual(response1.data.get('results')[0].get('title'), 'Article Python')
        #check abstract keyword filtering
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data.get('count'), 1)
        self.assertEqual(response2.data.get('results')[0].get('title'), 'Article Python')

    def test_article_export(self):
        response = self.client.get('/articles//download/')
        self.assertEqual(response.status_code, 200)



    def test_user_comment_update(self):
        response = self.client.patch(f'/comments/{self.comment1.id}/', {'text': 'Updated comment'})
        self.assertEqual(response.status_code,  200)
        # check if blocked for comment2 to update
        response = self.client.patch(f'/comments/{self.comment2.id}/', {'text': 'Updated comment'})
        self.assertIn(response.status_code, [401, 403])

    def test_user_comment_delete(self):
        response1 = self.client.delete(f'/comments/{self.comment1.id}/')
        self.assertEqual(response1.status_code, 204)
        response2 = self.client.delete(f'/comments/{self.comment2.id}/')
        self.assertIn(response2.status_code, [401, 403])

        # Attempt to delete the article owned by user1
        #response = self.client.delete(f'/articles/{self.article1.id}/')

        # Check that the request was forbidden (403)