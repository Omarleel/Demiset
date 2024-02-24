import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from Applications.AudioProcessing import AudioProcessing

class ParallelAudioProcessor:
    def __init__(self, temp_split_path, temp_processed_path):
        self.audio_processing = AudioProcessing()
        self.temp_split_path = temp_split_path
        self.temp_processed_path = temp_processed_path
        if not os.path.exists(self.temp_split_path):
                os.makedirs(self.temp_split_path)
        if not os.path.exists(self.temp_processed_path):
                os.makedirs(self.temp_processed_path)

    def process_in_parallel(self, input_audio_path, output_filename, output_audio_path, process_function, num_threads = 4):
        """
        Gestiona el procesamiento paralelo de archivos de audio.

        Args:
            input_audio_path (str): Ruta al archivo de audio de entrada.
            output_filename (str): Nombre del archivo de audio de salida.
            output_audio_path (str): Ruta para guardar el archivo de audio procesado.
            process_function (function): Función que procesa un segmento de audio.
            num_threads (int): Número de hilos a utilizar para el procesamiento paralelo.

        Returns:
            str or None: Ruta al archivo procesado si se ejecutó correctamente, None si ocurrió un error.
        """
        try:
            # Dividir el audio en segmentos de 60 segundos
            self.audio_processing.split_audio(input_audio_path, self.temp_split_path, 60000) # 60 segundos
            # Obtener la lista de archivos de segmento
            segment_files = os.listdir(self.temp_split_path)

            # Dividir la lista de archivos en partes iguales
            chunk_size = (len(segment_files) + num_threads - 1) // num_threads
            segment_chunks = [segment_files[i:i+chunk_size] for i in range(0, len(segment_files), chunk_size)]
            
            # Procesar los segmentos en paralelo usando el número de hilos especificado
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                for chunk in segment_chunks:
                    executor.map(process_function, chunk)
            
            # Combinar los segmentos procesados
            output_path = self.audio_processing.combine_audio(self.temp_processed_path, output_audio_path, output_filename)
            # Eliminar carpetas temporales        
            shutil.rmtree(self.temp_split_path)
            shutil.rmtree(self.temp_processed_path)        
            return output_path
        except Exception as e:
            print(f"Error al procesar el audio: {e}")
            return None
