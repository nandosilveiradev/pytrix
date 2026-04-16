
import os
import subprocess
def verify_commit(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.startswith('.'):  # Ignora arquivos ocultos
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    contents = f.read()
                    commit_message = f"Added file {file} containing:\n{cont[18D[K
containing:\n{contents[:100]}..."
                    subprocess.run(['git', 'add', filepath])
                    subprocess.run(['git', 'commit', '-m', commit_message])[16D[K
commit_message])
if __name__ == '__main__':
    verify_commit(os.getcwd())
```
Here's what I changed:
1. Instead of using `os.listdir(directory)`, I used `os.walk(directory)` to[2D[K
to traverse the directory and its subdirectories.
2. I removed the `with open(filepath, r) as file:` line since it's not nece[4D[K
necessary. We can simply use `'r'` as the mode when opening the file.
3. I replaced `[git, add, filepath]` with `['git', 'add', filepath]`, and s[1D[K
similarly for the commit command, to avoid a syntax error.
4. I added single quotes around the git commands to make them valid Python [K
strings.
Note that you'll need to have `git` installed and available in your system'[7D[K
system's PATH for this script to work.