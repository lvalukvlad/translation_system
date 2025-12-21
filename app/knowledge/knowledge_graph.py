import json
from pathlib import Path
from app.services.storage_service import StorageService

DATA_DIR = Path(__file__).parent.parent / 'data'

class KnowledgeGraphService:
    def __init__(self):
        self.graph_file = DATA_DIR / 'knowledge_graph.json'
        self.dataset_file = DATA_DIR / 'dataset.json'

        # Загружаем датасет
        self.dataset = StorageService.load_json('dataset.json', [])

        # Всегда строим граф из датасета
        self.graph = self._build_graph_from_dataset()
        StorageService.save_json('knowledge_graph.json', self.graph)

    def _build_graph_from_dataset(self):
        graph = {}
        for entry in self.dataset:
            ru = entry['ru']
            en = entry['en']
            contexts = entry.get('contexts', [])
            weight = entry.get('weight', 0.8)

            if ru not in graph:
                graph[ru] = {}

            if en not in graph[ru]:
                graph[ru][en] = {"weight": weight, "contexts": []}

            graph[ru][en]["contexts"].extend(contexts)
        return graph

    def get_best_translation(self, word, context):
        translations = self.graph.get(word.lower(), {})
        best = None
        best_weight = 0

        for trans, data in translations.items():
            for rule in data["contexts"]:
                match = True
                for k, v in rule.items():
                    if context.get(k) != v:
                        match = False
                        break
                if match and data["weight"] > best_weight:
                    best = trans
                    best_weight = data["weight"]  # ← Исправлено: убран лишний отступ

        return best or word  # Если не найден → возвращаем оригинал