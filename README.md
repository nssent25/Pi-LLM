# CS431 Pi-LLM

## Introduction
This is the code for a Raspberry Pi-based personal assistant. It uses open source libraries to perform tasks such as voice recognition, translation, image generation, and conversation. **This project is an excuse to mess with open source models and test them.** The project report is under ```Report/report.pdf```

## Server:
- [x] Flask server: ```server_main.py```
- [x] Chat model and classifier: ```chat_model.py```
- [x] Image generation: ```image_gen.py```
- [x] Translation: ```translator.py```
- [x] Transcription: ```whisper_speech.py```
- [ ] Text-to-speech: ```speech_transcribe.py```

## Client:
- [x] Recorder: ```audio.py```
- [x] Client-server interaction: ```client.py```
- [x] GUI: ```main_new.py```
- [ ] NFC emulation: ```nfctest.py, cli.py, beam.py```

## What needs work:
- [ ] Recognize and classify prompt accurately (classifier.txt, chat_model.py, fails hilariously sometimes, try Llama3?)
- [ ] Text-to-speech (Meta MBART?)
- [ ] NFC emulation pulls up Apple Pay instead of URL (PN532 issues)
