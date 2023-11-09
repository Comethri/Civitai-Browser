import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QGridLayout
from PyQt5.QtCore import QThread, pyqtSignal

import requests

model_api = "https://civitai.com/api/v1/models"
items_per_page = 10

class DataLoaderThread(QThread):
    data_loaded = pyqtSignal(dict)
    api_call_finished = pyqtSignal()  # Füge diese Zeile hinzu

    def __init__(self, page_number, search_text=None):
        super().__init__()
        self.page_number = page_number
        self.search_text = search_text

    def run(self):
        if self.search_text:
            url = f"{model_api}?page={self.page_number}&limit={items_per_page}&query={self.search_text}"
        else:
            url = f"{model_api}?page={self.page_number}&limit={items_per_page}"

        print("API Call:", url)
        r = requests.get(url)
        data = r.json()
        self.data_loaded.emit(data)
        self.api_call_finished.emit()


class ModelBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Loading gui")

        self.setWindowTitle("CivitAI Models Browser")
        self.setGeometry(100, 100, 800, 600)

        self.page_number_label = QLabel(self)
        self.page_number_label.setText("Page 1 of 1")
        self.page_number_label.setStyleSheet("font-size: 16px; color: #3498db;")

        self.prev_button = QPushButton("Previous Page", self)
        self.prev_button.clicked.connect(self.navigate_prev)
        self.prev_button.setEnabled(False)
        self.prev_button.setStyleSheet("background-color: #1971c2; color: #fff;")

        self.page_number_entry = QLineEdit(self)
        self.page_number_entry.setText("1")
        self.page_number_entry.returnPressed.connect(self.go_to_page)
        self.page_number_entry.setStyleSheet("padding: 5px; font-size: 14px;")

        self.go_button = QPushButton("Go to Page", self)
        self.go_button.clicked.connect(self.go_to_page)
        self.go_button.setStyleSheet("background-color: #2ecc71; color: #fff; padding: 8px;")

        self.next_button = QPushButton("Next Page", self)
        self.next_button.clicked.connect(self.navigate_next)
        self.next_button.setEnabled(False)
        self.next_button.setStyleSheet("background-color: #1971c2; color: #fff;")

        self.search_entry = QLineEdit(self)
        self.search_entry.setPlaceholderText("Search models...")
        self.search_entry.returnPressed.connect(self.search_models)
        self.search_entry.setStyleSheet("padding: 8px; font-size: 14px;")

        self.home_button = QPushButton("Home", self)
        self.home_button.clicked.connect(self.show_home_page)
        self.home_button.setStyleSheet("background-color: #e74c3c; color: #fff; padding: 8px;")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.page_number_entry)
        input_layout.addWidget(self.go_button)

        home_layout = QHBoxLayout()
        home_layout.addWidget(self.home_button)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_contents = QWidget()
        self.scroll_area.setWidget(self.scroll_contents)

        self.grid_layout = QGridLayout(self.scroll_contents)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.page_number_label)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.search_entry)
        main_layout.addLayout(home_layout)
        self.setLayout(main_layout)

        self.data_loader_thread = DataLoaderThread(1)
        self.data_loader_thread.data_loaded.connect(self.handle_data_loaded)
        self.data_loader_thread.api_call_finished.connect(self.api_call_finished)

        self.fetch_data(1)

    def api_call_finished(self):
        current_page = int(self.page_number_entry.text())
        print(f"Finish. Current Page: {current_page}")

    def closeEvent(self, event):
        # Bei Schließen des Fensters alle DataLoaderThreads beenden
        self.data_loader_thread.quit()
        self.data_loader_thread.wait()
        event.accept()

    def update_gui(self):
        QApplication.processEvents()

    def handle_data_loaded(self, data):
        items = data.get('items', [])
        metadata = data.get('metadata', {})

        current_page = metadata.get('currentPage', 1)
        total_pages = metadata.get('totalPages', 1)
        self.page_number_entry.setText(str(current_page))
        self.page_number_label.setText(f"Page {current_page} of {total_pages}")
        self.prev_button.setEnabled(current_page > 1)
        self.next_button.setEnabled(current_page < total_pages)
        self.print_items(items)
        self.update_gui()

    def fetch_data(self, page_number):
        self.data_loader_thread.page_number = page_number
        self.data_loader_thread.start()

    def display_item_info(self, item, grid_row, grid_col):
        id = item.get('id', 'N/A')
        name = item.get('name', 'N/A')
        type = item.get('type', 'N/A')

        info_text = f"ID: {id}\nName: {name}\nType: {type}"
        info_label = QLabel(info_text)
        self.grid_layout.addWidget(info_label, grid_row, grid_col + 1)

    def print_items(self, items):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        grid_row, grid_col = 0, 0

        for item in items:
            self.display_item_info(item, grid_row, grid_col)
            grid_row += 1

            if grid_row >= 5:
                grid_col += 2
                grid_row = 0

    def delayed_print_items(self, items):
        print("Laaaaaaaaaags")
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        grid_row, grid_col = 0, 0

        for item in items:
            self.display_item_info(item, grid_row, grid_col)
            grid_row += 1

            if grid_row >= 5:
                grid_col += 2
                grid_row = 0
        print("lags ended, loaded succesfully")

    def fetch_data(self, page_number):
        self.data_loader_thread.page_number = page_number
        self.data_loader_thread.start()

    def handle_data_loaded(self, data):
        items = data.get('items', [])
        metadata = data.get('metadata', {})

        current_page = metadata.get('currentPage', 1)
        total_pages = metadata.get('totalPages', 1)
        self.page_number_entry.setText(str(current_page))
        self.page_number_label.setText(f"Page {current_page} of {total_pages}")
        self.prev_button.setEnabled(current_page > 1)
        self.next_button.setEnabled(current_page < total_pages)
        self.print_items(items)

    def navigate_prev(self):
        current_page = int(self.page_number_entry.text())
        if current_page > 1:
            current_page -= 1
            self.fetch_data(current_page)

    def navigate_next(self):
        current_page = int(self.page_number_entry.text())
        total_pages = int(self.page_number_label.text().split(" of ")[-1])
        if current_page < total_pages:
            current_page += 1
            self.fetch_data(current_page)

    def go_to_page(self):
        current_page = int(self.page_number_entry.text())
        total_pages = int(self.page_number_label.text().split(" of ")[-1])
        if 1 <= current_page <= total_pages:
            self.fetch_data(current_page)

    def search_models(self):
        search_text = self.search_entry.text()
        print(f"Searching for: {search_text}")

        if search_text:
            # query search text
            self.fetch_data_with_search(search_text)
        else:
            # search nothing when searchbar is empty
            self.fetch_data(1)

    def fetch_data_with_search(self, search_text):
        self.data_loader_thread.page_number = 1
        self.data_loader_thread.search_text = search_text if search_text else None
        self.data_loader_thread.start()

    def show_home_page(self):
        print("Home Button clicked. Showing home page.")
        self.search_entry.clear()
        self.fetch_data_with_search("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    model_browser = ModelBrowser()
    model_browser.show()
    sys.exit(app.exec_())
