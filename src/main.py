import cv2
import os
import glob
import numpy as np
from try_on import aplicar_roupa, TipoRoupa

# Define o caminho da pasta de roupas
PASTA_ROUPAS = "imagens/roupas"
CAMINHO_PESSOA_TESTE = "imagens/pessoas/pessoa_camera.jpg"
CAMINHO_RESULTADO = "resultado_deepfake_try_on.jpg"

def simular_captura_camera():
    """
    Simula a captura de uma imagem da câmera.
    
    Em um ambiente real, você usaria:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite(CAMINHO_PESSOA_TESTE, frame)
    
    Aqui, usamos uma imagem de placeholder ou uma imagem real fornecida pelo usuário.
    """
    if not os.path.exists(CAMINHO_PESSOA_TESTE):
        # Cria uma imagem de placeholder se a imagem da pessoa não existir
        h, w = 600, 400
        img_pessoa = 255 * np.ones((h, w, 3), dtype=np.uint8) # Fundo branco
        cv2.putText(img_pessoa, "IMAGEM DA CAMERA AQUI", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.imwrite(CAMINHO_PESSOA_TESTE, img_pessoa)
        print(f"AVISO: Imagem de pessoa placeholder criada em: {CAMINHO_PESSOA_TESTE}")
        print("Substitua esta imagem por uma foto sua (pessoa_camera.jpg) para testar o sistema.")
        
    return CAMINHO_PESSOA_TESTE

def listar_roupas_disponiveis():
    """Lista as roupas disponíveis na pasta de roupas."""
    roupas = []
    # Busca por arquivos PNG na pasta de roupas
    for caminho in glob.glob(os.path.join(PASTA_ROUPAS, "*.png")):
        nome_arquivo = os.path.basename(caminho)
        
        # Tenta inferir o tipo de roupa pelo nome do arquivo (simplificação)
        if "camiseta" in nome_arquivo or "top" in nome_arquivo or "blusa" in nome_arquivo:
            tipo = TipoRoupa.TOP
        elif "calca" in nome_arquivo or "bottom" in nome_arquivo:
            tipo = TipoRoupa.BOTTOM
        elif "vestido" in nome_arquivo or "full" in nome_arquivo:
            tipo = TipoRoupa.FULL
        else:
            tipo = TipoRoupa.TOP # Padrão
            
        roupas.append({
            "nome": nome_arquivo,
            "caminho": caminho,
            "tipo": tipo
        })
    return roupas

def main():
    print("--- Sistema de Virtual Try-On (Deepfake Simulado) ---")
    
    # 1. Simula a captura da imagem da pessoa
    caminho_pessoa = simular_captura_camera()
    print(f"Imagem da pessoa (câmera) pronta em: {caminho_pessoa}")
    
    # 2. Lista as roupas disponíveis
    roupas_disponiveis = listar_roupas_disponiveis()
    
    if not roupas_disponiveis:
        print("\nERRO: Nenhuma imagem de roupa (PNG) encontrada na pasta.")
        print(f"Por favor, adicione imagens de roupa em: {PASTA_ROUPAS}")
        return

    print("\n--- Roupas Disponíveis ---")
    for i, roupa in enumerate(roupas_disponiveis):
        print(f"[{i+1}] {roupa['nome']} (Tipo: {roupa['tipo'].value})")
        
    # 3. Seleção da roupa
    while True:
        try:
            escolha = input("Selecione o número da roupa para o Try-On (ou 's' para sair): ")
            if escolha.lower() == 's':
                return
            
            indice = int(escolha) - 1
            if 0 <= indice < len(roupas_disponiveis):
                roupa_selecionada = roupas_disponiveis[indice]
                break
            else:
                print("Seleção inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite o número da roupa.")

    print(f"\nIniciando Try-On com: {roupa_selecionada['nome']}")
    
    # 4. Executa o Try-On
    imagem_final = aplicar_roupa(
        caminho_pessoa, 
        roupa_selecionada['caminho'], 
        roupa_selecionada['tipo']
    )
    
    # 5. Salva e exibe o resultado
    if imagem_final is not None:
        cv2.imwrite(CAMINHO_RESULTADO, imagem_final)
        print(f"\n--- SUCESSO ---")
        print(f"Resultado (Deepfake Simulado) salvo em: {CAMINHO_RESULTADO}")
        print("Verifique o arquivo 'resultado_deepfake_try_on.jpg' na pasta do projeto.")
    else:
        print("\n--- FALHA ---")
        print("Não foi possível realizar o Try-On. Verifique se a imagem da pessoa é clara e se a detecção de pose funcionou.")

if __name__ == "__main__":
    main()
