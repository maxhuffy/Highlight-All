import tkinter as tk
from tkinter import filedialog, colorchooser
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class PDFBulkHighlighter:
    def __init__(self):
        self.current_pdf = None
        self.current_page = 0

        self.colors_backup = [(255.0, 255.0, 119.0), "#FFFF77"]
        self.colors = [(255.0, 255.0, 119.0), "#FFFF77"]
        self.page_count = 0
        self.no_highlights = True

        self.selected_pdf = None

        self.root = tk.Tk()
        self.root.title("PDF Bulk Highlighter")
        self._build_gui()
        self.root.resizable(0, 0)
        self.root.mainloop()

    def _build_gui(self):
        # select_frame = tk.Frame(self.root)
        # select_frame.grid(row=0, column=0, padx=5, pady=5, rowspan=5, columnspan=7)

        # text_finder_frame = tk.Frame(self.root)
        # text_finder_frame.grid(row=6, column=0, padx=5, pady=5)

        # text_finder_buttons_frame = tk.Frame(text_finder_frame)
        # text_finder_buttons_frame.grid(row=0, column=0, padx=5, rowspan=2)

        # text_finder_list_frame = tk.Frame(text_finder_frame)
        # text_finder_list_frame.grid(row=1, column=0, padx=5, pady=5)

        # preview_frame = tk.Frame(self.root)
        # preview_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Select PDFs frame
        select_button = tk.Button(self.root, text="Select PDFs", command=self.select_pdfs, width=13)
        select_button.grid(row=0, column=1, pady=5, sticky="w")

        clear_button = tk.Button(self.root, text="Clear PDFs", command=self.clear_pdfs, width=13)
        clear_button.grid(row=0, column=2, pady=0, sticky="w")

        self.pdf_listbox = tk.Listbox(self.root, width=75)
        self.pdf_listbox.grid(row=1, column=1, pady=5, columnspan=12, sticky="w", rowspan=5)
        self.pdf_listbox.bind("<<ListboxSelect>>", self.on_pdf_selected)

        spacer = tk.Frame(self.root, width=10, height=30)
        spacer.grid(row=2+5, column=1)

        # Text Finder frame
        modifiers_add_button = tk.Button(self.root, text="Add Text", command=self.add_text, width=13)
        modifiers_add_button.grid(row=3+5, column=1, pady=5, sticky="w")

        modifiers_remove_button = tk.Button(self.root, text="Remove Text", command=self.remove_text, width=13)
        modifiers_remove_button.grid(row=3+5, column=2, pady=5, sticky="w")

        modifiers_text = tk.Label(self.root, text="Find:")
        modifiers_text.grid(row=4+5, column=0, padx=5, sticky="e")

        self.modifiers_text_entry = tk.Entry(self.root, width=37)
        self.modifiers_text_entry.grid(row=4+5, column=1, sticky="w", columnspan=3)

        self.modifiers_text_listbox = tk.Listbox(self.root, width=37, selectmode=tk.EXTENDED)
        self.modifiers_text_listbox.grid(row=5+5, column=1, pady=5, sticky="w", columnspan=3, rowspan=6)

        ##########

        highlight_options_button = tk.Button(self.root, text="Color Picker", command=self.change_color, width=13)
        highlight_options_button.grid(row=5+5, column=4, padx=10, sticky="w")
        self.highlight_options_selected_color = tk.Frame(self.root, bg=self.colors[1], width=75, height=25)
        self.highlight_options_selected_color.grid(row=5+5, column=5, padx=25)

        apply_highlight_button = tk.Button(self.root, text="Apply Highlight", command=self.apply_highlight, width=13)
        apply_highlight_button.grid(row=6+5, column=4, padx=10, sticky="w")

        reset_highlight_button = tk.Button(self.root, text="Reset Highlights", command=self.reset_pdf, width=13)
        reset_highlight_button.grid(row=6+5+1, column=4, padx=10, sticky="w")

        save_highlight_button = tk.Button(self.root, text="Save File", command=self.save_file, width=13)
        save_highlight_button.grid(row=13+18, column=1, sticky="w")
        self.markLong = tk.IntVar()
        long_marking_checkbox = tk.Checkbutton(self.root, text="Highlight entire line?", variable=self.markLong)
        long_marking_checkbox.grid(row=6+5, column=5, sticky="w")

     
        # # Preview frame

        self.pdf_preview = tk.Label(self.root)
        self.pdf_preview.grid(row=2, column=10, padx=5, pady=5, rowspan=30)

        page_controls = tk.Frame(self.root)
        page_controls.grid(row=0, column=10, padx=5, pady=5)

        pdf_preview_title = tk.Label(page_controls, text="Page")
        pdf_preview_title.grid(row=0, column=0, padx=5)
        pdf_preview_title.config(font=("Arial", 14))

        prev_button = tk.Button(page_controls, text="<", command=lambda: self.change_page(-1))
        prev_button.grid(row=0, column=1)

        self.total_page_number_var = tk.StringVar(value="0/0")
        total_page_entry = tk.Label(page_controls, textvariable=self.total_page_number_var)
        total_page_entry.grid(row=0, column=2)
        total_page_entry.config(font=("Arial", 16))

        self.page_number_var = tk.StringVar()
        page_entry = tk.Entry(page_controls, textvariable=self.page_number_var, width=5)
        page_entry.grid(row=1, column=2)

        page_entry.bind("<Return>", lambda event: self.go_to_page())

        next_button = tk.Button(page_controls, text=">", command=lambda: self.change_page(1))
        next_button.grid(row=0, column=3)

    def select_pdfs(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for file_path in file_paths:
            self.pdf_listbox.insert(tk.END, file_path)
        if len(file_paths) == 1:
            self.pdf_listbox.selection_set(0)
            self.on_pdf_selected()

    def clear_pdfs(self):
        self.pdf_listbox.delete(0, tk.END)
        self.current_pdf = None
        self.page_count = 0
        self.update_preview()

    def reset_pdf(self):
        self.current_pdf = fitz.open(self.selected_pdf)
        self.update_preview()

    def on_pdf_selected(self, event=None):
        self.no_highlights = True
        self.selected_pdf = self.pdf_listbox.get(self.pdf_listbox.curselection())
        # Stores the doc as a internal variable
        self.current_pdf = fitz.open(self.selected_pdf)
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
        self.colors = colorchooser.askcolor(title="Highlighter Color", color=self.colors[1])
        if self.colors[0]:
            self.highlight_options_selected_color.config(bg=self.colors[1])
            self.colors_backup = self.colors
        else:
            self.colors = self.colors_backup

    def mark_word(self, page, text):
        """Underline each word that contains 'text'."""
        
        stroke_color = tuple([i/255.0 for i in self.colors[0]])
        text = text.lower()
        
        wlist = page.get_text("words")  # make the word list
        for w in wlist:  # scan through all words on page
            if text == w[4].lower():  # w[4] is the word's string 
                r = fitz.Rect(w[:4])  # make rect from word bbox

                if self.markLong.get() == 1:    
                    r.x0 = 0
                    r.x1 = page.rect.x1
                    if r.y0 > 4:
                        r.y0 -= 4
                    if r.y1 < page.rect.y1 - 4:
                        r.y1 += 4

                highlight = page.add_highlight_annot(r)
                highlight.set_colors({"stroke":stroke_color})
                highlight.update()
    
    def mark_spaced_word(self, page, text):
        """Underline each word that contains 'text'."""
        
        stroke_color = tuple([i/255.0 for i in self.colors[0]])

        num_of_words = len(text.split())
        text_list = text.split()
        
        wlist = page.get_text("words")
        for w in range(len(wlist)-1):
            space_count = 0  
            for i in range(num_of_words):
                if text_list[i].lower() == wlist[w+i][4].lower():
                    space_count += 1
            
            if space_count == num_of_words:
                # Avoid double highlighting since the colors can stack
                

                if self.markLong.get() == 1:
                    r = fitz.Rect(wlist[w+i][:4])     
                    r.x0 = 0
                    r.x1 = page.rect.x1
                    if r.y0 > 6:
                        r.y0 -= 6
                    if r.y1 < page.rect.y1 - 6:
                        r.y1 += 6

                    highlight = page.add_highlight_annot(r)
                    highlight.set_colors({"stroke":stroke_color})
                    highlight.update()
                else:
                    for i in range(num_of_words):
                        r = fitz.Rect(wlist[w+i][:4])  
                        highlight = page.add_highlight_annot(r)
                        highlight.set_colors({"stroke":stroke_color})
                        highlight.update()
                    
                

    def apply_highlight(self):
        # Write code to apply the highlight to the selected text in the PDF
        self.no_highlights = False

        for page in self.current_pdf:
            for word in self.modifiers_text_listbox.get(0, tk.END):
                if " " in word:
                    self.mark_spaced_word(page, word)
                else:
                    self.mark_word(page, word)
        self.update_preview()

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