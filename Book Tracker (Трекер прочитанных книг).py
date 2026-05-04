import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker — Трекер прочитанных книг")
        self.root.geometry("800x600")
        
        self.books = []
        self.load_books()
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для формы добавления книги
        form_frame = ttk.LabelFrame(self.root, text="Добавить книгу", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поля ввода
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, pady=2, padx=(0, 10))

        ttk.Label(form_frame, text="Автор:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.author_entry = ttk.Entry(form_frame, width=30)
        self.author_entry.grid(row=1, column=1, pady=2, padx=(0, 10))

        ttk.Label(form_frame, text="Жанр:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.genre_entry = ttk.Entry(form_frame, width=30)
        self.genre_entry.grid(row=2, column=1, pady=2, padx=(0, 10))

        ttk.Label(form_frame, text="Страниц:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.pages_entry = ttk.Entry(form_frame, width=30)
        self.pages_entry.grid(row=3, column=1, pady=2, padx=(0, 10))

        # Кнопка добавления
        ttk.Button(form_frame, text="Добавить книгу", command=self.add_book).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky=tk.W)
        self.genre_filter = ttk.Combobox(filter_frame, state="readonly")
        self.genre_filter.grid(row=0, column=1, padx=(10, 0))
        self.genre_filter.bind("<<ComboboxSelected>>", self.apply_filters)

        ttk.Label(filter_frame, text="Страниц >").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.pages_filter = ttk.Entry(filter_frame, width=10)
        self.pages_filter.grid(row=0, column=3, padx=(5, 0))
        self.pages_filter.bind("<KeyRelease>", self.apply_filters)

        # Таблица книг
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")

        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=120)
        self.tree.column("pages", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Обновить жанры", command=self.update_genres).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Очистить фильтры", command=self.clear_filters).pack(side=tk.LEFT, padx=(10, 0))

        self.refresh_display()

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_text = self.pages_entry.get().strip()

        if not all([title, author, genre, pages_text]):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            pages = int(pages_text)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }

        self.books.append(book)
        self.save_books()
        self.refresh_display()
        self.clear_form()
        messagebox.showinfo("Успех", "Книга успешно добавлена!")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def refresh_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in self.books:
            self.tree.insert("", tk.END, values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))
        self.update_genres()

    def update_genres(self):
        genres = list(set(book["genre"] for book in self.books))
        self.genre_filter["values"] = [""] + genres
        self.genre_filter.set("")

    def apply_filters(self, event=None):
        filtered_books = self.books

        selected_genre = self.genre_filter.get()
        if selected_genre:
            filtered_books = [book for book in filtered_books if book["genre"] == selected_genre]

        pages_filter_text = self.pages_filter.get().strip()
        if pages_filter_text:
            try:
                min_pages = int(pages_filter_text)
                filtered_books = [book for book in filtered_books if book["pages"] >= min_pages]
            except ValueError:
                pass

        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in filtered_books:
            self.tree.insert("", tk.END, values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))
    def clear_filters(self):
        self.genre_