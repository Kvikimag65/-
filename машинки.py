import sys
import json
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox, QFileDialog
)

class RoyalCarriage:
    """Класс, описывающий одну единицу транспорта."""
    def __init__(self, beast_kind: str, swiftness: float, seal=None, state="в стойле"):
        self.seal = seal if seal else f"УКАЗ-№{random.randint(1000, 9999)}"
        self.beast_kind = beast_kind
        self.swiftness = swiftness
        self.state = state

    def to_dict(self):
        return {
            "seal": self.seal,
            "kind": self.beast_kind,
            "speed": self.swiftness,
            "state": self.state
        }

class KingdomRegistry:
    """Класс для хранения списка транспорта и вычисления статистики."""
    def __init__(self):
        self.fleet = []

    def enlist_carriage(self, kind: str, swiftness: float):
        new_c = RoyalCarriage(kind, swiftness)
        self.fleet.append(new_c)
        return new_c.seal

    def export_scroll(self, path):
        data_to_save = [c.to_dict() for c in self.fleet]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def import_scroll(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.fleet = []
        for item in loaded_data:
            new_c = RoyalCarriage(
                beast_kind=item['kind'],
                swiftness=item['speed'],
                seal=item['seal'],
                state=item['state']
            )
            self.fleet.append(new_c)

    def gather_tribute_stats(self):
        fleet_size = len(self.fleet)
        driving = len([c for c in self.fleet if c.state == "гонит"])
        dead = len([c for c in self.fleet if c.state == "загнана"])
        stable = len([c for c in self.fleet if c.state == "в стойле"])
        all_swiftness = [c.swiftness for c in self.fleet]
        
        if fleet_size > 0:
            g_min, g_max, g_avg = min(all_swiftness), max(all_swiftness), sum(all_swiftness)/fleet_size
        else:
            g_min = g_max = g_avg = 0.0
        return fleet_size, driving, dead, stable, (g_min, g_max, g_avg)

class ThroneRoom(QMainWindow):
    """Главный класс графического интерфейса PyQt6."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Царский Указ: Управление транспортом (PyQt6)")
        self.resize(700, 550)
        
        # Исправленные стили! Теперь добавлены ЧЕРНЫЕ чернила (color: #000000;)
        self.setStyleSheet("""
            QMainWindow { background-color: #f4e1c1; }
            QWidget { font-family: Arial; font-size: 14px; color: #000000; }
            QLabel { font-weight: bold; }
            QLineEdit { background-color: #ffffff; color: #000000; border: 1px solid #8b4513; padding: 4px; }
            QPushButton { border-radius: 5px; padding: 6px; font-weight: bold; color: #000000; border: 1px solid #8b4513; }
            QPushButton:hover { opacity: 0.8; }
            QListWidget { background-color: #fffdf7; border: 2px solid #8b4513; color: #000000; padding: 5px; }
        """)

        self.registry = KingdomRegistry()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self._build_ui()
        self.update_list()

    def _build_ui(self):
        # 1. Блок ввода данных
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Тип (порода):"))
        self.kind_input = QLineEdit()
        input_layout.addWidget(self.kind_input)
        
        input_layout.addWidget(QLabel("Скорость:"))
        self.speed_input = QLineEdit()
        self.speed_input.setFixedWidth(80)
        input_layout.addWidget(self.speed_input)

        add_btn = QPushButton("Добавить")
        add_btn.setStyleSheet("background-color: #d4af37;")
        add_btn.clicked.connect(self.add_new)
        input_layout.addWidget(add_btn)

        # НОВАЯ КНОПКА: Изменить существующее
        edit_btn = QPushButton("Изменить (Правка)")
        edit_btn.setStyleSheet("background-color: #f0e68c;")
        edit_btn.clicked.connect(self.edit_carriage)
        input_layout.addWidget(edit_btn)
        
        self.main_layout.addLayout(input_layout)

        # 2. Блок сохранения и загрузки
        file_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить (Экспорт)")
        save_btn.setStyleSheet("background-color: #c0c0c0;")
        save_btn.clicked.connect(self.save_data)
        
        load_btn = QPushButton("Загрузить (Импорт)")
        load_btn.setStyleSheet("background-color: #c0c0c0;")
        load_btn.clicked.connect(self.load_data)

        file_layout.addWidget(save_btn)
        file_layout.addWidget(load_btn)
        self.main_layout.addLayout(file_layout)

        # 3. Список транспорта
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_select)
        self.main_layout.addWidget(self.list_widget)

        # 4. Блок кнопок управления
        control_layout = QHBoxLayout()
        go_btn = QPushButton("Погнать (Start)")
        go_btn.setStyleSheet("background-color: #ff9999;") # Сделал цвет чуть сочнее
        go_btn.clicked.connect(self.go_carriage)
        
        stop_btn = QPushButton("Остановить (Stop)")
        stop_btn.setStyleSheet("background-color: #87ceeb;") # Сделал цвет чуть сочнее
        stop_btn.clicked.connect(self.stop_carriage)
        
        report_btn = QPushButton("Статистика (Отчет)")
        report_btn.setStyleSheet("background-color: #98fb98;")
        report_btn.clicked.connect(self.show_report)

        control_layout.addWidget(go_btn)
        control_layout.addWidget(stop_btn)
        control_layout.addWidget(report_btn)
        self.main_layout.addLayout(control_layout)

        # 5. Статус-бар внизу окна
        self.statusBar().showMessage("Государь, программа готова к работе.")

    def update_list(self):
        """Обновление списка на экране."""
        self.list_widget.clear()
        for c in self.registry.fleet:
            self.list_widget.addItem(f"{c.seal} | {c.beast_kind} | Прыть: {c.swiftness} | Статус: {c.state}")
        
        self.statusBar().showMessage(f"Всего записей в реестре: {len(self.registry.fleet)}")

    def on_select(self):
        """Реакция на выбор элемента в списке. Теперь заполняет поля для удобного редактирования!"""
        selected_items = self.list_widget.selectedIndexes()
        if selected_items:
            row = selected_items[0].row()
            c = self.registry.fleet[row]
            self.statusBar().showMessage(f"Выбрана повозка: {c.seal} ({c.state})")
            
            # Автоматически подставляем данные в верхние поля, чтобы барину было легче править
            self.kind_input.setText(c.beast_kind)
            self.speed_input.setText(str(c.swiftness))

    def add_new(self):
        kind = self.kind_input.text().strip()
        speed_text = self.speed_input.text().strip()
        
        if not kind:
            QMessageBox.warning(self, "Ошибка", "Укажите тип повозки!")
            return
            
        try:
            speed = float(speed_text)
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Скорость должна быть числом!")
            return

        self.registry.enlist_carriage(kind, speed)
        self.update_list()
        self.kind_input.clear()
        self.speed_input.clear()

    def edit_carriage(self):
        """Новая царская функция: Переписать указ (изменить данные)"""
        c = self.get_selected_carriage()
        if not c:
            return # Ошибка уже показана в get_selected_carriage
            
        kind = self.kind_input.text().strip()
        speed_text = self.speed_input.text().strip()
        
        if not kind:
            QMessageBox.warning(self, "Ошибка", "Укажите тип повозки!")
            return
            
        try:
            speed = float(speed_text)
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Скорость должна быть числом!")
            return

        # Меняем данные у выбранной повозки
        c.beast_kind = kind
        c.swiftness = speed
        
        self.update_list()
        QMessageBox.information(self, "Успех", f"Данные для {c.seal} успешно изменены!")
        self.kind_input.clear()
        self.speed_input.clear()

    def get_selected_carriage(self):
        """Вспомогательная функция для получения выбранной повозки."""
        selected_items = self.list_widget.selectedIndexes()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Сначала выберите повозку из списка!")
            return None
        return self.registry.fleet[selected_items[0].row()]

    def go_carriage(self):
        c = self.get_selected_carriage()
        if c:
            c.state = "гонит"
            self.update_list()

    def stop_carriage(self):
        c = self.get_selected_carriage()
        if c:
            c.state = "загнана"
            self.update_list()

    def show_report(self):
        sz, drv, dead, stb, (mi, ma, av) = self.registry.gather_tribute_stats()
        report_text = (
            f"Всего транспорта: {sz}\n"
            f"В движении: {drv}\n"
            f"Остановлено: {dead}\n"
            f"Ожидает: {stb}\n\n"
            f"Минимальная скорость: {mi:.1f}\n"
            f"Максимальная скорость: {ma:.1f}\n"
            f"Средняя скорость: {av:.1f}"
        )
        QMessageBox.information(self, "Казначейский отчет", report_text)

    def save_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "JSON Files (*.json)")
        if path:
            self.registry.export_scroll(path)
            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")

    def load_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "JSON Files (*.json)")
        if path:
            try:
                self.registry.import_scroll(path)
                self.update_list()
                QMessageBox.information(self, "Успех", "Данные загружены!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось прочитать файл:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThroneRoom()
    window.show()
    sys.exit(app.exec())
