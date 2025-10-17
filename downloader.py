import os
import yt_dlp
import re

def progreso_hook(app):
    def hook(d):
        if d['status'] == 'downloading':
            porcentaje_str_raw = d.get('_percent_str', '0.0%').strip()
            match = re.search(r"(\d+\.?\d*)", porcentaje_str_raw)
            if match:
                porcentaje_num = float(match.group(1))
                total_bytes_str = d.get('_total_bytes_str', 'N/A')
                speed_str = d.get('_speed_str', 'N/A')
                texto_actual = app.label_progreso.cget("text").split(' - ')[0]
                texto_progreso = f"{texto_actual} - {porcentaje_num:.1f}% de {total_bytes_str} a {speed_str}"
                app.root.after(0, app.actualizar_progreso, texto_progreso, porcentaje_num)
        elif d['status'] == 'finished':
            texto_final = app.label_progreso.cget("text").split(' - ')[0] + " - Procesando y finalizando..."
            app.root.after(0, app.actualizar_progreso, texto_final, 100)
    return hook

def descargar(url, carpeta, formatos, tipo_descarga, app, custom_name):
    total_formatos = len(formatos)

    for i, (formato, add_meta) in enumerate(formatos.items()): # ESTA ES LA LÍNEA QUE DABA EL ERROR
        texto_estado = f"Descargando {formato.upper()} ({i+1}/{total_formatos})..."
        app.root.after(0, app.actualizar_progreso, texto_estado, 0)
        
        if custom_name:
            outtmpl_base = f'{custom_name}.%(ext)s'
        else:
            outtmpl_base = '%(artist,uploader)s - %(track,title)s.%(ext)s' if formato == 'mp3' else '%(title)s.%(ext)s'
        
        opciones = {
            'outtmpl': os.path.join(carpeta, outtmpl_base),
            'progress_hooks': [progreso_hook(app)],
            'noplaylist': tipo_descarga == "video",
            'nocheckcertificate': True,
            'no_color': True,
        }
        postprocessors = []
        if add_meta:
            opciones['writethumbnail'] = True
            postprocessors.extend([{'key': 'FFmpegMetadata', 'add_metadata': True}, {'key': 'EmbedThumbnail'}])

        if formato == "mp3":
            opciones.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '320'}] + postprocessors
            })
        else: # Para MP4 y WEBM
            if formato == "mp4":
                opciones['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else: # WEBM
                opciones['format'] = 'bestvideo[ext=webm]+bestaudio[ext=webm]/best'
            if postprocessors:
                opciones['postprocessors'] = postprocessors
        
        try:
            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])
        except Exception as e:
            error_msg = f"Error descargando {formato}: {e}"
            print(error_msg)
            app.root.after(0, app.actualizar_progreso, error_msg, 0)
            continue