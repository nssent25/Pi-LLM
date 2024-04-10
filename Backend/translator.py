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
        'English': 'eng_Latn',
        'Chinese': 'zho_Hans',
        'Mandarin': 'zho_Hans',
    }

    def __init__(self, model_name='nllb-distilled-1.3B'):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.models_dict[model_name])
        self.tokenizer = AutoTokenizer.from_pretrained(self.models_dict[model_name])

    def translate(self, source_lang, target_lang, text):
        try:
            source = self.flores_language_codes[source_lang]
        except KeyError:
            return jsonify({'error': 'Invalid source language ' + source_lang}), 400
        try:
            target = self.flores_language_codes[target_lang]
        except KeyError:
            return jsonify({'error': 'Invalid target language ' + target_lang}), 400
        
        start_time = time.time()
        translator = pipeline('translation', model=self.model,
                              tokenizer=self.tokenizer, src_lang=source, tgt_lang=target)
        output = translator(text, max_length=400)
        end_time = time.time()

        result = {'inference_time': end_time - start_time,
                  'source': source_lang,
                  'target': target_lang,
                  'input': text,
                  'result': output[0]['translation_text'],
                  'task': 'Translation'}
        return result
    