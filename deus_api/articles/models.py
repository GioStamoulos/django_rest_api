from django.db import models
from django.contrib.auth.models import User  

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    authors = models.ManyToManyField(Author, related_name='articles')
    tags = models.ManyToManyField(Tag, related_name='articles')
    publication_date = models.DateField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.article}"