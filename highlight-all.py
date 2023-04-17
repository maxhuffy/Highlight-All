import tkinter as tk
from tkinter import filedialog, colorchooser

import os

from PIL import Image, ImageTk
import fitz  # PyMuPDF

# Handles paths for images added to binary .exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PDFBulkHighlighter:
    def __init__(self):
        self.current_pdf = None
        self.current_page = 0

        self.colors_backup = [(255.0, 255.0, 119.0), "#FFFF77"]
        self.colors = [(255.0, 255.0, 119.0), "#FFFF77"]
        self.page_count = 0
        self.no_highlights = True

        self.selected_pdf = None

        self.long_mark_width_num = 4

        self.root = tk.Tk()
        self.root.iconbitmap(resource_path("icon.ico"))
        self.root.title("PDF Bulk Highlighter")
        self._build_gui()
        self.disable_buttons()
        self.root.resizable(0, 0)
        self.root.mainloop()

    def _build_gui(self):
        # Select PDFs
        self.select_button = tk.Button(self.root, text="Select PDFs", command=self.select_pdfs, width=13)
        self.select_button.grid(row=0, column=1, pady=5, sticky="w")

        self.clear_button = tk.Button(self.root, text="Clear PDFs", command=self.clear_pdfs, width=13)
        self.clear_button.grid(row=0, column=2, pady=0, sticky="w")

        self.pdf_listbox = tk.Listbox(self.root, width=75)
        self.pdf_listbox.grid(row=1, column=1, pady=5, columnspan=12, sticky="w", rowspan=5)
        self.pdf_listbox.bind("<<ListboxSelect>>", self.on_pdf_selected)

        spacer = tk.Frame(self.root, width=10, height=30)
        spacer.grid(row=2+5, column=1)

        # Text Finder
        self.add_text_button = tk.Button(self.root, text="Add Text", command=self.add_text, width=13)
        self.add_text_button.grid(row=3+5, column=1, pady=5, sticky="w")

        self.remove_text_button = tk.Button(self.root, text="Remove Text", command=self.remove_text, width=13)
        self.remove_text_button.grid(row=3+5, column=2, pady=5, sticky="w")

        find_label = tk.Label(self.root, text="Find:")
        find_label.grid(row=4+5, column=0, padx=5, sticky="e")

        self.text_entry = tk.Entry(self.root, width=37)
        self.text_entry.grid(row=4+5, column=1, sticky="w", columnspan=3)
        self.text_entry.bind("<Return>", self.add_text)

        self.text_listbox = tk.Listbox(self.root, width=37, selectmode=tk.EXTENDED)
        self.text_listbox.grid(row=5+5, column=1, pady=5, sticky="w", columnspan=3, rowspan=6)

        # Highlight Buttons
        self.color_picker_button = tk.Button(self.root, text="Color Picker", command=self.change_color, width=13)
        self.color_picker_button.grid(row=5+5, column=4, padx=10, sticky="w")
        self.selected_color_display = tk.Frame(self.root, bg=self.colors[1], width=75, height=25)
        self.selected_color_display.grid(row=5+5, column=5, padx=25)

        self.apply_highlight_button = tk.Button(self.root, text="Apply Highlight", command=self.apply_highlight, width=13)
        self.apply_highlight_button.grid(row=6+5, column=4, padx=10, sticky="w")

        self.reset_highlights_button = tk.Button(self.root, text="Reset Highlights", command=self.reset_pdf, width=13)
        self.reset_highlights_button.grid(row=6+5+1, column=4, padx=10, sticky="w")

        self.save_file_button = tk.Button(self.root, text="Save File", command=self.save_file, width=13)
        self.save_file_button.grid(row=13+18, column=1, sticky="w")
        

        long_mark_width_frame = tk.Frame(self.root)
        long_mark_width_frame.grid(row=11, column=5)
        
        self.markLong = tk.IntVar()
        self.highlight_whole_line_checkbox = tk.Checkbutton(long_mark_width_frame, text="Highlight entire line?", variable=self.markLong)
        self.highlight_whole_line_checkbox.pack(side=tk.TOP)
        self.highlight_whole_line_checkbox.bind("<Button>", lambda event: self.disable_long_mark_width())


        long_mark_label = tk.Label(long_mark_width_frame, text="Vertical Width:")
        long_mark_label.pack(side=tk.LEFT)
        self.long_mark_width = tk.IntVar(value=4)
        self.long_mark_width_entry = tk.Entry(long_mark_width_frame, textvariable=self.long_mark_width, width=6)
        self.long_mark_width_entry.pack(side=tk.LEFT)
        self.long_mark_width_entry.bind("<Key>", lambda event: self.update_long_mark_width())
     
        # Preview
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
    
    def disable_buttons(self):
        """Disable buttons when no PDF is selected."""
        self.clear_button.config(state=tk.DISABLED)
        self.add_text_button.config(state=tk.DISABLED)
        self.remove_text_button.config(state=tk.DISABLED)
        self.color_picker_button.config(state=tk.DISABLED)
        self.apply_highlight_button.config(state=tk.DISABLED)
        self.reset_highlights_button.config(state=tk.DISABLED)
        self.save_file_button.config(state=tk.DISABLED)
        self.highlight_whole_line_checkbox.config(state=tk.DISABLED)
        self.long_mark_width_entry.config(state=tk.DISABLED)

    def enable_buttons(self):
        """Enable buttons when a PDF is selected."""
        self.clear_button.config(state=tk.NORMAL)
        self.add_text_button.config(state=tk.NORMAL)
        self.remove_text_button.config(state=tk.NORMAL)
        self.color_picker_button.config(state=tk.NORMAL)
        self.apply_highlight_button.config(state=tk.NORMAL)
        self.reset_highlights_button.config(state=tk.NORMAL)
        self.save_file_button.config(state=tk.NORMAL)
        self.highlight_whole_line_checkbox.config(state=tk.NORMAL)

    # PDF handling methods
    def select_pdfs(self):
        """Open file dialog, add selected PDFs to pdf_listbox."""
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for file_path in file_paths:
            self.pdf_listbox.insert(tk.END, file_path)
        if len(file_paths) == 1:
            self.pdf_listbox.selection_set(0)
            self.on_pdf_selected()
        if len(file_paths) > 0:
            self.enable_buttons()

    def clear_pdfs(self):
        """Remove PDFs from pdf_listbox, reset attributes, clear preview."""
        self.pdf_listbox.delete(0, tk.END)
        self.current_pdf = None
        self.page_count = 0
        self.update_preview()
        self.disable_buttons()

    def reset_pdf(self):
        """Reload current PDF, discard unsaved highlights."""
        self.current_pdf = fitz.open(self.selected_pdf)
        self.update_preview()

    def on_pdf_selected(self, event=None):
        """Load selected PDF, update attributes and preview."""
        # Catch errors
        if not self.pdf_listbox.curselection():
            return
            
        self.no_highlights = True
        self.selected_pdf = self.pdf_listbox.get(self.pdf_listbox.curselection())
        # Stores the doc as a internal variable
        self.current_pdf = fitz.open(self.selected_pdf)
        self.page_count = len(self.current_pdf)
        self.current_page = 0
        self.update_preview()

    def save_file(self):
        """Save highlighted PDF, open file dialog for location."""
        init_f = os.path.splitext(os.path.basename(self.selected_pdf))[0]
        save_path = filedialog.asksaveasfilename(initialfile=f"{init_f}_HIGHLIGHTED", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if save_path:
            self.current_pdf.save(save_path)

    # Text handling methods
    def add_text(self, event=None):
        """Add entered text to text_listbox."""
        text = self.text_entry.get()

        # If we paste in a large number of terms
        if "\n" in text:
            text = text.split("\n")
            for t in text:
                if t:
                    self.text_listbox.insert(tk.END, t)
                    self.text_entry.delete(0, tk.END)
            return

        if text:
            self.text_listbox.insert(tk.END, text)
            self.text_entry.delete(0, tk.END)

    def remove_text(self):
        """Remove selected text entries from text_listbox."""
        selected_indices = self.text_listbox.curselection()
        for index in reversed(selected_indices):
            self.text_listbox.delete(index)

    # Color handling methods
    def change_color(self):
        """Open color picker, update selected_color_display."""
        self.colors = colorchooser.askcolor(title="Highlighter Color", color=self.colors[1])
        if self.colors[0]:
            self.selected_color_display.config(bg=self.colors[1])
            self.colors_backup = self.colors
        else:
            self.colors = self.colors_backup

    # Highlight handling methods
    def mark_word(self, page, text):
        """Highlight word/line on PDF page with selected color."""
        stroke_color = tuple([i/255.0 for i in self.colors[0]])
        text = text.lower()
        
        word_list = page.get_text("words")  # make the word list
        for w in word_list:  # scan through all words on page
            if text == w[4].lower():  # w[4] is the word's string 
                highlight_rect = fitz.Rect(w[:4])  # make rect from word bbox

                if self.markLong.get() == 1:    
                    highlight_rect.x0 = 0
                    highlight_rect.x1 = page.rect.x1

                    if highlight_rect.y0 > self.long_mark_width_num:
                        highlight_rect.y0 -= self.long_mark_width_num
                    if highlight_rect.y1 < page.rect.y1 - self.long_mark_width_num:
                        highlight_rect.y1 += self.long_mark_width_num

                highlight = page.add_highlight_annot(highlight_rect)
                highlight.set_colors({"stroke":stroke_color})
                highlight.update()
    
    def mark_spaced_word(self, page, text):
        """Highlight spaced words/lines on PDF page with color."""
        stroke_color = tuple([i/255.0 for i in self.colors[0]])

        num_of_words = len(text.split())
        text_list = text.split()

        while text_list[-1] == " ":
            print(text_list.pop[-1])
        
        word_list = page.get_text("words")
        for w in range(len(word_list) - num_of_words + 1):
            space_count = 0  
            for i in range(num_of_words):
                if text_list[i].lower() == word_list[w+i][4].lower():
                    space_count += 1

            
            if space_count == num_of_words:
                # Avoid double highlighting since the colors can stack
                if self.markLong.get() == 1:
                    highlight_rect = fitz.Rect(word_list[w+i][:4])     
                    highlight_rect.x0 = 0
                    highlight_rect.x1 = page.rect.x1
                    if highlight_rect.y0 > self.long_mark_width_num:
                        highlight_rect.y0 -= self.long_mark_width_num
                    if highlight_rect.y1 < page.rect.y1 - self.long_mark_width_num:
                        highlight_rect.y1 += self.long_mark_width_num

                    highlight = page.add_highlight_annot(highlight_rect)
                    highlight.set_colors({"stroke":stroke_color})
                    highlight.update()
                else:
                    for i in range(num_of_words):
                        highlight_rect = fitz.Rect(word_list[w+i][:4])  
                        highlight = page.add_highlight_annot(highlight_rect)
                        highlight.set_colors({"stroke":stroke_color})
                        highlight.update()
                    
    def update_long_mark_width(self, event=None):
        try:
            self.long_mark_width_num = float(self.long_mark_width_entry.get())
        except:
            self.long_mark_width.set(4)
            self.long_mark_width_num = float(self.long_mark_width_entry.get())
            

    def disable_long_mark_width(self, event=None):
        if self.markLong.get() == 1:
            self.long_mark_width_entry.config(state=tk.DISABLED)
        else:
            self.long_mark_width_entry.config(state=tk.NORMAL)
    
    def apply_highlight(self):
        """Apply highlights to PDF, update preview."""
        self.no_highlights = False
        self.update_long_mark_width()

        for page in self.current_pdf:
            for word in self.text_listbox.get(0, tk.END):
                if " " in word:
                    self.mark_spaced_word(page, word)
                else:
                    self.mark_word(page, word)
        self.update_preview()

    # Preview handling methods
    def update_preview(self):
        """Update PDF preview, display highlights and page number."""
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
        """Change current page by delta, update preview."""
        if self.current_pdf:
            new_page = self.current_page + delta
            if 0 <= new_page < self.page_count:
                self.current_page = new_page
                self.update_preview()

    def go_to_page(self):
        """Go to specified page, update preview."""
        page_num = self.page_number_var.get()
        try:
            page_num = int(page_num) - 1
            if 0 <= page_num < self.page_count:
                self.current_page = page_num
                self.update_preview()
        except ValueError:
            pass


foo = PDFBulkHighlighter()