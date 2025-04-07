"""
Main entry point for the AI Study Assistant application.
"""
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid

# Import modules
from modules.ai_core import OllamaAI
from modules.voice_chat import VoiceProcessor
from modules.image_processor import ImageAnalyzer
from modules.language_support import LanguageManager
from modules.study_strategies import StudyStrategies

# Import config
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Initialize components
ai_core = OllamaAI()
voice_processor = VoiceProcessor()
image_analyzer = ImageAnalyzer()
language_manager = LanguageManager()
study_strategies = StudyStrategies()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', 
                          supported_languages=config.SUPPORTED_LANGUAGES,
                          current_language="en")

@app.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html',
                          supported_languages=config.SUPPORTED_LANGUAGES)

@app.route('/games')
def games():
    """Render the games page."""
    return render_template('games.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages from the user."""
    data = request.json
    user_message = data.get('message', '')
    language = data.get('language', 'en')
    
    # Translate to English if not already
    if language != 'en':
        user_message = language_manager.translate_to_english(user_message, language)
    
    # Get AI response
    response = ai_core.get_response(user_message)
    
    # Translate response if needed
    if language != 'en':
        response = language_manager.translate_from_english(response, language)
    
    # Get study tips based on content if relevant
    study_tips = study_strategies.get_related_tips(user_message)
    
    return jsonify({
        'response': response,
        'study_tips': study_tips
    })

@app.route('/api/voice', methods=['POST'])
def voice_chat():
    """Process voice input from the user."""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    language = request.form.get('language', 'en')
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(filepath)
    
    try:
        # Process voice
        transcription = voice_processor.transcribe(filepath, language)
        
        # Get AI response
        response = ai_core.get_response(transcription)
        
        # Generate voice response
        audio_response_path = voice_processor.text_to_speech(response, language)
        
        return jsonify({
            'transcription': transcription,
            'response': response,
            'audio_url': f"/audio/{os.path.basename(audio_response_path)}"
        })
    finally:
        # Clean up the uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/api/image', methods=['POST'])
def process_image():
    """Process image uploads and extract text."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    language = request.form.get('language', 'en')
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}{os.path.splitext(image_file.filename)[1]}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(filepath)
    
    try:
        # Extract text from image
        extracted_text = image_analyzer.extract_text(filepath, language)
        
        # Analyze image content
        content_analysis = image_analyzer.analyze_content(filepath)
        
        # Get AI interpretation of the content
        interpretation = ai_core.get_response(
            f"Analyze this extracted text from an image: {extracted_text}\n"
            f"Image content appears to show: {content_analysis}\n"
            f"Provide educational insights and study notes based on this content."
        )
        
        return jsonify({
            'extracted_text': extracted_text,
            'analysis': content_analysis,
            'interpretation': interpretation,
            'image_url': f"/uploads/{filename}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    """Serve generated audio files."""
    return send_from_directory(voice_processor.output_dir, filename)

@app.route('/uploads/<filename>')
def get_upload(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/study/tips', methods=['GET'])
def get_study_tips():
    """Get general study tips."""
    category = request.args.get('category', 'general')
    count = int(request.args.get('count', 5))
    tips = study_strategies.get_tips(category, count)
    return jsonify({'tips': tips})

if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=config.PORT)