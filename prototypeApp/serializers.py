# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'profile_picture']

class CatSerializer(serializers.ModelSerializer):
    submitted_by = UserSerializer()

    class Meta:
        model = Cat
        fields = ['id','name','age','breed','description','profile_picture','submitted_by','in_review']
        read_only_fields = ['submitted_by','in_review']

class CommunityCatSerializer(serializers.ModelSerializer):
    reported_by = UserSerializer()
    class Meta:
        model = CommunityCat
        fields = ['id', 'name', 'cat_img','location', 'description', 'last_seen','reported_by']
        read_only_fields = ['reported_by']


class ThreadSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Thread
        fields = ['id', 'title', 'content', 'image', 'author', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    class Meta:
        model = Comment
        fields = ['id', 'thread', 'author', 'content', 'created_at']