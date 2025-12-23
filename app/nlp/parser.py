from langdetect import detect, DetectorFactory

# Устанавливаем seed для стабильности определения языка
DetectorFactory.seed = 0

def parse(text):
    try:
        detected_lang = detect(text)
        
        # Улучшенная логика для коротких текстов
        if len(text.split()) <= 3:
            text_lower = text.lower()
            # Английские фразы
            if text_lower in ['i love you', 'hello', 'bye', 'thanks', 'yes', 'no', 'i hate you', 'i like you', 'goodbye']:
                detected_lang = 'en'
            # Русские фразы - проверяем по характерным словам
            elif any(word in text_lower for word in ['я', 'ты', 'тебя', 'меня', 'мне', 'люблю', 'нравишься', 'нравится']):
                detected_lang = 'ru'
        
        # Если langdetect определил как 'uk', но текст содержит русские слова - исправляем на 'ru'
        if detected_lang == 'uk':
            russian_indicators = ['я', 'ты', 'тебя', 'меня', 'мне', 'люблю', 'нравишься', 'нравится', 'спасибо', 'привет', 'пока']
            text_lower = text.lower()
            if any(indicator in text_lower for indicator in russian_indicators):
                detected_lang = 'ru'
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