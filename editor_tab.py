"""
Модуль вкладки редактора с подсветкой строк
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class LineNumberArea(QWidget):
    """Область с номерами строк"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
        
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Редактор кода с подсветкой строк"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width()
        self.highlight_current_line()
        
        # Настройка шрифта
        font = QFont("Courier New", 10)
        self.setFont(font)
        
    def line_number_area_width(self):
        """Вычисление ширины области номеров строк"""
        digits = len(str(self.blockCount()))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
        
    def update_line_number_area_width(self):
        """Обновление ширины области номеров строк"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def update_line_number_area(self, rect, dy):
        """Обновление области номеров строк"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()
            
    def resizeEvent(self, event):
        """Обработка изменения размера"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        
    def line_number_area_paint_event(self, event):
        """Рисование номеров строк"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(240, 240, 240))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(100, 100, 100))
                painter.drawText(0, int(top), self.line_number_area.width() - 2, self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
                
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
            
    def highlight_current_line(self):
        """Подсветка текущей строки"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(230, 240, 255)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
            
        self.setExtraSelections(extra_selections)


class EditorTab(QWidget):
    """Вкладка редактора"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.text_modified = False
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.code_editor = CodeEditor()
        self.code_editor.textChanged.connect(self.on_text_changed)
        
        layout.addWidget(self.code_editor)
        
    def on_text_changed(self):
        """Обработчик изменения текста"""
        self.text_modified = True
        
    def get_text(self):
        """Получение текста"""
        return self.code_editor.toPlainText()
        
    def set_text(self, text):
        """Установка текста"""
        self.code_editor.setPlainText(text)
        self.text_modified = False