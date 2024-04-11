import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from flask import jsonify
import time

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
    }

    def __init__(self, model_name='nllb-distilled-1.3B'):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.models_dict[model_name], torch_dtype=self.torch_dtype)
        self.model.to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.models_dict[model_name])

    def translate(self, text, src_lang, tgt_lang):
        try:
            source = self.flores_language_codes[src_lang]
        except KeyError:
            return jsonify({'error': 'Invalid source language ' + src_lang}), 400
        try:
            target = self.flores_language_codes[tgt_lang]
        except KeyError:
            return jsonify({'error': 'Invalid target language ' + tgt_lang}), 400
        
        start_time = time.time()
        translator = pipeline('translation', 
                              model=self.model,
                              torch_dtype=self.torch_dtype,
                              device=self.device,
                              tokenizer=self.tokenizer, 
                              src_lang=source, 
                              tgt_lang=target)
        output = translator(text, max_length=400)
        end_time = time.time()

        result = {'inference_time': end_time - start_time,
                  'source': src_lang,
                  'target': tgt_lang,
                  'input': text,
                  'result': output[0]['translation_text'],
                  'task': 'Translation'}
        return result
    