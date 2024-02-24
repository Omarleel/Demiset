import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
from Applications.ParallelAudioProcessor import ParallelAudioProcessor

class SilenceRemover:
    def __init__(self):
        pass

    def remove_silence(self, input_audio_path, output_audio_path):
        """
        Elimina las partes silenciosas del audio y guarda el resultado.

        Args:
            input_audio_path (str): Ruta al archivo de audio de entrada.
            output_audio_path (str): Ruta para guardar el archivo de audio procesado.

        Returns:
            str or None: Ruta al archivo de audio procesado si se ejecutó correctamente, None si ocurrió un error.
        """
        try:
            if not os.path.exists(output_audio_path):
                os.makedirs(output_audio_path)

            temp_split_path = os.path.join(output_audio_path, "temp_split")
            temp_processed_path = os.path.join(output_audio_path, "temp_silences_removed")
            
            parallel_procesor = ParallelAudioProcessor(temp_split_path, temp_processed_path)
                
            # Función para procesar cada segmento en paralelo
            def process_segment(segment_file):
                # Cargar el archivo de audio de entrada
                sound = AudioSegment.from_file(os.path.join(temp_split_path, segment_file))

                # Dividir el audio en segmentos basados en las partes silenciosas
                audio_chunks = split_on_silence(sound,
                                                min_silence_len=100,  # Longitud mínima del silencio en milisegundos
                                                silence_thresh=sound.dBFS - 15,   # Umbral de silencio en dBFS
                                                keep_silence=30       # Mantener esta cantidad de silencio al principio y al final de cada segmento
                                                )
                processed_sound = sum(audio_chunks, AudioSegment.empty())
                output_filename = f"without_silence_{segment_file}"
                output_path = os.path.join(temp_processed_path, output_filename)
                processed_sound.export(output_path, format="wav")

            output_path = parallel_procesor.process_in_parallel(input_audio_path, f"without_silence_{os.path.basename(input_audio_path)}", output_audio_path, process_segment)
            return output_path

        except Exception as e:
            print(f"Error al procesar el audio: {e}")
            return None
