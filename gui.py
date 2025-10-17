import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import yt_dlp
from downloader import descargar
from utils import validar_campos

class DownloaderApp:
    # --- CAMBIO 1: 'root' renombrado a 'master' para evitar el warning ---
    def __init__(self, master):
        self.root = master # Seguimos usando self.root internamente, pero el argumento es 'master'
        self.root.title("Descargador de videos")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        self.url_var, self.carpeta_var, self.tipo_var, self.custom_name_var = tk.StringVar(), tk.StringVar(), tk.StringVar(value="video"), tk.StringVar()
        self.mp4_var, self.mp4_meta_var = tk.BooleanVar(), tk.BooleanVar(value=False)
        self.webm_var, self.webm_meta_var = tk.BooleanVar(), tk.BooleanVar(value=False)
        self.mp3_var, self.mp3_meta_var = tk.BooleanVar(value=True), tk.BooleanVar(value=True)
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="URL:").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,2))
        self.entry_url = ttk.Entry(main_frame, textvariable=self.url_var)
        self.entry_url.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        self.entry_url.bind("<FocusOut>", self.iniciar_autocompletado_titulo)

        ttk.Label(main_frame, text="Carpeta:").grid(row=2, column=0, columnspan=3, sticky="w", pady=(0,2))
        self.entry_carpeta = ttk.Entry(main_frame, textvariable=self.carpeta_var)
        self.entry_carpeta.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Button(main_frame, text="Elegir...", command=self.elegir_carpeta).grid(row=3, column=2, sticky="e", padx=(5, 0))
        
        ttk.Label(main_frame, text="Nombre personalizado (se autocompleta desde la URL):").grid(row=4, column=0, columnspan=3, sticky="w", pady=(0,2))
        self.entry_custom_name = ttk.Entry(main_frame, textvariable=self.custom_name_var)
        self.entry_custom_name.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        # (El resto de la GUI se mantiene igual)
        opciones_frame = ttk.LabelFrame(main_frame, text="Opciones", padding=10)
        opciones_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=10)
        opciones_frame.columnconfigure(1, weight=1)
        tipo_frame = ttk.Frame(opciones_frame)
        tipo_frame.grid(row=0, column=0, rowspan=4, sticky="ns", padx=(0, 20))
        ttk.Label(tipo_frame, text="Tipo").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(tipo_frame, text="Video único", variable=self.tipo_var, value="video").grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(tipo_frame, text="Lista", variable=self.tipo_var, value="playlist").grid(row=2, column=0, sticky="w")
        ttk.Label(opciones_frame, text="Formato").grid(row=0, column=1, sticky="w")
        ttk.Label(opciones_frame, text="Añadir Metadatos").grid(row=0, column=2, sticky="n")
        ttk.Checkbutton(opciones_frame, text="Video MP4", variable=self.mp4_var).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(opciones_frame, variable=self.mp4_meta_var).grid(row=1, column=2, sticky="n", padx=30)
        ttk.Checkbutton(opciones_frame, text="Video WEBM", variable=self.webm_var).grid(row=2, column=1, sticky="w")
        ttk.Checkbutton(opciones_frame, variable=self.webm_meta_var).grid(row=2, column=2, sticky="n", padx=30)
        ttk.Checkbutton(opciones_frame, text="Audio MP3", variable=self.mp3_var).grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(opciones_frame, variable=self.mp3_meta_var).grid(row=3, column=2, sticky="n", padx=30)
        self.btn_descargar = ttk.Button(main_frame, text="Descargar", command=self.iniciar_descarga, style='Accent.TButton')
        self.btn_descargar.grid(row=7, column=0, columnspan=3, pady=15, ipady=5)
        self.style.configure('Accent.TButton', foreground='white', background='green', font=('Helvetica', 10, 'bold'))
        self.label_progreso = ttk.Label(main_frame, text="Esperando descarga...")
        self.label_progreso.grid(row=8, column=0, columnspan=3, pady=(10, 0))
        self.barra_progreso = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.barra_progreso.grid(row=9, column=0, columnspan=3, sticky="ew", pady=5)

    def elegir_carpeta(self):
        ruta = filedialog.askdirectory()
        if ruta: self.carpeta_var.set(ruta)
        
    # --- CAMBIO 2: 'event' renombrado a '_event' para indicar que no se usa ---
    def iniciar_autocompletado_titulo(self, _event=None):
        url = self.url_var.get().strip()
        if url.lower().startswith(('http://', 'https://')) and not self.custom_name_var.get():
            threading.Thread(target=self.autocompletar_titulo_thread, args=(url,)).start()

    def autocompletar_titulo_thread(self, url):
        try:
            self.root.after(0, self.entry_custom_name.config, {'state': 'disabled'})
            self.root.after(0, self.custom_name_var.set, "Obteniendo título...")
            ydl_opts = {'quiet': True, 'noplaylist': True, 'nocheckcertificate': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                titulo = info.get('title', '')
                self.root.after(0, self.custom_name_var.set, titulo)
        except Exception as e:
            print(f"No se pudo obtener el título: {e}")
            self.root.after(0, self.custom_name_var.set, "")
        finally:
            self.root.after(0, self.entry_custom_name.config, {'state': 'normal'})

    # (El resto de funciones no cambian)
    def iniciar_descarga(self):
        url, carpeta, custom_name = self.url_var.get().strip(), self.carpeta_var.get().strip(), self.custom_name_var.get().strip()
        if not validar_campos(url, carpeta): return
        formatos_a_descargar = {}
        if self.mp4_var.get(): formatos_a_descargar['mp4'] = self.mp4_meta_var.get()
        if self.webm_var.get(): formatos_a_descargar['webm'] = self.webm_meta_var.get()
        if self.mp3_var.get(): formatos_a_descargar['mp3'] = self.mp3_meta_var.get()
        if not formatos_a_descargar:
            messagebox.showwarning("Sin formato", "Selecciona al menos un formato.")
            return
        self.btn_descargar.config(state="disabled")
        self.barra_progreso['value'] = 0
        threading.Thread(target=self.proceso_descarga_thread, args=(url, carpeta, formatos_a_descargar, self.tipo_var.get(), custom_name)).start()

    def proceso_descarga_thread(self, url, carpeta, formatos, tipo, custom_name):
        try:
            descargar(url, carpeta, formatos, tipo, self, custom_name)
            messagebox.showinfo("Éxito", "Descargas completadas.")
        except Exception as e:
            error_info = f"{e.__class__.__name__}: {e}"
            messagebox.showerror("Error", f"Ocurrió un problema:\n\n{error_info}")
        finally:
            self.root.after(0, self.resetear_gui)

    def actualizar_progreso(self, texto, valor):
        self.label_progreso.config(text=texto)
        self.barra_progreso['value'] = valor

    def resetear_gui(self):
        self.btn_descargar.config(state="normal")
        self.label_progreso.config(text="Esperando descarga...")

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()