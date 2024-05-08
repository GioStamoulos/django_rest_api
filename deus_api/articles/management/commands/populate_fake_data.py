from django.core.management.base import BaseCommand
import random
from django.contrib.auth.models import User
from faker import Faker
from articles.models import Author, Tag, Article, Comment
from datetime import timedelta

class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        fake = Faker()
        tags = [Tag.objects.create(name=fake.word()) for _ in range(300)]
        authors = [Author.objects.create(name=fake.name(), email=fake.email()) for _ in range(250)]
        users = [User.objects.create_user(username=fake.user_name(), email=fake.email()) for _ in range(50)]
        for _ in range(500):
            title = fake.sentence()
            abstract = fake.paragraph()
            publication_date = fake.date_between(start_date='-3y', end_date='today')
            author = random.choice(authors)
            tags_for_article = random.sample(tags, k=random.randint(1, 5))
            user = random.choice(users)
            article = Article.objects.create(title=title, abstract=abstract, publication_date=publication_date, user=user)
            article.authors.add(author)
            article.tags.add(*tags_for_article)

        for _ in range(350):
            article = random.choice(Article.objects.all())
            user= random.choice(users)
            text = fake.paragraph()
            Comment.objects.create(article=article, user=user, text=text)
