import os
import json
import threading
import time
import urllib.request
import pyqrcode
from PIL import Image
from pyngrok import ngrok
from flask import Flask, render_template_string
from flask_socketio import SocketIO

NGROK_TOKEN = "3DMmg0eNoeaCSHAEFjI8rpRJLEp_7Dejc2z5ZfmHNHdFsEe8"
KEYS_FILE = "authorized_keys.json"

flask_app = Flask(__name__)
socketio = SocketIO(flask_app, cors_allowed_origins="*")
evento_registado = threading.Event()


def _carregar_chaves():
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except:
            pass
    return []


def _guardar_chave(nova_chave):
    chaves = _carregar_chaves()
    if nova_chave not in chaves:
        chaves.append(nova_chave)
        with open(KEYS_FILE, "w") as f:
            json.dump(chaves, f, indent=2)
        print(f"[keys] Chave adicionada. Total: {len(chaves)} dispositivo(s) autorizado(s).")
    else:
        print("[keys] Esta chave já estava registada.")


@flask_app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Registar Biometria</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
            <style>
                body {
                    background: #000;
                    color: #00ffff;
                    text-align: center;
                    font-family: sans-serif;
                    padding-top: 60px;
                }
                h1 { font-size: 1.5em; color: #FFD700; }
                p { color: #0099DD; }
                .sensor-btn {
                    width: 140px;
                    height: 140px;
                    border-radius: 50%;
                    border: 3px solid #FFD700;
                    background: none;
                    color: #FFD700;
                    font-size: 44px;
                    cursor: pointer;
                    box-shadow: 0 0 20px #FFD700;
                    margin-top: 30px;
                }
                #status { margin-top: 30px; font-size: 1.1em; }
            </style>
        </head>
        <body>
            <h1>◈ REGISTAR NOVO DISPOSITIVO ◈</h1>
            <p>Carrega no botão e usa o sensor biométrico</p>
            <button class="sensor-btn" onclick="registar()">BIO</button>
            <div id="status" style="color:#00ffff">A aguardar...</div>

            <script>
                var socket = io();

                // Limpa sempre o localStorage para forçar novo registo
                localStorage.removeItem('jarvis_cred_id');

                async function registar() {
                    const status = document.getElementById('status');

                    if (!window.PublicKeyCredential) {
                        status.innerText = "Dispositivo não suporta WebAuthn.";
                        return;
                    }

                    try {
                        status.innerText = "A registar biometria...";

                        const options = {
                            publicKey: {
                                challenge: new Uint8Array([1,2,3,4,5,6]),
                                rp: { name: "Jarvis System" },
                                user: {
                                    id: new Uint8Array([1]),
                                    name: "admin",
                                    displayName: "Admin"
                                },
                                pubKeyCredParams: [{ alg: -7, type: "public-key" }],
                                authenticatorSelection: { authenticatorAttachment: "platform" },
                                timeout: 60000
                            }
                        };

                        const credential = await navigator.credentials.create(options);
                        const rawId = btoa(String.fromCharCode(...new Uint8Array(credential.rawId)));

                        // Guarda no localStorage para uso futuro neste dispositivo
                        localStorage.setItem('jarvis_cred_id', rawId);

                        socket.emit('guardar_nova_biometria', { key: rawId });
                        status.innerHTML = "<b style='color:lime'>✔ DISPOSITIVO REGISTADO!</b><br><small style='color:#aaa'>Podes fechar esta página.</small>";

                    } catch (err) {
                        status.innerHTML = "<b style='color:red'>Erro: " + err.message + "</b>";
                        console.error(err);
                    }
                }
            </script>
        </body>
        </html>
    ''')


@socketio.on('guardar_nova_biometria')
def guardar_nova_biometria(data):
    chave = data.get('key')
    if not chave:
        print("✖ Nenhuma chave recebida.")
        return

    _guardar_chave(chave)
    evento_registado.set()


def _fechar_tuneis():
    try:
        req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels")
        with urllib.request.urlopen(req, timeout=3) as resp:
            tuneis = json.loads(resp.read()).get("tunnels", [])
        for t in tuneis:
            nome = t.get("name", "")
            del_req = urllib.request.Request(
                f"http://127.0.0.1:4040/api/tunnels/{nome}", method="DELETE")
            urllib.request.urlopen(del_req, timeout=3)
            print(f"[ngrok] Túnel '{nome}' fechado.")
        time.sleep(3)
    except Exception as e:
        print(f"[ngrok] API local indisponível: {e}")
    try:
        ngrok.kill()
    except:
        pass
    time.sleep(1)


def main():
    print("=" * 50)
    print("  JARVIS — REGISTAR NOVO DISPOSITIVO")
    print("=" * 50)

    chaves_atuais = _carregar_chaves()
    print(f"[keys] Dispositivos já registados: {len(chaves_atuais)}")

    ngrok.set_auth_token(NGROK_TOKEN)
    _fechar_tuneis()

    try:
        tunel = ngrok.connect(5000)
        url = tunel.public_url
        print(f"[ngrok] ✔ URL: {url}")
    except Exception as e:
        print(f"[ngrok] ✖ Erro: {e}")
        print("\nFecha o túnel ativo em dashboard.ngrok.com e tenta novamente.")
        return

    qr = pyqrcode.create(url)
    qr.png('registo_qr.png', scale=10)
    print(f"\n✔ QR Code guardado em 'registo_qr.png'")
    print(f"✔ Ou abre no telemóvel: {url}\n")

    try:
        Image.open('registo_qr.png').show()
    except:
        pass

    threading.Thread(
        target=lambda: socketio.run(
            flask_app, port=5000,
            debug=False, use_reloader=False,
            allow_unsafe_werkzeug=True
        ),
        daemon=True
    ).start()

    print("A aguardar registo no telemóvel...")
    evento_registado.wait()
    print("\n✔ CONCLUÍDO!")

    chaves_final = _carregar_chaves()
    print(f"[keys] Total de dispositivos autorizados: {len(chaves_final)}")
    print(f"[keys] Ficheiro: {os.path.abspath(KEYS_FILE)}")

    input("\nPrime ENTER para sair...")
    ngrok.kill()


if __name__ == "__main__":
    main()

