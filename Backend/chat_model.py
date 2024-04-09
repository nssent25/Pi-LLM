# chat_model.py
# This program uses the Ollama API to chat with a model and generate text based on a prompt
#
# Nithun Selva, Clio Zhu
# March 2024

import ollama
import asyncio

class ChatModel:
    def __init__(self, model_name="gemma:7b", host=None):
        self.model = model_name
        self.host = host # example: "http://localhost:11434"
        self.message_history = []
        if host:
            self.client = ollama.AsyncClient(host=host, timeout = 60)
        else:
            self.client = ollama.AsyncClient()

        try:
          ollama.chat(model_name)
        except ollama.ResponseError as e:
          print('Error:', e.error)
          if e.status_code == 404:
            print('Model not found. Run $ ollama pull', model_name, 'to download it.')
            # print('Model not found. Attempting to download...')
            # ollama.pull(model_name)

    # Sends a message to the model and returns the response as a string
    # message: the message to send to the model
    # to return, use await asyncio.create_task(chat_model.chat(message))
    async def chat(self, message):
        self.message_history.append({'role': 'user', 'content': message})
        response = await self.client.chat(model=self.model, messages=self.message_history)
        self.message_history.append({'role': 'assistant', 'content': response['message']['content']})
        return response
    
    # unused
    # Sends a message to the model and prints the response as it comes in
    async def chat_stream(self, messages):
        async for part in await self.client.chat(model=self.model, messages=[
            {'role': 'user', 'content': messages,},], stream=True):
            print(part['message']['content'], end='', flush=True)
        print()
    
    # unused
    # Generates text based on a prompt and returns the response as a string
    async def generate(self, prompt):
        response = await self.client.generate(model=self.model, prompt=prompt)
        return response
    
    # returns the full response from the model
    def get_response(self, response):
        return response['message']['content']
    
    # prints the full response from the model
    def print_response(self, response):
        print(self.get_response(response))

class ChatModelSync:
    def __init__(self, model_name="gemma:7b", host=None):
        self.model = model_name
        self.host = host # example: "http://localhost:11434"
        self.message_history = []
        if host:
            self.client = ollama.Client(host=host, timeout = 60)
        else:
            self.client = ollama.Client()

        try:
          ollama.chat(model_name)
        except ollama.ResponseError as e:
          print('Error:', e.error)
          if e.status_code == 404:
            print('Model not found. Run $ ollama pull', model_name, 'to download it.')
            # print('Model not found. Attempting to download...')
            # ollama.pull(model_name)

    # Sends a message to the model and returns the response as a string
    def chat(self, message):
        self.message_history.append({'role': 'user', 'content': message})
        response = self.client.chat(model=self.model, messages=self.message_history)
        self.message_history.append({'role': 'assistant', 'content': response['message']['content']})
        return response

    # Generates text based on a prompt and returns the response as a string
    def generate(self, prompt):
        response = self.client.generate(model=self.model, prompt=prompt)
        return response

    # returns the full response from the model
    def get_response(self, response):
        return response['message']['content']

    # prints the full response from the model
    def print_response(self, response):
        print(self.get_response(response))


class Classifier(ChatModelSync):
    def __init__(self, model_name="gemma:7b", host=None):
        super().__init__(model_name, host)
        self.add_initial_messages()

    def add_message(self, message, response):
        self.message_history.append({'role': 'user', 'content': message})
        self.message_history.append({'role': 'assistant', 'content': response})

    def add_initial_messages(self):
        messages = [{'user':'{"Input": "hey"}'},
                    {"assistant":'{"Text/Chat Generation":"hey"}'},
                    {'user':'{"Input": "what is the weather like today?"}'},
                    {"assistant":'{"Text/Chat Generation":"what is the weather like today?"}'},
                    {'user':'{"Input": "show me a picture of a capybara in a japanese onsen"}'},
                    {"assistant":'{"Image Generation":"a capybara in a japanese onsen"}'},
                    {'user':'{"Input": "tell me about the meiji restoration"}'},
                    {"assistant":'{"Text/Chat Generation":"tell me about the meiji restoration"}'},
                    {'user':'{"{"Input": "how to say thank you in chinese"}'},
                    {"assistant":'{"Translation":"Chinese$~$thank you"}'},
                    {'user':'{"Input": "what is the capital of france?"}'},
                    {"assistant":'{"Text/Chat Generation":"what is the capital of france?"}'},
                    {'user':'{"Input": "show me pikachu but pink"}'},
                    {"assistant":'{"Image Generation":"a pink pikachu"}'},
                    {'user':'{"Input": "translate hello to spanish"}'},
                    {"assistant":'{"Translation":"Spanish$~$hello"}'},
                    {'user':'{"Input": "show me a quesadilla hat"}'},
                    {"assistant":'{"Image Generation":"a quesadilla shaped like a hat"}'},
                    {'user':'{"Input": "what is I am sorry I exist in Tamil"}'},
                    {"assistant":'{"Translation":"Tamil$~$I am sorry I exist"}'}]
        formatted_messages = []
        for message in messages:
            for role, content in message.items():
                formatted_message = {'role': role, 'content': content}
                formatted_messages.append(formatted_message)
        self.message_history = formatted_messages