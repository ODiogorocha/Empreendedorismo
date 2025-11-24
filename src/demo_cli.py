import cv2
import os
from database import get_session, Pessoa, Roupa, TipoRoupa
from try_on import aplicar_roupa
from sqlalchemy import select

# Caminho base para as imagens
BASE_DIR = "/home/ubuntu/virtual_try_on/imagens"

def listar_pessoas(session):
    """Lista todas as pessoas no banco de dados."""
    pessoas = session.execute(select(Pessoa)).scalars().all()
    print("\n--- Pessoas Disponíveis ---")
    if not pessoas:
        print("Nenhuma pessoa encontrada.")
        return None
    for p in pessoas:
        print(f"ID: {p.id}, Nome: {p.nome}, Imagem: {os.path.basename(p.caminho_imagem)}")
    return pessoas

def listar_roupas(session):
    """Lista todas as roupas no banco de dados."""
    roupas = session.execute(select(Roupa)).scalars().all()
    print("\n--- Roupas Disponíveis ---")
    if not roupas:
        print("Nenhuma roupa encontrada.")
        return None
    for r in roupas:
        print(f"ID: {r.id}, Nome: {r.nome}, Tipo: {r.tipo.value}, Imagem: {os.path.basename(r.caminho_imagem)}")
    return roupas

def adicionar_pessoa(session, nome, caminho_imagem):
    """Adiciona uma nova pessoa ao banco de dados."""
    try:
        nova_pessoa = Pessoa(nome=nome, caminho_imagem=caminho_imagem)
        session.add(nova_pessoa)
        session.commit()
        print(f"Pessoa '{nome}' adicionada com sucesso.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar pessoa: {e}")

def adicionar_roupa(session, nome, tipo, caminho_imagem):
    """Adiciona uma nova roupa ao banco de dados."""
    try:
        tipo_enum = TipoRoupa(tipo.lower())
        nova_roupa = Roupa(nome=nome, tipo=tipo_enum, caminho_imagem=caminho_imagem)
        session.add(nova_roupa)
        session.commit()
        print(f"Roupa '{nome}' ({tipo}) adicionada com sucesso.")
    except ValueError:
        print(f"Erro: Tipo de roupa inválido. Use 'top', 'bottom' ou 'full'.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar roupa: {e}")

def main():
    session = get_session()
    
    print("--- Sistema de Virtual Try-On (Deepfake Simulado) ---")
    
    while True:
        print("\nOpções:")
        print("1. Listar Pessoas")
        print("2. Listar Roupas")
        print("3. Adicionar Pessoa (para teste)")
        print("4. Adicionar Roupa (para teste)")
        print("5. Realizar Try-On")
        print("6. Sair")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            listar_pessoas(session)
            
        elif escolha == '2':
            listar_roupas(session)
            
        elif escolha == '3':
            nome = input("Nome da Pessoa: ")
            caminho = input(f"Caminho da Imagem (ex: {BASE_DIR}/pessoas/minha_foto.jpg): ")
            adicionar_pessoa(session, nome, caminho)
            
        elif escolha == '4':
            nome = input("Nome da Roupa: ")
            tipo = input("Tipo (top/bottom/full): ")
            caminho = input(f"Caminho da Imagem (ex: {BASE_DIR}/roupas/camiseta.png): ")
            adicionar_roupa(session, nome, tipo, caminho)
            
        elif escolha == '5':
            pessoas = listar_pessoas(session)
            roupas = listar_roupas(session)
            
            if not pessoas or not roupas:
                print("Adicione pessoas e roupas antes de realizar o Try-On.")
                continue
                
            try:
                pessoa_id = int(input("ID da Pessoa para Try-On: "))
                roupa_id = int(input("ID da Roupa para Try-On: "))
            except ValueError:
                print("ID inválido.")
                continue
                
            pessoa = session.get(Pessoa, pessoa_id)
            roupa = session.get(Roupa, roupa_id)
            
            if not pessoa or not roupa:
                print("Pessoa ou Roupa não encontrados.")
                continue
                
            print(f"Aplicando '{roupa.nome}' em '{pessoa.nome}'...")
            
            imagem_final = aplicar_roupa(pessoa.caminho_imagem, roupa.caminho_imagem, roupa.tipo)
            
            if imagem_final is not None:
                output_path = "/home/ubuntu/virtual_try_on/resultado_try_on.jpg"
                cv2.imwrite(output_path, imagem_final)
                print(f"\n--- SUCESSO ---")
                print(f"Resultado salvo em: {output_path}")
                print("Você pode visualizar o resultado usando o comando: `cat /home/ubuntu/virtual_try_on/resultado_try_on.jpg`")
            else:
                print("\n--- FALHA ---")
                print("Não foi possível realizar o Try-On. Verifique se a imagem da pessoa é clara e se a detecção de pose funcionou.")
                
        elif escolha == '6':
            print("Saindo do sistema.")
            break
            
        else:
            print("Opção inválida. Tente novamente.")

    session.close()

if __name__ == "__main__":
    main()
