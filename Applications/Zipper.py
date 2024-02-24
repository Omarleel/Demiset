import os
import zipfile

class Zipper:
    def __init__(self):
        pass

    def zip_files(self, directory, zip_filename):
        """
        Comprime todos los archivos de un directorio en un archivo .zip.

        Args:
            directory (str): Ruta al directorio que contiene los archivos.
            zip_filename (str): Nombre del archivo .zip de salida.

        Returns:
            str: Ruta completa del archivo .zip creado si se realiza con éxito, None en caso de error.
        """
        try:
            zip_path = os.path.join(directory, zip_filename)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(directory):  # Iterar solo sobre los archivos en el directorio
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path) and file != zip_filename:  # Verificar si es un archivo y no el zip
                        zipf.write(file_path, file)  # Escribir el archivo en el zip con su nombre sin ruta

            return zip_path
        except Exception as e:
            print(f"Error al comprimir archivos: {e}")
            return None
