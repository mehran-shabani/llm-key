# Feature: Image Processing with OCR
# Description: Extract text from images using OCR with multiple language support
# Library: Django, pytesseract, Pillow, opencv-python

# 1. models.py - OCR result storage
from django.db import models
import uuid

class OCRResult(models.Model):
    LANGUAGE_CHOICES = [
        ('eng', 'English'),
        ('spa', 'Spanish'),
        ('fra', 'French'),
        ('deu', 'German'),
        ('chi_sim', 'Chinese Simplified'),
        ('jpn', 'Japanese'),
        ('ara', 'Arabic'),
        ('rus', 'Russian'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    filename = models.CharField(max_length=200)
    image_format = models.CharField(max_length=10)
    languages = models.CharField(max_length=100, default='eng')  # Comma-separated language codes
    extracted_text = models.TextField()
    confidence_score = models.FloatField(null=True, blank=True)
    word_count = models.IntegerField(default=0)
    processing_time_ms = models.IntegerField(default=0)
    image_width = models.IntegerField(null=True, blank=True)
    image_height = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# 2. ocr_processor.py - OCR processing logic
import os
import time
import tempfile
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import pytesseract

class OCRProcessor:
    
    # Supported languages mapping
    SUPPORTED_LANGUAGES = {
        'eng': 'English',
        'spa': 'Spanish', 
        'fra': 'French',
        'deu': 'German',
        'chi_sim': 'Chinese Simplified',
        'jpn': 'Japanese',
        'ara': 'Arabic',
        'rus': 'Russian',
        'ita': 'Italian',
        'por': 'Portuguese',
        'nld': 'Dutch',
        'kor': 'Korean',
        'hin': 'Hindi',
    }
    
    def __init__(self, languages=['eng'], max_execution_time=300):
        self.languages = self.parse_languages(languages)
        self.max_execution_time = max_execution_time
        
        # Verify tesseract installation
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            raise Exception("Tesseract OCR is not installed or not in PATH")
    
    def parse_languages(self, languages):
        """Parse and validate language codes"""
        if isinstance(languages, str):
            languages = [lang.strip() for lang in languages.split(',')]
        
        valid_languages = []
        for lang in languages:
            if lang in self.SUPPORTED_LANGUAGES:
                valid_languages.append(lang)
        
        return valid_languages if valid_languages else ['eng']
    
    def preprocess_image(self, image_path):
        """Preprocess image for better OCR accuracy"""
        try:
            # Load image with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Apply adaptive thresholding
            threshold = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Dilation and erosion to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)
            
            # Save processed image temporarily
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, processed)
                return temp_file.name
                
        except Exception as e:
            print(f"Image preprocessing failed: {str(e)}")
            return image_path  # Return original if preprocessing fails
    
    def extract_text_from_image(self, image_path, filename):
        """Extract text from image using OCR"""
        start_time = time.time()
        
        try:
            # Get image dimensions
            with Image.open(image_path) as img:
                width, height = img.size
                image_format = img.format.lower() if img.format else 'unknown'
            
            # Preprocess image for better OCR
            processed_image_path = self.preprocess_image(image_path)
            
            try:
                # Configure Tesseract
                language_string = '+'.join(self.languages)
                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?;:()'
                
                # Extract text with confidence scores
                data = pytesseract.image_to_data(
                    processed_image_path,
                    lang=language_string,
                    config=custom_config,
                    output_type=pytesseract.Output.DICT
                )
                
                # Extract text
                extracted_text = pytesseract.image_to_string(
                    processed_image_path,
                    lang=language_string,
                    config=custom_config
                )
                
                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                processing_time = int((time.time() - start_time) * 1000)
                
                return {
                    'success': True,
                    'text': extracted_text.strip(),
                    'confidence': avg_confidence,
                    'word_count': len(extracted_text.split()) if extracted_text.strip() else 0,
                    'processing_time_ms': processing_time,
                    'image_width': width,
                    'image_height': height,
                    'image_format': image_format,
                    'languages_used': self.languages
                }
                
            finally:
                # Clean up preprocessed image if different from original
                if processed_image_path != image_path and os.path.exists(processed_image_path):
                    os.unlink(processed_image_path)
                    
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'error': str(e),
                'processing_time_ms': processing_time
            }

# 3. views.py - OCR API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import tempfile
import os
import json

@method_decorator(csrf_exempt, name='dispatch')
class ImageOCRView(View):
    def post(self, request):
        try:
            if 'image' not in request.FILES:
                return JsonResponse({'error': 'No image file provided'}, status=400)
            
            image_file = request.FILES['image']
            filename = image_file.name
            languages = request.POST.get('languages', 'eng').split(',')
            
            # Validate file type
            allowed_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in allowed_extensions:
                return JsonResponse({
                    'error': f'Unsupported image type: {file_ext}. Allowed: {allowed_extensions}'
                }, status=400)
            
            # Save image temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Initialize OCR processor
                ocr_processor = OCRProcessor(languages=languages)
                
                # Process the image
                result = ocr_processor.extract_text_from_image(temp_path, filename)
                
                if not result['success']:
                    return JsonResponse({'error': result['error']}, status=400)
                
                # Save OCR result to database
                ocr_result = OCRResult.objects.create(
                    filename=filename,
                    image_format=result['image_format'],
                    languages=','.join(result['languages_used']),
                    extracted_text=result['text'],
                    confidence_score=result['confidence'],
                    word_count=result['word_count'],
                    processing_time_ms=result['processing_time_ms'],
                    image_width=result['image_width'],
                    image_height=result['image_height']
                )
                
                return JsonResponse({
                    'success': True,
                    'ocr_result': {
                        'id': str(ocr_result.id),
                        'filename': ocr_result.filename,
                        'languages': ocr_result.languages,
                        'extracted_text': ocr_result.extracted_text,
                        'confidence_score': ocr_result.confidence_score,
                        'word_count': ocr_result.word_count,
                        'processing_time_ms': ocr_result.processing_time_ms,
                        'image_dimensions': f"{ocr_result.image_width}x{ocr_result.image_height}",
                        'text_preview': ocr_result.extracted_text[:200] + '...' if len(ocr_result.extracted_text) > 200 else ocr_result.extracted_text,
                        'created_at': ocr_result.created_at.isoformat()
                    }
                })
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class OCRResultsView(View):
    def get(self, request):
        try:
            results = OCRResult.objects.all()[:20]
            
            results_list = []
            for result in results:
                results_list.append({
                    'id': str(result.id),
                    'filename': result.filename,
                    'languages': result.languages,
                    'word_count': result.word_count,
                    'confidence_score': result.confidence_score,
                    'processing_time_ms': result.processing_time_ms,
                    'text_preview': result.extracted_text[:100] + '...' if len(result.extracted_text) > 100 else result.extracted_text,
                    'created_at': result.created_at.isoformat()
                })
            
            return JsonResponse({
                'results': results_list,
                'supported_languages': OCRProcessor.SUPPORTED_LANGUAGES
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class OCRResultDetailView(View):
    def get(self, request, result_id):
        try:
            result = OCRResult.objects.get(id=result_id)
            
            return JsonResponse({
                'id': str(result.id),
                'filename': result.filename,
                'image_format': result.image_format,
                'languages': result.languages,
                'extracted_text': result.extracted_text,
                'confidence_score': result.confidence_score,
                'word_count': result.word_count,
                'processing_time_ms': result.processing_time_ms,
                'image_dimensions': f"{result.image_width}x{result.image_height}",
                'created_at': result.created_at.isoformat()
            })
            
        except OCRResult.DoesNotExist:
            return JsonResponse({'error': 'OCR result not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 4. urls.py
from django.urls import path
from .views import ImageOCRView, OCRResultsView, OCRResultDetailView

urlpatterns = [
    path('images/ocr/', ImageOCRView.as_view()),
    path('ocr/results/', OCRResultsView.as_view()),
    path('ocr/results/<uuid:result_id>/', OCRResultDetailView.as_view()),
]