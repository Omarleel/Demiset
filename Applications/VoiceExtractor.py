import os
import demucs.api
from Applications.AudioProcessing import AudioProcessing
from Applications.ParallelAudioProcessor import ParallelAudioProcessor

class VoiceExtractor:
    def __init__(self):
        self.audio_processing = AudioProcessing()
        # Inicializar el separador Demucs con el modelo predeterminado
        try:
            self.separator = demucs.api.Separator(model="htdemucs_ft", segment=6)
        except Exception as e:
            print(f"Error al inicializar el separador Demucs: {e}")

    def extract_vocals(self, input_audio_path, output_audio_path):
        """
        Extrae las vocales de un archivo de audio y guarda las pistas separadas.

        Args:
            input_audio_path (str): Ruta al archivo de audio de entrada.
            output_audio_path (str): Directorio donde guardar las pistas de audio separadas.

        Returns:
            str: Ruta al archivo de voz extraído si se ejecutó correctamente, None si ocurrió un error.
        """
        try:
            if not os.path.exists(output_audio_path):
                os.makedirs(output_audio_path)

            temp_split_path = os.path.join(output_audio_path, "temp_split")
            temp_processed_path = os.path.join(output_audio_path, "temp_voices")
            
            parallel_procesor = ParallelAudioProcessor(temp_split_path, temp_processed_path)

            # Función para procesar cada segmento en paralelo
            def process_segment(segment_file):
                segment_path = os.path.join(temp_split_path, segment_file)
                stem_output_path = os.path.join(temp_processed_path, f"vocals_{segment_file}")
                origin, separated = self.separator.separate_audio_file(segment_path)
                demucs.api.save_audio(separated["vocals"], stem_output_path, samplerate=self.separator.samplerate)

            output_path = parallel_procesor.process_in_parallel(input_audio_path, f"vocals_{os.path.basename(input_audio_path)}", output_audio_path, process_segment, 1)
            return output_path

        except Exception as e:
            print(f"Error al extraer las vocales del archivo de audio: {e}")
