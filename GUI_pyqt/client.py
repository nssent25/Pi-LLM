import requests

class AudioServerClient:
    def __init__(self, url = "http://frodo.colby.edu:5000/chat", auth_key ="?Djk8;<jz:.~s*6Bn2dc>Y4TrT<P=E" , directory = ''):
        self.url = url
        self.auth_key = auth_key
        self.directory = directory

    def send_audio(self, audio_files):
        """
        Sends audio files to the server and prints the server's response.

        :param audio_files: A list of audio file names to be sent.
        """
        for audio_file in audio_files:
            audio_file_path = self.directory + audio_file
            print('\n\nReading audio file')
            # Read the audio file
            with open(audio_file_path, "rb") as audio_dat:
                audio_data = audio_dat.read()

            # Send a POST request to the server
            print('Sending request\n')
            response = requests.post(
                self.url,
                headers={"Auth-Key": self.auth_key},
                data=audio_data,
                timeout=60
            )
            # Print the server's response
            print('User:', response.json()['input'])
            print('Assistant:', response.json()['response'])
        
        #save the audio file
        with open('response.wav', 'wb') as f:
            f.write(response.content)
        #return the text
        return response.json()['response']

# Example usage
if __name__ == "__main__":
    # URL of the server
    url = "http://frodo.colby.edu:5000/chat"
    # Correct authentication key
    auth_key = "?Djk8;<jz:.~s*6Bn2dc>Y4TrT<P=E"
    # Directory containing audio files
    directory = "Backend/AudioTests/"
    # List of audio files to send
    audio_files = ["joke.m4a", "3body.m4a"]

    client = AudioServerClient(url, auth_key, directory)
    client.send_audio(audio_files)
