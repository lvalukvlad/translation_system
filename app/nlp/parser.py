from langdetect import detect

def parse(text):
    try:
        detected_lang = detect(text)
        if len(text.split()) <= 3:
            if text.lower() in ['i love you', 'hello', 'bye', 'thanks', 'yes', 'no', 'i hate you', 'i like you', 'goodbye']:
                detected_lang = 'en'
    except:
        detected_lang = 'unknown'

    return {
        'words': text.split(),
        'detected_language': detected_lang
    }

class NLPService:
    @staticmethod
    def parse(text):
        return parse(text)