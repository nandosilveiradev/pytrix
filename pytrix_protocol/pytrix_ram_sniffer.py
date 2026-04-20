#pytrix_ram_sniffer.py
import os
import re

def ram_to_file(pid, output_file):
    maps_path = f"/proc/{pid}/maps"
    mem_path = f"/proc/{pid}/mem"
    
    try:
        with open(maps_path, 'r') as maps_file:
            with open(mem_path, 'rb', 0) as mem_file:
                with open(output_file, 'w') as out:
                    for line in maps_file.readlines():
                        if 'rw-p' in line:
                            parts = line.split()
                            start, end = [int(x, 16) for x in parts[0].split('-')]
                            mem_file.seek(start)
                            try:
                                chunk = mem_file.read(end - start)
                                strings = re.findall(b'[\x20-\x7E]{10,}', chunk)
                                for s in strings:
                                    out.write(s.decode('utf-8', errors='ignore') + '\n')
                            except: continue
        print(f"✅ Dump concluído: {output_file}")
    except PermissionError:
        print("❌ Roda como root, patrão!")

# pgrep ollama pra pegar o PID