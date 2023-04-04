import tkinter as tk
from tkinter import filedialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk

def select_pdfs():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    if file_paths:
        for file_path in file_paths:
            pdf_listbox.insert(tk.END, file_path)

def update_preview(file_path, page_number):
    pdf_doc = fitz.open(file_path)
    page_count = len(pdf_doc)

    if 0 <= page_number < page_count:
        page = pdf_doc[page_number]
        zoom = 0.7
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)

        pil_image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        image_tk = ImageTk.PhotoImage(pil_image)

        pdf_preview.config(image=image_tk)
        pdf_preview.image = image_tk

        pdf_preview_modified.config(image=image_tk)
        pdf_preview_modified.image = image_tk

        page_number_var.set(f"{page_number + 1}/{page_count}")

def on_pdf_selected(event):
    global current_pdf
    global current_page

    current_pdf = pdf_listbox.get(pdf_listbox.curselection())
    current_page = 0
    update_preview(current_pdf, current_page)

def change_page(increment):
    global current_page
    if current_pdf:
        current_page += increment
        update_preview(current_pdf, current_page)

def go_to_page():
    if current_pdf:
        page_number = int(page_entry.get()) - 1
        update_preview(current_pdf, page_number)

current_pdf = None
current_page = 0

root = tk.Tk()
root.title("PDF Bulk Highlighter")


select_frame = tk.Frame(root)
select_frame.pack(anchor='nw', padx=5, pady=5)

modifiers_frame = tk.Frame(root)
modifiers_frame.pack(anchor='ne', padx=5, pady=5)

preview_frame = tk.Frame(root)
preview_frame.pack(anchor='s', padx=5, pady=5)


select_button = tk.Button(select_frame, text="Select PDFs", command=select_pdfs)
select_button.grid(row=0, column=0, pady=10)

pdf_listbox = tk.Listbox(select_frame, width=100)
pdf_listbox.grid(row=1, column=0, pady=10)
pdf_listbox.bind("<<ListboxSelect>>", on_pdf_selected)


pdf_preview = tk.Label(preview_frame)
pdf_preview.pack(side=tk.LEFT, padx=10, pady=10)

pdf_preview_modified = tk.Label(preview_frame)
pdf_preview_modified.pack(side=tk.RIGHT, padx=10, pady=10)

page_controls = tk.Frame(preview_frame)
page_controls.pack(side=tk.TOP, padx=10, pady=10)

prev_button = tk.Button(page_controls, text="<", command=lambda: change_page(-1))
prev_button.grid(row=0, column=0)

page_number_var = tk.StringVar()
page_entry = tk.Entry(page_controls, textvariable=page_number_var, width=10)
page_entry.grid(row=0, column=1)

page_entry.bind("<Return>", lambda event: go_to_page())

next_button = tk.Button(page_controls, text=">", command=lambda: change_page(1))
next_button.grid(row=0, column=2)

# Prevent the user from resizing the window
root.resizable(0, 0)

root.mainloop()
