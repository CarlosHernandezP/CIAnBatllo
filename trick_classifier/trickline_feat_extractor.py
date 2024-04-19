import os
import mediapipe as mp
import cv2
import numpy as np
import matplotlib.pyplot as plt
from time import time
import imageio
import glob


"""
MEJORA DEL RESULTADO DEL PROCESADO:

-Mayor contraste
-Plano vertical
-Colores más heterogéneos.
-Mayor resolución
-Mayores FPSs

"""

partes_cuerpo = {
    0: "Nariz",
    1: "Ojo Izquierdo Interno",
    2: "Ojo Izquierdo",
    3: "Ojo Izquierdo Externo",
    4: "Ojo Derecho Interno",
    5: "Ojo Derecho",
    6: "Ojo Derecho Externo",
    7: "Oreja Izquierda",
    8: "Oreja Derecha",
    9: "Boca Izquierda",
    10: "Boca Derecha",
    11: "Hombro Izquierdo",
    12: "Hombro Derecho",
    13: "Codo Izquierdo",
    14: "Codo Derecho",
    15: "Muñeca Izquierda",
    16: "Muñeca Derecha",
    17: "Meñique Izquierdo",
    18: "Meñique Derecho",
    19: "Índice Izquierdo",
    20: "Índice Derecho",
    21: "Pulgar Izquierdo",
    22: "Pulgar Derecho",
    23: "Cadera Izquierda",
    24: "Cadera Derecha",
    25: "Rodilla Izquierda",
    26: "Rodilla Derecha",
    27: "Tobillo Izquierdo",
    28: "Tobillo Derecho",
    29: "Talón Izquierdo",
    30: "Talón Derecho",
    31: "Índice del Pie Izquierdo",
    32: "Índice del Pie Derecho"
}

def coorVideoConVideoChatGpt(video_path):
    """Devuelve un tensor con los fotogramas y en cada fotograma, la matriz con las coordenadas de los puntos

    Args:
        nombre_video (_type_): Video en formato .mp4

    Returns:
        (np.array, int, int, int, list[int]): Tensor de dimension (len_fotogramas_video, 33, 3) y los fps del video, ancho y alto, una lista con los frames colapsados
    """
    print("-"*100)
    print("-"*100)

    # Inicializar MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # Cargar el video
    cap = cv2.VideoCapture(video_path)

    # Obtiene el fps del video. Redondea hacia abajo
    fps_video = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"El vídeo tiene {fps_video} FPSs.")

    # Obtener las dimensiones del video
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    tensor = []
    drop_frames = []

    # Iterar sobre cada fotograma del video
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir la imagen a RGB y procesarla con MediaPipe Pose
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        matriz = []
        # Dibujar los landmarks si están disponibles
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                # Convertir las coordenadas normalizadas a coordenadas de píxeles
                height, width, _ = frame.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                cv2.circle(frame, (cx, cy), 1, (0, 255, 0), -1)
                # Sacamos las cositas
                x = landmark.x
                y = landmark.y
                z = landmark.z if landmark.HasField('z') else None
                fila = [x, y, z]
                if not fila:  # Si la fila está vacía, usamos la última entrada registrada
                    fila = matriz[-1] if matriz else [0, 0, 0]  # Usar la última entrada si existe, sino usar [0,0,0]
                matriz.append(fila)

        if len(matriz) < 33:
            print('Inside second if')
            matriz = []

            for _ in range(33):
                matriz.append([0,0,0])
            drop_frames.append(i)
        tensor.append(matriz)
        
        # Mostrar el fotograma procesado
        
        #cv2.imshow('Pose Estimation', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        i += 1

    # Liberar los recursos
    cap.release()
    cv2.destroyAllWindows()
    return (np.array(tensor), fps_video, ancho, alto, drop_frames)

def coordenadasPunto(punto:int, tensor:np.array):
    """Devuelve un np.array (len_video, 3) que representa la secuencia del punto dado

    Args:
        punto (int): el punto que representa la parte del cuerpo. Está entre 0 y 32.
        tensor (np.array): El array de donde sacar los puntos

    Returns:
        np.array: La serie temporal del punto.
    """
    if punto not in range(33):
        raise Exception("No metiste un número entre 0 y 32")
    return tensor[:,punto,:]

def graficasEnCarpetas(tensor:np.array, carpeta_guardado:str):
    """Guarda las series temporales de cada punto en la carpeta indicada.

    Args:
        tensor (np.array): El tensor de donde se van a guardar los puntos.
        carpeta_guardado (str): La dirección dentro de la carpeta raíz donde se guardarán las 33 gráficas.
    """
    # Si no existe la carpeta indicada, se crea.
    if not os.path.exists(carpeta_guardado):
        os.makedirs(carpeta_guardado)
    
    for punto in range(32):
        coord_punto = coordenadasPunto(punto, tensor)
        coords_x = coord_punto[:,0]
        coords_y = coord_punto[:,1]
        coords_z = coord_punto[:,2]

        plt.plot(coords_x, color="blue", label="x")
        plt.plot(coords_y, color="red", label="y")
        plt.plot(coords_z, color="green", label="z")
        plt.xlabel("fotogramas")
        plt.legend()
        plt.title(f"Evolución {partes_cuerpo[punto]}")
        #plt.show()

        # Guardar la gráfica en la carpeta especificada
        nombre_archivo = f"{partes_cuerpo[punto]}.png"
        ruta_guardado = os.path.join(carpeta_guardado, nombre_archivo)
        plt.savefig(ruta_guardado)

        plt.close()  # Cerrar la figura para liberar recursos

def ploteaPunto(punto:int, tensor:np.array, carpeta_guardado:str = None):
    """Enseña una gráfica con la serie temporal del punto elegido del tensor elegido.
        Es posible guardarla en la ruta indicada.

    Args:
        punto (int): El punto entre 0 y 32.
        tensor (np.array): El tensor de donde se va a sacar la gráfica.
        carpeta_guardado (str): Es la direccion de la carpeta dentro de la carpeta raíz donde se guardará la gráfica si se desea guardar.
    """
    coord_punto = coordenadasPunto(punto, tensor)
    coords_x = coord_punto[:,0]
    coords_y = coord_punto[:,1]
    coords_z = coord_punto[:,2]

    plt.plot(coords_x, color="blue", label="x")
    plt.plot(coords_y, color="red", label="y")
    plt.plot(coords_z, color="green", label="z")
    plt.xlabel("fotogramas")
    plt.legend()
    plt.title(f"Evolución marca {partes_cuerpo[punto]}")
    if carpeta_guardado != None:
        # Si no existe la carpeta indicada, se crea.
        if not os.path.exists(carpeta_guardado):
            os.makedirs(carpeta_guardado)
        ruta_guardado = os.path.join(carpeta_guardado, partes_cuerpo[punto])
        plt.savefig(ruta_guardado)
    else:
        plt.show()

def crear_video_puntos(lista_matrices, nombre_video_salida, fps, ancho, alto):
    # Dimensiones del video
    #height, width = 720, 1280  # Puedes ajustar estas dimensiones según sea necesario
    # Ajustar las dimensiones del video para que sean divisibles por 16
    alto = alto + (16 - alto % 16) % 16
    ancho = ancho + (16 - ancho % 16) % 16

    # Lista para almacenar los fotogramas del video
    frames = []

    # Iterar sobre cada matriz de coordenadas (cada fotograma)
    for matriz in lista_matrices:
        # Crear un fondo blanco
        frame = np.ones((alto, ancho, 3), dtype=np.uint8) * 255

        # Dibujar los puntos en el fotograma
        for punto in matriz:
            x, y, _ = punto  # Ignoramos la tercera dimensión (z)

            # Escalar las coordenadas al tamaño del video
            x = int(x * ancho)
            y = int(y * alto)

            # Asegurar que las coordenadas estén dentro de los límites del video
            x = max(0, min(ancho - 1, x))
            y = max(0, min(alto - 1, y))


            cv2.circle(frame, (int(x), int(y)), 1, (0, 0, 255), -1)  # Dibujar un círculo rojo en cada punto

        # Agregar el fotograma a la lista de fotogramas
        frames.append(frame)

    # Guardar los fotogramas como un video usando imageio
    imageio.mimwrite(nombre_video_salida + '.mp4', frames, fps=fps)

def interpola(tensor:np.array, dropped_frames:list[int], coord:bool) -> np.array:
    """_summary_

    Args:
        tensor (np.array): El tensor sobre el que hará la interpolacion
        dropped_frames (list[int]): lista de los indices donde colapsa el frame
        coord (bool): True si se interpola la X, False si se interpola sobre la Y
    
    Returns:
        (np.array): El tensor interpolado con errores corregidos.
    """
    # Creamos el soporte de interpolación.
    soporte = [i for i in range(len(tensor)) if i not in dropped_frames]

    # Interpolamos en cada punto
    for i in range(33):
        
        # Sacamos la lista de los valores xyz de cada frame.
        valores_punto = coordenadasPunto(i, tensor)
        
        # Creamos el conjunto sobre el que se va a interpolar.
        conjunto_coord_verdaderas = [valores_punto[i] for i in soporte]


if __name__ == "__main__":
    inicio = time()
    
    # Get list of video filenames from the "videos_trickline" directory
    video_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'videos_trickline'))
    #import ipdb;ipdb.set_trace()
    video_files = glob.glob(os.path.join(video_folder, "**/*.mp4"), recursive=True)
    #import pdb;pdb.set_trace()
    """
    for video_file in video_files:
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        res, fpss, ancho, alto, drop_frames = coorVideoConVideoChatGpt(video_file)
        print(f"Dimension del array: {res.shape}")
        np.save(video_file+".npy", res)
        #graficasEnCarpetas(res, video_name)
        #crear_video_puntos(res, video_name, fpss, ancho, alto)
    """

    for tensor in glob.glob(os.path.join(video_folder, "*.npy"), recursive=True):
        tensor = np.load(tensor)


    fin = time()
    print(f"Ejecución finalizada en: {fin-inicio} segundos")