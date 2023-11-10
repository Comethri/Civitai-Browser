import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QGridLayout, QDialog
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, Qt
import requests
import configparser
import os
import webbrowser

script_path = os.path.dirname(os.path.abspath(__file__))

ini_path = os.path.join(script_path, 'stuff', 'config.ini')
model_api = "https://civitai.com/api/v1/models"

config = configparser.ConfigParser()
config.read(ini_path)

items_per_page = int(config['General']['items_per_page'])

class DataLoaderThread(QThread):
    data_loaded = pyqtSignal(dict)

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

# Detailed information, coming upo when left clicked on model info, TBQ
class ModelDetailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model Details")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout(self)
        self.details_label = QLabel()
        self.layout.addWidget(self.details_label)

        self.setStyleSheet("QDialog {background-color: #2d2d2d; color: white;}")
        self.details_label.setStyleSheet("QLabel {color: white;}")

    def set_model_details(self, details):
        if not isinstance(details, dict):
            details = {}

        # information about model
        details_text = f"Name: {details.get('name', 'N/A')}\n"
        details_text += f"Type: {details.get('type', 'N/A')}\n"
        details_text += f"NSFW: {self.convert_boolean_to_string(details.get('nsfw', False))}\n"
        details_text += f"Allow Commercial Use: {self.convert_boolean_to_string(details.get('allowCommercialUse', False))}\n"

        # show model version
        model_versions = details.get('modelVersions', [])
        if model_versions:
            details_text += "\nModel Versions:\n"
            for version in model_versions:
                model_details_text = ""

                model_details_text += f"  - Name: {version.get('name', 'N/A')}\n"
                model_details_text += f"    BaseModel: {version.get('baseModel', 'N/A')}\n"
                
                # Download button
                download_url = version.get('downloadUrl', 'N/A')
                model_details_text += f"    DownloadUrl: {download_url}\n"

                download_button = QPushButton("Download")
                download_button.clicked.connect(lambda _, url=download_url: self.download_file(url))

                model_version_label = QLabel(model_details_text)
                model_version_label.setStyleSheet("QLabel {color: white;}")
                self.layout.addWidget(model_version_label)
                self.layout.addWidget(download_button)

        self.details_label.setText(details_text)

    def convert_boolean_to_string(self, boolean_value):
        return "Yes" if boolean_value else "No"
    
    def download_file(self, url):
        print("Open Browser to download: ")
        webbrowser.open(url)

class ModelBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("CivitAI Models Browser")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("ModelBrowser {background-color: #2d2d2d; color: white;}")

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
        self.scroll_area.setStyleSheet("QScrollArea {background-color: #2d2d2d;}")

        self.scroll_contents = QWidget()
        self.scroll_area.setWidget(self.scroll_contents)
        self.scroll_contents.setStyleSheet("QWidget {background-color: #2d2d2d; color: #fff;}")

        self.grid_layout = QGridLayout(self.scroll_contents)
        self.grid_layout.setHorizontalSpacing(0)
        self.grid_layout.setVerticalSpacing(0)

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

        self.fetch_data(1)

    def closeEvent(self, event):
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
        nsfw = item.get('nsfw', False)
        nsfw_string = self.convert_boolean_to_string(nsfw)
        allow_commercial_use = item.get('allowCommercialUse', False)
        allow_commercial_use_string = self.convert_boolean_to_string(allow_commercial_use)
        model_versions = item.get('modelVersions', [])
        num_model_versions = len(model_versions)

        info_text = f"ID: {id}\nName: {name}\nType: {type}\nNSFW: {nsfw_string}\nAllow Commercial Use: {allow_commercial_use_string}"
        info_text += f"\nNumber of Model Versions: {num_model_versions}"
        info_label = QLabel(info_text)
        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        frame.setLayout(QVBoxLayout())
        frame.layout().addWidget(info_label)
        self.grid_layout.addWidget(frame, grid_row, grid_col)

        frame.mousePressEvent = lambda event, item=item: self.show_model_details(item)

    def convert_boolean_to_string(self, boolean_value):
        return "Yes" if boolean_value else "No"
    
    def show_model_details(self, item):
        model_name = item.get('name', 'N/A')
        print(f"Open Model Details: {model_name}")
        
        details_dialog = ModelDetailDialog(self)
        details_dialog.setWindowTitle(f"{model_name}")
        details_dialog.set_model_details(item)
        details_dialog.exec_()

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
            self.fetch_data_with_search(search_text)
        else:
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
