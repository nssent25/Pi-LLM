# whisper_speech.py
# This program uses the OpenAI Whisper model to transcribe and translate audio samples.
#
# Nithun Selva, Clio Zhu
# CS431 Spring 2024

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset

# The WhisperSpeech class provides functionality for transcribing and translating
# audio samples using the OpenAI Whisper model.
class WhisperSpeech:
    def __init__(self, model_id="openai/whisper-large-v3"):
        """
        Initializes the WhisperSpeech class with the specified model, setting 
        up the necessary components for speech recognition and translation.
        
        Args:
            model_id (str, optional): Identifier for the pre-trained Whisper 
                model. Defaults to "openai/whisper-large-v3".
        """
        # Determine the execution device based on CUDA availability
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        # Choose the appropriate data type for tensors based on device capabilities
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        # Load the pre-trained Whisper model and associated processor
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        self.model.to(self.device) # Move the model to the execution device
        self.processor = AutoProcessor.from_pretrained(model_id)

        # Setup a pipeline for automatic speech recognition tasks
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=256, # Maximum number of new tokens to generate
            chunk_length_s=30, # 30-second chunks
            batch_size=16, # Process 16 chunks at a time
            return_timestamps=True,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )

    def transcribe(self, audio_sample):
        """
        Transcribes a given audio sample into text using the OpenAI Whisper
        model. Retains the language of the source audio.
        
        Args:
            audio_sample (str or data): The audio sample to transcribe.
        
        Returns:
            dict: The transcription result including the text and language.
        """
        # Process the audio sample and return the transcription results
        result = self.pipe(audio_sample, return_language=True)
        return result

    def translate(self, audio_sample, lang="english"):
        """
        Translates the given audio sample to the specified language using the Whisper model.
        
        Args:
            audio_sample (str or data): The audio sample to translate.
            lang (str, optional): Target language for translation, defaults to "english".
        
        Returns:
            dict: The translation result including the translated text and language.
        """
        # Process the audio sample, specifying translation as the task
        result = self.pipe(audio_sample, 
                           generate_kwargs={
                               "language" : lang,
                               "task": "translate"},
                               return_language=True)
        return result
    
# # Usage
# transcriber = WhisperSpeech()
# dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
# sample = dataset[0]["audio"]
# print(transcriber.transcribe(sample)["text"])