"""
Модуль для поиска подстрок с использованием регулярных выражений и конечных автоматов
"""

import re
from typing import List, Dict, Tuple


class SearchResult:
    """Класс для хранения результата поиска"""
    
    def __init__(self, text: str, start_line: int, start_char: int, length: int):
        self.text = text
        self.start_line = start_line
        self.start_char = start_char
        self.length = length
        
    def to_dict(self):
        return {
            "text": self.text,
            "line": self.start_line,
            "char": self.start_char,
            "length": self.length
        }


class OctalNumberAutomaton:
    """Конечный автомат для поиска восьмеричных чисел"""
    
    def __init__(self):
        # Состояния: 0 - начальное, 1 - после '0', 2 - после '0o', 3 - после '&', 
        # 4 - после '&O', 5 - в числе после 0o, 6 - в числе после &O, 7 - в числе после 0
        self.transitions = {
            0: {'0': 1, '&': 3},
            1: {'o': 2},
            2: {},
            3: {'O': 4},
            4: {},
            5: {},
            6: {},
            7: {}
        }
        
        # Добавить переходы для восьмеричных цифр
        octal_digits = '01234567'
        for digit in octal_digits:
            self.transitions[1][digit] = 7  # из 1 (после 0) в 7
            self.transitions[2][digit] = 5  # из 2 (после 0o) в 5
            self.transitions[4][digit] = 6  # из 4 (после &O) в 6
            self.transitions[5][digit] = 5  # в числе 0o
            self.transitions[6][digit] = 6  # в числе &O
            self.transitions[7][digit] = 7  # в числе 0
        
        self.accepting_states = {5, 6, 7}
        self.start_state = 0
    
    def search(self, text: str) -> List[Dict]:
        """Поиск восьмеричных чисел в тексте"""
        results = []
        i = 0
        n = len(text)
        
        while i < n:
            state = self.start_state
            start_pos = i
            current_pos = i
            found = False
            
            while current_pos < n:
                char = text[current_pos]
                if char in self.transitions[state]:
                    state = self.transitions[state][char]
                    current_pos += 1
                    if state in self.accepting_states:
                        found = True
                        end_pos = current_pos
                else:
                    break
            
            if found:
                match = text[start_pos:end_pos]
                # Проверка границ слова
                is_word_boundary_start = (start_pos == 0 or not text[start_pos - 1].isalnum())
                is_word_boundary_end = (end_pos == n or not text[end_pos].isalnum())
                
                if is_word_boundary_start and is_word_boundary_end:
                    # Вычисление строки и позиции
                    line_num = text[:start_pos].count('\n') + 1
                    last_newline = text.rfind('\n', 0, start_pos)
                    char_pos = start_pos - last_newline - 1 if last_newline != -1 else start_pos
                    
                    result = SearchResult(
                        text=match,
                        start_line=line_num,
                        start_char=char_pos + 1,
                        length=len(match)
                    )
                    results.append(result.to_dict())
                
                i = end_pos
            else:
                i += 1
        
        return results


class UnixPathAutomaton:
    """Конечный автомат для поиска путей Unix"""
    
    def __init__(self):
        # Состояния: 0 - начальное, 1 - после '/', 2 - в компоненте, 3 - после компонента, 
        # 4 - после '.', 5 - в расширении
        self.transitions = {
            0: {'/': 1},
            1: {},
            2: {},
            3: {},
            4: {},
            5: {}
        }
        
        # Символы для компонентов пути
        path_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.'
        ext_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        for char in path_chars:
            self.transitions[1][char] = 2  # из 1 в 2
            self.transitions[2][char] = 2  # в компоненте
            self.transitions[3]['/'] = 1   # из 3 в 1
            self.transitions[3]['.'] = 4   # из 3 в 4
            self.transitions[5]['/'] = 1   # из 5 в 1
        
        for char in ext_chars:
            self.transitions[4][char] = 5  # из 4 в 5
            self.transitions[5][char] = 5  # в расширении
        
        self.accepting_states = {1, 2, 3, 5}  # 1 для '/', 2 для конца компонента, 3 для конца пути, 5 для конца с расширением
        self.start_state = 0
    
    def search(self, text: str) -> List[Dict]:
        """Поиск путей Unix в тексте"""
        results = []
        i = 0
        n = len(text)
        
        while i < n:
            state = self.start_state
            start_pos = i
            current_pos = i
            found = False
            
            while current_pos < n:
                char = text[current_pos]
                if char in self.transitions[state]:
                    state = self.transitions[state][char]
                    current_pos += 1
                    if state in self.accepting_states:
                        found = True
                        end_pos = current_pos
                else:
                    # Если не можем перейти, но в принимающем состоянии, можем остановиться
                    if state in self.accepting_states:
                        found = True
                        end_pos = current_pos
                    break
            
            # Также проверить, если в конце строки и состояние принимающее
            if current_pos == n and state in self.accepting_states:
                found = True
                end_pos = current_pos
            
            if found:
                match = text[start_pos:end_pos]
                # Проверка, что перед / не слово (для (?<!\w))
                is_valid_start = (start_pos == 0 or not text[start_pos].isalnum() or text[start_pos] != '/')
                # Для нашего автомата, поскольку начинаем с /, и (?<!\w)/ означает / не после слова
                is_valid_start = (start_pos == 0 or not text[start_pos - 1].isalnum())
                
                if is_valid_start:
                    # Вычисление строки и позиции
                    line_num = text[:start_pos].count('\n') + 1
                    last_newline = text.rfind('\n', 0, start_pos)
                    char_pos = start_pos - last_newline - 1 if last_newline != -1 else start_pos
                    
                    result = SearchResult(
                        text=match,
                        start_line=line_num,
                        start_char=char_pos + 1,
                        length=len(match)
                    )
                    results.append(result.to_dict())
                
                i = end_pos
            else:
                i += 1
        
        return results


class RegexSearchEngine:
    """Движок поиска с использованием регулярных выражений и автоматов"""
    
    def __init__(self):
        self.results = []
        self.full_text = ""
        self.pattern = None
        self.octal_automaton = OctalNumberAutomaton()
        self.unix_path_automaton = UnixPathAutomaton()
        
    def search(self, text: str, pattern: str, task_name: str = "", ignore_case: bool = False) -> List[Dict]:
        """Выполняет поиск всех совпадений в тексте"""
        self.full_text = text
        self.results = []
        
        if not text or not pattern:
            return []
        
        # Для восьмеричных чисел и путей Unix используем автоматы
        if task_name == "Восьмеричные числа":
            self.results = self.octal_automaton.search(text)
            return self.results
        elif task_name == "Пути Unix":
            self.results = self.unix_path_automaton.search(text)
            return self.results
        
        # Для остальных используем регулярные выражения
        flags = re.MULTILINE
        if ignore_case:
            flags |= re.IGNORECASE
            
        try:
            regex = re.compile(pattern, flags)
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for match in regex.finditer(line):
                    char_pos_in_line = match.start()
                    start_char = char_pos_in_line + 1
                    
                    result = SearchResult(
                        text=match.group(),
                        start_line=line_num,
                        start_char=start_char,
                        length=len(match.group())
                    )
                    self.results.append(result)
                    
            return [r.to_dict() for r in self.results]
            
        except re.error as e:
            print(f"Ошибка в регулярном выражении: {e}")
            return []
    
    def get_global_position(self, result_index: int) -> Tuple[int, int]:
        """Получает глобальную позицию в тексте для выделения"""
        if result_index >= len(self.results):
            return (0, 0)
            
        result = self.results[result_index]
        lines = self.full_text.split('\n')
        global_start = 0
        
        for i in range(result.start_line - 1):
            global_start += len(lines[i]) + 1
            
        global_start += (result.start_char - 1)
        global_end = global_start + result.length
        
        return (global_start, global_end)
    
    def get_count(self) -> int:
        """Возвращает количество найденных совпадений"""
        return len(self.results)