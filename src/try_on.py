import cv2
import numpy as np
from detector import detectar_pose, obter_coordenadas_chave
from enum import Enum
from deepfake_generator import refinar_imagem_deepfake
import os

def carregar_imagem_com_alpha(caminho_imagem):
    """Carrega uma imagem, suportando canais de transparência (alpha)."""
    img = cv2.imread(caminho_imagem, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Erro ao carregar imagem: {caminho_imagem}")
        return None
    
    if img.shape[2] == 4:
        # Imagem com canal alpha (PNG)
        return img
    else:
        # Imagem sem canal alpha (JPG)
        # Adiciona um canal alpha opaco (todos 255)
        b, g, r = cv2.split(img)
        alpha = np.ones(b.shape, dtype=b.dtype) * 255
        return cv2.merge((b, g, r, alpha))

class TipoRoupa(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    FULL = "full"

def aplicar_roupa(imagem_pessoa_path, imagem_roupa_path, tipo_roupa: TipoRoupa):
    """
    Aplica a imagem da roupa na imagem da pessoa usando detecção de pose e segmentação.
    
    Args:
        imagem_pessoa_path (str): Caminho para a imagem da pessoa.
        imagem_roupa_path (str): Caminho para a imagem da roupa (deve ser PNG com transparência).
        tipo_roupa (TipoRoupa): Tipo de roupa (TOP, BOTTOM, FULL).
        
    Returns:
        np.array: Imagem resultante com a roupa aplicada.
    """
    
    # 1. Detecção de Pose e Segmentação
    imagem_pessoa_bgr = cv2.imread(imagem_pessoa_path)
    if imagem_pessoa_bgr is None:
        print("Erro: Imagem da pessoa não encontrada.")
        return None
        
    # Reutilizando a função de detecção para obter os landmarks
    _, landmarks = detectar_pose(imagem_pessoa_path)
    if not landmarks:
        print("Erro: Não foi possível detectar a pose da pessoa.")
        return imagem_pessoa_bgr

    coordenadas = obter_coordenadas_chave(landmarks)
    h, w, _ = imagem_pessoa_bgr.shape
    
    # Converte as coordenadas normalizadas (0-1000) para pixels
    def to_pixel(coord):
        return (int(coord[0] * w / 1000), int(coord[1] * h / 1000))

    ombro_esq = to_pixel(coordenadas['ombro_esq'])
    ombro_dir = to_pixel(coordenadas['ombro_dir'])
    quadril_esq = to_pixel(coordenadas['quadril_esq'])
    quadril_dir = to_pixel(coordenadas['quadril_dir'])
    
    # 2. Carregar e Preparar Imagem da Roupa
    roupa_img_rgba = carregar_imagem_com_alpha(imagem_roupa_path)
    if roupa_img_rgba is None:
        return imagem_pessoa_bgr
        
    h_roupa, w_roupa, _ = roupa_img_rgba.shape
    
    # 3. Definir a Área de Aplicação (Pontos de Destino)
    # Pontos de destino na imagem da pessoa (em pixels)
    pontos_destino = np.float32([
        ombro_esq,
        ombro_dir,
        quadril_dir,
        quadril_esq
    ])
    
    # Pontos de origem na imagem da roupa (assumindo que a roupa está em uma pose frontal)
    pontos_origem = np.float32([
        [0, 0], # Canto superior esquerdo (ombro esquerdo)
        [w_roupa - 1, 0], # Canto superior direito (ombro direito)
        [w_roupa - 1, h_roupa - 1], # Canto inferior direito (quadril direito)
        [0, h_roupa - 1] # Canto inferior esquerdo (quadril esquerdo)
    ])
    
    # 4. Transformação de Perspectiva (Warp)
    M = cv2.getPerspectiveTransform(pontos_origem, pontos_destino)
    roupa_warp = cv2.warpPerspective(roupa_img_rgba, M, (w, h))
    
    # 5. Mistura (Blending)
    b_roupa, g_roupa, r_roupa, alpha_roupa = cv2.split(roupa_warp)
    
    # Normaliza o canal alpha para 0.0 a 1.0
    alpha_roupa = alpha_roupa.astype(float) / 255
    
    # Cria a imagem da roupa em BGR
    roupa_bgr = cv2.merge((b_roupa, g_roupa, r_roupa))
    
    # Inverte o alpha (para a área da pessoa que não será coberta pela roupa)
    alpha_inv = 1.0 - alpha_roupa
    
    # Multiplica a imagem da pessoa pela máscara invertida (mantém a área da pessoa)
    for c in range(0, 3):
        imagem_pessoa_bgr[:, :, c] = (alpha_inv * imagem_pessoa_bgr[:, :, c] +
                                      alpha_roupa * roupa_bgr[:, :, c])
                                      
    # 6. Refinamento Deepfake (Simulação)
    imagem_refinada = refinar_imagem_deepfake(imagem_pessoa_bgr)
    
    return imagem_refinada

if __name__ == "__main__":
    # Exemplo de uso para teste
    
    # Simulação de caminhos
    pessoa_path = "/home/ubuntu/virtual_try_on/imagens/pessoas/modelo1.jpg"
    roupa_path = "/home/ubuntu/virtual_try_on/imagens/roupas/camiseta_vermelha.png"
    
    # Cria uma imagem de pessoa placeholder para teste (deve ser substituída por uma imagem real)
    if not os.path.exists(pessoa_path):
        h, w = 600, 400
        img_pessoa = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.putText(img_pessoa, "IMAGEM DE PESSOA AQUI", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite(pessoa_path, img_pessoa)
        print(f"Imagem de pessoa placeholder criada em: {pessoa_path}")

    # Executa a aplicação da roupa
    imagem_final = aplicar_roupa(pessoa_path, roupa_path, TipoRoupa.TOP)
    
    if imagem_final is not None:
        output_path = "/home/ubuntu/virtual_try_on/resultado_try_on.jpg"
        cv2.imwrite(output_path, imagem_final)
        print(f"Resultado salvo em: {output_path}")
    else:
        print("Falha na aplicação da roupa.")
