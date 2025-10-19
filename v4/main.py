import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os, uuid, datetime

DATA_FILE = "tasks_v6.json"
CATEGORIES = ["General", "Work", "Study", "Home", "Shopping", "Personal", "Health"]
PRIORITIES = ["Low", "Medium", "High", "Urgent"]

STATUS_EMOJI = {"Pending": "⏳", "Completed": "✅"}
PRIORITY_EMOJI = {"Low": "○", "Medium": "●", "High": "◉", "Urgent": "🔴"}


class AdvancedTodo:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🚀 Advanced To-Do List v6")
        self.root.geometry("1100x600")
        self.root.configure(bg="#f6f7f9")

        # in-memory store: item_id -> task_dict
        self.items = {}

        self._build_ui()
        self._load_from_disk()
        self._update_stats()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- UI ----------
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg="#203646", height=80)
        hdr.pack(fill="x", padx=10, pady=10)
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="🚀 Advanced Task Manager", fg="white", bg="#203646",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=20, pady=20)

        # Search & filters
        top = tk.Frame(self.root, bg="#f6f7f9")
        top.pack(fill="x", padx=20)

        tk.Label(top, text="Search:", bg="#f6f7f9", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.var_search = tk.StringVar()
        ent_search = tk.Entry(top, textvariable=self.var_search, width=30, relief="solid")
        ent_search.grid(row=0, column=1, padx=6)
        ent_search.bind("<KeyRelease>", self._apply_filters)

        tk.Label(top, text="Filter:", bg="#f6f7f9", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=(20, 5))
        self.var_status = tk.StringVar(value="All")
        cb_status = ttk.Combobox(top, values=["All", "Pending", "Completed"], state="readonly",
                                 textvariable=self.var_status, width=10)
        cb_status.grid(row=0, column=3)
        cb_status.bind("<<ComboboxSelected>>", self._apply_filters)

        tk.Label(top, text="Category:", bg="#f6f7f9", font=("Segoe UI", 10, "bold")).grid(row=0, column=4, padx=(20, 5))
        self.var_cat_filter = tk.StringVar(value="All")
        cb_catf = ttk.Combobox(top, values=["All"] + CATEGORIES, textvariable=self.var_cat_filter,
                               state="readonly", width=12)
        cb_catf.grid(row=0, column=5)
        cb_catf.bind("<<ComboboxSelected>>", self._apply_filters)

        # New task form
        form = tk.Frame(self.root, bg="#f6f7f9")
        form.pack(fill="x", padx=20, pady=(10, 0))

        tk.Label(form, text="New Task:", bg="#f6f7f9", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.var_task = tk.StringVar()
        tk.Entry(form, textvariable=self.var_task, width=60, relief="solid").grid(row=1, column=0, columnspan=6, sticky="we", pady=(2, 8))

        tk.Label(form, text="Category:", bg="#f6f7f9", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.var_cat = tk.StringVar(value="General")
        ttk.Combobox(form, values=CATEGORIES, textvariable=self.var_cat, state="readonly", width=15)\
            .grid(row=2, column=1, sticky="w", padx=(6, 20))

        tk.Label(form, text="Priority:", bg="#f6f7f9", font=("Segoe UI", 10)).grid(row=2, column=2, sticky="w")
        self.var_pri = tk.StringVar(value="Medium")
        ttk.Combobox(form, values=PRIORITIES, textvariable=self.var_pri, state="readonly", width=12)\
            .grid(row=2, column=3, sticky="w", padx=(6, 20))

        tk.Button(form, text="➕ Add Task", bg="#28a745", fg="white", width=14, bd=0,
                  activebackground="#23923d", command=self._add_task)\
            .grid(row=2, column=5, sticky="e")

        # List (Treeview)
        list_wrap = tk.Frame(self.root, bg="#f6f7f9")
        list_wrap.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Status", "Priority", "Category", "Task", "Created")
        self.tree = ttk.Treeview(list_wrap, columns=cols, show="headings", height=18)
        self.tree.heading("Status", text="🧭 Status")
        self.tree.heading("Priority", text="🎯 Priority")
        self.tree.heading("Category", text="📁 Category")
        self.tree.heading("Task", text="📝 Task")
        self.tree.heading("Created", text="⏰ Created")

        self.tree.column("Status", width=90, anchor="center")
        self.tree.column("Priority", width=90, anchor="center")
        self.tree.column("Category", width=110, anchor="w")
        self.tree.column("Task", width=560, anchor="w")
        self.tree.column("Created", width=140, anchor="center")

        vs = ttk.Scrollbar(list_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        # Row tag styles (hidden = gray)
        self.tree.tag_configure("hidden", foreground="#b9bdc3")

        # Context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Toggle Done", command=self._toggle_done)
        self.menu.add_command(label="Edit", command=self._edit_task)
        self.menu.add_command(label="Delete", command=self._delete_selected)
        self.tree.bind("<Button-3>", self._show_menu)  # right-click
        self.tree.bind("<Double-1>", lambda e: self._edit_task())

        # Bottom action bar
        actions = tk.Frame(self.root, bg="#f6f7f9")
        actions.pack(fill="x", padx=20, pady=(0, 6))

        tk.Button(actions, text="Toggle Done", command=self._toggle_done, width=12, bg="#e3f2fd", bd=0)\
            .pack(side="left", padx=4)
        tk.Button(actions, text="Edit", command=self._edit_task, width=12, bg="#ffe0b2", bd=0)\
            .pack(side="left", padx=4)
        tk.Button(actions, text="Delete", command=self._delete_selected, width=12, bg="#ffcdd2", bd=0)\
            .pack(side="left", padx=4)
        tk.Button(actions, text="Stats", command=self._show_stats, width=12, bg="#e1bee7", bd=0)\
            .pack(side="left", padx=4)
        tk.Button(actions, text="Refresh", command=self._apply_filters, width=12, bg="#c8e6c9", bd=0)\
            .pack(side="left", padx=4)

        # Status bar
        self.stats_label = tk.Label(self.root, text="📊 Tasks: 0 Completed | 0 Pending | 0 Total",
                                    bg="#f6f7f9", anchor="w")
        self.stats_label.pack(fill="x", padx=20, pady=(0, 8))

    # ---------- Core ops ----------
    def _add_task(self):
        text = self.var_task.get().strip()
        if not text:
            messagebox.showwarning("Validation", "Enter a task description.")
            return

        task = {
            "id": str(uuid.uuid4()),
            "text": text,
            "category": self.var_cat.get(),
            "priority": self.var_pri.get(),
            "status": "Pending",
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.var_task.set("")
        self._insert_task(task)
        self._save_to_disk()
        self._update_stats()

    def _insert_task(self, task: dict):
        row = (
            STATUS_EMOJI[task["status"]],
            PRIORITY_EMOJI.get(task["priority"], "●"),
            task["category"],
            task["text"],
            task["created"],
        )
        item_id = self.tree.insert("", "end", values=row)
        self.items[item_id] = task
        self._apply_filters()

    def _toggle_done(self):
        to_toggle = self.tree.selection()
        if not to_toggle:
            return
        for iid in to_toggle:
            task = self.items.get(iid)
            if not task:
                continue
            task["status"] = "Completed" if task["status"] == "Pending" else "Pending"
            self.tree.set(iid, "Status", STATUS_EMOJI[task["status"]])
        self._save_to_disk()
        self._apply_filters()
        self._update_stats()

    def _edit_task(self):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        task = self.items[iid]

        new_text = simpledialog.askstring("Edit Task", "Task:", initialvalue=task["text"], parent=self.root)
        if new_text is None:
            return
        new_text = new_text.strip()
        if not new_text:
            messagebox.showwarning("Validation", "Task cannot be empty.")
            return

        # Optional: edit category and priority too
        new_cat = simpledialog.askstring("Edit Category", f"Category [{task['category']}]:",
                                         initialvalue=task["category"], parent=self.root)
        if new_cat is None or not new_cat.strip():
            new_cat = task["category"]
        new_pri = simpledialog.askstring("Edit Priority (Low/Medium/High/Urgent)",
                                         initialvalue=task["priority"], parent=self.root)
        if new_pri is None or new_pri.strip() not in PRIORITIES:
            new_pri = task["priority"]

        task["text"] = new_text
        task["category"] = new_cat.strip()
        task["priority"] = new_pri.strip()

        self.tree.set(iid, "Task", task["text"])
        self.tree.set(iid, "Category", task["category"])
        self.tree.set(iid, "Priority", PRIORITY_EMOJI.get(task["priority"], "●"))

        self._save_to_disk()
        self._apply_filters()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(sel)} selected task(s)?"):
            return
        for iid in sel:
            self.tree.delete(iid)
            self.items.pop(iid, None)
        self._save_to_disk()
        self._update_stats()

    # ---------- Filters / Search ----------
    def _apply_filters(self, _event=None):
        q = self.var_search.get().lower().strip()
        fstat = self.var_status.get()
        fcat = self.var_cat_filter.get()

        for iid in self.tree.get_children(""):
            task = self.items.get(iid, {})
            text_ok = (q in task.get("text", "").lower()) if q else True
            stat_ok = (fstat == "All") or (task.get("status") == fstat)
            cat_ok = (fcat == "All") or (task.get("category") == fcat)

            if text_ok and stat_ok and cat_ok:
                self.tree.item(iid, tags=())
            else:
                self.tree.item(iid, tags=("hidden",))

    # ---------- Stats / Persistence ----------
    def _show_stats(self):
        total = len(self.items)
        completed = sum(1 for t in self.items.values() if t["status"] == "Completed")
        pending = total - completed

        by_cat = {}
        for t in self.items.values():
            by_cat[t["category"]] = by_cat.get(t["category"], 0) + 1

        txt = [
            "📊 Detailed Statistics",
            f"✅ Completed: {completed}",
            f"⏳ Pending:   {pending}",
            f"Σ Total:      {total}",
            "",
            "📁 By Category:",
        ]
        for k, v in sorted(by_cat.items()):
            txt.append(f" • {k}: {v}")
        messagebox.showinfo("Statistics", "\n".join(txt))

    def _update_stats(self):
        total = len(self.items)
        completed = sum(1 for t in self.items.values() if t["status"] == "Completed")
        pending = total - completed
        self.stats_label.config(text=f"📊 Tasks: {completed} Completed | {pending} Pending | {total} Total")

    def _save_to_disk(self):
        try:
            data = [t for t in self.items.values()]
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _load_from_disk(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for task in data:
                self._insert_task(task)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _on_close(self):
        self._save_to_disk()
        self.root.destroy()

    # ---------- Context menu ----------
    def _show_menu(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self.tree.selection_set(row)
            self.menu.tk_popup(event.x_root, event.y_root)


if __name__ == "__main__":
    tk.mainloop(AdvancedTodo(tk.Tk()))
