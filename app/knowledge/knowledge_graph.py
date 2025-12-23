import json
from pathlib import Path
from app.services.storage_service import StorageService

DATA_DIR = Path(__file__).parent.parent / 'data'

class KnowledgeGraphService:
    def __init__(self):
        self.graph_file = DATA_DIR / 'knowledge_graph.json'
        self.dataset_file = DATA_DIR / 'dataset.json'

        # Загружаем датасеты
        self.dataset = StorageService.load_json('dataset.json', [])
        # Загружаем мультиязычный датасет
        multilang_dataset = StorageService.load_json('dataset_multilang.json', [])
        # Загружаем датасет с базовыми фразами
        common_phrases = StorageService.load_json('dataset_common_phrases.json', [])
        # Объединяем все датасеты
        self.dataset.extend(multilang_dataset)
        self.dataset.extend(common_phrases)

        # Всегда строим граф из датасета (перестраиваем при каждом запуске для актуальности)
        self.graph = self._build_graph_from_dataset()
        # Сохраняем граф для визуализации, но при следующем запуске он будет перестроен
        StorageService.save_json('knowledge_graph.json', self.graph)

    def _build_graph_from_dataset(self):
        # Поддержка разных языковых пар: {source_lang: {word: {target_lang: {translation: data}}}}
        # Старый формат для обратной совместимости: {word: {translation: data}} для ru->en
        graph = {}
        graph_by_lang = {}  # Новый формат: {source_lang: {word: {target_lang: {translation: data}}}}
        
        for entry in self.dataset:
            # Поддерживаем ru->en (старый формат для обратной совместимости)
            if 'ru' in entry and 'en' in entry:
                ru = entry['ru']
                en = entry['en']
                contexts = entry.get('contexts', [])
                weight = entry.get('weight', 0.8)

                # Старый формат (для обратной совместимости)
                if ru not in graph:
                    graph[ru] = {}
                if en not in graph[ru]:
                    graph[ru][en] = {"weight": weight, "contexts": []}
                graph[ru][en]["contexts"].extend(contexts)
                
                # Новый формат (для поддержки разных языков)
                if 'ru' not in graph_by_lang:
                    graph_by_lang['ru'] = {}
                if ru not in graph_by_lang['ru']:
                    graph_by_lang['ru'][ru] = {}
                if 'en' not in graph_by_lang['ru'][ru]:
                    graph_by_lang['ru'][ru]['en'] = {}
                if en not in graph_by_lang['ru'][ru]['en']:
                    graph_by_lang['ru'][ru]['en'][en] = {"weight": weight, "contexts": []}
                graph_by_lang['ru'][ru]['en'][en]["contexts"].extend(contexts)
            
            # Поддержка других языковых пар (расширяемый формат)
            # Формат: {"source": "ru", "target": "fr", "source_text": "...", "target_text": "...", ...}
            if 'source' in entry and 'target' in entry:
                source_lang = entry['source']
                target_lang = entry['target']
                source_text = entry.get('source_text', '')
                target_text = entry.get('target_text', '')
                contexts = entry.get('contexts', [])
                weight = entry.get('weight', 0.8)
                
                if source_lang not in graph_by_lang:
                    graph_by_lang[source_lang] = {}
                if source_text not in graph_by_lang[source_lang]:
                    graph_by_lang[source_lang][source_text] = {}
                if target_lang not in graph_by_lang[source_lang][source_text]:
                    graph_by_lang[source_lang][source_text][target_lang] = {}
                if target_text not in graph_by_lang[source_lang][source_text][target_lang]:
                    graph_by_lang[source_lang][source_text][target_lang][target_text] = {"weight": weight, "contexts": []}
                
                graph_by_lang[source_lang][source_text][target_lang][target_text]["contexts"].extend(contexts)
        
        # Сохраняем оба формата
        self.graph_by_lang = graph_by_lang
        return graph  # Возвращаем старый формат для обратной совместимости

    def get_best_translation(self, word, context, source_lang='ru', target_lang='en'):
        # Поддержка старого формата (ru->en) - обратная совместимость
        if source_lang == 'ru' and target_lang == 'en':
            translations = self.graph.get(word.lower(), {})
        else:
            # Новый формат для других языковых пар
            translations = {}
            if hasattr(self, 'graph_by_lang'):
                lang_graph = self.graph_by_lang.get(source_lang, {})
                if lang_graph:
                    word_translations = lang_graph.get(word.lower(), {})
                    if word_translations:
                        target_translations = word_translations.get(target_lang, {})
                        # Преобразуем формат: {translation_text: {weight, contexts}}
                        for trans_text, trans_data in target_translations.items():
                            translations[trans_text] = trans_data
        best = None
        best_weight = 0
        fallback_best = None
        fallback_weight = 0

        # Сначала ищем точное совпадение контекста
        for trans, data in translations.items():
            # Сохраняем лучший перевод как fallback (на случай, если контекст не совпадет)
            if data["weight"] > fallback_weight:
                fallback_best = trans
                fallback_weight = data["weight"]
            
            # Ищем совпадение контекста - улучшенная логика
            for rule in data["contexts"]:
                match_score = 0
                total_params = 0
                
                # Проверяем совпадение параметров
                for k, v in rule.items():
                    total_params += 1
                    if context.get(k) == v:
                        match_score += 1
                    elif k == 'style' and context.get(k) == 'neutral' and v in ['casual', 'formal']:
                        # Нейтральный стиль частично совпадает с casual/formal
                        match_score += 0.5
                
                # Если все параметры совпали или совпало большинство
                if match_score > 0 and (match_score == total_params or match_score / total_params >= 0.7):
                    # Учитываем вес и количество совпадений
                    combined_weight = data["weight"] * (match_score / total_params)
                    if combined_weight > best_weight:
                        best = trans
                        best_weight = combined_weight

        # Если нашли точное совпадение - возвращаем его, иначе fallback
        result = best if best is not None else fallback_best
        return result if result is not None else word  # Если не найден → возвращаем оригинал
    
    def update_from_feedback(self, original, draft, final):
        """Обновляет граф знаний на основе обратной связи пользователя"""
        # Если финальная версия отличается от черновика - добавляем новую пару в датасет
        if final and final != draft and final.lower() != original.lower():
            # Добавляем новую пару в датасет (только для ru->en пока)
            new_entry = {
                'ru': original.lower(),
                'en': final.lower(),
                'contexts': [{'style': 'adaptive'}],
                'weight': 0.9
            }
            # Загружаем текущий датасет
            current_dataset = StorageService.load_json('dataset.json', [])
            # Проверяем, нет ли уже такой записи
            if not any(e.get('ru') == original.lower() and e.get('en') == final.lower() for e in current_dataset):
                current_dataset.append(new_entry)
                StorageService.save_json('dataset.json', current_dataset)
                # Перестраиваем граф
                self.dataset = current_dataset
                self.graph = self._build_graph_from_dataset()
                StorageService.save_json('knowledge_graph.json', self.graph)