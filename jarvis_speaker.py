import subprocess

def falar(texto):
    # O aplay toca direto no hardware
    comando = f'echo "{texto}" | piper --model pt_BR-faber-medium.onnx --output_raw | aplay -r 22050 -f S16_LE -t raw -'
    subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Exemplo: falar("Sistema carregado no root, Fernando.")