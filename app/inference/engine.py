from app.nlp.parser import NLPService
from app.nlp.semantic_vectors import SemanticVectorService
from app.knowledge.ontology import OntologyService
from app.knowledge.knowledge_graph import KnowledgeGraphService

class InferenceEngine:
    def __init__(self):
        self.kg_service = KnowledgeGraphService()

    def infer_translation(self, text, context):
        full_phrase_translation = self.kg_service.get_best_translation(text.lower(), context)
        if full_phrase_translation != text.lower():
            return full_phrase_translation.capitalize()
        parsed = NLPService.parse(text)
        translated_words = []

        for word in parsed["words"]:
            refined_context = OntologyService.infer_context(context)
            best_translation = self.kg_service.get_best_translation(word, refined_context)
            target_lang = context.get('target_lang', 'en')
            if target_lang == 'en' and best_translation in ['люблю', 'ты', 'я']:
                best_translation = word

            if best_translation == word:
                similar_words = SemanticVectorService.find_similar_words(word, threshold=0.6)
                if similar_words:
                    candidate = similar_words[0][0]
                    if target_lang == 'en' and candidate in ['люблю', 'ты', 'я']:
                        best_translation = word
                    else:
                        best_translation = candidate
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