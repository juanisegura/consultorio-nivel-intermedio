import sqlite3
import os

class BaseDatos:
    """Clase para manejar la conexión y operaciones con la base de datos SQLite."""
    
    def __init__(self):
        """Inicializa la conexión con la base de datos y crea la tabla si no existe."""
        self.db_path = os.path.join(os.path.dirname(__file__), "consultorio.db")
        self.conectar()
        self.crear_tabla()

    def conectar(self):
        """Establece la conexión con la base de datos."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")

    def cerrar_conexion(self):
        """Cierra la conexión con la base de datos."""
        if self.conn:
            self.conn.close()

    def crear_tabla(self):
        """Crea la tabla de pacientes si no existe."""
        query = '''
        CREATE TABLE IF NOT EXISTS consultorio (
            dni TEXT PRIMARY KEY,
            nombre_apellido TEXT NOT NULL,
            telefono TEXT NOT NULL,
            obra_social TEXT NOT NULL,
            expediente_numero TEXT,
            juzgado_civil TEXT,
            abogado_demanda TEXT,
            abogado_demandada TEXT,
            fecha_nacimiento TEXT,
            edad INTEGER,
            domicilio TEXT
        )'''
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error al crear la tabla: {e}")

    def ejecutar_consulta(self, query, parametros=()):
        """Ejecuta una consulta SQL con manejo de errores."""
        try:
            self.cursor.execute(query, parametros)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al ejecutar consulta: {e}")
            return False

    def obtener_datos(self, query, parametros=()):
        """Ejecuta una consulta SELECT y devuelve los resultados."""
        try:
            self.cursor.execute(query, parametros)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener datos: {e}")
            return []

class Paciente:
    """Clase que representa a un paciente y sus datos en la base de datos."""

    def __init__(self, dni, nombre, telefono, obra_social, expediente=None, juzgado=None,
                 abogado_demanda=None, abogado_demandada=None, fecha_nacimiento=None,
                 edad=None, domicilio=None):
        """Inicializa un paciente con sus datos personales y judiciales."""
        self.dni = dni
        self.nombre = nombre
        self.telefono = telefono
        self.obra_social = obra_social
        self.expediente = expediente
        self.juzgado = juzgado
        self.abogado_demanda = abogado_demanda
        self.abogado_demandada = abogado_demandada
        self.fecha_nacimiento = fecha_nacimiento
        self.edad = edad
        self.domicilio = domicilio

    def guardar(self, db):
        """Guarda un nuevo paciente en la base de datos."""
        query = '''
        INSERT INTO consultorio (dni, nombre_apellido, telefono, obra_social, expediente_numero, juzgado_civil,
        abogado_demanda, abogado_demandada, fecha_nacimiento, edad, domicilio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        valores = (self.dni, self.nombre, self.telefono, self.obra_social, self.expediente, self.juzgado,
                   self.abogado_demanda, self.abogado_demandada, self.fecha_nacimiento, self.edad, self.domicilio)
        return db.ejecutar_consulta(query, valores)

    @staticmethod
    def obtener_todos(db):
        """Devuelve una lista con todos los pacientes."""
        query = "SELECT * FROM consultorio"
        return db.obtener_datos(query)

    @staticmethod
    def obtener_por_dni(db, dni):
        """Busca un paciente por su DNI."""
        query = "SELECT * FROM consultorio WHERE dni = ?"
        resultado = db.obtener_datos(query, (dni,))
        return resultado[0] if resultado else None

    def actualizar(self, db):
        """Actualiza los datos de un paciente en la base de datos."""
        query = '''
        UPDATE consultorio SET nombre_apellido = ?, telefono = ?, obra_social = ?, expediente_numero = ?,
        juzgado_civil = ?, abogado_demanda = ?, abogado_demandada = ?, fecha_nacimiento = ?, edad = ?, domicilio = ?
        WHERE dni = ?
        '''
        valores = (self.nombre, self.telefono, self.obra_social, self.expediente, self.juzgado, self.abogado_demanda,
                   self.abogado_demandada, self.fecha_nacimiento, self.edad, self.domicilio, self.dni)
        return db.ejecutar_consulta(query, valores)

    @staticmethod
    def eliminar(db, dni):
        """Elimina un paciente de la base de datos."""
        query = "DELETE FROM consultorio WHERE dni = ?"
        return db.ejecutar_consulta(query, (dni,))
