from flask import Flask, request, jsonify 
from gevent.pywsgi import WSGIServer
from whisper_speech import WhisperSpeech 
from chat_model import ChatModelSync

app = Flask(__name__)
transcriber = WhisperSpeech()
chat_model = ChatModelSync(model_name="gemma:7b")

@app.route('/chat', methods=['POST'])
def chat():
    print('Received request')
    auth_key = request.headers.get('Auth-Key')
    correct_auth_key = "your_correct_auth_key"  # key

    if not auth_key or auth_key != correct_auth_key:
        return jsonify({'error': 'Invalid or missing authentication key'}), 403

    audio_data = request.data
    if not audio_data:
        return jsonify({'error': 'No audio data provided'}), 400

    print('Transcribing audio')
    text = transcriber.transcribe(audio_data)
    print('transcribed text:', text)
    response = chat_model.chat(text)
    response_text = chat_model.get_response(response)

    return jsonify({'input': text, 'response': response_text})

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()