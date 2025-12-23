"""
State Machine для управления состояниями UI
"""
from enum import Enum

class UIState(Enum):
    """Состояния UI системы"""
    ENTRY = "entry"  # Вход
    VIEW = "view"  # Просмотр
    EDIT = "edit"  # Редактирование
    APPROVAL = "approval"  # Утверждение
    LOCALIZATION = "localization"  # Локализация

class StateMachineService:
    """Сервис для управления состояниями UI"""
    
    # Матрица переходов состояний
    TRANSITIONS = {
        UIState.ENTRY: [UIState.VIEW],
        UIState.VIEW: [UIState.EDIT, UIState.APPROVAL, UIState.LOCALIZATION],
        UIState.EDIT: [UIState.VIEW, UIState.APPROVAL],
        UIState.APPROVAL: [UIState.VIEW, UIState.LOCALIZATION],
        UIState.LOCALIZATION: [UIState.VIEW, UIState.APPROVAL]
    }
    
    def __init__(self, initial_state=UIState.ENTRY):
        self.current_state = initial_state
        self.state_history = [initial_state]
    
    def can_transition(self, target_state):
        """Проверяет, возможен ли переход в целевое состояние"""
        return target_state in self.TRANSITIONS.get(self.current_state, [])
    
    def transition(self, target_state):
        """Выполняет переход в целевое состояние"""
        if self.can_transition(target_state):
            self.current_state = target_state
            self.state_history.append(target_state)
            return True
        return False
    
    def get_current_state(self):
        """Возвращает текущее состояние"""
        return self.current_state
    
    def get_available_transitions(self):
        """Возвращает список доступных переходов"""
        return self.TRANSITIONS.get(self.current_state, [])
    
    def reset(self):
        """Сбрасывает состояние машины в начальное"""
        self.current_state = UIState.ENTRY
        self.state_history = [UIState.ENTRY]

