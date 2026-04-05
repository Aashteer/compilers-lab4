"""
Модуль с вкладкой для поиска по регулярным выражениям
"""

import re
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from regex_patterns import RegexPatterns
from search_module import RegexSearchEngine


class RegexSearchTab(QWidget):
    """Вкладка для поиска по регулярным выражениям"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.search_engine = RegexSearchEngine()
        self.current_results = []
        self.current_font_size = 10
        
        self.initUI()
        
    def initUI(self):
        """Инициализация интерфейса вкладки"""
        main_layout = QVBoxLayout(self)
        
        # Верхняя панель управления
        control_group = QGroupBox(self.tr("Управление поиском"))
        control_layout = QHBoxLayout(control_group)
        
        # Выбор типа поиска
        control_layout.addWidget(QLabel(self.tr("Тип поиска:")))
        self.search_combo = QComboBox()
        self.search_combo.addItems(list(RegexPatterns.get_patterns_dict().keys()))
        control_layout.addWidget(self.search_combo)
        
        # Флаг игнорирования регистра
        self.ignore_case_check = QCheckBox(self.tr("Игнорировать регистр"))
        control_layout.addWidget(self.ignore_case_check)
        
        # Кнопка поиска
        self.search_button = QPushButton(self.tr("Найти"))
        self.search_button.setShortcut('F5')
        self.search_button.clicked.connect(self.perform_search)
        control_layout.addWidget(self.search_button)
        
        # Кнопка очистки
        self.clear_button = QPushButton(self.tr("Очистить"))
        self.clear_button.clicked.connect(self.clear_results)
        control_layout.addWidget(self.clear_button)
        
        # Кнопка примера
        self.example_button = QPushButton(self.tr("Загрузить пример"))
        self.example_button.clicked.connect(self.load_examples)
        control_layout.addWidget(self.example_button)
        
        control_layout.addStretch()
        main_layout.addWidget(control_group)
        
        # Создание разделителя для результатов и информации
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Верхняя часть - результаты поиска
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Информация о количестве результатов
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel(self.tr("Найдено совпадений:")))
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        count_layout.addWidget(self.count_label)
        count_layout.addStretch()
        results_layout.addLayout(count_layout)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            self.tr("Найденная подстрока"),
            self.tr("Строка"),
            self.tr("Позиция"),
            self.tr("Длина")
        ])
        
        # Настройка таблицы
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.itemSelectionChanged.connect(self.on_result_select)
        
        results_layout.addWidget(self.results_table)
        
        # Нижняя часть - информация
        info_tabs = QTabWidget()
        
        # Вкладка с описанием задания
        task_info_widget = QWidget()
        task_info_layout = QVBoxLayout(task_info_widget)
        self.task_info_browser = QTextBrowser()
        self.task_info_browser.setStyleSheet("QTextBrowser { background-color: #2b2b2b; color: #ffffff; }")
        task_info_layout.addWidget(self.task_info_browser)
        info_tabs.addTab(task_info_widget, self.tr("Информация о задании"))
        
        # Вкладка с примерами
        examples_widget = QWidget()
        examples_layout = QVBoxLayout(examples_widget)
        self.examples_browser = QTextBrowser()
        self.examples_browser.setStyleSheet("QTextBrowser { background-color: #2b2b2b; color: #ffffff; }")
        examples_layout.addWidget(self.examples_browser)
        info_tabs.addTab(examples_widget, self.tr("Примеры"))
        
        # Вкладка с регулярным выражением
        regex_widget = QWidget()
        regex_layout = QVBoxLayout(regex_widget)
        self.regex_browser = QTextBrowser()
        self.regex_browser.setStyleSheet("QTextBrowser { background-color: #2b2b2b; color: #ffffff; font-family: monospace; }")
        regex_layout.addWidget(self.regex_browser)
        info_tabs.addTab(regex_widget, self.tr("Регулярное выражение"))
        
        splitter.addWidget(results_widget)
        splitter.addWidget(info_tabs)
        splitter.setSizes([400, 300])
        
        main_layout.addWidget(splitter)
        
        # Подключение сигналов
        self.search_combo.currentTextChanged.connect(self.on_task_change)
        self.on_task_change()
        
    def load_examples(self):
        """Загрузка примеров в текстовую область"""
        example_text = """Пример текста для поиска различных элементов:

1. СЛОВА НА M/M:
   machine learning is fascinating
   Mouse and keyboard are input devices
   Moscow is a beautiful city
   My mother makes amazing meals
   The word "am" does not start with m
   Mountain climbing is exciting
   Microsoft develops software

2. ВОСЬМЕРИЧНЫЕ ЧИСЛА:
   Права доступа: 0755, 0644, 0777
   В Python: 0o755, 0o644, 0o777
   В некоторых системах: &O755, &O644
   Обычные числа: 755, 644 (это десятичные)
   Некорректные: 0o8, &O9, 08

3. ПУТИ UNIX:
   /home/user/documents/file.txt
   /etc/passwd
   /var/log/syslog
   /usr/bin/python3
   /home/user/
   / (корневой каталог)
   /home/user/.config/settings.conf
   /tmp/ (временная директория)
   /opt/application/bin/start.sh

Смешанный текст для проверки:
   Файл /home/user/0755 имеет права доступа 0755
   Команда chmod 0755 script.py
   В каталоге /home/mike есть файлы с правами 0o755
   Mouse pointer at position /usr/share/icons/mouse.png
   Mountain path: /mnt/mountain/0755/trail.jpg
"""
        editor = self.parent.get_current_editor()
        if editor:
            editor.set_text(example_text)
            self.parent.status_bar.showMessage(self.tr("Пример текста загружен"), 3000)
        else:
            QMessageBox.warning(self, self.tr("Предупреждение"), 
                               self.tr("Нет активного редактора для загрузки примера"))
        
    def on_task_change(self):
        """Обработчик изменения выбранного задания"""
        task_name = self.search_combo.currentText()
        task_info = RegexPatterns.get_task_info(task_name)
        
        if task_info:
            info_text = f"""<h3 style="color: #4CAF50;">{self.tr("Описание задания")}</h3>
<p><b>{task_info['description']}</b></p>

<h3 style="color: #4CAF50;">{self.tr("Подробности")}</h3>
<p>{self.tr("Данное регулярное выражение предназначено для поиска всех вхождений указанного паттерна в тексте.")}</p>

<h3 style="color: #4CAF50;">{self.tr("Особенности")}</h3>
<ul>
<li>{self.tr("Учитывает границы слов (для задания 1)")}</li>
<li>{self.tr("Поддерживает различные форматы (для задания 2)")}</li>
<li>{self.tr("Работает с путями Unix (для задания 3)")}</li>
</ul>

<h3 style="color: #4CAF50;">{self.tr("Примечание")}</h3>
<p>{self.tr("Поиск может выполняться с игнорированием регистра символов.")}</p>"""
            self.task_info_browser.setHtml(info_text)
            
            examples_text = f"""<h3 style="color: #4CAF50;">{self.tr("Примеры, которые ДОЛЖНЫ находиться:")}</h3>
{''.join(f'<p style="color: #81c784;">✓ {ex}</p>' for ex in task_info['examples_correct'][:6])}

<h3 style="color: #f44336;">{self.tr("Примеры, которые НЕ ДОЛЖНЫ находиться:")}</h3>
{''.join(f'<p style="color: #e57373;">✗ {ex}</p>' for ex in task_info['examples_incorrect'][:6])}"""
            self.examples_browser.setHtml(examples_text)
            
            regex_text = f"""<h3 style="color: #4CAF50;">{self.tr("Регулярное выражение:")}</h3>
<p><code style="font-size: 14px; background-color: #1e1e1e; padding: 5px; display: block;">{task_info['pattern']}</code></p>

<h3 style="color: #4CAF50;">{self.tr("Пояснение:")}</h3>
<p><b>{self.tr("Задание 1 (Слова на m/M):")}</b><br>
{self.tr("Реализация с использованием регулярных выражений")}<br>
\\b - {self.tr("граница слова")}<br>
[mM] - {self.tr("буква m в любом регистре")}<br>
[a-zA-Z]* - {self.tr("любые буквы (0 или более)")}<br>
\\b - {self.tr("граница слова")}</p>

<p><b>{self.tr("Задание 2 (Восьмеричные числа):")}</b><br>
{self.tr("Реализация с использованием конечного автомата")}<br>
{self.tr("Автомат распознает форматы: 0o755, &O755, 0755")}<br>
{self.tr("Состояния: начальное, после префикса, в числе")}<br>
{self.tr("Принимает только восьмеричные цифры 0-7")}</p>

<p><b>{self.tr("Задание 3 (Пути Unix):")}</b><br>
{self.tr("Реализация с использованием конечного автомата")}<br>
{self.tr("Автомат распознает пути вида /path/to/file.ext")}<br>
{self.tr("Состояния: начальное, после /, в компоненте, после точки")}<br>
{self.tr("Проверяет границы слов для корректного распознавания")}</p>"""
            self.regex_browser.setHtml(regex_text)
            
    def perform_search(self):
        """Выполнение поиска"""
        editor = self.parent.get_current_editor()
        if not editor:
            QMessageBox.warning(self, self.tr("Предупреждение"), 
                               self.tr("Нет активного редактора для поиска"))
            return
            
        text = editor.get_text()
        if not text.strip():
            QMessageBox.warning(self, self.tr("Предупреждение"), 
                               self.tr("Нет данных для поиска"))
            return
            
        task_name = self.search_combo.currentText()
        patterns_dict = RegexPatterns.get_patterns_dict()
        pattern = patterns_dict.get(task_name, "")
        
        if not pattern:
            QMessageBox.critical(self, self.tr("Ошибка"), 
                                self.tr("Не выбран тип поиска"))
            return
            
        self.clear_results()
        
        ignore_case = self.ignore_case_check.isChecked()
        results = self.search_engine.search(text, pattern, task_name, ignore_case)
        self.current_results = results
        
        self.results_table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            self.results_table.setItem(i, 0, QTableWidgetItem(result['text']))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(result['line'])))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(result['char'])))
            self.results_table.setItem(i, 3, QTableWidgetItem(str(result['length'])))
            
        count = self.search_engine.get_count()
        self.count_label.setText(str(count))
        
        if count > 0:
            self.parent.status_bar.showMessage(
                self.tr("Найдено совпадений: {}").format(count), 3000
            )
        else:
            self.parent.status_bar.showMessage(self.tr("Совпадений не найдено"), 3000)
        
        if count == 0:
            QMessageBox.information(self, self.tr("Результаты поиска"), 
                                   self.tr("Совпадений не найдено"))
            
    def clear_results(self):
        """Очистка результатов поиска"""
        self.results_table.setRowCount(0)
        self.count_label.setText("0")
        self.current_results = []
        
        editor = self.parent.get_current_editor()
        if editor:
            cursor = editor.code_editor.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setCharFormat(QTextCharFormat())
            cursor.clearSelection()
            editor.code_editor.setTextCursor(cursor)
        
        self.parent.status_bar.showMessage(self.tr("Результаты очищены"), 2000)
            
    def on_result_select(self):
        """Обработчик выбора строки в таблице результатов"""
        selected_rows = self.results_table.selectedItems()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        if row >= len(self.current_results):
            return
            
        result = self.current_results[row]
        start_pos, end_pos = self.search_engine.get_global_position(row)
        
        if start_pos >= 0 and end_pos > start_pos:
            editor = self.parent.get_current_editor()
            if not editor:
                return
                
            cursor = editor.code_editor.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setCharFormat(QTextCharFormat())
            
            cursor = editor.code_editor.textCursor()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
            
            format = QTextCharFormat()
            format.setBackground(QColor("yellow"))
            format.setForeground(QColor("black"))
            cursor.setCharFormat(format)
            
            editor.code_editor.setTextCursor(cursor)
            editor.code_editor.ensureCursorVisible()
            
            self.parent.status_bar.showMessage(
                self.tr("Выделен результат: {} (строка {}, позиция {})").format(
                    result['text'], result['line'], result['char']
                ), 3000
            )
            
    def change_font_size(self, delta):
        """Изменение размера шрифта"""
        self.current_font_size = max(8, min(72, self.current_font_size + delta))
        font = self.results_table.font()
        font.setPointSize(self.current_font_size)
        self.results_table.setFont(font)
        
    def retranslateUi(self):
        """Обновление текста интерфейса"""
        self.results_table.setHorizontalHeaderLabels([
            self.tr("Найденная подстрока"),
            self.tr("Строка"),
            self.tr("Позиция"),
            self.tr("Длина")
        ])
        
        self.ignore_case_check.setText(self.tr("Игнорировать регистр"))
        self.search_button.setText(self.tr("Найти"))
        self.clear_button.setText(self.tr("Очистить"))
        self.example_button.setText(self.tr("Загрузить пример"))
        
        info_tabs = self.findChild(QTabWidget)
        if info_tabs:
            info_tabs.setTabText(0, self.tr("Информация о задании"))
            info_tabs.setTabText(1, self.tr("Примеры"))
            info_tabs.setTabText(2, self.tr("Регулярное выражение"))
        
        self.on_task_change()