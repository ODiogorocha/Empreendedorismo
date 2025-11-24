import cv2
import mediapipe as mp
import time

# Inicialização dos Módulos MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# --- CONFIGURAÇÕES ---
# 1. PONTOS DE INTERESSE:
# Escolha os índices dos keypoints que correspondem à sua roupa. 
# Exemplo abaixo: Ombro Esquerdo (11), Ombro Direito (12), Cotovelo Esquerdo (13), Cotovelo Direito (14).
# A lista completa tem 33 pontos.
PONTOS_ROUPA = [11, 12, 13, 14, 23, 24] # Ombro, Cotovelo, Quadril (apenas um exemplo)

# Cor e espessura do marcador
COR_MARCADOR = (0, 255, 0) # Verde em BGR
ESPESSURA_MARCADOR = 6 
# --- FIM DAS CONFIGURAÇÕES ---

def marcar_pontos_na_webcam():
    # 1. Inicializa a captura da webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmera.")
        return

    # 2. Inicializa o modelo MediaPipe Pose
    # model_complexity=1 oferece bom equilíbrio entre velocidade e precisão
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1) as pose:
        
        tempo_anterior = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Ignorando frame vazio.")
                continue

            # Inverte o frame horizontalmente para uma visualização mais natural (opcional)
            frame = cv2.flip(frame, 1)
            # Converte de BGR para RGB (MediaPipe prefere RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Torna o frame não-gravável para melhor performance
            frame_rgb.flags.writeable = False
            
            # 3. Processa o frame para detecção de pose
            results = pose.process(frame_rgb)

            # Torna o frame gravável novamente para desenhar
            frame_rgb.flags.writeable = True
            
            # Converte de volta para BGR (para exibição no OpenCV)
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # 4. Desenha os pontos de interesse
            if results.pose_landmarks:
                h, w, c = frame.shape
                
                for idx in PONTOS_ROUPA:
                    # Verifica se o ponto de interesse foi detectado
                    if idx < len(results.pose_landmarks.landmark):
                        landmark = results.pose_landmarks.landmark[idx]
                        
                        # Converte as coordenadas normalizadas (0 a 1) para pixels
                        cx, cy = int(landmark.x * w), int(landmark.y * h)
                        
                        # Desenha um círculo no ponto (marcando a roupa)
                        cv2.circle(frame, (cx, cy), ESPESSURA_MARCADOR, COR_MARCADOR, cv2.FILLED)

                # Opcional: Desenha todas as conexões (skeleton) para debug
                # mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # 5. Exibir FPS (opcional)
            tempo_atual = time.time()
            fps = 1 / (tempo_atual - tempo_anterior)
            tempo_anterior = tempo_atual
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # 6. Exibir o frame
            cv2.imshow('Webcam - Marcador de Pontos na Roupa', frame)
            
            # 7. Sair com a tecla 'q'
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    # Libera os recursos
    cap.release()
    cv2.destroyAllWindows()

# Executar a função
if __name__ == '__main__':
    marcar_pontos_na_webcam()