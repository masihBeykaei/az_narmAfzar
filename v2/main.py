import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class ChecklistApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List v2 - With Timestamp")
        self.geometry("450x500")
        self.configure(bg="#ffffff")

        self.tasks = {}

        # --- Top input bar ---
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        self.entry_task = ttk.Entry(top)
        self.entry_task.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(top, text="Add Task", command=self.add_task).pack(side="left")

        # --- Task list area ---
        self.tasks_frame = ttk.Frame(self, padding=10)
        self.tasks_frame.pack(fill="both", expand=True)

        # --- Bottom buttons ---
        bottom = tk.Frame(self, bg="#ffffff")
        bottom.pack(fill="x", pady=5)
        self.btn_done = tk.Button(bottom, text="Mark Done", command=self.mark_done, bg="#2196F3", fg="white", width=10)
        self.btn_done.pack(side="left", padx=10)
        self.btn_delete = tk.Button(bottom, text="Delete Task", command=self.delete_selected, bg="#f44336", fg="white", width=10)
        self.btn_delete.pack(side="left", padx=10)
        self.btn_clear = tk.Button(bottom, text="Clear All", command=self.clear_all, bg="#9C27B0", fg="white", width=10)
        self.btn_clear.pack(side="right", padx=10)

    def add_task(self):
        task_text = self.entry_task.get().strip()
        if not task_text:
            messagebox.showwarning("Warning", "Please enter a task!")
            return

        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M]")
        display_text = f"{task_text} - {timestamp}"
        self.entry_task.delete(0, tk.END)

        row = ttk.Frame(self.tasks_frame)
        row.pack(fill="x", pady=2)

        var = tk.BooleanVar()
        chk = ttk.Checkbutton(row, variable=var)
        chk.pack(side="left")

        lbl = ttk.Label(row, text=display_text)
        lbl.pack(side="left", padx=5)

        self.tasks[row] = {"text": display_text, "done": False, "var": var, "label": lbl}

    def mark_done(self):
        for r, info in self.tasks.items():
            if info["var"].get():
                info["done"] = True
                info["label"].config(text="✓ " + info["text"])
                info["var"].set(False)

    def delete_selected(self):
        for r in list(self.tasks):
            if self.tasks[r]["var"].get():
                self._remove_task(r)

    def _remove_task(self, row):
        row.destroy()
        del self.tasks[row]

    def clear_all(self):
        if not self.tasks:
            messagebox.showinfo("Empty", "No tasks to clear.")
            return
        if not messagebox.askyesno("Clear All", "Are you sure you want to delete all tasks?"):
            return
        for r in list(self.tasks):
            self._remove_task(r)

if __name__ == "__main__":
    app = ChecklistApp()
    app.mainloop()
