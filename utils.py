import os
from tkinter import messagebox

def validar_campos(url, carpeta):
    """Verifica que el URL y la carpeta sean válidos."""
    if not url.strip() or not carpeta.strip():
        messagebox.showwarning("Campos incompletos", "Por favor, introduce una URL y selecciona una carpeta de destino.")
        return False

    if not os.path.isdir(carpeta):
        messagebox.showerror("Error de Carpeta", "La carpeta de destino seleccionada no existe o no es válida.")
        return False
    
    # Validación simple para asegurar que parece una URL
    if not url.lower().startswith(('http://', 'https://')):
        messagebox.showwarning("URL Inválida", "La URL debe empezar con 'http://' o 'https://'.")
        return False

    return True