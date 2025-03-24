# -*- coding: utf-8 -*-
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import shutil
import os
from datetime import datetime

# Константы
BG_COLOR = "#e0e0e0"
BUTTON_COLOR = "#4CAF50"
BROWSE_COLOR = "#2196F3"
CHECKBOX_BG = "#f0f0f0"
WINDOW_SIZE = "800x500"
MAIN_SIZE = "450x250"
ACTION_SIZE = "400x200"


class FileSearcher:
    """Класс для поиска файлов и сбора статистики."""

    @staticmethod
    def search_files(source_dir, attributes):
        start_time = time.time()
        source_path = Path(source_dir)
        found_files, file_stats, all_files = {}, {}, []

        for attr in attributes:
            for file_path in source_path.rglob(f'*.{attr}'):
                parent = file_path.parent
                found_files.setdefault(parent, []).append(file_path.name)
                file_stats.setdefault(parent, [0, 0])[0] += 1
                file_stats[parent][1] += file_path.stat().st_size
                all_files.append(file_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = source_path / f"log_search_{timestamp}.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("Протокол найденных файлов:\n")
            f.writelines(f"{file.name} - {file}\n" for file in all_files)

        total_files = sum(stats[0] for stats in file_stats.values())
        total_size = sum(stats[1] for stats in file_stats.values())
        search_time = time.time() - start_time
        return found_files, file_stats, total_files, total_size, search_time, source_path


class Tooltip:
    """Класс для всплывающих подсказок."""

    def __init__(self, widget, text):
        self.widget, self.text, self.tooltip = widget, text, None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event):
        x, y = self.widget.winfo_pointerxy()
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x + 10}+{y + 10}")
        tk.Label(self.tooltip, text=self.text, bg="#ffffe0", relief="solid", borderwidth=1).pack()

    def hide(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class ActionWindow:
    """Класс для окна действий с файлами."""

    def __init__(self, parent, selected_folders, found_files, source_root):
        self.window = tk.Toplevel(parent)
        self.window.title("Действия с файлами")
        self.window.geometry(ACTION_SIZE)
        self.window.configure(bg=BG_COLOR)
        self.selected_folders = selected_folders
        self.found_files = found_files
        self.source_root = source_root
        self.action_var = tk.StringVar(value="copy")  # Инициализация
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.window, text="Папка-приёмник:", bg=BG_COLOR).pack(pady=5)
        path_frame = tk.Frame(self.window, bg=BG_COLOR)
        path_frame.pack(pady=5)
        self.dest_entry = tk.Entry(path_frame, width=40)
        self.dest_entry.pack(side='left')
        tk.Button(path_frame, text="Обзор", command=self.browse, bg=BROWSE_COLOR, fg="white").pack(side='left', padx=5)

        tk.Label(self.window, text="Действие:", bg=BG_COLOR).pack(pady=5)
        self.copy_radio = tk.Radiobutton(self.window, text="Копировать", variable=self.action_var, value="copy",
                                         bg=BG_COLOR, command=lambda: self.action_var.set("copy"))
        self.copy_radio.pack(anchor='w', padx=10)
        self.move_radio = tk.Radiobutton(self.window, text="Перенести", variable=self.action_var, value="move",
                                         bg=BG_COLOR, command=lambda: self.action_var.set("move"))
        self.move_radio.pack(anchor='w', padx=10)

        # Устанавливаем начальное значение
        self.action_var.set("copy")
        self.copy_radio.select()
        print(f"Initial action: {self.action_var.get()}")

        tk.Button(self.window, text="Выполнить", command=self.execute, bg=BUTTON_COLOR, fg="white").pack(pady=10)
        self.window.grab_set()

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)
            self.window.after(100, lambda: self.window.focus_force())

    def execute(self):
        dest_dir = self.dest_entry.get().strip()
        if not dest_dir:
            messagebox.showerror("Ошибка", "Укажите папку-приёмник!")
            return
        if not Path(dest_dir).exists():
            messagebox.showerror("Ошибка", "Папка-приёмник не существует!")
            return

        dest_root = Path(dest_dir)
        action = self.action_var.get()
        print(f"Executing action: {action}")  # Отладочный вывод перед выполнением
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = dest_root / f"log_{action}_{timestamp}.txt"

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Протокол {'копирования' if action == 'copy' else 'переноса'} файлов:\n")
            for folder in self.selected_folders:
                if folder == self.source_root:
                    dest_folder = dest_root / self.source_root.name
                else:
                    relative_path = folder.relative_to(self.source_root)
                    dest_folder = dest_root / self.source_root.name / relative_path
                dest_folder.mkdir(parents=True, exist_ok=True)

                for file_name in self.found_files[folder]:
                    src_path = folder / file_name
                    dest_path = dest_folder / file_name
                    try:
                        if action == "copy":
                            shutil.copy2(src_path, dest_path)
                            f.write(f"Скопировано: {src_path} -> {dest_path}\n")
                        elif action == "move":
                            shutil.move(src_path, dest_path)
                            if src_path.exists():
                                os.remove(src_path)
                                f.write(f"Удалён исходный файл: {src_path}\n")
                            f.write(f"Перенесено: {src_path} -> {dest_path}\n")
                        else:
                            f.write(f"Неизвестное действие: {action}\n")
                    except Exception as e:
                        f.write(f"Ошибка при обработке {src_path}: {e}\n")
                        if action == "move" and src_path.exists():
                            try:
                                os.remove(src_path)
                                f.write(f"Исходный файл удалён после ошибки: {src_path}\n")
                            except Exception as del_e:
                                f.write(f"Не удалось удалить исходный файл {src_path}: {del_e}\n")
        messagebox.showinfo("Успех", f"Действие выполнено. Лог сохранён в {log_file}")
        self.window.destroy()


class ResultsWindow:
    """Класс для окна результатов поиска."""

    def __init__(self, found_files, file_stats, total_files, total_size, search_time, source_root, main_root):
        self.root = tk.Tk()
        self.root.title("Структура папок с найденными файлами")
        self.root.geometry(WINDOW_SIZE)
        self.found_files = found_files
        self.file_stats = file_stats
        self.total_files = total_files
        self.total_size = total_size
        self.search_time = search_time
        self.source_root = source_root
        self.main_root = main_root  # Ссылка на главное окно
        self.checkbox_widgets = {}
        self.action_window = None  # Ссылка на окно "Действия с файлами"
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def setup_ui(self):
        info = f"Всего найдено: {self.total_files} файлов, {self.format_size(self.total_size)} | Время поиска: {self.search_time:.2f} сек"
        tk.Label(self.root, text=info, bg=BG_COLOR, font=("Arial", 10, "bold")).pack(pady=5)

        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill='both', expand=True)

        checkbox_frame = tk.Frame(paned, bg=CHECKBOX_BG)
        self.checkbox_canvas = tk.Canvas(checkbox_frame, bg=CHECKBOX_BG)
        scrollbar = ttk.Scrollbar(checkbox_frame, orient="vertical", command=self.checkbox_canvas.yview)
        self.checkbox_inner = tk.Frame(self.checkbox_canvas, bg=CHECKBOX_BG)
        self.checkbox_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.checkbox_canvas.pack(side='left', fill='both', expand=True)
        self.checkbox_canvas.create_window((0, 0), window=self.checkbox_inner, anchor='nw')

        tk.Label(self.checkbox_inner, text="Выбрать папки:", bg=CHECKBOX_BG, font=("Arial", 10, "bold")).pack(
            anchor='n')
        self.add_select_all()
        self.add_checkboxes()

        tree_frame = tk.Frame(paned)
        self.tree = ttk.Treeview(tree_frame)
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        self.populate_tree()

        self.checkbox_inner.bind("<Configure>", lambda e: self.checkbox_canvas.configure(
            scrollregion=self.checkbox_canvas.bbox("all")))
        self.tree.bind("<Configure>", lambda e: self.tree.update_idletasks())

        paned.add(checkbox_frame, weight=1)
        paned.add(tree_frame, weight=1)

        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(side='bottom', fill='x', pady=5)
        tk.Button(btn_frame, text="Действия с файлами", command=self.open_action_window, bg=BUTTON_COLOR,
                  fg="white").pack(side='left', padx=5)
        tk.Button(btn_frame, text="Настройки поиска", command=self.show_main_window, bg=BROWSE_COLOR, fg="white").pack(
            side='left', padx=5)

    def show_main_window(self):
        self.main_root.deiconify()  # Показываем главное окно

    def add_select_all(self):
        self.select_all_chk = ttk.Checkbutton(self.checkbox_inner, text="Выбрать все", command=self.toggle_all)
        self.select_all_chk.state(['!alternate'])
        self.select_all_chk.pack(anchor='w', pady=2)

    def toggle_all(self):
        state = 'selected' if self.select_all_chk.instate(['selected']) else '!selected'
        for folder, widget in self.checkbox_widgets.items():
            widget.state([state])
        self.root.update_idletasks()

    def add_checkboxes(self):
        for folder in self.found_files.keys():
            frame = tk.Frame(self.checkbox_inner, bg=CHECKBOX_BG)
            frame.pack(anchor='w', fill='x')
            chk = ttk.Checkbutton(frame, text=folder.name)
            chk.state(['!alternate'])
            chk.pack(side='left')
            self.checkbox_widgets[folder] = chk
            stats = self.file_stats[folder]
            tk.Label(frame, text=f"({stats[0]} файлов, {self.format_size(stats[1])})", bg=CHECKBOX_BG,
                     font=("Arial", 8)).pack(side='left', padx=5)
            Tooltip(chk, str(folder))

    def open_action_window(self):
        self.root.update()

        def check_and_open():
            selected = [folder for folder, widget in self.checkbox_widgets.items() if widget.instate(['selected'])]
            if not selected:
                messagebox.showerror("Ошибка", "Выберите хотя бы одну папку!")
                return
            if self.action_window and self.action_window.window.winfo_exists():
                self.action_window.window.lift()  # Поднимаем окно на передний план
                self.action_window.window.focus_force()  # Делаем его активным
            else:
                self.action_window = ActionWindow(self.root, selected, self.found_files, self.source_root)
                self.action_window.window.protocol("WM_DELETE_WINDOW", self.on_action_window_close)

        self.root.after(100, check_and_open)

    def on_action_window_close(self):
        """Обработчик закрытия окна 'Действия с файлами'."""
        if self.action_window and self.action_window.window.winfo_exists():
            self.action_window.window.destroy()
        self.action_window = None

    def on_closing(self):
        """Обработчик закрытия окна 'Структура папок'."""
        if self.action_window and self.action_window.window.winfo_exists():
            self.action_window.window.destroy()
        self.root.destroy()
        self.main_root.deiconify()  # Показываем главное окно
        self.main_root.focus_force()  # Делаем его активным

    def populate_tree(self):
        root_node = self.tree.insert("", "end", text="Найденные файлы", open=True)
        for folder, files in self.found_files.items():
            folder_node = self.tree.insert(root_node, "end", text=folder.name, open=True)
            for file in files:
                self.tree.insert(folder_node, "end", text=file)

    def run(self):
        self.root.mainloop()


class ExtensionsWindow:
    """Класс для окна выбора расширений."""

    def __init__(self, parent, callback):
        self.window = tk.Toplevel(parent)
        self.window.title("Выбор расширений")
        self.window.geometry("400x350")
        self.window.configure(bg=CHECKBOX_BG)
        self.callback = callback
        self.extension_sets = {
            "Видео/Аудио": ['mp4', 'avi', 'mkv', 'mp3', 'wav', 'flac'],
            "Электронные книги": ['epub', 'mobi', 'pdf', 'djvu', 'fb2'],
            "Изображения": ['jpg', 'png', 'gif', 'bmp', 'tiff']
        }
        self.vars = {}
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.window, text="Выберите набор расширений:", bg=CHECKBOX_BG).pack(pady=5)
        self.vars = {name: tk.BooleanVar() for name in self.extension_sets}
        for name, exts in self.extension_sets.items():
            chk = tk.Checkbutton(self.window, text=f"{name} ({', '.join(exts)})", variable=self.vars[name],
                                 command=self.update_entry, bg=CHECKBOX_BG)
            chk.pack(anchor='w', padx=10)

        tk.Label(self.window, text="Выбранные расширения (редактируйте, если нужно):", bg=CHECKBOX_BG).pack(pady=10)
        self.ext_entry = tk.Entry(self.window, width=40)
        self.ext_entry.pack(pady=5)

        tk.Button(self.window, text="Сохранить", command=self.save, bg=BUTTON_COLOR, fg="white").pack(pady=10)
        self.window.grab_set()

    def update_entry(self):
        """Обновляет строку ввода на основе выбранных флажков."""
        selected_exts = []
        for name, var in self.vars.items():
            if var.get():
                selected_exts.extend(self.extension_sets[name])
        self.ext_entry.delete(0, tk.END)
        self.ext_entry.insert(0, ', '.join(selected_exts))

    def save(self):
        """Сохраняет только то, что в строке ввода."""
        extensions = [ext.strip() for ext in self.ext_entry.get().split(',') if ext.strip()]
        for ext in extensions:
            if not ext.isalnum():
                messagebox.showerror("Ошибка", f"Некорректное расширение: {ext}")
                return
        if not extensions:
            messagebox.showerror("Ошибка", "Укажите хотя бы одно расширение!")
            return
        self.callback(extensions)
        self.window.destroy()


class MainWindow:
    """Класс для главного окна."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Настройки поиска файлов")
        self.root.geometry(MAIN_SIZE)
        self.root.configure(bg=BG_COLOR)
        self.selected_extensions = []
        self.extensions_window = None  # Ссылка на окно "Выбор расширений"
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        tk.Label(self.root, text="Путь к папке поиска:", bg=BG_COLOR, font=("Arial", 10)).pack(pady=5)
        path_frame = tk.Frame(self.root, bg=BG_COLOR)
        path_frame.pack(pady=5)

        self.path_entry = tk.Entry(path_frame, width=40)
        self.path_entry.pack(side='left')
        self.path_entry.insert(0, "C:/Users/User/javarush/3365410/javarush-project/EDF")
        tk.Button(path_frame, text="Обзор", command=self.browse, bg=BROWSE_COLOR, fg="white").pack(side='left', padx=5)

        tk.Button(self.root, text="Выбрать расширения", command=self.open_extensions, bg=BROWSE_COLOR, fg="white").pack(
            pady=10)
        self.ext_label = tk.Label(self.root, text="Выбраны расширения: (пока не выбраны)", bg=BG_COLOR)
        self.ext_label.pack(pady=5)

        tk.Button(self.root, text="Начать поиск", command=self.start_search, bg=BUTTON_COLOR, fg="white").pack(pady=20)

    def browse(self):
        folder = filedialog.askdirectory(initialdir=self.path_entry.get())
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def open_extensions(self):
        if self.extensions_window and self.extensions_window.window.winfo_exists():
            self.extensions_window.window.lift()  # Поднимаем окно на передний план
            self.extensions_window.window.focus_force()  # Делаем его активным
        else:
            self.extensions_window = ExtensionsWindow(self.root, self.set_extensions)
            self.extensions_window.window.protocol("WM_DELETE_WINDOW", self.on_extensions_window_close)

    def on_extensions_window_close(self):
        """Обработчик закрытия окна 'Выбор расширений'."""
        if self.extensions_window and self.extensions_window.window.winfo_exists():
            self.extensions_window.window.destroy()
        self.extensions_window = None

    def set_extensions(self, exts):
        self.selected_extensions = exts
        self.ext_label.config(text=f"Выбраны расширения: {', '.join(exts)}")

    def start_search(self):
        source_dir = self.path_entry.get().strip()
        if not source_dir or not Path(source_dir).exists() or not self.selected_extensions:
            messagebox.showerror("Ошибка", "Укажите существующую папку и выберите расширения!")
            return

        results = FileSearcher.search_files(source_dir, self.selected_extensions)
        if results[0]:
            self.root.withdraw()  # Скрываем главное окно
            ResultsWindow(*results, self.root).run()  # Передаём ссылку на главное окно
        else:
            messagebox.showinfo("Результат", "Файлы с заданными атрибутами не найдены.")

    def on_closing(self):
        """Обработчик закрытия главного окна."""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите закрыть программу?"):
            self.root.quit()  # Завершаем весь цикл Tkinter, закрывая все окна
            self.root.destroy()  # Уничтожаем корневое окно

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    MainWindow().run()