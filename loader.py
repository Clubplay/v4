import requests
from cryptography.fernet import Fernet
from pathlib import Path
import sys

LICENCA = "76C30179C7F7EBC1776C30179C7F7EBC16C76C30179C7F7EBC13017976C30179C7F7EBC1C7F7EBC1"
URL_CHAVE = f"https://painel.drmserve.com.br/api/get_key.php?licenca={LICENCA}"
ARQUIVO_ENC = "drm.py.enc"

def obter_chave():
    try:
        r = requests.get(URL_CHAVE, timeout=5)
        if r.status_code != 200:
            print("Servidor recusou a licença:", r.text)
            sys.exit(1)
        return r.text.strip().encode()
    except Exception as e:
        print("Falha ao conectar ao servidor:", e)
        sys.exit(1)

def main():
    encfile = Path(ARQUIVO_ENC)
    if not encfile.exists():
        print("???.")
        sys.exit(1)
        
    key = obter_chave()
    f = Fernet(key)

    try:
        encrypted = encfile.read_bytes()
        source = f.decrypt(encrypted).decode('utf-8')
    except Exception as e:
        print("?????:", e)
        sys.exit(1)

    module_globals = {"__name__": "__main__", "__file__": "drm.py"}
    exec(compile(source, "drm.py", "exec"), module_globals)

if __name__ == "__main__":
    main()
