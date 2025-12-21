from app.nlp.parser import NLPService
from app.nlp.semantic_vectors import SemanticVectorService
from app.knowledge.ontology import OntologyService
from app.knowledge.knowledge_graph import KnowledgeGraphService

class InferenceEngine:
    def __init__(self):
        self.kg_service = KnowledgeGraphService()

    def infer_translation(self, text, context):
        print(f"[DEBUG] Text: {text}, Context: {context}")  # ← Добавь
        # Проверим, есть ли **вся фраза** в графе знаний
        full_phrase_translation = self.kg_service.get_best_translation(text.lower(), context)
        print(f"[DEBUG] Full phrase result: {full_phrase_translation}")  # ← Добавь
        if full_phrase_translation != text.lower():
            return full_phrase_translation.capitalize()

        # Если нет — разбираем по словам
        parsed = NLPService.parse(text)
        print(f"[DEBUG] Parsed: {parsed}")  # ← Добавь
        translated_words = []

        for word in parsed["words"]:
            # Уточняем контекст через онтологию
            refined_context = OntologyService.infer_context(context)

            # Ищем лучший перевод через граф знаний
            best_translation = self.kg_service.get_best_translation(word, refined_context)
            print(f"[DEBUG] Word '{word}' -> '{best_translation}'")  # ← Добавь

            # Если не найден — ищем семантически похожие слова
            if best_translation == word:
                similar_words = SemanticVectorService.find_similar_words(word, threshold=0.6)
                if similar_words:
                    best_translation = similar_words[0][0]

            translated_words.append(best_translation)

        result = " ".join(translated_words)
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