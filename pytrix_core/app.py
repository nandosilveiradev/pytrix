import subprocess
from pytrix_validator import PytrixValidator

def pytrix_main():
    px_xml_path = "dados.xml"
    
    try:
        # Tenta validar o XML
        px_val = PytrixValidator(px_xml_path)
        if not px_val.pytrix_executar_validacao():
            raise ValueError("XML Corrompido ou Malformado")
        
        px_dados = px_val.pytrix_finalizar()
        print("Pytrix: Dados carregados com sucesso.")

    except Exception as px_erro:
        print(f"\n[ALERTA PYTRIX] Interrompido por: {px_erro}")
        print("Invocando Brain Watcher para intervenção manual...")
        
        # O subprocess agora está importado corretamente
        # Ele vai pausar o Python e abrir o seu menu em C
        subprocess.run(["./pytrix_brain_watcher"])
        
        print("\nPytrix: Retornando do Cérebro. Verifique se o XML foi corrigido.")

if __name__ == "__main__":
    pytrix_main()