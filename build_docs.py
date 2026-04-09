import pdoc
from pathlib import Path
import sys
import os

def generate_docs():
    # Garante que o diretório atual está no PATH do Python
    current_dir = Path(__file__).parent.absolute()
    sys.path.append(str(current_dir))
    
    output_dir = current_dir / "docs"
    
    # Configurações para evitar erro de browser e focar nos arquivos locais
    try:
        # Mudamos de '.' para o nome da pasta ou lista de arquivos
        pdoc.pdoc(current_dir, output_directory=output_dir)
        print(f"✅ Sucesso! Documentação gerada em: {output_dir}")
    except Exception as e:
        print(f"❌ Erro ao gerar documentação: {e}")
        print("\n💡 Dica: Verifique se o arquivo 'app.py' tem erros de sintaxe")
        print("ou se você esqueceu de instalar alguma dependência que o 'app' usa.")

if __name__ == "__main__":
    generate_docs()





