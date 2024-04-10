# chat_model.py
# This program uses the Ollama API to chat with a model and generate text based
# on a prompt. It includes both asynchronous and synchronous versions of the 
# chat model, as well as a custom classifier.
#
# Nithun Selva, Clio Zhu
# CS431 Spring 2024

import ollama
import asyncio

# The ChatModel class provides functionalities to interact with the Ollama API,
# allowing for text generation and conversation with a local AI model.
class ChatModel:
    def __init__(self, model_name="gemma:7b", host=None, timeout=60):
        """
        Initializes a new ChatModel instance.
        
        Args:
            model_name (str, optional): The name of the model to use for 
                chatting and text generation.
            host (str, optional): The host URL of the Ollama API service. If 
                None, defaults to the standard API endpoint.
            timeout (int, optional): The timeout for API requests (seconds).
        """
        self.model = model_name
        self.host = host # Host URL, example: "http://localhost:11434"
        self.message_history = [] # Stores the conversation history

        # Initialize the Ollama client, setting a timeout and custom host
        if host:
            self.client = ollama.Client(host=host, timeout = timeout)
        else:
            self.client = ollama.Client()

        # Check if the specified model exists and handle any errors
        try:
            ollama.chat(model_name) # check if model exists
        except ollama.ResponseError as e:
            print('Error:', e.error)
            if e.status_code == 404:
                print('Model not found. Run $ ollama pull', model_name, 'to download it.')
                # print('Model not found. Attempting to download...')
                # ollama.pull(model_name)

    def chat(self, message):
        """
        Sends a message to the model and returns the model's response.
        
        Args:
            message (str): The message to send to the model.
        
        Returns:
            dict: The response from the model.
        """
        # Record the user's message in the history before sending it
        self.message_history.append({'role': 'user', 'content': message})

        # Send the message to the model and get the response
        response = self.client.chat(model=self.model, messages=self.message_history)

        # Record the model's response in the history
        self.message_history.append({'role': 'assistant', 'content': response['message']['content']})
        
        return response

    def generate(self, prompt):
        """
        Generates text only based on the given prompt using the model.
        
        Args:
            prompt (str): The prompt to generate text from.
        
        Returns:
            dict: The response from the model.
        """
        response = self.client.generate(model=self.model, prompt=prompt)
        return response

    def get_response(self, response):
        """
        Extracts and returns the content from the response message.
        
        Args:
            response (dict): The response dictionary containing the message content.
        
        Returns:
            str: The content of the response message.
        """
        return response['message']['content']

    def print_response(self, response):
        """
        Prints the content of the response message.
        
        Args:
            response (dict): The response dictionary containing the message content.
        """
        print(self.get_response(response))

# The Classifier class extends ChatModel to provide additional functionality
# for classifying prompts using the custom Ollama model in classifier.txt.
class Classifier(ChatModel):    
    def __init__(self, model_name="classify", host=None, timeout=60):
        """
        Initializes a new Classifier instance, inheriting from ChatModel.
        
        Args:
            model_name (str, optional): The name of the model to use for 
                classification.
            host (str, optional): The host URL of the Ollama API service. If 
                None, defaults to the standard API endpoint.
            timeout (int, optional): The timeout for API requests (seconds).
        """
        super().__init__(model_name, host, timeout)
        self.add_initial_messages() # Add initial messages to help accuracy

    def add_message(self, message, response):
        """
        Adds a user message and its corresponding assistant response to the message history.
        
        Args:
            message (str): The user message to add.
            response (str): The assistant's response to the message.
        """
        self.message_history.append({'role': 'user', 'content': message})
        self.message_history.append({'role': 'assistant', 'content': response})

    def add_initial_messages(self):
        """
        Populates the message history with predefined messages and responses
        for classification purposes.
        """
        messages = [
            # A series of predefined messages and responses
            # These serve as initial data for classification and model interaction
            {'user':'{"Input": "hey"}'},
            {"assistant":'{"Text/Chat Generation":"hey"}'},
            {'user':'{"Input": "what is the weather like today?"}'},
            {"assistant":'{"Text/Chat Generation":"what is the weather like today?"}'},
            {'user':'{"Input": "show me a picture of a capybara in a japanese onsen"}'},
            {"assistant":'{"Image Generation":"a capybara in a japanese onsen"}'},
            {'user':'{"Input": "tell me about the meiji restoration"}'},
            {"assistant":'{"Text/Chat Generation":"tell me about the meiji restoration"}'},
            {'user':'{"Input": "how to say thank you in chinese"}'},
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
            {"assistant":'{"Translation":"Tamil$~$I am sorry I exist"}'}
        ]
        formatted_messages = []
        # Process and add the predefined messages to the message history
        for message in messages:
            for role, content in message.items():
                formatted_message = {'role': role, 'content': content}
                formatted_messages.append(formatted_message)
        self.message_history = formatted_messages

# The ChatModelAsync class provides functionalities to interact with the Ollama
# API, similar to ChatModel but designed for asynchronous operation.
class ChatModelAsync:
    def __init__(self, model_name="gemma:7b", host=None, timeout=60):
        """
        Initializes a new asynchronous ChatModel instance.
        
        Args:
            model_name (str, optional): The name of the model to use for 
                chatting and text generation.
            host (str, optional): The host URL of the Ollama API service. If 
                None, defaults to the standard API endpoint.
            timeout (int, optional): The timeout for API requests (seconds).
        """
        self.model = model_name
        self.host = host # Host URL, example: "http://localhost:11434"
        self.message_history = [] # Stores the conversation history

        # Initialize the Ollama client, setting a timeout and custom host
        if host:
            self.client = ollama.AsyncClient(host=host, timeout=timeout)
        else:
            self.client = ollama.AsyncClient()

        # Check if the specified model exists and handle any errors
        try:
            ollama.chat(model_name) # check if model exists
        except ollama.ResponseError as e:
            print('Error:', e.error)
            if e.status_code == 404:
                print('Model not found. Run $ ollama pull', model_name, 'to download it.')
                # print('Model not found. Attempting to download...')
                # ollama.pull(model_name)

    async def chat(self, message):
        """
        Sends a message to the model and returns the model's response asynchronously.
        
        Args:
            message (str): The message to send to the model.
        
        Returns:
            dict: The response from the model.
        """
        # Record the user's message in the history before sending it
        self.message_history.append({'role': 'user', 'content': message})

        # Send the message to the model and get the response
        response = await self.client.chat(model=self.model, messages=self.message_history)
        
        # Record the model's response in the history
        self.message_history.append({'role': 'assistant', 'content': response['message']['content']})
        
        # to return, use await asyncio.create_task(chat_model.chat(message))
        return response
    
    async def chat_stream(self, messages):
        """
        Streams the model's response to a message as it is generated and prints it.
        
        Args:
            messages (str): The message text to send to the model.
        """
        # Stream the response from the model and print each part as it arrives
        async for part in await self.client.chat(model=self.model, messages=[
            {'role': 'user', 'content': messages,},], stream=True):
            print(part['message']['content'], end='', flush=True)
        print()
    
    async def generate(self, prompt):
        """
        Generates text only based on the given prompt using the model.
        
        Args:
            prompt (str): The prompt to generate text from.
        
        Returns:
            dict: The response from the model.
        """
        response = await self.client.generate(model=self.model, prompt=prompt)
        return response
    
    def get_response(self, response):
        """
        Extracts and returns the content from the response message.
        
        Args:
            response (dict): The response dictionary containing the message content.
        
        Returns:
            str: The content of the response message.
        """
        return response['message']['content']
    
    def print_response(self, response):
        """
        Prints the content of the response message.
        
        Args:
            response (dict): The response dictionary containing the message content.
        """
        print(self.get_response(response))
