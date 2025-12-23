from app.nlp.parser import NLPService
from app.nlp.semantic_vectors import SemanticVectorService
from app.knowledge.ontology import OntologyService
from app.knowledge.knowledge_graph import KnowledgeGraphService

class InferenceEngine:
    def __init__(self):
        # Создаем новый экземпляр KnowledgeGraphService при каждой инициализации
        # Это гарантирует, что граф знаний перестроится с актуальными данными
        self.kg_service = KnowledgeGraphService()

    def infer_translation(self, text, context, source_lang='ru', target_lang='en', translation_type='adaptive'):
        # Адаптируем контекст в зависимости от типа перевода
        adapted_context = context.copy()
        if translation_type == 'literal':
            # Буквальный перевод - игнорируем стиль, используем нейтральный
            adapted_context['style'] = 'neutral'
            adapted_context['translation_type'] = 'literal'
        elif translation_type == 'creative':
            # Креативный перевод - приоритет поэтическому стилю
            if adapted_context.get('style') == 'neutral':
                adapted_context['style'] = 'poetic'
            adapted_context['translation_type'] = 'creative'
        else:  # adaptive
            adapted_context['translation_type'] = 'adaptive'
        
        # Проверим, есть ли **вся фраза** в графе знаний
        full_phrase_translation = self.kg_service.get_best_translation(text.lower(), adapted_context, source_lang, target_lang)
        
        # Если перевод найден и отличается от оригинала - возвращаем
        # Важно: проверяем, что full_phrase_translation не None и не равен оригиналу
        if full_phrase_translation is not None and full_phrase_translation != text.lower() and full_phrase_translation != "":
            return full_phrase_translation.capitalize()

        # Если нет прямого перевода фразы — разбираем по словам
        parsed = NLPService.parse(text)
        translated_words = []

        for word in parsed["words"]:
            # Уточняем контекст через онтологию
            refined_context = OntologyService.infer_context(context)

            # Ищем лучший перевод через граф знаний
            best_translation = self.kg_service.get_best_translation(word, refined_context, source_lang, target_lang)
            
            # Fallback через английский для неподдерживаемых языков (только если прямой перевод не найден)
            if best_translation == word and source_lang != 'en' and target_lang != 'en' and source_lang != target_lang:
                # Переводим на английский
                en_word = self.kg_service.get_best_translation(word, refined_context, source_lang, 'en')
                if en_word != word and en_word:
                    # Пытаемся перевести с английского на целевой
                    target_word = self.kg_service.get_best_translation(en_word, refined_context, 'en', target_lang)
                    if target_word != en_word and target_word:
                        best_translation = target_word
                    # Не используем английский как fallback - лучше оставить оригинал

            # Если не найден — НЕ ищем семантически похожие слова для отдельных слов
            # (это может привести к замене на противоположные по смыслу слова)
            # Вместо этого оставляем оригинальное слово
            # Поиск похожих слов отключен, чтобы избежать ошибок типа "люблю" -> "ненавижу"
            
            translated_words.append(best_translation)

        result = " ".join(translated_words)
        
        # Если после перевода по словам результат совпадает с оригиналом - пробуем fallback через английский
        if result.lower() == text.lower() and source_lang != 'en' and target_lang != 'en' and source_lang != target_lang:
            # Fallback: используем английский как промежуточный язык
            en_translation = self.kg_service.get_best_translation(text.lower(), adapted_context, source_lang, 'en')
            if en_translation != text.lower() and en_translation:
                # Затем переводим с английского на целевой язык
                final_translation = self.kg_service.get_best_translation(en_translation.lower(), adapted_context, 'en', target_lang)
                if final_translation != en_translation.lower() and final_translation:
                    result = final_translation
        
        return result.capitalize()

    def _find_similar_phrase(self, text, context):
        for phrase in self.kg_service.graph:
            if SemanticVectorService.cosine_similarity(
                SemanticVectorService.get_vector(text),
                SemanticVectorService.get_vector(phrase)
            ) > 0.7:
                translation = self.kg_service.get_best_translation(phrase, context)
                if translation != phrase:
                    return translation
        return None