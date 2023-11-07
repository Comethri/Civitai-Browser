import tkinter as tk
import requests
from PIL import Image, ImageTk
import io

model_api = "https://civitai.com/api/v1/models"
page_number = 1
items_per_page = 20
canvas = None

def fetch_and_display_image(url, grid_row, grid_col):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)

            image_label = tk.Label(canvas, image=photo)
            image_label.grid(row=grid_row, column=grid_col, sticky="w")
            image_label.photo = photo
    except Exception as e:
        print(f"error loading image: {e}")

def display_item_info(item, grid_row, grid_col):
    id = item.get('id', 'N/A')
    name = item.get('name', 'N/A')
    type = item.get('type', 'N/A')

    if 'modelVersions' in item and 'images' in item['modelVersions'][0]:
        image_url = item['modelVersions'][0]['images'][0]['url']
        fetch_and_display_image(image_url, grid_row, grid_col)

    info_text = f"ID: {id}\nName: {name}\nType: {type}"
    info_label = tk.Label(canvas, text=info_text, justify=tk.LEFT)
    info_label.grid(row=grid_row, column=grid_col + 1, sticky="w")

def print_items(items):
    global canvas
    if canvas:
        canvas.destroy()

    canvas = tk.Frame(root)
    canvas.grid(row=1, column=0, sticky="w")

    grid_row, grid_col = 0, 0

    for item in items:
        display_item_info(item, grid_row, grid_col)
        grid_row += 1

        if grid_row >= 5:
            grid_col += 2
            grid_row = 0

def fetch_data(page_number):
    global canvas
    url = f"{model_api}?page={page_number}"
    r = requests.get(url)
    data = r.json()
    items = data.get('items', [])
    metadata = data.get('metadata', {})
    current_page = metadata.get('currentPage', 1)
    total_pages = metadata.get('totalPages', 1)
    page_number_entry.delete(0, "end")
    page_number_entry.insert(0, str(current_page))
    print_items(items)
    page_number_label.config(text=f"Page {current_page} of {total_pages}")
    
    prev_button.config(state=tk.NORMAL if current_page > 1 else tk.DISABLED)
    next_button.config(state=tk.NORMAL if current_page < total_pages else tk.DISABLED)

def navigate_prev():
    current_page = int(page_number_entry.get())
    if current_page > 1:
        current_page -= 1
        fetch_data(current_page)

def navigate_next():
    current_page = int(page_number_entry.get())
    total_pages = int(page_number_label.cget("text").split(" of ")[-1])
    if current_page < total_pages:
        current_page += 1
        fetch_data(current_page)

def go_to_page():
    current_page = int(page_number_entry.get())
    total_pages = int(page_number_label.cget("text").split(" of ")[-1])
    if 1 <= current_page <= total_pages:
        fetch_data(current_page)

root = tk.Tk()
root.title("CivitAI Models")

page_number_label = tk.Label(root, text="Page 1 of 1")
page_number_label.grid(row=0, column=0, sticky="w")

prev_button = tk.Button(root, text="Previous Page", state=tk.DISABLED, command=navigate_prev)
prev_button.grid(row=0, column=1, sticky="w")

page_number_entry = tk.Entry(root)
page_number_entry.grid(row=0, column=2, sticky="w")
page_number_entry.insert(0, str(page_number))

go_button = tk.Button(root, text="Go", command=go_to_page)
go_button.grid(row=0, column=3, sticky="w")

next_button = tk.Button(root, text="Next Page", state=tk.DISABLED, command=navigate_next)
next_button.grid(row=0, column=4, sticky="w")

fetch_data(page_number)

root.mainloop()
