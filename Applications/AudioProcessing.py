from concurrent.futures import ThreadPoolExecutor
import os
import ffmpeg
import librosa
from pydub import AudioSegment
import numpy as np
import torch
from scipy.signal import butter, filtfilt
import soundfile as sf
from numba import prange, jit

class AudioProcessing:
    def __init__(self):
         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def convert_to_mp3(self, input_audio_path, file):
        """
        Convierte un archivo de audio a formato MP3.

        Args:
            input_audio_path (str): Ruta que contiene el archivo de audio de entrada.
            file (str): Nombre del archivo de audio a convertir.

        Returns:
            str: Ruta al archivo de audio MP3 convertido si se ejecutó correctamente, None si ocurrió un error.
        """
        try:
            ts_file_path = os.path.join(input_audio_path, file)
            mp3_file_path = os.path.join(input_audio_path, file.replace(".ts", ".mp3").replace(".m4a", ".mp3"))
            # Convierte el archivo .ts o .m4a a .mp3
            stream = ffmpeg.input(ts_file_path)
            stream = ffmpeg.output(stream, mp3_file_path, loglevel='quiet')
            ffmpeg.run(stream, overwrite_output=True)
            os.remove(ts_file_path) # Elimina el archivo .ts o .m4a
            return mp3_file_path
        except Exception as e:
            print(f"Error al convertir {file} a MP3: {e}")
            return None

    def combine_audio(self, input_audio_path, output_audio_path, filename="combined_audio.wav"):
        """
        Combina múltiples archivos de audio en uno solo.

        Args:
            input_audio_path (str): Ruta que contiene los archivos de audio de entrada.
            output_audio_path (str): Ruta para guardar el archivo de audio combinado.
            filename (str): Nombre del archivo de audio combinado. Por defecto, se llama "combined_audio.wav".

        Returns:
            str: Ruta al archivo de audio combinado si se ejecutó correctamente, None si ocurrió un error.
        """
        try:
            if not os.path.exists(output_audio_path):
                os.makedirs(output_audio_path)
                
            with ThreadPoolExecutor() as executor:
                # Lista de archivos que deben convertirse a MP3
                files_to_convert = [file for file in os.listdir(input_audio_path) if file.endswith(".ts") or file.endswith(".m4a")]

                # Convierte los archivos a MP3 en paralelo
                mp3_paths = list(executor.map(lambda f: self.convert_to_mp3(input_audio_path, f), files_to_convert))
                # mp3_paths solo estará disponible si existen archivos tipo .ts o .m4a
                
            combined_audio = None
            for file in os.listdir(input_audio_path):
                audio_path = os.path.join(input_audio_path, file)
                if file.endswith(".mp3") or file.endswith(".wav") or file.endswith(".wma"):
                    audio = AudioSegment.from_file(audio_path)
                    if combined_audio is None:
                        combined_audio = audio
                    else:
                        combined_audio += audio
            
            if combined_audio:
                combine_path = os.path.join(output_audio_path, filename)
                combined_audio.export(combine_path, format="wav")
                return combine_path
            else:
                return None
        except Exception as e:
            print(f"Error al combinar los archivos de audio: {e}")
            return None
    
    def split_audio(self, input_audio_path, output_audio_path, time_ms=10000):
        """
        Divide un archivo de audio en segmentos de duración específica.

        Args:
            input_audio_path (str): Ruta al archivo de audio de entrada.
            output_audio_path (str): Directorio donde guardar los segmentos de audio divididos.
            time_ms (int): Duración de cada segmento en milisegundos. Por defecto, 10000 ms (10 segundos).

        Returns:
            str: Ruta al archivo de audio dvidido si se ejecutó correctamente, None si ocurrió un error.
        """
        try:
            if not os.path.exists(output_audio_path):
                os.makedirs(output_audio_path)
                
            audio = AudioSegment.from_file(input_audio_path)
            duration = len(audio)
            start = 0
            index = 1
            while start < duration:
                end = min(start + time_ms, duration)
                segment = audio[start:end]
                segment.export(os.path.join(output_audio_path, f"segment_{index}.wav"), format="wav")
                start = end
                index += 1
            
            return output_audio_path
        except Exception as e:
            print(f"Error al dividir el archivo de audio: {e}")
            return None
        
    def enhance_audio(self, input_audio_path, output_audio_path):
        """
        Mejora la calidad de un archivo de audio mediante filtrado y normalización.

        Args:
            input_audio_path (str): Ruta al archivo de audio de entrada.
            output_audio_path (str): Ruta donde se guardará el archivo de audio mejorado.

        Returns:
            str or None: Ruta al archivo de audio mejorado si se ejecutó correctamente, None si ocurrió un error.
        """
        try:
            if not os.path.exists(output_audio_path):
                os.makedirs(output_audio_path)
            
            # Verificar si el archivo de audio de entrada existe
            if not os.path.exists(input_audio_path):
                raise FileNotFoundError(f"No se encontró el archivo de audio de entrada '{input_audio_path}'.")

            # Cargar el archivo de audio
            audio_data, sample_rate = librosa.load(input_audio_path, sr=None)
            
            # Aplicar cancelación de eco adaptativa
            audio_data_no_echo = self.cancel_echo(audio_data, delay=100, mu=0.01)
            
            # Aplicar filtro paso-bajo para eliminar frecuencias no deseadas
            filtered_audio = self.low_pass_filter(audio_data_no_echo, sample_rate, cutoff_freq=5000)
            
            # Aplicar normalización de volumen
            normalized_audio = self.normalize_volume(filtered_audio)
            
            # Guardar el audio procesado
            output_filename = f"enhance_{os.path.basename(input_audio_path)}"
            output_path = os.path.join(output_audio_path, output_filename)
            sf.write(output_path, normalized_audio, sample_rate)
            print(f"Finalizando {input_audio_path}")
            return output_path

        except Exception as e:
            print(f"Error al mejorar el audio: {e}")
            return None

    
    def cancel_echo(self, audio_data, delay=100, mu=0.01):
        """
        Cancela el eco en el audio de forma adaptativa.

        Args:
            audio_data (ndarray): Datos de audio.
            delay (int): Retraso del eco en muestras.
            mu (float): Coeficiente de aprendizaje.

        Returns:
            ndarray: Audio con eco cancelado.
        """
        # Generar eco artificial
        echo = np.zeros_like(audio_data)
        echo[delay:] = audio_data[:-delay] * 0.8  # Ajustar el valor del eco según sea necesario

        # Restar eco del audio original de forma adaptativa
        return self._subtract_echo(audio_data, echo, delay, mu)
    
    @staticmethod
    @jit(parallel=True, nopython=True)
    def _subtract_echo(audio_data, echo, delay, mu):
        for i in prange(delay, len(audio_data)):
            audio_data[i] -= mu * echo[i-delay]

        return audio_data
        
    def low_pass_filter(self, audio_data, sample_rate, cutoff_freq=5000):
        """
        Aplica un filtro paso-bajo al audio.

        Args:
            audio_data (ndarray): Datos de audio.
            sample_rate (int): Tasa de muestreo del audio.
            cutoff_freq (int): Frecuencia de corte del filtro paso-bajo.

        Returns:
            ndarray: Audio filtrado.
        """
        nyquist_freq = 0.5 * sample_rate
        normal_cutoff = cutoff_freq / nyquist_freq
        b, a = butter(6, normal_cutoff, btype='low', analog=False)
        filtered_audio = filtfilt(b, a, audio_data)
        return filtered_audio
    
    def normalize_volume(self, audio_data):
        """
        Normaliza el volumen del audio.

        Args:
            audio_data (ndarray): Datos de audio.

        Returns:
            ndarray: Audio normalizado.
        """
        max_amp = np.max(np.abs(audio_data))
        normalized_audio = audio_data / max_amp
        return normalized_audio
        
    def get_audio_duration(self, audio_path):
        """
        Obtiene la duración de un archivo de audio en segundos.

        Args:
            audio_path (str): Ruta al archivo de audio.

        Returns:
            float: Duración del archivo de audio en segundos.
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            duration_seconds = audio.duration_seconds
            return duration_seconds
        except Exception as e:
            print(f"Error al obtener la duración del archivo de audio: {e}")
            return None