import requests
import json

class AudioServerClient:
    def __init__(self, url = "http://frodo.colby.edu:5000/chat", auth_key ="?Djk8;<jz:.~s*6Bn2dc>Y4TrT<P=E" , directory = ''):
        self.url = url
        self.auth_key = auth_key
        self.directory = directory

    def send_audio(self, audio_file):
        """
        Sends audio files to the server and prints the server's response.

        :param audio_files: audio file names to be sent.
        """
        
        audio_file_path = self.directory + audio_file
        print('\n\nReading audio file')
        # Read the audio file
        with open(audio_file_path, "rb") as audio_dat:
            audio_data = audio_dat.read()
            print('audio data:', audio_file_path)

        # Send a POST request to the server
        print('Sending request\n')
        response = requests.post(
            self.url,
            headers={"Auth-Key": self.auth_key},
            data=audio_data,
            timeout=60)
            # # Print the server's response
        #print(json.dumps(response, indent=4)) 
        json_response = response.json()
        if json_response['task'] == 'Translation':
            print('User:', json_response['input'])
            print('Assistant:', json_response['response'])
            print('Source Language:', json_response['source'])
            print('Target Language:', json_response['language'])

        elif json_response['task'] == 'Image Generation':
            print('User:', json_response['input'])
            print('Task:', json_response['task'])

        else:
            print('User:', json_response['input'])
            print('Assistant:', json_response['response'])

# Example usage
if __name__ == "__main__":
    # URL of the server
    url = "http://frodo.colby.edu:5000/chat"
    # Correct authentication key
    auth_key = "?Djk8;<jz:.~s*6Bn2dc>Y4TrT<P=E"
    # Directory containing audio files
    directory = "Backend/AudioTests/"
    # List of audio files to send

    client = AudioServerClient(url, auth_key, directory)
    #client.send_audio(audio_files)
