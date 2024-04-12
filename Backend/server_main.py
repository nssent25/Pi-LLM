# server_main.py
# This program implements a Flask server to handle chat requests, including audio
# transcription, classification, and processing based on the classified task.
#
# Execute the following command to start the server on port 5000:
# $ sudo iptables -A INPUT -p tcp --dport 5000 -s 137.146.0.0/16 -j ACCEPT
#
# Nithun Selva, Clio Zhu
# CS431 Spring 2024

import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
import torch
from flask import Flask, request, jsonify, abort
import json
import re
import base64
from PIL import Image
from io import BytesIO
from gevent.pywsgi import WSGIServer
from whisper_speech import WhisperSpeech # Speech recognition
from image_gen import ImageGenerator # Image generation
from translator import Translator # Translation
# from speech_transcribe import SpeechTranscriber # Speech transcription
from chat_model import ChatModel, Classifier # Chat generation, classification

app = Flask(__name__) # Create Flask app

# Initialize models
transcriber = WhisperSpeech()
classifier = Classifier(model_name="classify")
chat_model = ChatModel(model_name="mistral:7b")
image_model = ImageGenerator()
translator = Translator()
# speech_transcriber = SpeechTranscriber()

# @app.before_request
# def limit_remote_addr():
#     if not request.remote_addr.startswith('137.146'):
#         abort(403)  # Restrict to Colby IPs, redundant with port configuration

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint to handle chat requests. Performs audio transcription, classification, 
    and processes requests based on the classified task (image generation, 
    translation, or chatting).
    """
    print('\nReceived request')

    # Authenticate the request using a predefined secret key
    auth_key = request.headers.get('Auth-Key')
    correct_auth_key = "?Djk8;<jz:.~s*6Bn2dc>Y4TrT<P=E"  # Key
    if not auth_key or auth_key != correct_auth_key:
        return jsonify({'error': 'Invalid or missing authentication key'}), 403
    
    # Ensure that audio data is provided with the request
    audio_data = request.data
    if not audio_data:
        return jsonify({'error': 'No audio data provided'}), 400

    # Transcribe the provided audio data to text
    print('Transcribing audio')
    src_text = transcriber.transcribe(audio_data) # Transcribe audio
    src_language = src_text['chunks'][0]['language'] # Get language of audio
    original_text = src_text['text'] # Original foreign language text
    if src_language != 'english': # If not in English, translate to English
        print('Translating audio from', src_language)
        src_text = transcriber.translate(audio_data)
    text = src_text['text'] 
    print('transcribed text:', text)

    # Classify the transcribed text to determine the intended task
    print('Classifying input')
    to_classify = '{"Input": "' + text + '"}' # Format text for classification
    classification = classifier.chat(to_classify)
    print('classification:', classifier.get_response(classification))
    json_classification = extract_json(classifier.get_response(classification))
    print('json_classification:', json_classification)

    # Generate an image if the classified task is image generation
    if "Image Generation" in json_classification:
        print('Generating image')
        torch.cuda.empty_cache() # Clear GPU memory
        image = image_model.generate(json_classification['Image Generation'])
        torch.cuda.empty_cache()
        return jsonify({'input': original_text, 
                        'response': image_to_base64(image), 
                        'task': 'Image Generation'})
    
    # Perform text translation if the classified task is translation
    elif "Translation" in json_classification:
        print('Translating text')
        language, to_translate = json_classification['Translation'].split('$~$')
        language = language.strip().lower()
        print('Translating to', language)
        translation = translator.translate(to_translate, src_language, language)
        response_text = translation['result']
        return jsonify({'input': original_text, 
                        'response': response_text, 
                        'task': 'Translation',
                        'source': src_language,
                        'language': language})
    
    # Default to chat generation for other types of requests
    else:
        print('Chatting with model')
        # response = chat_model.chat(json_classification['Text/Chat Generation'])
        response = chat_model.chat(text)
        response_text = chat_model.get_response(response)

        # Translate the chat response back to the original language if necessary
        if src_language != 'english':
            print('Translating response back to', src_language)
            response_text = translator.translate(text=response_text,
                                                 src_lang='english', 
                                                 tgt_lang=src_language)['result']
        return jsonify({'input': original_text, 
                        'response': response_text,
                        'task': 'Chat'})

def extract_json(text):
    """
    Extracts a JSON object from a string.
    
    Args:
        text (str): The string containing the JSON object.
    
    Returns:
        dict or str: The extracted JSON object as a dictionary, 
            or the original text.
    """
    match = re.search(r'{.*}', text) # Match the JSON object within the string
    if match:
        string_json = match.group(0) 
        return json.loads(string_json) # Parse and return the JSON object
    else:
        return text # Return the original text if no JSON object is found
    
def image_to_base64(img):
    """
    Converts an image to a base64-encoded string.

    Args:
        img (PIL.Image): The image to convert.

    Returns:
        str: The base64-encoded image string.
    """
    buffered = BytesIO() # Create a buffer to store the image
    img.save(buffered, format="JPEG") # Save the image to the buffer
    img_str = base64.b64encode(buffered.getvalue()) # Encode the image to base64
    return img_str.decode('utf-8') 

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    print('\nServer running...')
    http_server.serve_forever() # Start the server
