"""
Image processing module for analyzing images and extracting text.
"""
import os
import logging
import pytesseract
from PIL import Image
import numpy as np
from transformers import ViTImageProcessor, ViTForImageClassification

from config import OCR_LANGUAGE

class ImageAnalyzer:
    """
    Handles image analysis and text extraction from images.
    """
    
    def __init__(self):
        """Initialize the image analyzer."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Set up Tesseract OCR
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Load image classification model for content analysis
        try:
            self.image_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
            self.image_model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')
            self.vision_model_loaded = True
        except Exception as e:
            self.logger.warning(f"Could not load vision model: {e}")
            self.logger.info("Image classification will be limited.")
            self.vision_model_loaded = False
    
    def extract_text(self, image_path, language="en"):
        """
        Extract text from an image using OCR.
        
        Args:
            image_path (str): Path to the image file
            language (str): Language code for OCR
            
        Returns:
            str: Extracted text
        """
        try:
            # Map language code to Tesseract format
            lang_map = {
                "en": "eng", "es": "spa", "fr": "fra", "de": "deu", 
                "it": "ita", "ja": "jpn", "ko": "kor", "zh-cn": "chi_sim",
                "ru": "rus", "ar": "ara", "hi": "hin"
            }
            
            ocr_lang = lang_map.get(language, OCR_LANGUAGE)
            
            # Open the image
            image = Image.open(image_path)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=ocr_lang)
            
            if not text.strip():
                self.logger.info("No text detected in the image.")
                return "No text was detected in this image."
            
            self.logger.info(f"Extracted text from image: {text[:50]}...")
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from image: {e}")
            return "An error occurred while extracting text from the image."
    
    def analyze_content(self, image_path):
        """
        Analyze image content to determine what's in the image.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Description of the image content
        """
        try:
            if not self.vision_model_loaded:
                return "Image content analysis unavailable."
            
            # Open and process the image
            image = Image.open(image_path)
            inputs = self.image_processor(images=image, return_tensors="pt")
            outputs = self.image_model(**inputs)
            
            # Get predictions
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            label = self.image_model.config.id2label[predicted_class_idx]
            
            self.logger.info(f"Image classified as: {label}")
            
            # Get top 3 predictions for more context
            softmax_scores = logits.softmax(dim=1)[0]
            top_scores, top_indices = softmax_scores.topk(3)
            
            top_labels = [
                f"{self.image_model.config.id2label[idx]} ({score:.1%})"
                for score, idx in zip(top_scores.tolist(), top_indices.tolist())
            ]
            
            return f"This image appears to contain: {', '.join(top_labels)}"
        except Exception as e:
            self.logger.error(f"Error analyzing image content: {e}")
            return "Image content analysis couldn't be performed."
    
    def detect_charts(self, image_path):
        """
        Detect if the image contains charts or diagrams.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            bool: True if charts are detected
        """
        try:
            # This is a simplified implementation
            # A real implementation would use a specialized model for chart detection
            image = Image.open(image_path).convert('L')  # Convert to grayscale
            img_array = np.array(image)
            
            # Simple heuristic: check for grid-like patterns using horizontal and vertical lines
            horizontal_variance = np.var(np.mean(img_array, axis=0))
            vertical_variance = np.var(np.mean(img_array, axis=1))
            
            # High variance in both directions might indicate a chart or table
            if horizontal_variance > 1000 and vertical_variance > 1000:
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"Error detecting charts: {e}")
            return False