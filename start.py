import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QGridLayout
from PyQt5.QtGui import QPixmap
import requests
from PIL import Image
import io
from PyQt5.QtGui import QImage

model_api = "https://civitai.com/api/v1/models"
page_number = 1
items_per_page = 10

class ModelBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("CivitAI Models Browser")
        self.setGeometry(100, 100, 800, 600)

        self.page_number_label = QLabel(self)
        self.page_number_label.setText("Page 1 of 1")

        self.prev_button = QPushButton("Previous Page", self)
        self.prev_button.clicked.connect(self.navigate_prev)
        self.prev_button.setEnabled(False)

        self.page_number_entry = QLineEdit(self)
        self.page_number_entry.setText(str(page_number))

        self.go_button = QPushButton("Go", self)
        self.go_button.clicked.connect(self.go_to_page)

        self.next_button = QPushButton("Next Page", self)
        self.next_button.clicked.connect(self.navigate_next)
        self.next_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.page_number_entry)
        input_layout.addWidget(self.go_button)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_contents = QWidget()
        self.scroll_area.setWidget(self.scroll_contents)

        self.grid_layout = QGridLayout(self.scroll_contents)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.page_number_label)
        self.layout.addLayout(button_layout)
        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

        self.fetch_data(page_number)


    def fetch_and_display_image(self, url, grid_row, grid_col):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image_data = response.content
                image = Image.open(io.BytesIO(image_data))

                max_size = (150, 150)  # max width, height
                image.thumbnail(max_size, Image.LANCZOS)

                # kp ob das nötig ist.
                if image.mode != "RGB":
                    image = image.convert("RGB")

                q_image = QImage(image.tobytes("raw", "RGB"), image.width, image.height, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)

                image_label = QLabel()
                image_label.setPixmap(pixmap)

                self.grid_layout.addWidget(image_label, grid_row, grid_col)
        except Exception as e:
            print(f"error loading image: {e}")


    def display_item_info(self, item, grid_row, grid_col):
        id = item.get('id', 'N/A')
        name = item.get('name', 'N/A')
        type = item.get('type', 'N/A')

        if 'modelVersions' in item and 'images' in item['modelVersions'][0]:
            image_url = item['modelVersions'][0]['images'][0]['url']
            self.fetch_and_display_image(image_url, grid_row, grid_col)

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

    def fetch_data(self, page_number):
        url = f"{model_api}?page={page_number}&limit={items_per_page}"
        print("API Call:", url)
        r = requests.get(url)
        data = r.json()
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    model_browser = ModelBrowser()
    model_browser.show()
    sys.exit(app.exec_())
