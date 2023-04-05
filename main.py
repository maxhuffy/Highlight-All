import tkinter as tk
from tkinter import filedialog, colorchooser
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class PDFBulkHighlighter:
    def __init__(self):
        self.current_pdf = None
        self.current_page = 0
        self.colors = [None, "#FFFF77"]
        self.page_count = 0
        self.modified_pdf_doc = None
        self.no_init_highlights = True

        self.root = tk.Tk()
        self.root.title("PDF Bulk Highlighter")
        self._build_gui()
        self.root.resizable(0, 0)
        self.root.mainloop()

    def _build_gui(self):
        select_frame = tk.Frame(self.root)
        select_frame.grid(row=0, column=0, padx=5, pady=5, rowspan=2)

        text_finder_frame = tk.Frame(self.root)
        text_finder_frame.grid(row=0, column=1, padx=5, pady=5, rowspan=3)

        text_finder_buttons_frame = tk.Frame(text_finder_frame)
        text_finder_buttons_frame.grid(row=0, column=0, padx=5)

        text_finder_list_frame = tk.Frame(text_finder_frame)
        text_finder_list_frame.grid(row=1, column=0, padx=5, pady=5)

        preview_frame = tk.Frame(self.root)
        preview_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Select PDFs frame
        select_button = tk.Button(select_frame, text="Select PDFs", command=self.select_pdfs)
        select_button.grid(row=0, column=0, pady=10)

        clear_button = tk.Button(select_frame, text="Clear PDFs", command=self.clear_pdfs)
        clear_button.grid(row=0, column=1, pady=10)

        self.pdf_listbox = tk.Listbox(select_frame, width=75)
        self.pdf_listbox.grid(row=1, column=0, columnspan=2, pady=10)
        self.pdf_listbox.bind("<<ListboxSelect>>", self.on_pdf_selected)

        # Text Finder frame
        modifiers_add_button = tk.Button(text_finder_buttons_frame, text="Add Text", command=self.add_text)
        modifiers_add_button.grid(row=0, column=0, pady=10, padx=5)

        modifiers_remove_button = tk.Button(text_finder_buttons_frame, text="Remove Text", command=self.remove_text)
        modifiers_remove_button.grid(row=0, column=1, pady=10, padx=5)

        modifiers_text = tk.Label(text_finder_list_frame, text="Find:")
        modifiers_text.grid(row=0, column=0, padx=5)

        self.modifiers_text_entry = tk.Entry(text_finder_list_frame, width=33)
        self.modifiers_text_entry.grid(row=0, column=1, padx=5)

        self.modifiers_text_listbox = tk.Listbox(text_finder_list_frame, width=33, selectmode=tk.EXTENDED)
        self.modifiers_text_listbox.grid(row=1, column=1, pady=10)

        highlight_options_button = tk.Button(text_finder_list_frame, text="Choose Highlight", command=self.change_color)
        highlight_options_button.grid(row=0, column=3, pady=10)
        self.highlight_options_selected_color = tk.Frame(text_finder_list_frame, bg=self.colors[1], width=35, height=35)
        self.highlight_options_selected_color.grid(row=0, column=2, pady=10, padx=10)

        apply_highlight_button = tk.Button(text_finder_list_frame, text="Find Words", command=self.apply_highlight)
        apply_highlight_button.grid(row=1, column=2, pady=10)
        save_highlight_button = tk.Button(text_finder_list_frame, text="Save Highlight ", command=self.save_file)
        save_highlight_button.grid(row=1, column=3, pady=10)

        # Preview frame
        self.pdf_preview = tk.Label(preview_frame)
        self.pdf_preview.grid(row=2, column=0, padx=5, pady=5)
        pdf_preview_title = tk.Label(preview_frame, text="Preview")
        pdf_preview_title.grid(row=1, column=0, padx=5)
        pdf_preview_title.config(font=("Arial", 14))

        page_controls = tk.Frame(preview_frame)
        page_controls.grid(row=1, column=1, padx=5, pady=5)

        prev_button = tk.Button(page_controls, text="<", command=lambda: self.change_page(-1))
        prev_button.grid(row=0, column=0)

        self.total_page_number_var = tk.StringVar(value="0/0")
        total_page_entry = tk.Label(page_controls, textvariable=self.total_page_number_var)
        total_page_entry.grid(row=0, column=1)
        total_page_entry.config(font=("Arial", 16))

        self.page_number_var = tk.StringVar()
        page_entry = tk.Entry(page_controls, textvariable=self.page_number_var, width=5)
        page_entry.grid(row=1, column=1)

        page_entry.bind("<Return>", lambda event: self.go_to_page())

        next_button = tk.Button(page_controls, text=">", command=lambda: self.change_page(1))
        next_button.grid(row=0, column=2)

    def select_pdfs(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for file_path in file_paths:
            self.pdf_listbox.insert(tk.END, file_path)

    def clear_pdfs(self):
        self.pdf_listbox.delete(0, tk.END)
        self.current_pdf = None
        self.page_count = 0
        self.update_preview()

    def on_pdf_selected(self, event):
        selected_pdf = self.pdf_listbox.get(self.pdf_listbox.curselection())
        self.current_pdf = fitz.open(selected_pdf)
        self.page_count = len(self.current_pdf)
        self.current_page = 0
        self.update_preview()

    def add_text(self):
        text = self.modifiers_text_entry.get()
        if text:
            self.modifiers_text_listbox.insert(tk.END, text)
            self.modifiers_text_entry.delete(0, tk.END)

    def remove_text(self):
        selected_indices = self.modifiers_text_listbox.curselection()
        for index in reversed(selected_indices):
            self.modifiers_text_listbox.delete(index)

    def change_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.colors[1] = color
            self.highlight_options_selected_color.config(bg=color)

    def apply_highlight(self):
        # Write code to apply the highlight to the selected text in the PDF
        None

    def save_file(self):
        # Write code to apply the highlight to the selected text in the PDF
        None

    def update_preview(self):
        if self.current_pdf:
            page = self.current_pdf.load_page(self.current_page)
            zoom_matrix = fitz.Matrix(0.8, 0.8)
            pix = page.get_pixmap(matrix=zoom_matrix)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img = ImageTk.PhotoImage(img)
            self.pdf_preview.config(image=img)
            self.pdf_preview.image = img
            self.total_page_number_var.set(f"{self.current_page + 1}/{self.page_count}")
            self.page_number_var.set(str(self.current_page + 1))
        else:
            self.pdf_preview.config(image="")
            self.total_page_number_var.set("0/0")

    def change_page(self, delta):
        if self.current_pdf:
            new_page = self.current_page + delta
            if 0 <= new_page < self.page_count:
                self.current_page = new_page
                self.update_preview()

    def go_to_page(self):
        page_num = self.page_number_var.get()
        try:
            page_num = int(page_num) - 1
            if 0 <= page_num < self.page_count:
                self.current_page = page_num
                self.update_preview()
        except ValueError:
            pass


a = PDFBulkHighlighter()