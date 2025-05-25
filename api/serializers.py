from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Document, Question

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class DocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    title = serializers.CharField(required=False)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'user']
        read_only_fields = ['content', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Ensure user is added from context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'document', 'question_text', 'answer_text', 'created_at']
        read_only_fields = ['answer_text', 'created_at']
