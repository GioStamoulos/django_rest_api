from articles.models import Author, Tag, Article, Comment
from .serializers import AuthorSerializer, TagSerializer, ArticleSerializer, CommentSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as django_filters
import csv
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'

class CommonViewSet(viewsets.ModelViewSet):
    permission_classes_by_action = {
        'list':[permissions.IsAuthenticated],
        'create': [permissions.IsAuthenticated], 
        'retrieve': [permissions.IsAuthenticated],
        'update': [permissions.IsAuthenticated],            
        'partial_update': [permissions.IsAuthenticated],    
        'destroy': [permissions.IsAuthenticated],           
    }
    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return False
    pagination_class = CustomPagination

class AuthorViewSet(CommonViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class TagViewSet(CommonViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ArticleFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name='publication_date__year')
    month = django_filters.NumberFilter(field_name='publication_date__month')
    authors = django_filters.CharFilter(field_name='authors__name', lookup_expr='icontains')
    tags = django_filters.CharFilter(field_name='tags__name', lookup_expr='icontains')
    keywords = django_filters.CharFilter(field_name='title', method='filter_keywords')

    def filter_keywords(self, queryset, name, value):
        return queryset.filter(title__icontains=value) | queryset.filter(abstract__icontains=value)

    class Meta:
        model = Article
        fields = ['year', 'month', 'authors', 'tags', 'keywords']


class OwnerAuthenticator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user_id == request.user

class ArticleViewSet(CommonViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes_by_action = {
        'list':[permissions.IsAuthenticated],
        'create': [permissions.AllowAny], 
        'retrieve': [permissions.IsAuthenticated],
        'update': [OwnerAuthenticator],            
        'partial_update': [OwnerAuthenticator],    
        'destroy': [OwnerAuthenticator],           
    }

    filter_backends = [filters.OrderingFilter, django_filters.DjangoFilterBackend]
    filterset_class = ArticleFilter

       
    def create(self, request, *args, **kwargs):
        request.data['user_id'] = request.user.id 
        response = super().create(request, *args, **kwargs)
        return response


class CommentViewSet(CommonViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer 
    permission_classes_by_action = {
        'list':[permissions.IsAuthenticated],
        'create': [permissions.AllowAny], 
        'retrieve': [permissions.IsAuthenticated],
        'update': [OwnerAuthenticator],            
        'partial_update': [OwnerAuthenticator],    
        'destroy': [OwnerAuthenticator],           
    }
       
    def create(self, request, *args, **kwargs):
        request.data['user_id'] = request.user.id 
        response = super().create(request, *args, **kwargs)
        return response



class ArticleExport(ArticleViewSet):
    def list(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        authors = request.query_params.getlist('authors')
        tags = request.query_params.getlist('tags')
        keywords = request.query_params.get('keywords')

        queryset = Article.objects.all()
        if year:
            queryset = queryset.filter(publication_date__year=year)
        if month:
            queryset = queryset.filter(publication_date__month=month)
        if authors:
            queryset = queryset.filter(authors__name__in=authors)
        if tags:
            queryset = queryset.filter(tags__name__in=tags)
        if keywords:
            queryset = queryset.filter(title__icontains=keywords) | queryset.filter(abstract__icontains=keywords)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="articles.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Abstract', 'Publication Date', 'Authors', 'Tags'])
        for article in queryset:
            writer.writerow([
                article.title,
                article.abstract,
                article.publication_date,
                ', '.join([author.name for author in article.authors.all()]),
                ', '.join([tag.name for tag in article.tags.all()])
            ])

        return response 

