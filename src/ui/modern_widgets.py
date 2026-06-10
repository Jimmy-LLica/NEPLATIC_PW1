import tkinter as tk
from tkinter import ttk


PALETTE = {
    "app_bg": "#eef2f7",
    "surface": "#ffffff",
    "surface_soft": "#f8fafc",
    "surface_alt": "#f1f5f9",
    "sidebar": "#0f172a",
    "sidebar_soft": "#1e293b",
    "text": "#0f172a",
    "text_muted": "#64748b",
    "border": "#dbe4ee",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "success": "#16a34a",
    "warning": "#f59e0b",
    "danger": "#dc2626",
    "shadow": "#c7d2e0",
}


def configure_base_theme(style: ttk.Style) -> None:
    style.theme_use("clam")

    style.configure(".", font=("Segoe UI", 10))

    style.configure(
        "App.TFrame",
        background=PALETTE["app_bg"],
    )
    style.configure(
        "Surface.TFrame",
        background=PALETTE["surface"],
    )
    style.configure(
        "SurfaceSoft.TFrame",
        background=PALETTE["surface_soft"],
    )
    style.configure(
        "Sidebar.TFrame",
        background=PALETTE["sidebar"],
    )
    style.configure(
        "SidebarSoft.TFrame",
        background=PALETTE["sidebar_soft"],
    )
    style.configure(
        "AppTitle.TLabel",
        background=PALETTE["sidebar"],
        foreground="#f8fafc",
        font=("Segoe UI Semibold", 16),
    )
    style.configure(
        "AppSubTitle.TLabel",
        background=PALETTE["sidebar"],
        foreground="#94a3b8",
        font=("Segoe UI", 9),
    )
    style.configure(
        "SectionTitle.TLabel",
        background=PALETTE["app_bg"],
        foreground=PALETTE["text"],
        font=("Segoe UI Semibold", 15),
    )
    style.configure(
        "SectionHint.TLabel",
        background=PALETTE["app_bg"],
        foreground=PALETTE["text_muted"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "CardTitle.TLabel",
        background=PALETTE["surface"],
        foreground=PALETTE["text"],
        font=("Segoe UI Semibold", 11),
    )
    style.configure(
        "CardValue.TLabel",
        background=PALETTE["surface"],
        foreground=PALETTE["text"],
        font=("Segoe UI Semibold", 22),
    )
    style.configure(
        "CardMeta.TLabel",
        background=PALETTE["surface"],
        foreground=PALETTE["text_muted"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "Modern.TLabelframe",
        background=PALETTE["surface"],
        bordercolor=PALETTE["border"],
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "Modern.TLabelframe.Label",
        background=PALETTE["surface"],
        foreground=PALETTE["text"],
        font=("Segoe UI Semibold", 10),
    )
    style.configure(
        "Modern.TEntry",
        fieldbackground=PALETTE["surface"],
        background=PALETTE["surface"],
        bordercolor=PALETTE["border"],
        lightcolor=PALETTE["border"],
        darkcolor=PALETTE["border"],
        relief="flat",
        padding=10,
    )
    style.configure(
        "Modern.TCombobox",
        fieldbackground=PALETTE["surface"],
        background=PALETTE["surface"],
        bordercolor=PALETTE["border"],
        lightcolor=PALETTE["border"],
        darkcolor=PALETTE["border"],
        relief="flat",
        padding=8,
    )
    style.map(
        "Modern.TCombobox",
        fieldbackground=[("readonly", PALETTE["surface"])],
        background=[("readonly", PALETTE["surface"])],
    )
    style.configure(
        "Modern.Treeview",
        background=PALETTE["surface"],
        fieldbackground=PALETTE["surface"],
        foreground=PALETTE["text"],
        rowheight=34,
        bordercolor=PALETTE["border"],
        lightcolor=PALETTE["border"],
        darkcolor=PALETTE["border"],
        relief="flat",
        font=("Segoe UI", 9),
    )
    style.configure(
        "Modern.Treeview.Heading",
        background=PALETTE["surface_soft"],
        foreground=PALETTE["text"],
        font=("Segoe UI Semibold", 9),
        padding=8,
    )
    style.map(
        "Modern.Treeview",
        background=[("selected", "#dbeafe")],
        foreground=[("selected", PALETTE["text"])],
    )
    style.configure(
        "Modern.Vertical.TScrollbar",
        gripcount=0,
        troughcolor=PALETTE["app_bg"],
        background=PALETTE["border"],
        darkcolor=PALETTE["border"],
        lightcolor=PALETTE["border"],
        bordercolor=PALETTE["app_bg"],
        arrowsize=12,
    )
    style.configure(
        "Modern.Horizontal.TScrollbar",
        gripcount=0,
        troughcolor=PALETTE["app_bg"],
        background=PALETTE["border"],
        darkcolor=PALETTE["border"],
        lightcolor=PALETTE["border"],
        bordercolor=PALETTE["app_bg"],
        arrowsize=12,
    )


class HoverButton(tk.Button):
    def __init__(
        self,
        parent,
        text,
        command=None,
        *,
        bg="#2563eb",
        fg="#ffffff",
        hover_bg="#1d4ed8",
        active_bg=None,
        border="#2563eb",
        font=("Segoe UI Semibold", 10),
        padx=14,
        pady=10,
        anchor="center",
        justify="center",
    ):
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg or hover_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=border,
            highlightcolor=border,
            font=font,
            padx=padx,
            pady=pady,
            cursor="hand2",
            anchor=anchor,
            justify=justify,
        )
        self._bg = bg
        self._hover_bg = hover_bg
        self._border = border
        self._fg = fg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, _event):
        self.configure(bg=self._hover_bg, highlightbackground=self._hover_bg)

    def _on_leave(self, _event):
        self.configure(bg=self._bg, highlightbackground=self._border)

    def _on_press(self, _event):
        self.configure(relief="sunken")

    def _on_release(self, _event):
        self.configure(relief="flat")


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *, bg=None, scrollbar_style="Modern.Vertical.TScrollbar"):
        super().__init__(parent)
        self._bg = bg or PALETTE["app_bg"]
        self.canvas = tk.Canvas(
            self,
            bg=self._bg,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style=scrollbar_style)
        self.scrollable_frame = ttk.Frame(self.canvas, style="App.TFrame")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self._window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux, add="+")
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux, add="+")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self._window_id, width=event.width)

    def _on_mousewheel(self, event):
        if self.winfo_containing(event.x_root, event.y_root) is None:
            return
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if self.winfo_containing(event.x_root, event.y_root) is None:
            return
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")


def style_treeview(tree: ttk.Treeview, style: ttk.Style) -> None:
    style.configure("Modern.Treeview", rowheight=34)
    style.configure("Modern.Treeview.Heading", padding=8)
    tree.tag_configure("odd", background="#ffffff")
    tree.tag_configure("even", background="#f8fafc")


def animate_window_in(window, *, from_alpha=0.0, to_alpha=1.0, step=0.08, delay=12):
    try:
        window.attributes("-alpha", from_alpha)
    except tk.TclError:
        return

    def tick(alpha):
        alpha = round(alpha, 2)
        if alpha >= to_alpha:
            try:
                window.attributes("-alpha", to_alpha)
            except tk.TclError:
                pass
            return
        try:
            window.attributes("-alpha", alpha)
        except tk.TclError:
            return
        window.after(delay, tick, alpha + step)

    window.after(delay, tick, from_alpha + step)
