import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import Scrollbar
import shutil
from modelo import BaseDatos, Paciente

class Controlador:
    """Clase que maneja la lógica de la aplicación y la comunicación entre modelo y vista."""

    def __init__(self, vista=None):
        """Inicializa la base de datos y asigna la vista."""
        self.db = BaseDatos()
        self.vista = vista
        self.historia_clinica_fields = {}  # Dictionary for historia clinica fields

    def obtener_pacientes(self):
        """Obtiene todos los pacientes desde la base de datos."""
        try:
            return Paciente.obtener_todos(self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener los pacientes: {e}")
            return []

    def agregar_paciente(self):
        """Abre ventana para agregar un paciente y lo guarda en la base de datos."""
        def save_turno():
            datos = {
                "dni": dni_entry.get(),
                "nombre": nombre_entry.get(),
                "telefono": telefono_entry.get(),
                "obra_social": obra_social_entry.get(),
            }

            if not all(datos.values()):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            paciente = Paciente(datos["dni"], datos["nombre"], datos["telefono"], datos["obra_social"])
            try:
                if paciente.guardar(self.db):
                    messagebox.showinfo("Éxito", "Turno añadido correctamente.")
                    self.vista.actualizar_lista()
                    add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar los datos: {e}")

        add_window = tk.Toplevel()
        add_window.title("Agregar historial clinico")
        add_window.geometry("400x300")

        tk.Label(add_window, text="DNI:").pack(pady=5)
        dni_entry = tk.Entry(add_window)
        dni_entry.pack(pady=5)

        tk.Label(add_window, text="Nombre y Apellido:").pack(pady=5)
        nombre_entry = tk.Entry(add_window)
        nombre_entry.pack(pady=5)

        tk.Label(add_window, text="Teléfono:").pack(pady=5)
        telefono_entry = tk.Entry(add_window)
        telefono_entry.pack(pady=5)

        tk.Label(add_window, text="Obra Social:").pack(pady=5)
        obra_social_entry = tk.Entry(add_window)
        obra_social_entry.pack(pady=5)

        tk.Button(add_window, text="Guardar", command=save_turno).pack(pady=10)
        tk.Button(add_window, text="Cancelar", command=add_window.destroy).pack(pady=5)

    def eliminar_paciente(self):
        """Elimina un paciente seleccionado en la vista."""
        selected_item = self.vista.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor, seleccione un turno para eliminar.")
            return

        dni = self.vista.tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar el turno con DNI: {dni}?")
        if confirm:
            try:
                if Paciente.eliminar(self.db, dni):
                    self.vista.actualizar_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el paciente: {e}")

    def editar_paciente(self):
        """Edita un paciente seleccionado."""
        selected_item = self.vista.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor, seleccione un turno para editar.")
            return

        dni, nombre, telefono, obra_social = self.vista.tree.item(selected_item)['values'][:4]  # Adjust based on columns

        def save_changes():
            new_dni = dni_entry.get()
            new_nombre = nombre_entry.get()
            new_telefono = telefono_entry.get()
            new_obra_social = obra_social_entry.get()

            if not all([new_dni, new_nombre, new_telefono, new_obra_social]):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            paciente = Paciente(new_dni, new_nombre, new_telefono, new_obra_social)
            try:
                if paciente.actualizar(self.db):
                    messagebox.showinfo("Éxito", "Paciente actualizado correctamente.")
                    self.vista.actualizar_lista()
                    edit_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el paciente: {e}")

        edit_window = tk.Toplevel()
        edit_window.title("Editar historal clínico")
        edit_window.geometry("400x400")

        tk.Label(edit_window, text="DNI:").pack(pady=5)
        dni_entry = tk.Entry(edit_window)
        dni_entry.insert(0, dni)
        dni_entry.pack(pady=5)

        tk.Label(edit_window, text="Nombre y Apellido:").pack(pady=5)
        nombre_entry = tk.Entry(edit_window)
        nombre_entry.insert(0, nombre)
        nombre_entry.pack(pady=5)

        tk.Label(edit_window, text="Teléfono:").pack(pady=5)
        telefono_entry = tk.Entry(edit_window)
        telefono_entry.insert(0, telefono)
        telefono_entry.pack(pady=5)

        tk.Label(edit_window, text="Obra Social:").pack(pady=5)
        obra_social_entry = tk.Entry(edit_window)
        obra_social_entry.insert(0, obra_social)
        obra_social_entry.pack(pady=5)

        tk.Button(edit_window, text="Guardar Cambios", command=save_changes).pack(pady=10)
        tk.Button(edit_window, text="Cancelar", command=edit_window.destroy).pack(pady=5)

    def buscar_paciente(self):
        """Busca pacientes según un criterio ingresado por el usuario."""
        def aplicar_busqueda():
            criterio = entry_busqueda.get().strip()
            if not criterio:
                messagebox.showerror("Error", "Por favor, ingrese un criterio de búsqueda.")
                return

            filtros = """
                juzgado_civil LIKE ? OR 
                nombre_apellido LIKE ? OR 
                dni LIKE ? OR 
                abogado_demanda LIKE ? OR 
                abogado_demandada LIKE ? OR 
                expediente_numero LIKE ?
            """
            valores = [f"%{criterio}%"] * 6

            query = f"SELECT dni, nombre_apellido, telefono, obra_social, expediente_numero FROM consultorio WHERE {filtros}"
            try:
                resultados = self.db.obtener_datos(query, valores)
                self.vista.tree.delete(*self.vista.tree.get_children())
                for row in resultados:
                    self.vista.tree.insert("", "end", values=row)
                buscar_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron aplicar los filtros: {e}")

        buscar_window = tk.Toplevel()
        buscar_window.title("Buscar Historias Clínicas")
        buscar_window.geometry("400x200")

        tk.Label(buscar_window, text="Ingrese criterio de búsqueda:").pack(pady=10)
        entry_busqueda = tk.Entry(buscar_window, width=50)
        entry_busqueda.pack(pady=5)

        tk.Button(buscar_window, text="Buscar", command=aplicar_busqueda).pack(pady=10)
        tk.Button(buscar_window, text="Cerrar", command=buscar_window.destroy).pack(pady=5)

    def mostrar_historia_clinica(self):
        """Muestra y gestiona la historia clínica del paciente seleccionado."""
        selected_item = self.vista.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor, seleccione un turno para ver los datos.")
            return

        dni = self.vista.tree.item(selected_item)['values'][0]

        def load_data(dni):
            try:
                paciente = Paciente.obtener_por_dni(self.db, dni)
                if paciente:
                    column_names = [desc[0] for desc in self.db.cursor.description]  # Assumes cursor persists
                    for field, value in zip(column_names, paciente):
                        if field in self.historia_clinica_fields:
                            self.historia_clinica_fields[field].config(state="normal")
                            self.historia_clinica_fields[field].delete(0, tk.END)
                            self.historia_clinica_fields[field].insert(0, str(value) if value is not None else "")
                            self.historia_clinica_fields[field].config(state="readonly")
                else:
                    messagebox.showinfo("Información", "No se encontró información para este DNI.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")

        def save_historia():
            data = {field: self.historia_clinica_fields[field].get() for field in self.historia_clinica_fields}
            non_empty_fields = {key: value for key, value in data.items() if value.strip()}
            if 'dni' not in non_empty_fields:
                messagebox.showerror("Error", "El campo DNI es obligatorio.")
                return

            try:
                paciente = Paciente(non_empty_fields.get("dni"), non_empty_fields.get("nombre_apellido"),
                                    non_empty_fields.get("telefono"), non_empty_fields.get("obra_social"))
                paciente_data = {k: non_empty_fields.get(k) for k in self.historia_clinica_fields.keys()}
                if Paciente.obtener_por_dni(self.db, paciente.dni):
                    paciente.actualizar(self.db, **paciente_data)
                else:
                    paciente.guardar(self.db, **paciente_data)
                messagebox.showinfo("Éxito", "Historia clínica guardada correctamente.")
                historia_window.destroy()
                self.vista.actualizar_lista()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar los datos: {e}")

        def enable_editing():
            for field in self.historia_clinica_fields.values():
                field.config(state="normal")
            save_button.config(state="normal")
            edit_button.config(state="disabled")

        def disable_editing():
            for field in self.historia_clinica_fields.values():
                field.config(state="readonly")
            save_button.config(state="disabled")
            edit_button.config(state="normal")

        historia_window = tk.Toplevel()
        historia_window.title("Historia Clínica")
        historia_window.geometry("900x1200")
        historia_window.resizable(False, False)

        main_frame = tk.Frame(historia_window)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        labels_fields = [
            ("Juzgado Civil:", "juzgado_civil", 0, 0),
            ("Expediente N°:", "expediente_numero", 0, 2),
            ("Autos:", "autos", 1, 0),
            ("Abogado demanda:", "abogado_demanda", 2, 0),
            ("Abogado demandada:", "abogado_demandada", 3, 0),
            ("Consultor Técnico:", "consultor_tecnico", 4, 0),
            ("Fecha de examen pericial:", "fecha_examen_pericial", 5, 0),
            ("Hora:", "hora_examen_pericial", 5, 2),
            ("Fecha del hecho:", "fecha_hecho", 6, 0),
            ("Hora:", "hora_hecho", 6, 2),
            ("Nombre y apellido:", "nombre_apellido", 7, 0),
            ("Estado civil:", "estado_civil", 7, 2),
            ("N° DNI:", "dni", 8, 0),
            ("T.E:", "telefono", 8, 2),
            ("Fecha de nacimiento:", "fecha_nacimiento", 9, 0),
            ("Edad:", "edad", 9, 2),
            ("Domicilio:", "domicilio", 10, 0),
            ("Trabajo anterior al hecho:", "trabajo_anterior_hecho", 11, 0),
            ("Días de reposo:", "dias_reposo", 12, 0),
            ("Trabajo posterior al hecho:", "trabajo_posterior_hecho", 13, 0),
            ("Estudios:", "estudios", 14, 0),
            ("Lado dominante:", "lado_dominante", 15, 0),
            ("Deportes Antes:", "deportes_antes", 16, 0),
            ("Deportes Después:", "deportes_despues", 16, 2),
            ("Peso:", "peso", 17, 0),
            ("Talla:", "talla", 17, 2),
            ("ART:", "art", 18, 0),
            ("Accidentes previos:", "accidentes_previos", 19, 0),
            ("Medicación actual:", "medicacion_actual", 20, 0),
            ("Cobertura Médica:", "cobertura_medica", 21, 0),
            ("Atención médica luego del accidente:", "atencion_medica_luego_accidente", 22, 0),
        ]

        self.historia_clinica_fields = {}
        for label_text, field_name, row, col in labels_fields:
            label = tk.Label(scrollable_frame, text=label_text, anchor="w")
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry = tk.Entry(scrollable_frame, state="readonly", width=30)
            entry.grid(row=row, column=col + 1, padx=10, pady=5, sticky="w")
            self.historia_clinica_fields[field_name] = entry

        load_data(dni)

        button_frame = tk.Frame(historia_window)
        button_frame.place(relx=1.0, rely=0.0, anchor="ne")

        edit_button = tk.Button(button_frame, text="EDITAR", command=enable_editing)
        edit_button.pack(side="right", padx=10, pady=10)

        save_button = tk.Button(button_frame, text="GUARDAR", command=save_historia, state="disabled")
        save_button.pack(side="right", padx=10, pady=10)

        cargar_archivos_button = ttk.Button(scrollable_frame, text="Cargar Archivos",
                                            command=lambda: self.cargar_archivos(archivos_listbox))
        cargar_archivos_button.grid(row=18, column=2, pady=(10, 0), sticky="w", columnspan=2)

        ttk.Label(scrollable_frame, text="Archivos:").grid(row=19, column=2, pady=(10, 0), sticky="w", columnspan=2)

        archivos_listbox = tk.Listbox(scrollable_frame, height=10, width=50)
        archivos_listbox.grid(row=20, column=2, columnspan=2, rowspan=20, pady=(0, 10), padx=10, sticky="w")
        archivos_listbox.bind("<Double-1>", lambda event: self.abrir_archivo(archivos_listbox))

        self.cargar_archivos_existentes(self.vista.tree.item(selected_item)['values'][1], archivos_listbox)
        disable_editing()

    def cargar_archivos_existentes(self, nombre_apellido, listbox):
        """Carga archivos existentes en la listbox."""
        listbox.delete(0, tk.END)
        carpeta_principal = os.path.join(os.path.dirname(__file__), "archivos")
        subcarpeta = os.path.join(carpeta_principal, nombre_apellido)

        if os.path.exists(subcarpeta):
            for archivo in os.listdir(subcarpeta):
                listbox.insert(tk.END, archivo)

    def cargar_archivos(self, listbox):
        """Carga nuevos archivos asociados al paciente."""
        selected_item = self.vista.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor, seleccione un turno para cargar archivos.")
            return

        nombre_apellido = self.vista.tree.item(selected_item)['values'][1]
        carpeta_principal = os.path.join(os.path.dirname(__file__), "archivos")
        subcarpeta = os.path.join(carpeta_principal, nombre_apellido)

        if not os.path.exists(subcarpeta):
            os.makedirs(subcarpeta)

        archivos = filedialog.askopenfilenames(title="Seleccionar Archivos",
                                               filetypes=[("Archivos PDF", "*.pdf"),
                                                          ("Documentos Word", "*.docx"),
                                                          ("Imágenes JPG", "*.jpg;*.jpeg"),
                                                          ("Imágenes PNG", "*.png"),
                                                          ("Archivos de Texto", "*.txt"),
                                                          ("Archivos ZIP", "*.zip"),
                                                          ("Archivos de Excel", "*.xlsx"),
                                                          ("Archivos de PowerPoint", "*.pptx")])

        for archivo in archivos:
            shutil.copy(archivo, subcarpeta)
        self.cargar_archivos_existentes(nombre_apellido, listbox)

    def abrir_archivo(self, listbox):
        """Abre el archivo seleccionado en la listbox."""
        seleccion = listbox.curselection()
        if seleccion:
            archivo_seleccionado = listbox.get(seleccion[0])
            nombre_apellido = self.vista.tree.item(self.vista.tree.selection()[0])['values'][1]
            carpeta_principal = os.path.join(os.path.dirname(__file__), "archivos")
            subcarpeta = os.path.join(carpeta_principal, nombre_apellido)
            ruta_archivo = os.path.join(subcarpeta, archivo_seleccionado)

            try:
                os.startfile(ruta_archivo)  # Windows-specific
            except Exception as e:
                messagebox.showerror("Error", f"No se puede abrir el archivo: {e}")