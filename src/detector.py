import cv2
import mediapipe as mp
import numpy as np

# Inicializa os módulos do MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def detectar_pose(caminho_imagem):
    """
    Detecta a pose e os pontos-chave (landmarks) de uma pessoa na imagem.

    Args:
        caminho_imagem (str): Caminho absoluto para a imagem da pessoa.

    Returns:
        tuple: (imagem_resultado, landmarks)
               imagem_resultado (np.array): Imagem com os pontos-chave desenhados.
               landmarks (list): Lista de objetos mp_pose.PoseLandmark.
    """
    try:
        # Carrega a imagem
        imagem = cv2.imread(caminho_imagem)
        if imagem is None:
            print(f"Erro: Não foi possível carregar a imagem em {caminho_imagem}")
            return None, None

        # Converte a imagem BGR para RGB
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        
        # Cria uma cópia para desenhar
        imagem_resultado = imagem.copy()
        
        # Inicializa o detector de pose
        with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=True,
            min_detection_confidence=0.5) as pose:

            # Processa a imagem
            resultados = pose.process(imagem_rgb)

            landmarks = []
            if resultados.pose_landmarks:
                # Desenha os pontos-chave na imagem
                mp_drawing.draw_landmarks(
                    imagem_resultado,
                    resultados.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                )
                landmarks = resultados.pose_landmarks.landmark
                
            return imagem_resultado, landmarks

    except Exception as e:
        print(f"Ocorreu um erro durante a detecção de pose: {e}")
        return None, None

def obter_coordenadas_chave(landmarks):
    """
    Extrai coordenadas específicas (ombros, quadris) dos landmarks.
    """
    if not landmarks:
        return None

    coordenadas = {}
    
    # Ombro Esquerdo (LEFT_SHOULDER) - índice 11
    coordenadas['ombro_esq'] = (
        int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * 1000),
        int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * 1000)
    )
    
    # Ombro Direito (RIGHT_SHOULDER) - índice 12
    coordenadas['ombro_dir'] = (
        int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * 1000),
        int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * 1000)
    )
    
    # Quadril Esquerdo (LEFT_HIP) - índice 23
    coordenadas['quadril_esq'] = (
        int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].x * 1000),
        int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].y * 1000)
    )
    
    # Quadril Direito (RIGHT_HIP) - índice 24
    coordenadas['quadril_dir'] = (
        int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x * 1000),
        int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y * 1000)
    )
    
    return coordenadas

if __name__ == "__main__":
    # Este módulo é usado por try_on.py
    print("Módulo detector de pose carregado.")
