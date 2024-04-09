import requests

# URL of the server
url = "http://frodo.colby.edu:5000/chat"
# Correct authentication key
auth_key = "?Djk8;<jz:.~s*6Bn2dc>Y4TrT<P=E"

directory = "Backend/AudioTests/"
audio_files = ["joke.m4a", "3body.m4a"]

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
        timeout=60
    )
    # Print the server's response
    print('User:', response.json()['input'])
    print('Assistant:', response.json()['response'])