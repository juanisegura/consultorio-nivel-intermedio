import tkinter as tk
from tkinter import ttk, messagebox

class Vista:
    """Clase que gestiona la interfaz gráfica de la aplicación con Tkinter."""

    def __init__(self, root, controlador):
        """
        Inicializa la interfaz gráfica.

        :param root: Ventana principal de Tkinter.
        :param controlador: Instancia del controlador que maneja la lógica de negocio.
        """
        self.root = root
        self.controlador = controlador
        self.root.title("Consultorio Médico - SIGEP")
        self.root.geometry("900x500")

        # Barra de navegación (botones superiores)
        self.nav_frame = tk.Frame(self.root, relief=tk.RAISED, bd=2)
        self.nav_frame.pack(fill=tk.X, side=tk.TOP)

        self.botones = [
            ("Agregar", self.controlador.agregar_paciente),
            ("Eliminar", self.controlador.eliminar_paciente),
            ("Editar", self.controlador.editar_paciente),
            ("Buscar", self.controlador.buscar_paciente),
            ("Datos", self.controlador.mostrar_historia_clinica),
            ("Actualizar", self.actualizar_lista)
        ]

        for text, command in self.botones:
            btn = tk.Button(self.nav_frame, text=text, padx=10, pady=5, command=command)
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Tabla de pacientes (TreeView)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.upcoming_frame = tk.LabelFrame(self.main_frame, text="Pacientes", width=400, height=400)
        self.upcoming_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            self.upcoming_frame,
            columns=("DNI", "Nombre", "Teléfono", "Obra Social", "N° Expediente"),
            show="headings"
        )
        for col in ("DNI", "Nombre", "Teléfono", "Obra Social", "N° Expediente"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Cargar datos iniciales
        self.actualizar_lista()

    def actualizar_lista(self):
        """Carga o refresca los datos de la tabla de pacientes."""
        try:
            self.tree.delete(*self.tree.get_children())  # Limpiar la tabla
            pacientes = self.controlador.obtener_pacientes()
            for paciente in pacientes:
                self.tree.insert("", "end", values=paciente)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la lista de pacientes: {e}")

    def obtener_seleccion(self):
        """Devuelve el DNI del paciente seleccionado en la tabla."""
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un paciente de la lista.")
            return None
        return self.tree.item(seleccionado)['values'][0]

    def iniciar(self):
        """Inicia el bucle principal de la interfaz gráfica."""
        self.root.mainloop()