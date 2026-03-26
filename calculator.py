import sys
import math
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QPushButton, QLineEdit, 
                            QTextEdit, QLabel, QComboBox, QScrollArea, QFrame,
                            QSplitter, QCheckBox, QToolButton, QDockWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QLinearGradient, QPen, QBrush, QRadialGradient


class StepByStepSolver:
    """Класс для пошагового решения математических выражений"""
    
    def __init__(self):
        self.steps = []
    
    def solve_with_steps(self, expression):
        """Решает выражение с пошаговым описанием"""
        self.steps = []
        try:
            # Очищаем выражение
            expr = expression.replace(' ', '')
            
            # Шаг 1: Анализ выражения
            self.steps.append(f"📝 Анализ выражения: {expression}")
            self.steps.append(f"🔍 Очищенное выражение: {expr}")
            
            # Шаг 2: Проверка скобок
            if '(' in expr or ')' in expr:
                self.steps.append("📐 Обнаружены скобки, начинаем решение изнутри")
                result = self._solve_parentheses(expr)
            else:
                # Шаг 3: Решаем без скобок
                result = self._solve_expression(expr)
            
            self.steps.append(f"✅ Финальный результат: {result}")
            return result, self.steps
            
        except Exception as e:
            self.steps.append(f"❌ Ошибка: {str(e)}")
            return None, self.steps
    
    def _solve_parentheses(self, expr):
        """Решает выражения в скобках"""
        while '(' in expr:
            # Находим внутренние скобки
            start = expr.rfind('(')
            end = expr.find(')', start)
            
            if end == -1:
                raise ValueError("Неправильно расставлены скобки")
            
            # Извлекаем выражение в скобках
            inner_expr = expr[start+1:end]
            self.steps.append(f"📦 Решаем выражение в скобках: {inner_expr}")
            
            # Решаем внутреннее выражение
            inner_result = self._solve_expression(inner_expr)
            self.steps.append(f"📦 Результат в скобках: {inner_result}")
            
            # Заменяем скобки на результат
            expr = expr[:start] + str(inner_result) + expr[end+1:]
            self.steps.append(f"🔄 Заменяем скобки: {expr}")
        
        return self._solve_expression(expr)
    
    def _solve_expression(self, expr):
        """Решает простое выражение"""
        # Обрабатываем степени
        expr = self._solve_powers(expr)
        
        # Обрабатываем умножение и деление
        expr = self._solve_multiplication_division(expr)
        
        # Обрабатываем сложение и вычитание
        result = self._solve_addition_subtraction(expr)
        
        return result
    
    def _solve_powers(self, expr):
        """Решает степени"""
        while '**' in expr or '^' in expr:
            if '**' in expr:
                pattern = r'(-?\d+\.?\d*)\*\*(-?\d+\.?\d*)'
                op = '**'
            else:
                pattern = r'(-?\d+\.?\d*)\^(-?\d+\.?\d*)'
                op = '^'
            
            match = re.search(pattern, expr)
            if match:
                a, b = float(match.group(1)), float(match.group(2))
                result = a ** b
                self.steps.append(f"🔢 Вычисляем степень: {a} {op} {b} = {result}")
                expr = expr.replace(match.group(0), str(result))
            else:
                break
        return expr
    
    def _solve_multiplication_division(self, expr):
        """Решает умножение и деление"""
        while True:
            # Ищем умножение или деление
            mult_match = re.search(r'(-?\d+\.?\d*)\*(-?\d+\.?\d*)', expr)
            div_match = re.search(r'(-?\d+\.?\d*)/(-?\d+\.?\d*)', expr)
            
            if mult_match and div_match:
                # Выбираем то, что встречается раньше
                if mult_match.start() < div_match.start():
                    match = mult_match
                    op = '*'
                else:
                    match = div_match
                    op = '/'
            elif mult_match:
                match = mult_match
                op = '*'
            elif div_match:
                match = div_match
                op = '/'
            else:
                break
            
            a, b = float(match.group(1)), float(match.group(2))
            
            if op == '*':
                result = a * b
                self.steps.append(f"🔢 Умножение: {a} × {b} = {result}")
            else:
                if b == 0:
                    raise ValueError("Деление на ноль")
                result = a / b
                self.steps.append(f"🔢 Деление: {a} ÷ {b} = {result}")
            
            expr = expr.replace(match.group(0), str(result))
        
        return expr
    
    def _solve_addition_subtraction(self, expr):
        """Решает сложение и вычитание"""
        # Преобразуем выражение в список чисел и операций
        tokens = re.findall(r'[-+]?\d+\.?\d*', expr)
        
        if not tokens:
            return 0
        
        result = float(tokens[0])
        self.steps.append(f"🔢 Начальное значение: {result}")
        
        i = 1
        while i < len(tokens):
            # Находим операцию перед числом
            pos = expr.find(tokens[i])
            if pos > 0:
                op = expr[pos-1]
            else:
                op = '+'
            
            num = float(tokens[i])
            
            if op == '+':
                result += num
                self.steps.append(f"🔢 Сложение: {result - num} + {num} = {result}")
            else:
                result -= num
                self.steps.append(f"🔢 Вычитание: {result + num} - {num} = {result}")
            
            i += 1
        
        return result


class CustomButton(QPushButton):
    """Кнопка в стиле клавиатуры с пастельными цветами"""
    
    def __init__(self, text, color_scheme):
        super().__init__(text)
        self.color_scheme = color_scheme
        self.base_size = 45  # Уменьшили размер кнопок
        self.setup_style()
        
    def setup_style(self):
        self.setMinimumHeight(self.base_size)
        self.setMinimumWidth(self.base_size)
        self.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))  # Уменьшили шрифт
        
        # Получаем цвета из схемы
        button_rgb = self.color_scheme.get('button_rgb', '200, 200, 200')
        border_rgb = self.color_scheme.get('border_rgb', '150, 150, 150')
        text_color = self.color_scheme.get('text', '#000000')
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({button_rgb}, 0.7), 
                    stop:0.8 rgba({button_rgb}, 0.5),
                    stop:1 rgba({button_rgb}, 0.3));
                border: 1px solid rgba({border_rgb}, 0.5);
                border-radius: 6px;
                color: {text_color};
                font-weight: 500;
                padding: 2px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({button_rgb}, 0.9), 
                    stop:0.8 rgba({button_rgb}, 0.6),
                    stop:1 rgba({button_rgb}, 0.4));
                border: 1px solid rgba({border_rgb}, 0.7);
            }}
            QPushButton:pressed {{
                background: rgba({button_rgb}, 0.5);
                border: 1px solid rgba({border_rgb}, 0.6);
            }}
        """)
    
    def update_size(self, scale_factor):
        """Обновляет размер кнопки"""
        new_size = max(35, int(self.base_size * scale_factor))  # Минимальный размер 35px
        self.setMinimumHeight(new_size)
        self.setMinimumWidth(new_size)
        self.setFont(QFont("Segoe UI", max(10, int(12 * scale_factor)), QFont.Weight.Medium))


class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.solver = StepByStepSolver()
        self.history = []
        self.current_theme = "light"
        
        # Более насыщенные розовато-пастельные и темно-бордовые цветовые схемы
        self.themes = {
            "light": {
                "bg": "rgba(248, 248, 252, 0.95)",
                "display_bg": "rgba(255, 255, 255, 0.9)",
                "text": "#2d3748",
                "button_rgb": "255, 200, 220",       # базовый розовый
                "border_rgb": "230, 180, 200",       # розоватые границы
                "operator_rgb": "255, 180, 200",     # операторы – светлый розовый
                "special_rgb": "255, 210, 230",      # научные кнопки – нежно-розовый
                "clear_rgb": "255, 190, 210",        # кнопка C – розовый
                "panel_bg": "rgba(250, 240, 245, 0.9)",
                "accent_rgb": "255, 160, 190",       # кнопка = – ярко-розовый
                "number_rgb": "255, 220, 240"        # цифровые кнопки – очень светлый розовый
            },
            "dark": {
                "bg": "rgba(25, 25, 35, 0.95)",
                "display_bg": "rgba(35, 35, 50, 0.9)",
                "text": "#e2e8f0",
                "button_rgb": "120, 40, 60",         # базовый бордовый
                "border_rgb": "90, 30, 45",          # тёмно-бордовые границы
                "operator_rgb": "140, 50, 70",       # операторы – насыщенный бордовый
                "special_rgb": "100, 35, 55",        # научные кнопки – тёмно-бордовый
                "clear_rgb": "110, 40, 60",          # кнопка C – бордовый
                "panel_bg": "rgba(30, 20, 30, 0.9)",
                "accent_rgb": "160, 60, 85",         # кнопка = – яркий бордовый
                "number_rgb": "130, 45, 70"          # цифровые кнопки – средний бордовый
            }
        }
        
        # Масштабирование для адаптивности
        self.scale_factor = 1.0
        self.min_window_size = QSize(400, 600)
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        self.setWindowTitle("🧮 Комфортный Калькулятор")
        self.setMinimumSize(self.min_window_size)
        self.setGeometry(100, 100, 450, 650)  # Компактнее по умолчанию
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout с минимальными отступами
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(int(5 * self.scale_factor))  # Уменьшили отступы
        main_layout.setContentsMargins(
            int(8 * self.scale_factor),  # Уменьшили margins
            int(8 * self.scale_factor), 
            int(8 * self.scale_factor), 
            int(8 * self.scale_factor)
        )
        
        # Верхняя панель с темой и кнопками - компактнее
        top_panel = QHBoxLayout()
        top_panel.setSpacing(int(5 * self.scale_factor))
        
        theme_label = QLabel("🎨:")
        theme_label.setFont(QFont("Segoe UI", int(10 * self.scale_factor), QFont.Weight.Medium))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Темная"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        
        self.steps_checkbox = QCheckBox("Пошагово")
        self.steps_checkbox.setChecked(True)
        self.steps_checkbox.setFont(QFont("Segoe UI", int(10 * self.scale_factor), QFont.Weight.Medium))
        
        # Кнопки для открытия панелей
        self.steps_button = QToolButton()
        self.steps_button.setText("📋")
        self.steps_button.setFont(QFont("Segoe UI", int(10 * self.scale_factor), QFont.Weight.Medium))
        self.steps_button.clicked.connect(self.toggle_steps_dock)
        self.steps_button.setToolTip("Пошаговое решение")
        
        self.history_button = QToolButton()
        self.history_button.setText("📚")
        self.history_button.setFont(QFont("Segoe UI", int(10 * self.scale_factor), QFont.Weight.Medium))
        self.history_button.clicked.connect(self.toggle_history_dock)
        self.history_button.setToolTip("История вычислений")
        
        top_panel.addWidget(theme_label)
        top_panel.addWidget(self.theme_combo)
        top_panel.addStretch()
        top_panel.addWidget(self.steps_checkbox)
        top_panel.addWidget(self.steps_button)
        top_panel.addWidget(self.history_button)
        
        main_layout.addLayout(top_panel)
        
        # Дисплей - компактнее
        self.display = QLineEdit()
        self.display.setMinimumHeight(int(60 * self.scale_factor))  # Уменьшили высоту
        self.display.setFont(QFont("Segoe UI", int(20 * self.scale_factor), QFont.Weight.Medium))
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        main_layout.addWidget(self.display)
        
        # Кнопки калькулятора
        self.create_buttons(main_layout)
        
        # Создаем док-панели
        self.create_dock_panels()
        
        # Подключаем событие изменения размера
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_resize)
    
    def resizeEvent(self, event):
        """Обрабатывает изменение размера окна"""
        super().resizeEvent(event)
        self.resize_timer.start(100)  # Задержка для избежания частых обновлений
    
    def handle_resize(self):
        """Обрабатывает изменение размера с задержкой"""
        new_width = self.width()
        new_height = self.height()
        
        # Вычисляем масштабный коэффициент
        base_width = 450  # Обновили базовые размеры
        base_height = 650
        width_scale = new_width / base_width
        height_scale = new_height / base_height
        
        # Используем минимальный масштаб для сохранения пропорций
        self.scale_factor = max(0.7, min(width_scale, height_scale))  # Увеличили минимальный масштаб
        
        # Обновляем размеры всех элементов
        self.update_ui_scaling()
    
    def update_ui_scaling(self):
        """Обновляет масштабирование всех элементов UI"""
        # Обновляем размер дисплея
        self.display.setMinimumHeight(int(60 * self.scale_factor))
        self.display.setFont(QFont("Segoe UI", max(14, int(20 * self.scale_factor)), QFont.Weight.Medium))
        
        # Обновляем размеры кнопок
        for button in self.findChildren(CustomButton):
            button.update_size(self.scale_factor)
        
        # Обновляем другие элементы
        self.theme_combo.setFont(QFont("Segoe UI", max(8, int(10 * self.scale_factor)), QFont.Weight.Medium))
        self.steps_checkbox.setFont(QFont("Segoe UI", max(8, int(10 * self.scale_factor)), QFont.Weight.Medium))
        self.steps_button.setFont(QFont("Segoe UI", max(8, int(10 * self.scale_factor)), QFont.Weight.Medium))
        self.history_button.setFont(QFont("Segoe UI", max(8, int(10 * self.scale_factor)), QFont.Weight.Medium))
        
        # Обновляем отступы
        main_layout = self.centralWidget().layout()
        main_layout.setSpacing(int(5 * self.scale_factor))
        main_layout.setContentsMargins(
            int(8 * self.scale_factor), 
            int(8 * self.scale_factor), 
            int(8 * self.scale_factor), 
            int(8 * self.scale_factor)
        )
        
        # Обновляем spacing в layout кнопок
        button_container = self.centralWidget().findChild(QWidget)
        if button_container and button_container.layout():
            button_container.layout().setSpacing(int(3 * self.scale_factor))
    
    def create_buttons(self, layout):
        """Создает компактные кнопки в стиле клавиатуры с правильной раскладкой"""
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(int(3 * self.scale_factor))  # Минимальные отступы
        buttons_layout.setContentsMargins(0, 0, 0, 0)  # Без отступов по краям
        
        # Определение кнопок - стандартная раскладка калькулятора
        # Одна большая кнопка "0" занимает две колонки (colspan=2)
        buttons = [
            ('C', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3)
        ]
        
        # Научные функции - отдельный ряд
        scientific_buttons = [
            ('sin', 5, 0), ('cos', 5, 1), ('tan', 5, 2), ('√', 5, 3),
            ('log', 6, 0), ('ln', 6, 1), ('x²', 6, 2), ('xʸ', 6, 3),
            ('π', 7, 0), ('e', 7, 1), ('(', 7, 2), (')', 7, 3)
        ]
        
        color_scheme = self.themes[self.current_theme]
        
        # Создание основных кнопок
        for btn_data in buttons:
            if len(btn_data) == 3:
                text, row, col = btn_data
                rowspan, colspan = 1, 1
            else:
                text, row, col, rowspan, colspan = btn_data
                
            btn = CustomButton(text, color_scheme)
            btn.update_size(self.scale_factor)
            
            # Цветовая схема для разных типов кнопок
            if text in ['÷', '×', '-', '+']:
                btn.color_scheme = color_scheme.copy()
                btn.color_scheme['button_rgb'] = color_scheme['operator_rgb']
                btn.setup_style()
            elif text == 'C':
                btn.color_scheme = color_scheme.copy()
                btn.color_scheme['button_rgb'] = color_scheme['clear_rgb']
                btn.setup_style()
            elif text == '=':
                btn.color_scheme = color_scheme.copy()
                btn.color_scheme['button_rgb'] = color_scheme['accent_rgb']
                btn.setup_style()
            elif text.isdigit():
                btn.color_scheme = color_scheme.copy()
                btn.color_scheme['button_rgb'] = color_scheme['number_rgb']
                btn.setup_style()
                
            btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))
            buttons_layout.addWidget(btn, row, col, rowspan, colspan)
        
        # Научные кнопки
        for text, row, col in scientific_buttons:
            btn = CustomButton(text, color_scheme)
            btn.color_scheme = color_scheme.copy()
            btn.color_scheme['button_rgb'] = color_scheme['special_rgb']
            btn.setup_style()
            btn.update_size(self.scale_factor)
            btn.clicked.connect(lambda checked, t=text: self.on_scientific_click(t))
            buttons_layout.addWidget(btn, row, col)
        
        # Устанавливаем column stretch для правильного распределения пространства
        buttons_layout.setColumnStretch(0, 1)
        buttons_layout.setColumnStretch(1, 1)
        buttons_layout.setColumnStretch(2, 1)
        buttons_layout.setColumnStretch(3, 1)
        
        # Устанавливаем row stretch для лучшего распределения
        for i in range(8):  # 8 строк (0-7)
            buttons_layout.setRowStretch(i, 1)
        
        # Увеличиваем stretch для строки с кнопкой 0 (строка 4), чтобы поднять её повыше от sin
        buttons_layout.setRowStretch(4, 2)   # <-- дополнительный отступ
        
        # Добавляем контейнер для кнопок чтобы они заполняли все пространство
        button_container = QWidget()
        button_container.setLayout(buttons_layout)
        layout.addWidget(button_container)
    
    def create_dock_panels(self):
        """Создает сворачиваемые панели для шагов и истории"""
        # Док-панель для шагов
        self.steps_dock = QDockWidget("📋 Пошаговое решение", self)
        self.steps_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)
        
        self.steps_display = QTextEdit()
        self.steps_display.setReadOnly(True)
        self.steps_display.setFont(QFont("Courier New", 11))
        self.steps_display.setMinimumWidth(400)
        self.steps_display.setMinimumHeight(300)
        
        self.steps_dock.setWidget(self.steps_display)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.steps_dock)
        self.steps_dock.hide()  # Сначала скрыта
        
        # Док-панель для истории
        self.history_dock = QDockWidget("📚 История вычислений", self)
        self.history_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)
        
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setFont(QFont("Arial", 10))
        self.history_display.setMinimumWidth(350)
        self.history_display.setMinimumHeight(200)
        
        self.history_dock.setWidget(self.history_display)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.history_dock)
        self.history_dock.hide()  # Сначала скрыта
    
    def toggle_steps_dock(self):
        """Переключает видимость панели шагов"""
        if self.steps_dock.isVisible():
            self.steps_dock.hide()
        else:
            self.steps_dock.show()
            self.history_dock.hide()  # Закрываем историю при открытии шагов
    
    def toggle_history_dock(self):
        """Переключает видимость панели истории"""
        if self.history_dock.isVisible():
            self.history_dock.hide()
        else:
            self.history_dock.show()
            self.steps_dock.hide()  # Закрываем шаги при открытии истории
    
    def on_button_click(self, text):
        """Обработка нажатия кнопок"""
        current_text = self.display.text()
        
        if text == 'C':
            self.display.clear()
            self.steps_display.clear()
        elif text == '=':
            self.calculate()
        elif text == '±':
            if current_text and current_text != '0':
                if current_text.startswith('-'):
                    self.display.setText(current_text[1:])
                else:
                    self.display.setText('-' + current_text)
        elif text == '%':
            try:
                value = float(current_text) / 100
                self.display.setText(str(value))
            except:
                pass
        elif text in ['÷', '×', '-', '+']:
            self.display.setText(current_text + ' ' + text + ' ')
        elif text == '.':
            if '.' not in current_text.split()[-1] if current_text else True:
                self.display.setText(current_text + text)
        else:  # Цифры
            self.display.setText(current_text + text)
    
    def on_scientific_click(self, text):
        """Обработка научных функций"""
        current_text = self.display.text()
        
        if text == 'π':
            self.display.setText(current_text + str(math.pi))
        elif text == 'e':
            self.display.setText(current_text + str(math.e))
        elif text == '√':
            self.display.setText(current_text + 'sqrt(')
        elif text == 'x²':
            self.display.setText(current_text + '**2')
        elif text == 'xʸ':
            self.display.setText(current_text + '**')
        elif text in ['sin', 'cos', 'tan']:
            self.display.setText(current_text + f'{text}(')
        elif text in ['log', 'ln']:
            if text == 'log':
                self.display.setText(current_text + 'log10(')
            else:
                self.display.setText(current_text + 'log(')
        elif text in ['(', ')']:
            self.display.setText(current_text + text)
    
    def calculate(self):
        """Выполняет вычисление"""
        expression = self.display.text()
        if not expression:
            return
        
        try:
            # Подготовка выражения для вычисления
            expr = expression.replace('÷', '/').replace('×', '*').replace('π', str(math.pi)).replace('e', str(math.e))
            
            # Заменяем научные функции
            expr = expr.replace('sqrt(', 'math.sqrt(')
            expr = expr.replace('sin(', 'math.sin(')
            expr = expr.replace('cos(', 'math.cos(')
            expr = expr.replace('tan(', 'math.tan(')
            expr = expr.replace('log10(', 'math.log10(')
            expr = expr.replace('log(', 'math.log(')
            
            if self.steps_checkbox.isChecked():
                # Пошаговое решение
                result, steps = self.solver.solve_with_steps(expression)
                if result is not None:
                    self.display.setText(str(result))
                    self.steps_display.setText('\n'.join(steps))
                    
                    # Добавляем в историю
                    self.add_to_history(expression, result)
                else:
                    self.steps_display.setText('\n'.join(steps))
            else:
                # Простое вычисление
                result = eval(expr)
                self.display.setText(str(result))
                self.steps_display.setText(f"✅ Результат: {result}")
                
                # Добавляем в историю
                self.add_to_history(expression, result)
                
        except Exception as e:
            self.display.setText("Ошибка")
            self.steps_display.setText(f"❌ Ошибка вычисления: {str(e)}")
    
    def add_to_history(self, expression, result):
        """Добавляет вычисление в историю"""
        history_entry = f"{expression} = {result}\n"
        self.history.append(history_entry)
        
        # Обновляем отображение истории
        self.history_display.setText(''.join(self.history[-10:]))  # Показываем последние 10 записей
    
    def change_theme(self, theme_name):
        """Изменяет тему интерфейса"""
        self.current_theme = "dark" if theme_name == "Темная" else "light"
        self.apply_theme()
    
    def apply_theme(self):
        """Применяет комфортную пастельную тему"""
        color_scheme = self.themes[self.current_theme]
        
        # Применяем стили к главному окну
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color_scheme['bg']}, 
                    stop:1 rgba({color_scheme['button_rgb']}, 0.05));
            }}
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color_scheme['display_bg']}, 
                    stop:1 rgba({color_scheme['button_rgb']}, 0.1));
                color: {color_scheme['text']};
                border: 1px solid rgba({color_scheme['border_rgb']}, 0.4);
                border-radius: 12px;
                padding: 15px;
                font-size: 24px;
                font-weight: 500;
                selection-background-color: rgba({color_scheme['accent_rgb']}, 0.2);
            }}
            QTextEdit {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color_scheme['panel_bg']}, 
                    stop:1 rgba({color_scheme['button_rgb']}, 0.05));
                color: {color_scheme['text']};
                border: 1px solid rgba({color_scheme['border_rgb']}, 0.3);
                border-radius: 10px;
                padding: 15px;
                selection-background-color: rgba({color_scheme['accent_rgb']}, 0.15);
            }}
            QLabel {{
                color: {color_scheme['text']};
                font-weight: 500;
            }}
            QComboBox {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color_scheme['display_bg']}, 
                    stop:1 rgba({color_scheme['button_rgb']}, 0.1));
                color: {color_scheme['text']};
                border: 1px solid rgba({color_scheme['border_rgb']}, 0.4);
                border-radius: 8px;
                padding: 8px;
                font-weight: 500;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid rgba({color_scheme['border_rgb']}, 0.8);
            }}
            QCheckBox {{
                color: {color_scheme['text']};
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid rgba({color_scheme['border_rgb']}, 0.5);
                border-radius: 4px;
                background: rgba({color_scheme['button_rgb']}, 0.2);
            }}
            QCheckBox::indicator:checked {{
                background: rgba({color_scheme['accent_rgb']}, 0.6);
                border: 1px solid rgba({color_scheme['accent_rgb']}, 0.8);
            }}
            QToolButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({color_scheme['button_rgb']}, 0.5), 
                    stop:1 rgba({color_scheme['button_rgb']}, 0.3));
                color: {color_scheme['text']};
                border: 1px solid rgba({color_scheme['border_rgb']}, 0.4);
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: 500;
            }}
            QToolButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({color_scheme['button_rgb']}, 0.7), 
                    stop:1 rgba({color_scheme['button_rgb']}, 0.4));
                border: 1px solid rgba({color_scheme['border_rgb']}, 0.6);
            }}
            QDockWidget {{
                color: {color_scheme['text']};
                font-weight: 500;
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
            }}
            QDockWidget::title {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba({color_scheme['button_rgb']}, 0.4), 
                    stop:1 rgba({color_scheme['accent_rgb']}, 0.2));
                padding: 10px;
                border-radius: 5px;
                font-weight: 500;
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
        """)
        
        # Обновляем кнопки
        self.update_buttons_style()
        
        # Обновляем кнопки док-панелей
        self.update_dock_buttons_style()
        
        # Принудительно перерисовываем интерфейс
        self.repaint()
    
    def update_dock_buttons_style(self):
        """Обновляет стиль кнопок док-панелей с пастельными цветами"""
        color_scheme = self.themes[self.current_theme]
        
        self.steps_button.setStyleSheet(f"""
            QToolButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({color_scheme['special_rgb']}, 0.5), 
                    stop:1 rgba({color_scheme['special_rgb']}, 0.3));
                color: {color_scheme['text']};
                border: 1px solid rgba({color_scheme['special_rgb']}, 0.5);
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: 500;
            }}
            QToolButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({color_scheme['special_rgb']}, 0.7), 
                    stop:1 rgba({color_scheme['special_rgb']}, 0.4));
                border: 1px solid rgba({color_scheme['special_rgb']}, 0.7);
            }}
        """)
        
        self.history_button.setStyleSheet(f"""
            QToolButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({color_scheme['operator_rgb']}, 0.5), 
                    stop:1 rgba({color_scheme['operator_rgb']}, 0.3));
                color: {color_scheme['text']};
                border: 1px solid rgba({color_scheme['operator_rgb']}, 0.5);
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: 500;
            }}
            QToolButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({color_scheme['operator_rgb']}, 0.7), 
                    stop:1 rgba({color_scheme['operator_rgb']}, 0.4));
                border: 1px solid rgba({color_scheme['operator_rgb']}, 0.7);
            }}
        """)
    
    def update_buttons_style(self):
        """Обновляет стиль кнопок с учётом их типа"""
        color_scheme = self.themes[self.current_theme]
        
        for button in self.findChildren(CustomButton):
            text = button.text()
            # Создаём копию схемы для индивидуальной настройки
            new_scheme = color_scheme.copy()
            # Определяем тип кнопки и устанавливаем нужный цвет
            if text in ['÷', '×', '-', '+']:
                new_scheme['button_rgb'] = color_scheme['operator_rgb']
            elif text == 'C':
                new_scheme['button_rgb'] = color_scheme['clear_rgb']
            elif text == '=':
                new_scheme['button_rgb'] = color_scheme['accent_rgb']
            elif text.isdigit():
                new_scheme['button_rgb'] = color_scheme['number_rgb']
            elif text in ['sin', 'cos', 'tan', '√', 'log', 'ln', 'x²', 'xʸ', 'π', 'e', '(', ')']:
                new_scheme['button_rgb'] = color_scheme['special_rgb']
            else:
                new_scheme['button_rgb'] = color_scheme['button_rgb']
            # Применяем новую схему и обновляем стиль
            button.color_scheme = new_scheme
            button.setup_style()


def main():
    app = QApplication(sys.argv)
    calculator = CalculatorApp()
    calculator.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
