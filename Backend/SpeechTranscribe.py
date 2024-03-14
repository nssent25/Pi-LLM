from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio

class SpeechTranscriber:
    def __init__(self, model_name="facebook/seamless-m4t-v2-large"):
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = SeamlessM4Tv2Model.from_pretrained(model_name)

    def text_to_speech(self, text, src_lang="eng", tgt_lang="rus"):
        text_inputs = self.processor(text=text, src_lang=src_lang, return_tensors="pt")
        audio_array = self.model.generate(**text_inputs, tgt_lang=tgt_lang)[0].cpu().numpy().squeeze()
        return audio_array

    def speech_to_text(self, audio_path, tgt_lang="rus"):
        audio, orig_freq = torchaudio.load(audio_path)
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000)
        audio_inputs = self.processor(audios=audio, return_tensors="pt")
        text_array = self.model.generate(**audio_inputs, tgt_lang=tgt_lang)[0].cpu().numpy().squeeze()
        return text_array

    def text_to_text(self, text, src_lang="eng", tgt_lang="rus"):
        text_inputs = self.processor(text=text, src_lang=src_lang, return_tensors="pt")
        text_array = self.model.generate(**text_inputs, tgt_lang=tgt_lang)[0].cpu().numpy().squeeze()
        return text_array