import tkinter as tk
from tkinter import ttk, messagebox

class ChecklistApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Checklist")
        self.geometry("450x500")
        self.configure(bg="#f2f2f2")

        self.tasks = {}

        
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        self.entry_task = ttk.Entry(top)
        self.entry_task.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(top, text="Add", command=self.add_task).pack(side="left")

      
        self.tasks_frame = ttk.Frame(self, padding=10)
        self.tasks_frame.pack(fill="both", expand=True)


        bottom = tk.Frame(self, bg="#f2f2f2")
        bottom.pack(fill="x", pady=5)
        self.btn_done = tk.Button(bottom, text="✓ Done", command=self.mark_done, bg="#4CAF50", fg="white", width=10)
        self.btn_done.pack(side="left", padx=10)
        self.btn_delete = tk.Button(bottom, text="🗑 Delete", command=self.delete_selected, bg="#f44336", fg="white", width=10)
        self.btn_delete.pack(side="left", padx=10)
        self.btn_clear = tk.Button(bottom, text="🧹 Clear All", command=self.clear_all, bg="#607D8B", fg="white", width=10)
        self.btn_clear.pack(side="right", padx=10)

    def add_task(self):
        task_text = self.entry_task.get().strip()
        if not task_text:
            messagebox.showwarning("Warning", "Please enter a task!")
            return
        self.entry_task.delete(0, tk.END)

        row = ttk.Frame(self.tasks_frame)
        row.pack(fill="x", pady=2)

        var = tk.BooleanVar()
        chk = ttk.Checkbutton(row, variable=var)
        chk.pack(side="left")

        lbl = ttk.Label(row, text=task_text)
        lbl.pack(side="left", padx=5)

        tick_label = ttk.Label(row, text="", foreground="green")
        tick_label.pack(side="right")

        def toggle_var(event):
            if not tick_label.cget("text"): 
                var.set(not var.get())
        row.bind("<Button-1>", toggle_var)
        lbl.bind("<Button-1>", toggle_var)
        tick_label.bind("<Button-1>", toggle_var)

        self.tasks[row] = {"text": task_text, "done": False, "var": var, "label": lbl, "tick": tick_label}

    def mark_done(self):
        for r, info in self.tasks.items():
            if info["var"].get():  
                info["done"] = True
                info["tick"].config(text="✅")  
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


app = ChecklistApp()
app.mainloop()