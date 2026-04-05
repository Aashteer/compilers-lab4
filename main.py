"""
Главный модуль приложения - интеграция поиска по регулярным выражениям
"""

import os
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from translator import Translator
from editor_tab import EditorTab
from result_tabs import ResultTab, SyntaxErrorResultTab
from scanner import Scanner
from parser import Parser
from regex_search_tab import RegexSearchTab


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translator = Translator()
        self.tr = self.translator.tr
        
        self.current_font_size = 11
        self.result_font_size = 10
        self.scanner = Scanner()
        
        self.initUI()
        self.retranslateUi()
        
        self.editor_tabs.currentChanged.connect(self.update_cursor_position)
    
    def initUI(self):
        # Создание вкладок редактора
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        
        # Создание вкладок результатов
        self.result_tabs = QTabWidget()
        
        self.text_result_tab = QWidget()
        text_result_layout = QVBoxLayout(self.text_result_tab)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #ffffff; border: 1px solid #555555; }")
        text_result_layout.addWidget(self.result_text)
        
        self.tokens_tab = ResultTab(self.tr, is_error_table=False)
        self.tokens_tab.set_main_window(self)
        
        self.error_table_tab = ResultTab(self.tr, is_error_table=True)
        self.error_table_tab.set_main_window(self)
        
        self.syntax_error_tab = SyntaxErrorResultTab(self.tr)
        self.syntax_error_tab.set_main_window(self)
        
        # Вкладка для поиска по регулярным выражениям
        self.regex_search_tab = RegexSearchTab(self)
        
        self.result_tabs.addTab(self.text_result_tab, self.tr("Текстовый ввод"))
        self.result_tabs.addTab(self.tokens_tab, self.tr("Лексемы"))
        self.result_tabs.addTab(self.error_table_tab, self.tr("Ошибки"))
        self.result_tabs.addTab(self.syntax_error_tab, self.tr("Синтаксис"))
        self.result_tabs.addTab(self.regex_search_tab, self.tr("Regex Поиск"))

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.editor_tabs)
        splitter.addWidget(self.result_tabs)
        splitter.setSizes([400, 300])

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(splitter)
        self.setCentralWidget(central)

        self.add_new_editor_tab()
        
        self.create_menu()
        self.create_toolbar()
        self.create_status_bar()
        
        self.setWindowTitle(self.tr("Текстовый редактор с поиском по регулярным выражениям"))
        self.resize(1000, 700)
        self.setMinimumSize(600, 400)
    
    def create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(self.tr('Готов'))
        
        self.cursor_position_label = QLabel(self.tr('Строка: 1, Столбец: 1'))
        self.file_info_label = QLabel(self.tr('Новый файл'))
        self.encoding_label = QLabel(self.tr('UTF-8'))
        
        self.status_bar.addPermanentWidget(self.cursor_position_label)
        self.status_bar.addPermanentWidget(self.file_info_label)
        self.status_bar.addPermanentWidget(self.encoding_label)
    
    def update_cursor_position(self):
        editor = self.get_current_editor()
        if not editor:
            self.cursor_position_label.setText(self.tr('Строка: -, Столбец: -'))
            return
        cursor = editor.code_editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_position_label.setText(f"{self.tr('Строка:')} {line}, {self.tr('Столбец:')} {col}")
    
    def update_file_info(self, file_name):
        if file_name:
            self.file_info_label.setText(os.path.basename(file_name))
        else:
            self.file_info_label.setText(self.tr('Новый файл'))
    
    def get_current_editor(self):
        return self.editor_tabs.currentWidget()
    
    def add_new_editor_tab(self, file_name=None, content=''):
        new_tab = EditorTab()
        if content:
            new_tab.set_text(content)
        
        base_name = self.tr('Новый файл')
        tab_name = os.path.basename(file_name) if file_name else f'{base_name} {self.editor_tabs.count() + 1}'
        index = self.editor_tabs.addTab(new_tab, tab_name)
        self.editor_tabs.setCurrentIndex(index)
        
        if file_name:
            new_tab.current_file = file_name
        
        new_tab.code_editor.cursorPositionChanged.connect(self.update_cursor_position)
        new_tab.code_editor.textChanged.connect(self.on_tab_text_changed)
        
        return new_tab
    
    def on_tab_text_changed(self):
        index = self.editor_tabs.currentIndex()
        tab_text = self.editor_tabs.tabText(index)
        if not tab_text.endswith('*'):
            self.editor_tabs.setTabText(index, tab_text + '*')
    
    def close_editor_tab(self, index):
        if self.editor_tabs.count() <= 1:
            return
            
        tab = self.editor_tabs.widget(index)
        if tab.text_modified:
            reply = QMessageBox.question(
                self, self.tr('Сохранение'),
                self.tr('Сохранить изменения в документе?'),
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_current_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.editor_tabs.removeTab(index)
    
    def change_editor_font_size(self, delta):
        self.current_font_size = max(8, min(72, self.current_font_size + delta))
        editor = self.get_current_editor()
        if editor:
            font = editor.code_editor.font()
            font.setPointSize(self.current_font_size)
            editor.code_editor.setFont(font)
            editor.code_editor.update_line_number_area_width()
        self.status_bar.showMessage(f"{self.tr('Размер шрифта редактора:')} {self.current_font_size}")
    
    def change_result_font_size(self, delta):
        self.result_font_size = max(8, min(72, self.result_font_size + delta))
        font = self.result_text.font()
        font.setPointSize(self.result_font_size)
        self.result_text.setFont(font)
        
        # Также меняем шрифт в таблице поиска по regex
        self.regex_search_tab.change_font_size(delta)
        
        self.status_bar.showMessage(f"{self.tr('Размер шрифта результатов:')} {self.result_font_size}")
    
    def create_menu(self):
        menubar = self.menuBar()
        menubar.clear()
        
        file_menu = menubar.addMenu(self.tr('Файл'))
        new_act = QAction(self.tr('Создать'), self)
        new_act.setShortcut('Ctrl+N')
        new_act.triggered.connect(lambda: self.add_new_editor_tab())
        file_menu.addAction(new_act)
        
        open_act = QAction(self.tr('Открыть'), self)
        open_act.setShortcut('Ctrl+O')
        open_act.triggered.connect(self.open_file)
        file_menu.addAction(open_act)
        
        save_act = QAction(self.tr('Сохранить'), self)
        save_act.setShortcut('Ctrl+S')
        save_act.triggered.connect(self.save_file)
        file_menu.addAction(save_act)
        
        save_as_act = QAction(self.tr('Сохранить как'), self)
        save_as_act.setShortcut('Ctrl+Shift+S')
        save_as_act.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_act)
        
        file_menu.addSeparator()
        
        exit_act = QAction(self.tr('Выход'), self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        edit_menu = menubar.addMenu(self.tr('Правка'))
        undo_act = QAction(self.tr('Отменить'), self)
        undo_act.setShortcut('Ctrl+Z')
        undo_act.triggered.connect(lambda: self.get_current_editor().code_editor.undo() if self.get_current_editor() else None)
        edit_menu.addAction(undo_act)
        
        redo_act = QAction(self.tr('Повторить'), self)
        redo_act.setShortcut('Ctrl+Y')
        redo_act.triggered.connect(lambda: self.get_current_editor().code_editor.redo() if self.get_current_editor() else None)
        edit_menu.addAction(redo_act)
        
        edit_menu.addSeparator()
        
        cut_act = QAction(self.tr('Вырезать'), self)
        cut_act.setShortcut('Ctrl+X')
        cut_act.triggered.connect(lambda: self.get_current_editor().code_editor.cut() if self.get_current_editor() else None)
        edit_menu.addAction(cut_act)
        
        copy_act = QAction(self.tr('Копировать'), self)
        copy_act.setShortcut('Ctrl+C')
        copy_act.triggered.connect(lambda: self.get_current_editor().code_editor.copy() if self.get_current_editor() else None)
        edit_menu.addAction(copy_act)
        
        paste_act = QAction(self.tr('Вставить'), self)
        paste_act.setShortcut('Ctrl+V')
        paste_act.triggered.connect(lambda: self.get_current_editor().code_editor.paste() if self.get_current_editor() else None)
        edit_menu.addAction(paste_act)
        
        del_act = QAction(self.tr('Удалить'), self)
        del_act.setShortcut('Del')
        del_act.triggered.connect(lambda: self.get_current_editor().code_editor.textCursor().removeSelectedText() if self.get_current_editor() else None)
        edit_menu.addAction(del_act)
        
        sel_all_act = QAction(self.tr('Выделить все'), self)
        sel_all_act.setShortcut('Ctrl+A')
        sel_all_act.triggered.connect(lambda: self.get_current_editor().code_editor.selectAll() if self.get_current_editor() else None)
        edit_menu.addAction(sel_all_act)

        view_menu = menubar.addMenu(self.tr('Вид'))
        inc_ed_font = QAction(self.tr('Увеличить шрифт редактора'), self)
        inc_ed_font.setShortcut('Ctrl++')
        inc_ed_font.triggered.connect(lambda: self.change_editor_font_size(1))
        view_menu.addAction(inc_ed_font)
        
        dec_ed_font = QAction(self.tr('Уменьшить шрифт редактора'), self)
        dec_ed_font.setShortcut('Ctrl+-')
        dec_ed_font.triggered.connect(lambda: self.change_editor_font_size(-1))
        view_menu.addAction(dec_ed_font)
        
        view_menu.addSeparator()
        
        inc_res_font = QAction(self.tr('Увеличить шрифт результатов'), self)
        inc_res_font.setShortcut('Ctrl+Shift++')
        inc_res_font.triggered.connect(lambda: self.change_result_font_size(1))
        view_menu.addAction(inc_res_font)
        
        dec_res_font = QAction(self.tr('Уменьшить шрифт результатов'), self)
        dec_res_font.setShortcut('Ctrl+Shift+-')
        dec_res_font.triggered.connect(lambda: self.change_result_font_size(-1))
        view_menu.addAction(dec_res_font)

        run_menu = menubar.addMenu(self.tr('Пуск'))
        run_act = QAction(self.tr('Запуск анализатора'), self)
        run_act.setShortcut('F5')
        run_act.triggered.connect(self.start_analyzer)
        run_menu.addAction(run_act)
        
        regex_run_act = QAction(self.tr('Поиск по Regex'), self)
        regex_run_act.setShortcut('Ctrl+F5')
        regex_run_act.triggered.connect(self.start_regex_search)
        run_menu.addAction(regex_run_act)

        help_menu = menubar.addMenu(self.tr('Справка'))
        help_act = QAction(self.tr('Вызов справки'), self)
        help_act.setShortcut('F1')
        help_act.triggered.connect(self.show_help)
        help_menu.addAction(help_act)
        
        about_act = QAction(self.tr('О программе'), self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

        lang_menu = menubar.addMenu(self.tr('Язык'))
        ru_act = QAction(self.tr('Русский'), self)
        ru_act.triggered.connect(lambda: self.change_language('ru'))
        lang_menu.addAction(ru_act)
        
        en_act = QAction(self.tr('English'), self)
        en_act.triggered.connect(lambda: self.change_language('en'))
        lang_menu.addAction(en_act)
    
    def start_regex_search(self):
        """Запуск поиска по регулярным выражениям"""
        self.result_tabs.setCurrentWidget(self.regex_search_tab)
        self.regex_search_tab.perform_search()
    
    def create_toolbar(self):
        self.toolbar = self.addToolBar(self.tr('Инструменты'))
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # Простые иконки
        new_act = QAction(self.tr('Создать'), self)
        new_act.triggered.connect(lambda: self.add_new_editor_tab())
        self.toolbar.addAction(new_act)
        
        open_act = QAction(self.tr('Открыть'), self)
        open_act.triggered.connect(self.open_file)
        self.toolbar.addAction(open_act)
        
        save_act = QAction(self.tr('Сохранить'), self)
        save_act.triggered.connect(self.save_file)
        self.toolbar.addAction(save_act)
        
        self.toolbar.addSeparator()
        
        run_act = QAction(self.tr('Запуск'), self)
        run_act.triggered.connect(self.start_analyzer)
        self.toolbar.addAction(run_act)
        
        regex_act = QAction(self.tr('Regex'), self)
        regex_act.triggered.connect(self.start_regex_search)
        self.toolbar.addAction(regex_act)
    
    def retranslateUi(self):
        self.setWindowTitle(self.tr("Текстовый редактор с поиском по регулярным выражениям"))
        
        menubar = self.menuBar()
        menubar.clear()
        self.create_menu()
        
        self.result_tabs.setTabText(0, self.tr("Текстовый ввод"))
        self.result_tabs.setTabText(1, self.tr("Лексемы"))
        self.result_tabs.setTabText(2, self.tr("Ошибки"))
        self.result_tabs.setTabText(3, self.tr("Синтаксис"))
        self.result_tabs.setTabText(4, self.tr("Regex Поиск"))
        
        self.tokens_tab.set_language(self.translator.lang)
        self.error_table_tab.set_language(self.translator.lang)
        self.syntax_error_tab.set_language(self.translator.lang)
        
        self.regex_search_tab.retranslateUi()
        
        self.status_bar.showMessage(self.tr('Готов'))
        self.update_cursor_position()
        self.update_file_info(None)
        
        for i in range(self.editor_tabs.count()):
            tab = self.editor_tabs.widget(i)
            if tab and not tab.current_file:
                current_text = self.editor_tabs.tabText(i).rstrip('*')
                if current_text.startswith('Новый файл') or current_text.startswith('Untitled'):
                    base_name = self.tr('Новый файл')
                    if current_text == 'Новый файл' or current_text == 'Untitled':
                        new_text = base_name
                    else:
                        try:
                            num = current_text.split()[-1]
                            new_text = f"{base_name} {num}"
                        except:
                            new_text = base_name
                    
                    if self.editor_tabs.tabText(i).endswith('*'):
                        new_text += '*'
                    self.editor_tabs.setTabText(i, new_text)
    
    def change_language(self, lang):
        self.translator.set_language(lang)
        self.retranslateUi()
        
        self.tokens_tab.set_language(lang)
        self.error_table_tab.set_language(lang)
        self.syntax_error_tab.set_language(lang)
        
        tab = self.get_current_editor()
        if tab and tab.get_text().strip():
            self.start_analyzer()
        
        QMessageBox.information(
            self,
            self.tr('Смена языка'),
            self.tr('Язык изменен на русский') if lang == 'ru' else self.tr('Язык изменен на английский')
        )
    
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, self.tr('Открыть файл'), '', 
            'Текстовые файлы (*.txt);;Все файлы (*)'
        )
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.add_new_editor_tab(file_name, content)
                self.status_bar.showMessage(f"{self.tr('Открыт файл:')} {file_name}")
                self.update_file_info(file_name)
            except Exception as e:
                QMessageBox.critical(self, self.tr('Ошибка'), f"{self.tr('Не удалось открыть файл:')} {str(e)}")
    
    def save_current_file(self):
        tab = self.get_current_editor()
        if not tab:
            return
        if tab.current_file:
            try:
                with open(tab.current_file, 'w', encoding='utf-8') as file:
                    file.write(tab.get_text())
                tab.text_modified = False
                idx = self.editor_tabs.currentIndex()
                title = self.editor_tabs.tabText(idx)
                if title.endswith('*'):
                    self.editor_tabs.setTabText(idx, title[:-1])
                self.status_bar.showMessage(f"{self.tr('Файл сохранен:')} {tab.current_file}")
            except Exception as e:
                QMessageBox.critical(self, self.tr('Ошибка'), f"{self.tr('Не удалось сохранить файл:')} {str(e)}")
        else:
            self.save_as_file()
    
    def save_file(self):
        self.save_current_file()
    
    def save_as_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, self.tr('Сохранить как'), '', 
            'Текстовые файлы (*.txt);;Все файлы (*)'
        )
        if file_name:
            tab = self.get_current_editor()
            if tab:
                tab.current_file = file_name
                self.save_current_file()
                self.editor_tabs.setTabText(self.editor_tabs.currentIndex(), os.path.basename(file_name))
                self.update_file_info(file_name)
    
    def go_to_position(self, line: int, column: int):
        editor = self.get_current_editor()
        if not editor:
            return
        
        cursor = editor.code_editor.textCursor()
        block = editor.code_editor.document().findBlockByNumber(line - 1)
        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, column - 1)
        editor.code_editor.setTextCursor(cursor)
        editor.code_editor.setFocus()
        editor.code_editor.centerCursor()
    
    def start_analyzer(self):
        tab = self.get_current_editor()
        if not tab:
            return
        
        text = tab.get_text()
        
        self.tokens_tab.clear_results()
        self.error_table_tab.clear_results()
        self.syntax_error_tab.clear_results()
        
        if not text.strip():
            self.result_text.setPlainText(self.tr('Текст для анализа отсутствует.'))
            return
        
        results = self.scanner.analyze(text)
        current_lang = self.translator.lang
        
        tokens_text = f"{self.tr('Результаты лексического анализа')}\n\n"
        tokens_text += f"{self.tr('Найдено лексем:')} {len(results['tokens'])}\n"
        tokens_text += f"{self.tr('Найдено ошибок:')} {len(results['errors'])}\n\n"
        
        self.result_text.setPlainText(tokens_text)
        
        self.status_bar.showMessage(
            f"{self.tr('Анализ завершен')}. {self.tr('Лексем:')} {len(results['tokens'])}, "
            f"{self.tr('Ошибок:')} {len(results['errors'])}"
        )
    
    def show_help(self):
        help_text = self.tr('Справка по текстовому редактору') + '\n\n' + \
                    self.tr('Функции меню "Файл":') + '\n' + \
                    "- " + self.tr('Создать') + ": " + self.tr('Создать новый документ (Ctrl+N)') + "\n" + \
                    "- " + self.tr('Открыть') + ": " + self.tr('Открыть существующий текстовый файл (Ctrl+O)') + "\n" + \
                    "- " + self.tr('Сохранить') + ": " + self.tr('Сохранить текущий документ (Ctrl+S)') + "\n" + \
                    "- " + self.tr('Сохранить как') + ": " + self.tr('Сохранить документ под новым именем (Ctrl+Shift+S)') + "\n" + \
                    "- " + self.tr('Выход') + ": " + self.tr('Закрыть программу (Ctrl+Q)') + "\n\n" + \
                    self.tr('Функции меню "Пуск":') + '\n' + \
                    "- " + self.tr('Запуск анализатора') + ": F5\n" + \
                    "- " + self.tr('Поиск по регулярным выражениям') + ": Ctrl+F5\n\n" + \
                    self.tr('Дополнительно:') + '\n' + \
                    "- " + self.tr('Нумерация строк') + "\n" + \
                    "- " + self.tr('Вкладки для нескольких документов') + "\n" + \
                    "- " + self.tr('Табличное отображение результатов поиска') + "\n" + \
                    "- " + self.tr('Строка состояния с информацией о позиции курсора') + "\n"

        dlg = QDialog(self)
        dlg.setWindowTitle(self.tr('Справка'))
        dlg.resize(650, 550)
        lay = QVBoxLayout(dlg)
        te = QTextEdit()
        te.setReadOnly(True)
        te.setPlainText(help_text)
        btn = QPushButton(self.tr('Закрыть'))
        btn.clicked.connect(dlg.close)
        lay.addWidget(te)
        lay.addWidget(btn)
        dlg.exec()
    
    def show_about(self):
        QMessageBox.about(
            self,
            self.tr('О программе'),
            self.tr("Текстовый редактор с поиском по регулярным выражениям") + "\n\n" +
            self.tr("С поддержкой трёх заданий:") + "\n" +
            "1. " + self.tr("Слова, начинающиеся на m/M") + "\n" +
            "2. " + self.tr("Восьмеричные числа") + "\n" +
            "3. " + self.tr("Пути Unix") + "\n\n" +
            self.tr("Разработчик: Александр АВТ-314") + "\n\n" +
            self.tr("© 2026 Все права защищены.")
        )
    
    def closeEvent(self, event):
        for i in range(self.editor_tabs.count()):
            tab = self.editor_tabs.widget(i)
            if tab.text_modified:
                reply = QMessageBox.question(
                    self, self.tr('Сохранение'),
                    self.tr('Есть несохраненные изменения. Закрыть программу?'),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    event.ignore()
                    return
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TextEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()