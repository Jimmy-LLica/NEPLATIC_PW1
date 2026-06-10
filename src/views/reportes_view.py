from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.controllers.reporte_controller import ReporteController
from src.services.report_generator import ReportGenerator
from src.ui.modern_widgets import PALETTE, HoverButton, style_treeview


class ReportesView(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg=PALETTE["app_bg"])
        self.current_user = current_user
        self.controller = ReporteController()
        self.exporter = ReportGenerator(str(Path.cwd() / "scratch" / "reports"))
        self.data = {}
        self._build()
        self.refresh()

    def _build(self):
        header = tk.Frame(self, bg=PALETTE["app_bg"])
        header.pack(fill=tk.X, padx=8, pady=(0, 12))
        tk.Label(header, text="Reportes", bg=PALETTE["app_bg"], fg=PALETTE["text"], font=("Segoe UI Semibold", 18)).pack(anchor="w")
        tk.Label(header, text="Tablas resumen, exportacion en Excel y PDF.", bg=PALETTE["app_bg"], fg=PALETTE["text_muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))

        actions = tk.Frame(self, bg=PALETTE["app_bg"])
        actions.pack(fill=tk.X, padx=8, pady=(0, 10))
        HoverButton(actions, text="Actualizar", command=self.refresh, bg=PALETTE["surface_soft"], fg=PALETTE["text"], hover_bg="#e2e8f0", active_bg="#e2e8f0", border=PALETTE["border"], font=("Segoe UI Semibold", 9), padx=12, pady=8).pack(side=tk.LEFT, padx=(0, 8))
        HoverButton(actions, text="Exportar Excel", command=self.export_excel, bg=PALETTE["accent"], hover_bg=PALETTE["accent_hover"], border=PALETTE["accent"], font=("Segoe UI Semibold", 9), padx=12, pady=8).pack(side=tk.LEFT, padx=(0, 8))
        HoverButton(actions, text="Exportar PDF", command=self.export_pdf, bg=PALETTE["surface_soft"], fg=PALETTE["text"], hover_bg="#e2e8f0", active_bg="#e2e8f0", border=PALETTE["border"], font=("Segoe UI Semibold", 9), padx=12, pady=8).pack(side=tk.LEFT)

        self.summary_frame = tk.Frame(self, bg=PALETTE["app_bg"])
        self.summary_frame.pack(fill=tk.X, padx=8, pady=(0, 10))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.tab_dashboard = tk.Frame(self.notebook, bg=PALETTE["surface"])
        self.tab_sector = tk.Frame(self.notebook, bg=PALETTE["surface"])
        self.tab_top = tk.Frame(self.notebook, bg=PALETTE["surface"])
        self.tab_evolution = tk.Frame(self.notebook, bg=PALETTE["surface"])

        self.notebook.add(self.tab_dashboard, text="Resumen")
        self.notebook.add(self.tab_sector, text="Por sector")
        self.notebook.add(self.tab_top, text="Top deudores")
        self.notebook.add(self.tab_evolution, text="Evolucion")

        self.dashboard_text = tk.Text(self.tab_dashboard, height=12, bg=PALETTE["surface_soft"], fg=PALETTE["text"], relief="flat", font=("Consolas", 10))
        self.dashboard_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_tree(self.tab_sector, "sector")
        self._build_tree(self.tab_top, "top")
        self._build_tree(self.tab_evolution, "evolution")

    def _build_tree(self, parent, kind):
        frame = tk.Frame(parent, bg=PALETTE["surface"])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tree = ttk.Treeview(frame, show="headings", style="Modern.Treeview")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview, style="Modern.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        style_treeview(tree, ttk.Style())
        setattr(self, f"{kind}_tree", tree)

    @staticmethod
    def _rows(rows):
        result = []
        for row in rows or []:
            if isinstance(row, dict):
                result.append(row)
            elif hasattr(row, "_mapping"):
                result.append(dict(row._mapping))
            else:
                result.append(dict(row))
        return result

    def refresh(self):
        try:
            self.data = self.controller.exportable_dashboard()
        except Exception as exc:
            messagebox.showerror("Reportes", f"No fue posible cargar los reportes.\n\nDetalle: {exc}", parent=self)
            self.data = {"dashboard": {}, "top_deudores": [], "sector": [], "evolucion": []}

        self._render_summary()
        self._render_tree(self.sector_tree, self._rows(self.data.get("sector")), ["codigo_sector", "nombre_sector", "total_deuda", "saldo_pendiente"])
        self._render_tree(self.top_tree, self._rows(self.data.get("top_deudores")), None)
        self._render_tree(self.evolution_tree, self._rows(self.data.get("evolucion")), None)

    def _render_summary(self):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        cards = []
        dashboard = self.data.get("dashboard") or {}
        keys = list(dashboard.items())[:4]
        if keys:
            for idx, (key, value) in enumerate(keys):
                card = tk.Frame(self.summary_frame, bg=PALETTE["surface"], highlightbackground=PALETTE["border"], highlightthickness=1)
                card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0))
                tk.Label(card, text=str(key).replace("_", " ").title(), bg=PALETTE["surface"], fg=PALETTE["text_muted"], font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 4))
                tk.Label(card, text=str(value), bg=PALETTE["surface"], fg=PALETTE["text"], font=("Segoe UI Semibold", 20)).pack(anchor="w", padx=14, pady=(0, 12))
                cards.append(card)
        else:
            card = tk.Frame(self.summary_frame, bg=PALETTE["surface"], highlightbackground=PALETTE["border"], highlightthickness=1)
            card.pack(fill=tk.X)
            tk.Label(card, text="No hay resumen disponible en las vistas de base de datos.", bg=PALETTE["surface"], fg=PALETTE["text_muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=14, pady=14)

        self.dashboard_text.delete("1.0", "end")
        self.dashboard_text.insert("end", "Resumen general\n")
        self.dashboard_text.insert("end", "=" * 60 + "\n")
        for key, value in dashboard.items():
            self.dashboard_text.insert("end", f"{key}: {value}\n")

    def _render_tree(self, tree, rows, explicit_columns):
        for item in tree.get_children():
            tree.delete(item)

        if not rows:
            cols = explicit_columns or ["mensaje"]
            tree["columns"] = cols
            for col in cols:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=180, anchor="w")
            tree.insert("", "end", values=("Sin datos disponibles",))
            return

        columns = explicit_columns or list(rows[0].keys())
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=160, anchor="w")

        for row in rows:
            tree.insert("", "end", values=[row.get(col, "") for col in columns])

    def export_excel(self):
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar reporte Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
        )
        if not path:
            return
        sections = {
            "resumen": [self.data.get("dashboard") or {}],
            "sector": self._rows(self.data.get("sector")),
            "top_deudores": self._rows(self.data.get("top_deudores")),
            "evolucion": self._rows(self.data.get("evolucion")),
        }
        saved = self.exporter.export_excel(path, sections)
        messagebox.showinfo("Reportes", f"Reporte exportado correctamente.\n\n{saved}", parent=self)

    def export_pdf(self):
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar reporte PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not path:
            return
        sections = {
            "resumen": [self.data.get("dashboard") or {}],
            "sector": self._rows(self.data.get("sector")),
            "top_deudores": self._rows(self.data.get("top_deudores")),
            "evolucion": self._rows(self.data.get("evolucion")),
        }
        saved = self.exporter.export_pdf(path, "Reporte Neplatic", sections)
        messagebox.showinfo("Reportes", f"Reporte exportado correctamente.\n\n{saved}", parent=self)

    def close(self):
        try:
            self.controller.close()
        except Exception:
            pass
