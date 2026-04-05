"""
Модуль с регулярными выражениями для трёх заданий
"""


class RegexPatterns:
    """
    Класс, содержащий регулярные выражения для поиска
    """
    
    # Задание 1: Слова, начинающиеся на букву m или M
    TASK1_PATTERN = r'\b[mM][a-zA-Z]*\b'
    TASK1_DESCRIPTION = "Слова, начинающиеся на m или M"
    
    # Задание 2: Восьмеричные числа
    TASK2_PATTERN = r'\b(?:0o[0-7]+|&O[0-7]+|0[0-7]+)\b'
    TASK2_DESCRIPTION = "Восьмеричные числа (форматы: 0o755, &O755, 0755)"
    
    # Задание 3: Путь к файлу в Unix
    TASK3_PATTERN = r'(?:/[\w\-\.]+(?:/[\w\-\.]+)*(?:\.[a-zA-Z0-9]+)?/?|/)'
    TASK3_DESCRIPTION = "Путь к файлу в Unix"
    
    @staticmethod
    def get_patterns_dict():
        """Возвращает словарь с паттернами"""
        return {
            "Слова на m/M": RegexPatterns.TASK1_PATTERN,
            "Восьмеричные числа": RegexPatterns.TASK2_PATTERN,
            "Пути Unix": RegexPatterns.TASK3_PATTERN
        }
    
    @staticmethod
    def get_task_info(task_name):
        """Возвращает информацию о задании"""
        info = {
            "Слова на m/M": {
                "pattern": RegexPatterns.TASK1_PATTERN,
                "description": RegexPatterns.TASK1_DESCRIPTION,
                "examples_correct": [
                    "machine", "Mouse", "mountain", "Moscow", "m", "M"
                ],
                "examples_incorrect": [
                    "am", "home", "Motorcycle", "m2", "m_ouse"
                ]
            },
            "Восьмеричные числа": {
                "pattern": RegexPatterns.TASK2_PATTERN,
                "description": RegexPatterns.TASK2_DESCRIPTION,
                "examples_correct": [
                    "0755", "0o755", "&O755", "0", "0777", "0o0"
                ],
                "examples_incorrect": [
                    "755", "0o8", "&O8", "08", "0x755", "0b101"
                ]
            },
            "Пути Unix": {
                "pattern": RegexPatterns.TASK3_PATTERN,
                "description": RegexPatterns.TASK3_DESCRIPTION,
                "examples_correct": [
                    "/home/user/file.txt",
                    "/etc/passwd",
                    "/var/log/syslog",
                    "/usr/bin/python3",
                    "/",
                    "/home/user/"
                ],
                "examples_incorrect": [
                    "home/file.txt",
                    "C:\\Windows\\file.txt",
                    "/home//user/file"
                ]
            }
        }
        return info.get(task_name, {})