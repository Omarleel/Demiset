# Demiset - Documentación del programa

## Introducción
Demiset es una herramienta diseñada para la generación de datasets de audio. Incorpora tecnologías avanzadas para realizar diversas tareas de procesamiento de audio de manera eficiente. Algunas de sus características principales incluyen:

- Descarga remota de archivos desde plataformas como Google Drive, Dropbox, Twitch, Youtube y enlaces de descarga directa.
- Procesamiento de audio en bruto para mejorar su calidad y claridad.
- Supresión de ruido para eliminar interferencias no deseadas.
- Extracción de voz utilizando el modelo DEMUCS para separar la voz del fondo.
- Removedor de silencio para eliminar partes no deseadas de silencio en los archivos de audio.
- Procesamiento en paralelo para obtener resultados más rápidos al dividir y procesar múltiples segmentos de audio simultáneamente.

## Instalación de CUDA compatible con Torch
Ejecuta los siguientes comandos:
```bash
# Desinstala cualquier versión de Torch que tengas
pip uninstall torch torchaudio
# Limpia la caché de pip para evitar conflictos
pip cache purge
# Instala la versión específica de Torch compatible con CUDA 11.8:
pip install torch==2.0.0+cu118 torchaudio==2.0.1+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
```
## Pruebas
Para correr el programa, puedes ejecutar el siguiente conjunto de comandos:
```bash
# Clonar el repositorio y acceder a la carpeta del programa
git clone https://github.com/Omarleel/Demiset
# Accede al proyecto
cd Demiset
# Instala los requerimientos
pip install -r requirements.txt
# Ejecutar el script
py Demiset.py
```
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Omarleel/Demiset/blob/main/Demiset.ipynb)

## Problemas comunes 
### LLVM ERROR: Symbol not found: __svml_cosf8_ha
Si te encuentras con este error, puedes resolverlo siguiendo estos pasos: 
1. Abre el sitio web [https://www.dll-files.com/svml_dispmd.dll.html](https://www.dll-files.com/svml_dispmd.dll.html).
2. Haz clic en el botón rojo "Download" para descargar el archivo DLL.
3. Después de descargarlo, descomprime el archivo y encontrarás el archivo DLL dentro.
4. Copia el archivo DLL y pégalo en la carpeta "C:\Windows\System32" de tu computadora.