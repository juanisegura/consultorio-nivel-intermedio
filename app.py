from tkinter import Tk
from controlador import Controlador
from vista import Vista

if __name__ == "__main__":
    root = Tk()
    controlador = Controlador(None)  # Se inicializa sin vista
    vista = Vista(root, controlador)  # Se pasa el controlador a la vista
    controlador.vista = vista  # Se asigna la vista al controlador
    vista.iniciar()