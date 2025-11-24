import cv2
import os
from database import get_session, Pessoa, Roupa, TipoRoupa
from try_on import aplicar_roupa
from sqlalchemy import select

# 1. Obter dados do banco de dados
session = get_session()
pessoa_stmt = select(Pessoa).where(Pessoa.nome == "Modelo 1")
roupa_stmt = select(Roupa).where(Roupa.nome == "Camiseta Azul")

pessoa = session.execute(pessoa_stmt).scalar_one_or_none()
roupa = session.execute(roupa_stmt).scalar_one_or_none()
session.close()

if not pessoa or not roupa:
    print("Erro: Pessoa ou Roupa de exemplo não encontrados no banco de dados.")
    exit()

# 2. Garantir que a imagem da roupa exista (cria uma simples se não existir)
if not os.path.exists(roupa.caminho_imagem):
    h_r, w_r = 300, 300
    img_roupa = np.zeros((h_r, w_r, 4), dtype=np.uint8)
    cv2.rectangle(img_roupa, (50, 50), (250, 250), (0, 255, 0, 255), -1) # Camiseta verde opaca
    cv2.imwrite(roupa.caminho_imagem, img_roupa)
    print(f"Imagem de roupa placeholder criada em: {roupa.caminho_imagem}")

# 3. Executar a aplicação da roupa
print(f"Aplicando '{roupa.nome}' em '{pessoa.nome}'...")
imagem_final = aplicar_roupa(pessoa.caminho_imagem, roupa.caminho_imagem, roupa.tipo)

# 4. Salvar o resultado
if imagem_final is not None:
    output_path = "/home/ubuntu/virtual_try_on/resultado_try_on_final.jpg"
    cv2.imwrite(output_path, imagem_final)
    print(f"\n--- SUCESSO ---")
    print(f"Resultado final salvo em: {output_path}")
else:
    print("\n--- FALHA ---")
    print("Não foi possível realizar o Try-On. Verifique se a imagem da pessoa é clara e se a detecção de pose funcionou.")
