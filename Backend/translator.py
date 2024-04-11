# translator.py
# This program uses the Meta NLLB model to translate text samples.
#
# Nithun Selva, Clio Zhu
# CS431 Spring 2024

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from flask import jsonify
import time

# The Translator class provides functionality for translating text samples
# using the Meta NLLB (No Language Left Behind) model.
class Translator:
    models_dict = {
        'nllb-1.3B': 'facebook/nllb-200-1.3B',
        'nllb-3.3B': 'facebook/nllb-200-3.3B',
        'nllb-distilled-600M': 'facebook/nllb-200-distilled-600M',
        'nllb-distilled-1.3B': 'facebook/nllb-200-distilled-1.3B',
    }

    flores_language_codes = {
        'english': 'eng_Latn',
        'chinese': 'zho_Hans',
        'mandarin': 'zho_Hans',
        'cantonese': 'yue_Hant', # no speech support
        'spanish': 'spa_Latn',
        'french': 'fra_Latn',
        'arabic': 'arb_Arab',
        # 'bengali': 'ben_Beng', # no whisper support
        # 'bangla': 'ben_Beng', # no whisper support
        'danish': 'dan_Latn',
        'german': 'deu_Latn',
        'hindi': 'hin_Deva',
        'italian': 'ita_Latn',
        'japanese': 'jpn_Jpan',
        'kannada': 'kan_Knda', # no speech support
        'kazakh': 'kaz_Cyrl', # no speech support
        'korean': 'kor_Hang',
        'dutch': 'nld_Latn',
        'nepali': 'npi_Deva', # no speech support
        'portuguese': 'por_Latn',
        'russian': 'rus_Cyrl',
        'swedish': 'swe_Latn',
        'tamil': 'tam_Taml', # no speech support
        # 'telugu': 'tel_Telu', # no whisper support
        'tagalog': 'tgl_Latn',
        'thai': 'tha_Thai',
        'turkish': 'tur_Latn',
        'urdu': 'urd_Arab',
        'vietnamese': 'vie_Latn',
    }

    def __init__(self, model_name='nllb-distilled-1.3B'):
        """
        Initializes the Translator class with the specified translation model.
        
        Args:
            model_name (str, optional): The key identifying the model in models_dict. 
            Defaults to 'nllb-distilled-1.3B'.
        """
        # Determine the execution device based on CUDA availability
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        # Choose the appropriate data type for tensors based on device capabilities
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # Load the pre-trained model and associated processor
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.models_dict[model_name], torch_dtype=self.torch_dtype)
        self.model.to(self.device) # Move the model to the execution device
        self.tokenizer = AutoTokenizer.from_pretrained(self.models_dict[model_name])

    def translate(self, text, src_lang, tgt_lang):
        """
        Translates the given text from the source language to the target language 
        using the loaded model.
        
        Args:
            text (str): The text to translate.
            src_lang (str): The source language.
            tgt_lang (str): The target language.
        
        Returns:
            dict or tuple: The translation result as a dictionary, or a tuple 
                containing an error message and HTTP status code.
        """
        # Get language codes for the source and target, handling invalid codes
        try:
            source = self.flores_language_codes[src_lang]
        except KeyError:
            return jsonify({'error': 'Invalid source language ' + src_lang}), 400
        try:
            target = self.flores_language_codes[tgt_lang]
        except KeyError:
            return jsonify({'error': 'Invalid target language ' + tgt_lang}), 400
        
        start_time = time.time()
        # Set up a translation pipeline with the loaded model
        translator = pipeline('translation', 
                              model=self.model,
                              torch_dtype=self.torch_dtype,
                              device=self.device,
                              tokenizer=self.tokenizer, 
                              src_lang=source, 
                              tgt_lang=target)
        # Perform the translation and capture the output
        output = translator(text, max_length=400)
        end_time = time.time()

        # Return the translation result as a dictionary
        result = {'inference_time': end_time - start_time, # time to run
                  'source': src_lang,
                  'target': tgt_lang,
                  'input': text,
                  'result': output[0]['translation_text'], # get translated text
                  'task': 'Translation'}
        return result
    