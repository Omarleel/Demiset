import os
import re
from urllib.parse import unquote
import requests
import streamlink
import ffmpeg
from pytube import YouTube

class RemoteFileDownloader:
    def __init__(self):
        pass
    
    def prepare_url(self, download_url):
        """
        Prepara la URL de descarga para garantizar que sea un enlace directo utilizable.

        Args:
            download_url (str): La URL original de descarga.

        Returns:
            str: La URL de descarga preparada.
        """
        try:
            # Patrón de expresión regular para enlaces
            patron_google_drive = r'https?://drive\.google\.com/file/d/.+/view(\?usp=sharing)?'
            patron_dropbox = r'https?://(www\.)?dropbox\.com/scl/.+'
            patron_twitch = r'^(?:https?://)?(?:www\.)?(?:twitch\.tv\/(?:[a-zA-Z0-9_]+\/clip\/|videos\/)?)([a-zA-Z0-9_]+)'
            patron_youtube = r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
            download_link = download_url

            # Verificar si la URL corresponde a un enlace de Google Drive
            if re.match(patron_google_drive, download_url):
                file_id_search = re.search(r'd/([a-zA-Z0-9_-]+)', download_url)
                if file_id_search:
                    file_id = file_id_search.group(1)
                    download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
            # Verificar si la URL corresponde a un enlace de Dropbox
            elif re.match(patron_dropbox, download_url):
                download_link = download_url.replace("?dl=0", "?dl=1")
            # Verificar si la URL corresponde a un enlace de Twitch
            elif re.match(patron_twitch, download_url):
                streams = streamlink.streams(download_url)
                if streams:
                    if 'audio' in streams:
                        stream_key = 'audio'
                    else:
                        stream_key = 'best'
                    selected_stream = streams[stream_key]
                    download_link = selected_stream.url
            elif re.match(patron_youtube, download_url):
                yt = YouTube(download_url)
                audio = yt.streams.filter(only_audio=True).first() # Obtener la secuencia de audio de mayor calidad disponible
                if audio:
                    download_link = audio.url
            else:
                pass

            return download_link
        except Exception as e:
            print(f"Error al preparar la URL de descarga: {e}")
            return None
    
    def download(self, download_url, output_path, output_filename=None):
        """
        Descarga un archivo desde una URL remota y lo guarda en el sistema de archivos local.

        Args:
            download_url (str): La URL del archivo a descargar.
            output_path (str): El directorio donde se guardará el archivo descargado.
            output_filename (str, opcional): El nombre del archivo descargado. Si es None, se utilizará el nombre de archivo original.

        Returns:
            str: La ruta al archivo descargado en el sistema de archivos local.
        """
        try:
            os.makedirs(output_path, exist_ok=True)
            # Envía una solicitud HTTP GET a la URL de descarga
            remote_download_url = self.prepare_url(download_url)
            response = requests.get(remote_download_url, stream=True, headers={'user-agent': 'Wget/1.16 (linux-gnu)'})
            response.raise_for_status()  # Lanza una excepción para códigos de estado 4xx o 5xx
            content_disposition = response.headers.get('content-disposition')
            if output_filename is None:
                if content_disposition:
                    # Extrae el nombre del archivo del encabezado si está presente
                    filename = re.findall('filename="(.+)"', content_disposition)
                    if filename:
                       output_filename = unquote(filename[0])
                else:
                    output_filename = 'file.ts'
            # Construye la ruta completa para el archivo de salida
            output_file_path = os.path.join(output_path, output_filename)

            if output_filename == 'file.ts':
                # Utiliza ffmpeg para descargar el archivo HLS
                ffmpeg.input(remote_download_url).output(output_file_path, loglevel='quiet').run(overwrite_output=True)
            else:
                # Si no es un archivo HLS escribe el contenido de la respuesta en el archivo de salida
                with open(output_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:  # Filtra los keep-alive nuevos chunks
                            f.write(chunk)
                            
            return output_file_path  # Devuelve la ruta al archivo descargado

        except Exception as e:
            print(f"Error al descargar el archivo desde {download_url}: {e}")
            return None
