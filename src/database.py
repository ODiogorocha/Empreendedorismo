from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
import enum

# Define o caminho do banco de dados
DATABASE_URL = "sqlite:///./virtual_try_on.db"

# Cria a base para os modelos declarativos
Base = declarative_base()

# Enum para o tipo de roupa
class TipoRoupa(enum.Enum):
    TOP = "top"
    BOTTOM = "bottom"
    FULL = "full"

# Modelo para a tabela Pessoa
class Pessoa(Base):
    __tablename__ = "pessoas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    caminho_imagem = Column(String, unique=True, nullable=False)

# Modelo para a tabela Roupa
class Roupa(Base):
    __tablename__ = "roupas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    tipo = Column(Enum(TipoRoupa), nullable=False)
    caminho_imagem = Column(String, unique=True, nullable=False)

# Função para inicializar o banco de dados
def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    return engine

# Função para obter uma sessão de banco de dados
def get_session():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

if __name__ == "__main__":
    # Inicializa o banco de dados e cria as tabelas
    engine = init_db()
    print(f"Banco de dados SQLite inicializado em: {DATABASE_URL}")

    # Exemplo de uso: Adicionar dados
    session = get_session()

    # Adicionar Pessoas (se não existirem)
    if not session.query(Pessoa).filter_by(nome="Modelo 1").first():
        pessoa1 = Pessoa(nome="Modelo 1", caminho_imagem="/home/ubuntu/virtual_try_on/imagens/pessoas/modelo1.jpg")
        session.add(pessoa1)

    # Adicionar Roupas (se não existirem)
    if not session.query(Roupa).filter_by(nome="Camiseta Azul").first():
        roupa1 = Roupa(nome="Camiseta Azul", tipo=TipoRoupa.TOP, caminho_imagem="/home/ubuntu/virtual_try_on/imagens/roupas/camiseta_azul.png")
        session.add(roupa1)
    
    if not session.query(Roupa).filter_by(nome="Calça Jeans").first():
        roupa2 = Roupa(nome="Calça Jeans", tipo=TipoRoupa.BOTTOM, caminho_imagem="/home/ubuntu/virtual_try_on/imagens/roupas/calca_jeans.png")
        session.add(roupa2)

    session.commit()
    session.close()
    print("Dados de exemplo adicionados.")
