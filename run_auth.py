# run_auth.py
import sys, webbrowser
from src.auth import build_auth_url, exchange_code_for_token

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("generate_url","exchange"):
        print("Uso:\n  python run_auth.py generate_url\n  python run_auth.py exchange <CODE>")
        sys.exit(1)

    if sys.argv[1] == "generate_url":
        url = build_auth_url("estado_teste_123")
        print("\n1) Abra esta URL no navegador e autorize o app:\n")
        print(url)
        webbrowser.open(url)
        print("\n2) Copie o valor de `code` da URL de redirect (ex.: `...?code=XYZ`).\n")
    else:
        code = sys.argv[2]
        print(f"🔧 Trocando código '{code}' por token...")
        try:
            token = exchange_code_for_token(code)
            print("\n✅ token.json atualizado:\n", token)
        except Exception as e:
            print("\n❌ Falha ao trocar código por token:", e)
            sys.exit(1)

if __name__=="__main__":
    main()
