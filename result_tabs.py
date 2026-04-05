"""
Модуль вкладок результатов
"""

from PyQt6.QtWidgets import *


class ResultTab(QWidget):
    """Вкладка для отображения результатов (лексемы или ошибки)"""
    
    def __init__(self, tr_func, is_error_table=False):
        super().__init__()
        self.tr = tr_func
        self.is_error_table = is_error_table
        self.main_window = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            self.tr('Условный код'),
            self.tr('Тип лексемы'),
            self.tr('Лексема'),
            self.tr('Местоположение')
        ])
        
        # Настройка таблицы
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_item_selected)
        
        layout.addWidget(self.table)
        
    def set_main_window(self, window):
        """Установка главного окна"""
        self.main_window = window
        
    def clear_results(self):
        """Очистка таблицы"""
        self.table.setRowCount(0)
        
    def add_result(self, *args):
        """Добавление результата в таблицу"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, value in enumerate(args):
            if col < 4:
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
                
    def set_language(self, lang):
        """Смена языка"""
        self.table.setHorizontalHeaderLabels([
            self.tr('Условный код'),
            self.tr('Тип лексемы'),
            self.tr('Лексема'),
            self.tr('Местоположение')
        ])
        
    def on_item_selected(self):
        """Обработчик выбора строки"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        location = self.table.item(row, 3).text()
        
        if self.main_window and location:
            try:
                # Парсим местоположение
                if self.tr('строка') in location or 'line' in location:
                    import re
                    numbers = re.findall(r'\d+', location)
                    if len(numbers) >= 2:
                        line = int(numbers[0])
                        col = int(numbers[1])
                        self.main_window.go_to_position(line, col)
            except Exception as e:
                print(f"Error navigating to position: {e}")


class SyntaxErrorResultTab(QWidget):
    """Вкладка для отображения синтаксических ошибок"""
    
    def __init__(self, tr_func):
        super().__init__()
        self.tr = tr_func
        self.main_window = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.update_headers()
        
        # Настройка таблицы
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_item_selected)
        
        layout.addWidget(self.table)
        
    def set_main_window(self, window):
        """Установка главного окна"""
        self.main_window = window
        
    def clear_results(self):
        """Очистка таблицы"""
        self.table.setRowCount(0)
        
    def add_row(self, fragment, location, message):
        """Добавление строки с ошибкой"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(fragment))
        self.table.setItem(row, 1, QTableWidgetItem(location))
        self.table.setItem(row, 2, QTableWidgetItem(message))
        
    def set_total(self, total):
        """Установка общего количества ошибок"""
        pass
        
    def update_headers(self):
        """Обновление заголовков"""
        self.table.setHorizontalHeaderLabels([
            self.tr("Фрагмент"),
            self.tr("Местоположение"),
            self.tr("Сообщение")
        ])
        
    def set_language(self, lang):
        """Смена языка"""
        self.update_headers()
        
    def on_item_selected(self):
        """Обработчик выбора строки"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        location = self.table.item(row, 1).text()
        
        if self.main_window and location:
            try:
                import re
                numbers = re.findall(r'\d+', location)
                if len(numbers) >= 2:
                    line = int(numbers[0])
                    col = int(numbers[1])
                    self.main_window.go_to_position(line, col)
            except Exception as e:
                print(f"Error navigating to position: {e}")