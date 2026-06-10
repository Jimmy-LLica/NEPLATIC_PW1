import tkinter as tk
from tkinter import messagebox, ttk

from src.controllers.ruta_controller import RutaController
from src.services.sync_service import SyncService
from src.ui.modern_widgets import PALETTE, HoverButton, style_treeview


class RutasView(tk.Frame):
    def __init__(self, parent, current_user, mode="rutas"):
        super().__init__(parent, bg=PALETTE["app_bg"])
        self.current_user = current_user
        self.mode = mode
        self.controller = RutaController(current_user)
        self.sync_service = SyncService()
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=PALETTE["app_bg"])
        header.pack(fill=tk.X, padx=8, pady=(0, 12))
        title = {
            "rutas": "Mis rutas",
            "deudas": "Mis deudas",
            "notificar": "Notificar visita",
        }.get(self.mode, "Rutas")
        subtitle = {
            "rutas": "Listado de rutas asignadas y estado general.",
            "deudas": "Deudas asociadas a la ruta actual.",
            "notificar": "Registro de visitas con validacion basica.",
        }.get(self.mode, "Modulo operativo")
        tk.Label(header, text=title, bg=PALETTE["app_bg"], fg=PALETTE["text"], font=("Segoe UI Semibold", 18)).pack(anchor="w")
        tk.Label(header, text=subtitle, bg=PALETTE["app_bg"], fg=PALETTE["text_muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))

        if self.mode == "notificar":
            self._build_notificar()
        else:
            self._build_listings()

    def _build_listings(self):
        actions = tk.Frame(self, bg=PALETTE["app_bg"])
        actions.pack(fill=tk.X, padx=8, pady=(0, 10))
        HoverButton(actions, text="Actualizar", command=self.refresh, bg=PALETTE["surface_soft"], fg=PALETTE["text"], hover_bg="#e2e8f0", active_bg="#e2e8f0", border=PALETTE["border"], font=("Segoe UI Semibold", 9), padx=12, pady=8).pack(side=tk.LEFT, padx=(0, 8))
        HoverButton(actions, text="Sincronizar cola", command=self.sync_queue, bg=PALETTE["accent"], hover_bg=PALETTE["accent_hover"], border=PALETTE["accent"], font=("Segoe UI Semibold", 9), padx=12, pady=8).pack(side=tk.LEFT)

        self.summary = tk.Frame(self, bg=PALETTE["app_bg"])
        self.summary.pack(fill=tk.X, padx=8, pady=(0, 10))

        card = tk.Frame(self, bg=PALETTE["surface"], highlightbackground=PALETTE["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        notebook = ttk.Notebook(card)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.routes_tab = tk.Frame(notebook, bg=PALETTE["surface"])
        self.debts_tab = tk.Frame(notebook, bg=PALETTE["surface"])
        notebook.add(self.routes_tab, text="Rutas")
        notebook.add(self.debts_tab, text="Deudas")

        self._build_tree_tab(self.routes_tab, "routes_tree", ["id_ruta", "fecha_ruta", "estado_ruta", "total_deudas", "deudas_atendidas", "distancia_estimada_km"])
        self._build_tree_tab(self.debts_tab, "deudas_tree", ["id_deuda", "codigo_lote", "orden_visita", "visitado"])

        self.refresh()

    def _build_tree_tab(self, parent, attr, columns):
        frame = tk.Frame(parent, bg=PALETTE["surface"])
        frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings", style="Modern.Treeview")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview, style="Modern.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        style_treeview(tree, ttk.Style())
        setattr(self, attr, tree)

    def _build_notificar(self):
        card = tk.Frame(self, bg=PALETTE["surface"], highlightbackground=PALETTE["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        inner = tk.Frame(card, bg=PALETTE["surface"], padx=18, pady=18)
        inner.pack(fill=tk.BOTH, expand=True)

        def field(label, row, show=None):
            tk.Label(inner, text=label, bg=PALETTE["surface"], fg=PALETTE["text"], font=("Segoe UI Semibold", 10)).grid(row=row * 2, column=0, sticky="w", pady=(0, 6))
            entry = ttk.Entry(inner, style="Modern.TEntry", show=show)
            entry.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 12))
            return entry

        inner.columnconfigure(0, weight=1)
        self.id_deuda_entry = field("ID de deuda", 0)
        self.direccion_entry = field("Direccion exacta", 1)
        self.persona_entry = field("Persona contactada", 2)
        self.parentesco_entry = field("Parentesco / relacion", 3)

        tk.Label(inner, text="Resultado de la visita", bg=PALETTE["surface"], fg=PALETTE["text"], font=("Segoe UI Semibold", 10)).grid(row=8, column=0, sticky="w", pady=(0, 6))
        self.estado_cb = ttk.Combobox(
            inner,
            values=[
                "1 - NOTIFICADO",
                "2 - AUSENTE",
                "3 - DIRECCION ERRADA",
                "4 - RECHAZADO",
                "5 - CONTRIBUYENTE FALLECIDO",
            ],
            state="readonly",
            style="Modern.TCombobox",
        )
        self.estado_cb.grid(row=9, column=0, sticky="ew", pady=(0, 14))
        self.estado_cb.current(0)

        HoverButton(inner, text="Guardar visita", command=self.submit, bg=PALETTE["accent"], hover_bg=PALETTE["accent_hover"], border=PALETTE["accent"], font=("Segoe UI Semibold", 10), padx=14, pady=10).grid(row=10, column=0, sticky="e", pady=(10, 0))

    def refresh(self):
        if self.mode != "notificar":
            self._render_stats()
            self._load_routes()
            self._load_debts()

    def _render_stats(self):
        for widget in self.summary.winfo_children():
            widget.destroy()

        try:
            routes = self.controller.listar_rutas_usuario()
            debts = self.controller.listar_deudas_asignadas()
            pending_sync = len(self.sync_service.obtener_cola_local().get("pending", []))
        except Exception as exc:
            messagebox.showerror("Rutas", f"No fue posible cargar la informacion.\n\nDetalle: {exc}", parent=self)
            routes = []
            debts = []
            pending_sync = 0

        cards = [
            ("Rutas", len(routes), "Asignadas al usuario"),
            ("Deudas", len(debts), "Pendientes de visita"),
            ("Cola", pending_sync, "Pendientes por sincronizar"),
        ]
        for index, (label, value, meta) in enumerate(cards):
            frame = tk.Frame(self.summary, bg=PALETTE["surface"], highlightbackground=PALETTE["border"], highlightthickness=1)
            frame.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 8, 0))
            tk.Label(frame, text=label, bg=PALETTE["surface"], fg=PALETTE["text_muted"], font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 4))
            tk.Label(frame, text=str(value), bg=PALETTE["surface"], fg=PALETTE["text"], font=("Segoe UI Semibold", 20)).pack(anchor="w", padx=14)
            tk.Label(frame, text=meta, bg=PALETTE["surface"], fg=PALETTE["text_muted"], font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(0, 12))

    def _load_routes(self):
        for item in self.routes_tree.get_children():
            self.routes_tree.delete(item)
        try:
            routes = self.controller.listar_rutas_usuario()
            self.routes_tree["columns"] = ["id_ruta", "fecha_ruta", "estado_ruta", "total_deudas", "deudas_atendidas", "distancia_estimada_km"]
            headings = {
                "id_ruta": "ID ruta",
                "fecha_ruta": "Fecha",
                "estado_ruta": "Estado",
                "total_deudas": "Total",
                "deudas_atendidas": "Atendidas",
                "distancia_estimada_km": "Km estimados",
            }
            for col, text in headings.items():
                self.routes_tree.heading(col, text=text)
                self.routes_tree.column(col, width=130, anchor="center")
            if routes:
                for route in routes:
                    self.routes_tree.insert("", "end", values=(
                        route.id_ruta,
                        getattr(route, "fecha_ruta", ""),
                        getattr(route, "estado_ruta", ""),
                        getattr(route, "total_deudas", 0),
                        getattr(route, "deudas_atendidas", 0),
                        getattr(route, "distancia_estimada_km", ""),
                    ))
            else:
                self.routes_tree.insert("", "end", values=("Sin datos", "", "", "", "", ""))
        except Exception as exc:
            self.routes_tree.insert("", "end", values=(f"Error: {exc}", "", "", "", "", ""))

    def _load_debts(self):
        for item in self.deudas_tree.get_children():
            self.deudas_tree.delete(item)
        try:
            debts = self.controller.listar_deudas_asignadas()
            self.deudas_tree["columns"] = ["id_deuda", "codigo_lote", "orden_visita", "visitado"]
            headings = {"id_deuda": "ID deuda", "codigo_lote": "Lote", "orden_visita": "Orden", "visitado": "Visitado"}
            for col, text in headings.items():
                self.deudas_tree.heading(col, text=text)
                self.deudas_tree.column(col, width=150, anchor="center")
            if debts:
                for debt in debts:
                    self.deudas_tree.insert("", "end", values=(
                        debt.id_deuda,
                        getattr(debt, "codigo_lote", ""),
                        getattr(debt, "orden_visita", ""),
                        "SI" if getattr(debt, "visitado", False) else "NO",
                    ))
            else:
                self.deudas_tree.insert("", "end", values=("Sin datos", "", "", ""))
        except Exception as exc:
            self.deudas_tree.insert("", "end", values=(f"Error: {exc}", "", "", ""))

    def sync_queue(self):
        result = self.sync_service.procesar_cola_pendiente()
        messagebox.showinfo("Sincronizacion", result.get("message", "Operacion completada"), parent=self)
        if self.mode != "notificar":
            self.refresh()

    def submit(self):
        try:
            id_deuda = int(self.id_deuda_entry.get().strip())
        except ValueError:
            messagebox.showerror("Validacion", "El ID de deuda debe ser un numero valido.", parent=self)
            return

        direccion = self.direccion_entry.get().strip()
        if not direccion:
            messagebox.showerror("Validacion", "La direccion es obligatoria.", parent=self)
            return

        persona = self.persona_entry.get().strip()
        parentesco = self.parentesco_entry.get().strip()
        id_estado = int(self.estado_cb.get().split(" - ")[0])

        try:
            result = self.controller.registrar_notificacion(id_deuda, direccion, persona, parentesco, id_estado)
            if result.get("success"):
                redis_info = " (Redis: OK)" if result.get("redis_published") else ""
                sync_info = f" [Sincronizacion: {result.get('sync_status', '?')}]"
                messagebox.showinfo("Visita registrada", f"{result['message']}{redis_info}{sync_info}", parent=self)
                for entry in [self.id_deuda_entry, self.direccion_entry, self.persona_entry, self.parentesco_entry]:
                    entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", f"No fue posible registrar la visita.\n\n{result.get('message', 'Error desconocido')}", parent=self)
        except Exception as exc:
            messagebox.showerror("Error", f"No fue posible registrar la visita.\n\nDetalle: {exc}", parent=self)

    def close(self):
        try:
            self.controller.close()
        except Exception:
            pass
