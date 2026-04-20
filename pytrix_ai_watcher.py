import os
import time

def main():
    print("--- PYTRIX WATCHER (Suggestion & Compile Panel) ---")
    last_mtime = 0
    while True:
        # Monitora o .env ou o arquivo atual
        if os.path.exists(".env-px-code"):
            mtime = os.path.getmtime(".env-px-code")
            if mtime > last_mtime:
                print(">> Config updated. Reloading flags...")
                last_mtime = mtime
        time.sleep(1)

if __name__ == "__main__":
    main()