from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio

class SpeechTranscriber:
    language_codes = {
        'english': 'eng',
        'chinese': 'cmn',
        'mandarin': 'cmn',
        'cantonese': 'yue', # no speech support
        'spanish': 'spa',
        'french': 'fra',
        'arabic': 'arb',
        # 'bengali': 'ben', # no whisper support
        # 'bangla': 'ben', # no whisper support
        'danish': 'dan',
        'german': 'deu',
        'hindi': 'hin',
        'italian': 'ita',
        'japanese': 'jpn',
        'kannada': 'kan', # no speech support
        'kazakh': 'kaz', # no speech support
        'korean': 'kor',
        'dutch': 'nld',
        'nepali': 'npi', # no speech support
        'russian': 'rus',
        'swedish': 'swe',
        'tamil': 'tam', # no speech support
        # 'telugu': 'tel', # no whisper support
        'tagalog': 'tgl',
        'thai': 'tha',
        'turkish': 'tur',
        'urdu': 'urd',
        'vietnamese': 'vie',
    }

    def __init__(self, model_name="facebook/seamless-m4t-v2-large"):
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = SeamlessM4Tv2Model.from_pretrained(model_name)

    def text_to_speech(self, text, src_lang="english", tgt_lang="english"):
        text_inputs = self.processor(text=text, 
                                     src_lang=self.language_codes[src_lang], 
                                     return_tensors="pt")
        audio_array = self.model.generate(**text_inputs, 
                                          tgt_lang=self.language_codes[tgt_lang]
                                          )[0].cpu().numpy().squeeze()
        return audio_array, self.model.config.sample_rate

    def speech_to_text(self, audio_path, tgt_lang="chinese"):
        audio, orig_freq = torchaudio.load(audio_path)
        audio = torchaudio.functional.resample(audio, 
                                               orig_freq=orig_freq, 
                                               new_freq=16_000)
        audio_inputs = self.processor(audios=audio, 
                                      return_tensors="pt")
        text_array = self.model.generate(**audio_inputs, 
                                         tgt_lang=self.language_codes[tgt_lang]
                                         )[0].cpu().numpy().squeeze()
        return text_array

    def translate(self, text, src_lang="english", tgt_lang="chinese"):
        text_inputs = self.processor(text=text, 
                                     src_lang=self.language_codes[src_lang],
                                     return_tensors="pt")
        text_array = self.model.generate(**text_inputs, 
                                         tgt_lang=self.language_codes[tgt_lang],
                                         generate_speech=False
                                         )[0].cpu().numpy().squeeze()
        return text_array