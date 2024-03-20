# chat_model.py

import ollama
import asyncio

class ChatModel:
    def __init__(self, model_name="llama2", host=None):
        self.model = model_name
        self.host = host
        if host:
            self.client = ollama.AsyncClient(host=host)
        else:
            self.client = ollama.AsyncClient()

    def chat(self, messages):
        response = self.client.chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': messages,
            },
        ])
        return response
    
    def generate(self, prompt):
        response = self.client.generate(model=self.model, prompt=prompt)
        return response
    