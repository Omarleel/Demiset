import os
import numpy as np
from scipy.io import wavfile
import noisereduce as nr

class NoiseReducer:
    def __init__(self):
        pass
    
    def reduce_noise(self, input_audio_path, output_audio_path, umbral_reduction):
        """
        Reduce el ruido del archivo de audio y guarda el resultado.

        Args:
            input_audio_path (str): Ruta al archivo de audio de entrada.
            output_audio_path (str): Ruta para guardar el archivo de audio procesado.
            umbral_reduction (float): Porcentaje de reducción del ruido.

        Returns:
            str or None: Ruta al archivo de audio procesado si se ejecutó correctamente, None si ocurrió un error.
        """
        try:
            sr = 44100
            porcentaje_reduccion = float(umbral_reduction/100)
            rate, data = wavfile.read(input_audio_path)
            orig_shape = data.shape
            data = np.reshape(data, (2, -1))
            
            ruido_reducido = nr.reduce_noise(y=data, sr=sr, prop_decrease=porcentaje_reduccion)  
            
            # Crear el nombre de archivo de salida
            output_filename = f"without_noise_{os.path.basename(input_audio_path)}"

            # Guardar el archivo de audio procesado
            output_path = os.path.join(output_audio_path, output_filename)
            
            wavfile.write(output_path, sr, ruido_reducido.reshape(orig_shape))
            return output_path
        except Exception as e:
            print(f"Error al reducir el ruido del archivo de audio: {e}")
            return None
