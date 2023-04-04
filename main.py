import tkinter as tk
from tkinter import filedialog, colorchooser
import fitz  # PyMuPDF
from PIL import Image, ImageTk

def select_pdfs():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    if file_paths:
        for file_path in file_paths:
            pdf_listbox.insert(tk.END, file_path)

def clear_pdfs():
    pdf_listbox.delete(0, tk.END)

def add_text():
    text = modifiers_text_entry.get()
    if text:
        modifiers_text_listbox.insert(tk.END, text)
        modifiers_text_entry.delete(0, tk.END)

def remove_text():
    selected = modifiers_text_listbox.curselection()
    if selected:
        for index in reversed(selected):
            modifiers_text_listbox.delete(index)

def update_preview(file_path, page_number):
    pdf_doc = fitz.open(file_path)
    
    global page_count
    page_count = len(pdf_doc)

    if 0 <= page_number < page_count:
        page = pdf_doc[page_number]
        zoom = 0.8
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)

        pil_image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        image_tk = ImageTk.PhotoImage(pil_image)

        pdf_preview.config(image=image_tk)
        pdf_preview.image = image_tk

        pdf_preview_modified.config(image=image_tk)
        pdf_preview_modified.image = image_tk

        page_number_var.set(f"{page_number + 1}")
        total_page_number_var.set(f"{page_number + 1}/{page_count}")

def on_pdf_selected(event):
    global current_pdf
    global current_page

    current_pdf = pdf_listbox.get(pdf_listbox.curselection())
    current_page = 0
    update_preview(current_pdf, current_page)

def change_page(increment):
    global current_page
    
    if (current_page == 0) and (increment < 0):
        return
    
    if (current_page == page_count-1) and (increment > 0):
        return

    if current_pdf:
        current_page += increment
        update_preview(current_pdf, current_page)

def go_to_page():
    if current_pdf:
        pg = int(page_entry.get())
        if pg < 1:
            pg = 1
        elif pg > page_count:
            pg = page_count
        else:
            None
        
        update_preview(current_pdf, pg-1)

def change_color():
    global colors
    colors = colorchooser.askcolor(title="Tkinter Color Chooser", color=colors[1])
    highlight_options_selected_color.configure(bg=colors[1])

current_pdf = None
current_page = 0

colors = [None, "#FFFF77"]

root = tk.Tk()
root.title("PDF Bulk Highlighter")

select_frame = tk.Frame(root)
select_frame.grid(row=0, column=0, padx=5, pady=5, rowspan=2)


text_finder_frame = tk.Frame(root)
text_finder_frame.grid(row=0, column=1, padx=5, pady=5, rowspan=3)

text_finder_buttons_frame = tk.Frame(text_finder_frame)
text_finder_buttons_frame.grid(row=0, column=0, padx=5)

text_finder_list_frame = tk.Frame(text_finder_frame)
text_finder_list_frame.grid(row=1, column=0, padx=5, pady=5)


preview_frame = tk.Frame(root)
preview_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

#######################################

select_button = tk.Button(select_frame, text="Select PDFs", command=select_pdfs)
select_button.grid(row=0, column=0, pady=10)

clear_button = tk.Button(select_frame, text="Clear PDFs", command=clear_pdfs)
clear_button.grid(row=0, column=1, pady=10)

pdf_listbox = tk.Listbox(select_frame, width=75)
pdf_listbox.grid(row=1, column=0, columnspan=2, pady=10)
pdf_listbox.bind("<<ListboxSelect>>", on_pdf_selected)


modifiers_add_button = tk.Button(text_finder_buttons_frame, text="Add Text", command=add_text)
modifiers_add_button.grid(row=0, column=0, pady=10, padx=5)

modifiers_remove_button = tk.Button(text_finder_buttons_frame, text="Remove Text", command=remove_text)
modifiers_remove_button.grid(row=0, column=1, pady=10, padx=5)

modifiers_text = tk.Label(text_finder_list_frame, text="Find:")
modifiers_text.grid(row=0, column=0, padx=5)

modifiers_text_entry = tk.Entry(text_finder_list_frame, width=33)
modifiers_text_entry.grid(row=0, column=1, padx=5)

modifiers_text_listbox = tk.Listbox(text_finder_list_frame, width=33, selectmode=tk.EXTENDED)
modifiers_text_listbox.grid(row=1, column=1, pady=10)

highlight_options_button = tk.Button(text_finder_list_frame, text="Choose Highlight", command=change_color)
highlight_options_button.grid(row=0, column=3, pady=10)
highlight_options_selected_color = tk.Frame(text_finder_list_frame, bg=colors[1], width=35, height=35)
highlight_options_selected_color.grid(row=0, column=2, pady=10, padx=10)

apply_highlight_button = tk.Button(text_finder_list_frame, text="Find Words")
apply_highlight_button.grid(row=1, column=2, pady=10)
apply_highlight_button = tk.Button(text_finder_list_frame, text="Apply")
apply_highlight_button.grid(row=1, column=3, pady=10)


pdf_preview = tk.Label(preview_frame)
pdf_preview.grid(row=2, column=0, padx=5, pady=5)
pdf_preview_title = tk.Label(preview_frame, text="Original")
pdf_preview_title.grid(row=1, column=0, padx=5)
pdf_preview_title.config(font =("Arial", 14))

page_controls = tk.Frame(preview_frame)
page_controls.grid(row=1, column=1, padx=5, pady=5)

pdf_preview_modified = tk.Label(preview_frame)
pdf_preview_modified.grid(row=2, column=2, padx=5, pady=5)
pdf_preview_title_modified = tk.Label(preview_frame, text="Modified")
pdf_preview_title_modified.grid(row=1, column=2, padx=5)
pdf_preview_title_modified.config(font =("Arial", 14))

prev_button = tk.Button(page_controls, text="<", command=lambda: change_page(-1))
prev_button.grid(row=0, column=0)

total_page_number_var = tk.StringVar(value="0/0")
total_page_entry = tk.Label(page_controls, textvariable=total_page_number_var)
total_page_entry.grid(row=0, column=1)
total_page_entry.config(font =("Arial", 16))

page_number_var = tk.StringVar()
page_entry = tk.Entry(page_controls, textvariable=page_number_var, width=5)
page_entry.grid(row=1, column=1)

page_entry.bind("<Return>", lambda event: go_to_page())

next_button = tk.Button(page_controls, text=">", command=lambda: change_page(1))
next_button.grid(row=0, column=2)

# Prevent the user from resizing the window
root.resizable(0, 0)

root.mainloop()
