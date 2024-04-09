from flask import Flask, request, jsonify, abort
import re
from gevent.pywsgi import WSGIServer
from whisper_speech import WhisperSpeech 
from chat_model import ChatModelSync, Classifier
from image_gen import ImageGenerator
from translator import Translator

app = Flask(__name__)
transcriber = WhisperSpeech()
classifier = Classifier(model_name="classify")
chat_model = ChatModelSync(model_name="gemma:7b")
image_model = ImageGenerator()
translator = Translator()

# @app.before_request
# def limit_remote_addr():
#     if not request.remote_addr.startswith('137.146'):
#         abort(403)  # Restrict to Colby IPs

@app.route('/chat', methods=['POST'])
def chat():
    print('Received request')
    auth_key = request.headers.get('Auth-Key')
    correct_auth_key = "?Djk8;<jz:.~s*6Bn2dc>Y4TrT<P=E"  # key

    if not auth_key or auth_key != correct_auth_key:
        return jsonify({'error': 'Invalid or missing authentication key'}), 403

    audio_data = request.data
    if not audio_data:
        return jsonify({'error': 'No audio data provided'}), 400

    print('Transcribing audio')
    text = transcriber.transcribe(audio_data)
    print('transcribed text:', text)

    print('Classifying input')
    classification = classifier.chat(text)
    print('classification:', classification)
    json_classification = extract_json(classification)

    # image generation
    if "Image Generation" in json_classification:
        print('Generating image')
        image = image_model.generate(json_classification['Image Generation'])
        return jsonify({'input': text, 'response': image, 
                        'task': 'Image Generation'})
    
    # translation
    elif "Translation" in json_classification:
        print('Translating text')
        language, to_translate = json_classification['Translation'].split('$~$')
        translation = chat_model.chat(to_translate)
        response_text = chat_model.get_response(translation)
        return jsonify({'input': text, 'response': response_text, 
                        'task': 'Translation',
                        'language': language})
    
    # default to chat generation
    else:
        print('Chatting with model')
        # response = chat_model.chat(json_classification['Text/Chat Generation'])
        response = chat_model.chat(text)
        response_text = chat_model.get_response(response)
        return jsonify({'input': text, 'response': response_text})

def extract_json(text):
    match = re.search(r'{.*}', text)
    if match:
        string_json = match.group(0)
        return jsonify(string_json)
    else:
        return None
    
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()