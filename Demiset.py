import os
import time
import matplotlib.pyplot as plt
from Applications.AudioProcessing import AudioProcessing
from Applications.NoiseReducer import NoiseReducer
from Applications.RemoteFileDownloader import RemoteFileDownloader
from Applications.SilenceRemover import SilenceRemover
from Applications.VoiceExtractor import VoiceExtractor
from Applications.Zipper import Zipper
import zipfile

def main():
    input_folder = "Test"
    input_url = 'https://www.youtube.com/watch?v=RzJ3QjBsqM0'
    output_folder = "Test\Outputs"
    noise_threshold = 50 
    ms_split = 15000 
    enhance_audio = True
        
    remote_file_downloader = RemoteFileDownloader()
    audio_processing = AudioProcessing()
    noise_reducer = NoiseReducer()
    voice_extractor = VoiceExtractor()
    silence_remover = SilenceRemover()
    zipper = Zipper()

    # Diccionario para almacenar los tiempos de cada paso
    tiempo_por_paso = {}

    start_time = time.time()
    # Descargar archivo remoto
    ruta_archivo_descargado = remote_file_downloader.download(input_url, input_folder)
    if ruta_archivo_descargado.endswith('.zip'):
        # Obtener la ruta del directorio donde se extraerá el archivo ZIP
        output_directory = os.path.dirname(ruta_archivo_descargado)
        # Extraer el archivo ZIP en el mismo directorio
        with zipfile.ZipFile(ruta_archivo_descargado, 'r') as zip_ref:
            zip_ref.extractall(output_directory)
    tiempo_por_paso["Descarga remota"] = time.time() - start_time
    
    start_time = time.time()
    # Combinar todos los audios en un solo archivo
    ruta_audio_combinado = audio_processing.combine_audio(input_folder, output_folder)
    tiempo_por_paso["Combinación de audio"] = time.time() - start_time

    start_time = time.time()
    # Extraer la voz del audio
    ruta_audio_voz = voice_extractor.extract_vocals(ruta_audio_combinado, output_folder)
    tiempo_por_paso["Extracción de voz"] = time.time() - start_time

    start_time = time.time()
    if noise_threshold > 0:
        # Reducir ruido del audio
        ruta_audio_sin_ruido = noise_reducer.reduce_noise(ruta_audio_voz, output_folder, noise_threshold)
        tiempo_por_paso["Reducción de ruido"] = time.time() - start_time
    else:
        ruta_audio_sin_ruido = ruta_audio_voz
        
    start_time = time.time()
    # Eliminar silencios del audio procesado
    ruta_sin_silencio = silence_remover.remove_silence(ruta_audio_sin_ruido, output_folder)
    tiempo_por_paso["Eliminación de silencio"] = time.time() - start_time

    start_time = time.time()
    # Mejorar la calidad del audio
    if enhance_audio:
        # Mejorar la calidad del audio
        ruta_audio_mejorado = audio_processing.enhance_audio(ruta_sin_silencio, output_folder)
        tiempo_por_paso["Mejora de audio"] = time.time() - start_time
    else:
        ruta_audio_mejorado = ruta_sin_silencio

    start_time = time.time()
    # Dividir archivo en audios de 15 segundos
    output_folder_dataset = os.path.join(output_folder, "dataset")
    ruta_audio_dividido = audio_processing.split_audio(ruta_audio_mejorado, output_folder_dataset, ms_split)
    tiempo_por_paso["División de audio"] = time.time() - start_time

    start_time = time.time()
    # Comprimir dataset en un zip
    ruta_dataset_comprimido = zipper.zip_files(ruta_audio_dividido, "dataset.zip")
    tiempo_por_paso["Compresión de dataset"] = time.time() - start_time

    # Mostrar el gráfico
    plt.figure(figsize=(10, 6))
    plt.bar(tiempo_por_paso.keys(), tiempo_por_paso.values(), color='skyblue')
    plt.xlabel('Proceso')
    plt.ylabel('Tiempo (segundos)')
    plt.title('Tiempo de ejecución por procesos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
