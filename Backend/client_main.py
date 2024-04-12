import requests
import base64
from PIL import Image
from io import BytesIO

# URL of the server
url = "http://frodo.colby.edu:5000/chat"
# Correct authentication key
auth_key = "?Djk8;<jz:.~s*6Bn2dc>Y4TrT<P=E"

directory = "Backend/AudioTests/"
audio_files = ["joke.m4a", "cat.m4a", "zh_test.m4a"]#,"3body.m4a", "fr_test.m4a", "ja_test.m4a"]

def base64_to_image(base64_str):
    img_bytes = base64.b64decode(base64_str)
    img = Image.open(BytesIO(img_bytes))
    return img

for audio_file in audio_files:
    audio_file_path = directory + audio_file
    print('\n\nReading audio file')
    # Read the audio file
    with open(audio_file_path, "rb") as audio_dat:
        audio_data = audio_dat.read()

    # Send a POST request to the server
    print('Sending request\n')
    response = requests.post(
        url,
        headers={"Auth-Key": auth_key},
        data=audio_data,
        timeout=30
    )
    # Print the server's response
    json_response = response.json()
    if json_response['task'] == 'Translation':
        print('User:', json_response['input'])
        print('Assistant:', json_response['response'])
        print('Source Language:', json_response['source'])
        print('Target Language:', json_response['language'])

    elif json_response['task'] == 'Image Generation':
        print('User:', json_response['input'])
        img = base64_to_image(json_response['response'])
        img.show()

    else:
        print('User:', json_response['input'])
        print('Assistant:', json_response['response'])

    # print('User:', response.json()['input'])
    # print('Assistant:', response.json()['response'])
