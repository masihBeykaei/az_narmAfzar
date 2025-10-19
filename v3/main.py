import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class ChecklistApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List v4 - Categories")
        self.geometry("500x520")
        self.configure(bg="#ffffff")

        self.tasks = {}
        self.categories = ["Home", "Study", "Shopping", "Work", "General"]

        # --- Top bar: input + category + add ---
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        self.entry_task = ttk.Entry(top)
        self.entry_task.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.category_var = tk.StringVar(value=self.categories[0])
        self.cmb_cat = ttk.Combobox(
            top, textvariable=self.category_var, values=self.categories, width=10, state="readonly"
        )
        self.cmb_cat.pack(side="left", padx=(0, 8))

        ttk.Button(top, text="Add Task", command=self.add_task).pack(side="left")

        # divider line
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=(4, 0))

        # --- Task list area ---
        self.tasks_frame = ttk.Frame(self, padding=10)
        self.tasks_frame.pack(fill="both", expand=True)

        # --- Bottom buttons ---
        bottom = tk.Frame(self, bg="#ffffff")
        bottom.pack(fill="x", pady=6)
        tk.Button(bottom, text="Delete Task", command=self.delete_selected,
                  bg="#f44336", fg="white", width=12).pack(side="left", padx=8)
        tk.Button(bottom, text="Mark Done", command=self.mark_done,
                  bg="#2196F3", fg="white", width=12).pack(side="left", padx=8)
        tk.Button(bottom, text="Clear All", command=self.clear_all,
                  bg="#7B1FA2", fg="white", width=12).pack(side="right", padx=8)

    def add_task(self):
        text = self.entry_task.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter a task!")
            return

        cat = self.category_var.get()
        ts = datetime.datetime.now().strftime("(%Y-%m-%d %H:%M)")
        display_text = f"[{cat}] {text}  {ts}"

        self.entry_task.delete(0, tk.END)

        row = ttk.Frame(self.tasks_frame)
        row.pack(fill="x", pady=2)

        var = tk.BooleanVar()
        chk = ttk.Checkbutton(row, variable=var)
        chk.pack(side="left")

        lbl = ttk.Label(row, text=display_text)
        lbl.pack(side="left", padx=5)

        # allow clicking row/label to toggle the checkbox
        def toggle_var(_e):
            var.set(not var.get())
        row.bind("<Button-1>", toggle_var)
        lbl.bind("<Button-1>", toggle_var)

        self.tasks[row] = {"cat": cat, "text": text, "stamp": ts,
                           "display": display_text, "done": False,
                           "var": var, "label": lbl}

    def mark_done(self):
        # visually mark done: add check mark and gray/italic
        for r, info in self.tasks.items():
            if info["var"].get():
                info["done"] = True
                info["var"].set(False)
                info["label"].config(text="✓ " + info["display"])
                # apply faint style
                current_font = tk.font.Font(font=info["label"]["font"])
                over = current_font.actual()
                info["label"].config(foreground="#555555",
                                     font=(over["family"], over["size"], "italic"))

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
        if not messagebox.askyesno("Clear All", "Delete all tasks?"):
            return
        for r in list(self.tasks):
            self._remove_task(r)

if __name__ == "__main__":
    # Tk needs this import only when using tk.font in mark_done
    import tkinter.font as tkfont  # noqa: F401 (ensures tk.font is available)
    app = ChecklistApp()
    app.mainloop()
