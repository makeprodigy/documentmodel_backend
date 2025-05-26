from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Document, Question
from .serializers import DocumentSerializer, QuestionSerializer, RegisterSerializer
from rest_framework.views import APIView
import google.generativeai as genai
from django.conf import settings
import os
import logging
import PyPDF2
import io
from rest_framework.exceptions import ValidationError
from django.http import JsonResponse
from time import sleep
from functools import wraps

logger = logging.getLogger(__name__)

# Constants
MAX_PROMPT_LENGTH = 30000  # Adjust based on model's token limit
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds

# Initialize Gemini model
def get_gemini_model():
    api_key = settings.GOOGLE_API_KEY
    logger.info("Initializing Gemini model...")
    
    if not api_key:
        logger.error("API key not found in settings")
        raise ValidationError("API key not configured")
    
    try:
        genai.configure(api_key=api_key)
        # Configure safety settings
        safety_settings = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        }
        
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
        logger.info("Gemini model initialized successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {str(e)}")
        raise ValidationError(f"Failed to initialize Gemini: {str(e)}")

def truncate_text(text, max_length):
    """Intelligently truncate text to stay within token limits."""
    if len(text) <= max_length:
        return text
    
    # Try to truncate at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    if last_period > 0:
        return truncated[:last_period + 1]
    return truncated

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User created successfully",
                "user": {"username": user.username}
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        if not file:
            raise ValidationError("No file provided")

        if not file.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed")

        try:
            # Read the PDF file
            file_bytes = io.BytesIO(file.read())
            pdf_reader = PyPDF2.PdfReader(file_bytes)
            
            # Extract text from all pages
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()

            if not text_content.strip():
                raise ValidationError("Could not extract text from PDF file")

            # Get title from form data or use filename
            title = self.request.data.get('title')
            if not title:
                title = os.path.splitext(file.name)[0]  # Use filename without extension

            # Save document with extracted text
            document = serializer.save(
                title=title,
                content=text_content,
                user=self.request.user
            )
            return document

        except PyPDF2.errors.EmptyFileError:
            raise ValidationError("Cannot read an empty PDF file")
        except PyPDF2.errors.PdfReadError:
            raise ValidationError("Invalid or corrupted PDF file")
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise ValidationError(f"Error processing file: {str(e)}")

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        document_id = self.request.query_params.get('document', None)
        if document_id:
            return Question.objects.filter(document_id=document_id, document__user=self.request.user)
        return Question.objects.filter(document__user=self.request.user)

    @action(detail=False, methods=['post'], url_path='ask')
    def ask(self, request):
        document_id = request.data.get('document')
        question_text = request.data.get('question')
        
        if not question_text:
            return Response(
                {"error": "Question text is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            document = Document.objects.get(id=document_id, user=request.user)
            
            if not document.content:
                logger.error(f"Document {document_id} has no content")
                return Response(
                    {"error": "Document has no content to analyze"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Truncate document content if needed
            doc_content = truncate_text(document.content, MAX_PROMPT_LENGTH)
            
            prompt = f"""Based on the following document content, please answer the question.
            If the answer cannot be found in the document, please state that explicitly.
            
            Document content:
            {doc_content}
            
            Question: {question_text}
            
            Please provide a clear and concise answer based only on the information in the document."""
            
            logger.info("Generating response from Gemini")
            
            for attempt in range(RETRY_ATTEMPTS):
                try:
                    model = get_gemini_model()
                    response = model.generate_content(prompt)
                    
                    # Check for blocked response
                    if hasattr(response, 'prompt_feedback'):
                        if response.prompt_feedback.block_reason:
                            logger.error(f"Response blocked: {response.prompt_feedback.block_reason}")
                            return Response(
                                {"error": "Response was blocked due to content safety policies"},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    
                    # Handle different response formats
                    answer = ""
                    if hasattr(response, 'text'):
                        answer = response.text
                    elif hasattr(response, 'parts'):
                        answer = ' '.join(part.text for part in response.parts)
                    else:
                        raise ValueError("Unexpected response format from Gemini API")
                    
                    if not answer.strip():
                        raise ValueError("Empty response from Gemini API")
                    
                    logger.info(f"Generated answer: {answer[:100]}...")  # Log first 100 chars
                    
                    question = Question.objects.create(
                        document=document,
                        question_text=question_text,
                        answer_text=answer
                    )
                    
                    # return Response({
                    #     "answer": answer,
                    #     "question_id": question.id
                    # })
                    serializer = QuestionSerializer(question)
                    return Response(serializer.data)
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < RETRY_ATTEMPTS - 1:
                        sleep(RETRY_DELAY)
                    else:
                        raise
            
        except Document.DoesNotExist:
            logger.error(f"Document not found or access denied: {document_id}")
            return Response(
                {"error": "Document not found or access denied"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
