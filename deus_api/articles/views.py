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


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class TagViewSet(viewsets.ModelViewSet):
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

class CustomPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'

class ArticleOwnerAuthenticator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user_id == request.user

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes_by_action = {
        'create': [permissions.AllowAny], 
        'retrieve': [permissions.AllowAny],
        'update': [ArticleOwnerAuthenticator],            # Only owners can update
        'partial_update': [ArticleOwnerAuthenticator],    # Only owners can partially update
        'destroy': [ArticleOwnerAuthenticator],           # Only owners can delete
    }

    filter_backends = [filters.OrderingFilter, django_filters.DjangoFilterBackend]
    filterset_class = ArticleFilter
    pagination_class = CustomPagination

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes_by_action['create']]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

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


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def article_detail(request, pk):
    try:
        article = Article.objects.get(pk=pk)
    except Article.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Check if the requesting user is the owner of the article
    if article.author != request.user:
        return Response({"message": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, article_id):
    try:
        article = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, article=article)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_comments(request, article_id):
    try:
        article = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    comments = Comment.objects.filter(article=article)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    #    Check if the requesting user is the owner of the comment
    if comment.user != request.user:
        return Response({"message": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)