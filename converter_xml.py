Aqui está um exemplo de script em Python que faz o que você pediu:
```python
import os
import git
# Define a pasta que deseja verificar
root_dir = '/path/to/directory'
# Inicializa o repositorio Git
repo = git.Repo()
# Loop through each file in the root directory
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        # Verifica se o arquivo não está com commit (i.e., não está rastrea[7D[K
rastreado pelo Git)
        if not repo.is_racked(os.path.join(dirpath, filename)):
            # Adiciona o arquivo ao staged (i.e., adiciona ao commit)
            repo.add([os.path.join(dirpath, filename)])
            # Cria um commit individual com base no conteúdo do arquivo
            with open(os.path.join(dirpath, filename), 'r') as f:
                file_contents = f.read()
            commit_message = f"Added {filename} with contents: {file_conten[12D[K
{file_contents[:100]}"
            repo.index.commit(commit_message)
```
Este script utiliza a biblioteca `git` para interagir com o repositório Git[3D[K
Git e a biblioteca `os` para iterar sobre os arquivos na pasta.
Ele faz o seguinte:
1. Define a pasta que deseja verificar (`root_dir`).
2. Inicializa o repositorio Git com `repo = git.Repo()`.
3. Loop through cada arquivo na pasta (usando `os.walk()` e `filenames`) e [K
para cada arquivo:
4. Verifica se o arquivo não está com commit (`repo.is_racked(os.path.join([30D[K
(`repo.is_racked(os.path.join(dirpath, filename))`). Se sim, adiciona o arq[3D[K
arquivo ao staged (`repo.add([os.path.join(dirpath, filename)])`).
5. Cria um commit individual com base no conteúdo do arquivo:
	* Abre o arquivo e lê o conteúdo (`with open(os.path.join(dirpath, filename[8D[K
filename), 'r') as f: file_contents = f.read()`).
	* Cria um mensagem de commit que descreve o arquivo e seu conteúdo (`commit[8D[K
(`commit_message = f"Added {filename} with contents: {file_contents[:100]}"[22D[K
{file_contents[:100]}"`).
	* Comita o arquivo com a mensagem criada (`repo.index.commit(commit_message[34D[K
(`repo.index.commit(commit_message)`).
Lembre-se de substituir `/path/to/directory` pelo caminho da pasta que você[4D[K
você deseja verificar.