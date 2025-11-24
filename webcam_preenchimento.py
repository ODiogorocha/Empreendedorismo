import cv2
import mediapipe as mp
import numpy as np
import time

# Inicialização dos Módulos MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# --- CONFIGURAÇÕES ---
# 1. PONTOS DO POLÍGONO (Para o Tronco):
# Usaremos 4 pontos para formar um retângulo que cobre o tronco:
# 11: Ombro Esquerdo, 12: Ombro Direito, 24: Quadril Direito, 23: Quadril Esquerdo
PONTOS_TRONCO = [11, 12, 24, 23] 

# 2. Cor do Preenchimento (Azul)
COR_PREENCHIMENTO = (255, 0, 0) # Azul em BGR (Blue, Green, Red)
# --- FIM DAS CONFIGURAÇÕES ---

def preencher_area_na_webcam():
    # 1. Inicializa a captura da webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmera.")
        return

    # 2. Inicializa o modelo MediaPipe Pose
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1) as pose:
        
        tempo_anterior = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Ignorando frame vazio.")
                continue

            frame = cv2.flip(frame, 1) # Inverte para visualização espelho
            
            # Prepara o frame para o MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            
            # 3. Processa o frame para detecção de pose
            results = pose.process(frame_rgb)

            # Prepara o frame para desenhar
            frame_rgb.flags.writeable = True
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # 4. Cria a Máscara Poligonal
            if results.pose_landmarks:
                h, w, c = frame.shape
                
                # Lista para armazenar as coordenadas dos pontos do polígono
                pontos_poligono = []
                todos_pontos_encontrados = True

                for idx in PONTOS_TRONCO:
                    if idx < len(results.pose_landmarks.landmark):
                        landmark = results.pose_landmarks.landmark[idx]
                        
                        # Converte coordenadas normalizadas para pixels
                        cx, cy = int(landmark.x * w), int(landmark.y * h)
                        pontos_poligono.append([cx, cy])
                    else:
                        todos_pontos_encontrados = False
                        break # Se um ponto vital não for encontrado, aborta o polígono

                # Verifica se temos os 4 pontos necessários
                if todos_pontos_encontrados and len(pontos_poligono) == 4:
                    
                    # Converte a lista de pontos para o formato esperado pelo OpenCV (numpy array)
                    pts = np.array(pontos_poligono, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    
                    # 5. Cria uma camada transparente para o preenchimento (Mask)
                    overlay = frame.copy()
                    
                    # 6. Preenche o polígono na camada de sobreposição
                    # -1 preenche o polígono; True define que o polígono é fechado
                    cv2.fillPoly(overlay, [pts], COR_PREENCHIMENTO, lineType=cv2.LINE_AA)
                    
                    # 7. Mistura (Blend) a camada de sobreposição com o frame original
                    # Este blending suaviza a cor, tornando-a menos agressiva (alfa=0.4)
                    alfa = 0.4
                    frame = cv2.addWeighted(overlay, alfa, frame, 1 - alfa, 0)
                    
                    # Opcional: Desenha os pontos de volta no frame para visualização
                    for ponto in pontos_poligono:
                        cv2.circle(frame, (ponto[0], ponto[1]), 5, (0, 255, 255), cv2.FILLED)

            # 8. Exibir FPS (opcional)
            tempo_atual = time.time()
            fps = 1 / (tempo_atual - tempo_anterior)
            tempo_anterior = tempo_atual
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # 9. Exibir o frame e sair
            cv2.imshow('Webcam - Poligono Azul', frame)
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    # Libera os recursos
    cap.release()
    cv2.destroyAllWindows()

# Executar a função
if __name__ == '__main__':
    preencher_area_na_webcam()