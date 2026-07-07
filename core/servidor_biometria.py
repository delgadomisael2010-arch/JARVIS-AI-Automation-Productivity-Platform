import threading
import time
import urllib.request
import urllib.error
import json
from PIL import Image
import pyqrcode
import customtkinter as ctk
from pyngrok import ngrok
from flask import Flask, render_template_string
from flask_socketio import SocketIO
import os
import os
from dotenv import load_dotenv

load_dotenv()

flask_app = Flask(__name__)
socketio = SocketIO(flask_app, cors_allowed_origins="*", async_mode='threading')
acesso_validado = False
evento_validado = threading.Event()

ADMIN_KEY_FILE = "admin_key.txt"
ADMIN_KEY_FILE2 = "admin_key2.txt"
NGROK_TOKEN = os.getenv("NGROK_TOKEN")


@flask_app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Jarvis Biometrics</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
            <style>
                body {
                    background: #000;
                    color: #00ffff;
                    text-align: center;
                    font-family: sans-serif;
                    padding-top: 50px;
                }
                .sensor-btn {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    border: 3px solid #00ffff;
                    background: none;
                    color: #00ffff;
                    font-size: 40px;
                    cursor: pointer;
                    box-shadow: 0 0 15px #00ffff;
                }
                #status {
                    margin-top: 25px;
                    color: #00ffff;
                }
            </style>
        </head>
        <body>
            <h1>SECURITY CHECK</h1>
            <p>Usa o sensor biométrico do dispositivo</p>
            <button class="sensor-btn" onclick="autenticarReal()">BIO</button>
            <div id="status">Aguardando...</div>

            <script>
                var socket = io();
                const CRED_KEY = 'jarvis_cred_id';

                async function autenticarReal() {
                    const status = document.getElementById('status');

                    if (!window.PublicKeyCredential) {
                        status.innerText = "Dispositivo incompatível.";
                        return;
                    }

                    const credIdGuardado = localStorage.getItem(CRED_KEY);

                    try {
                        if (!credIdGuardado) {
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

                            localStorage.setItem(CRED_KEY, rawId);
                            socket.emit('validar_biometria_hardware', { key: rawId });
                            status.innerHTML = "<b style='color:lime'>REGISTADO E AUTENTICADO!</b>";

                        } else {
                            status.innerText = "Coloca o dedo no sensor...";

                            const credIdBytes = Uint8Array.from(atob(credIdGuardado), c => c.charCodeAt(0));

                            const assertOptions = {
                                publicKey: {
                                    challenge: new Uint8Array([1,2,3,4,5,6]),
                                    allowCredentials: [{
                                        id: credIdBytes.buffer,
                                        type: "public-key",
                                        transports: ["internal"]
                                    }],
                                    userVerification: "required",
                                    timeout: 60000
                                }
                            };

                            const assertion = await navigator.credentials.get(assertOptions);
                            socket.emit('validar_biometria_hardware', { key: credIdGuardado });
                            status.innerHTML = "<b style='color:lime'>AUTENTICADO!</b>";
                        }

                    } catch (err) {
                        status.innerText = "Cancelado ou erro no sensor.";
                        console.error(err);
                    }
                }
            </script>
        </body>
        </html>
    ''')


@socketio.on('validar_biometria_hardware')
def validar_hardware(data):
    global acesso_validado
    chave_dispositivo = data.get('key')

    if not chave_dispositivo:
        print("✖ Nenhuma chave recebida.")
        return

    if not os.path.exists(ADMIN_KEY_FILE):
        with open(ADMIN_KEY_FILE, "w") as f:
            f.write(chave_dispositivo)
        acesso_validado = True
        evento_validado.set()
        print("★ BIOMETRIA PRINCIPAL REGISTADA!")
        return

    with open(ADMIN_KEY_FILE, "r") as f:
        chave_admin = f.read().strip()

    chave_admin2 = None
    if os.path.exists(ADMIN_KEY_FILE2):
        with open(ADMIN_KEY_FILE2, "r") as f:
            chave_admin2 = f.read().strip()

    if chave_dispositivo == chave_admin:
        acesso_validado = True
        evento_validado.set()
        print("✔ BIOMETRIA PRINCIPAL CONFIRMADA.")

    elif chave_admin2 and chave_dispositivo == chave_admin2:
        acesso_validado = True
        evento_validado.set()
        print("✔ BIOMETRIA SECUNDÁRIA CONFIRMADA.")
    else:
        print("✖ ACESSO NEGADO: Hardware não reconhecido.")


def _fechar_tuneis_via_api_rest():
    api_local = "http://127.0.0.1:4040/api/tunnels"

    try:
        req = urllib.request.Request(api_local)
        with urllib.request.urlopen(req, timeout=3) as resp:
            dados = json.loads(resp.read())
            tuneis = dados.get("tunnels", [])

        if not tuneis:
            print("[ngrok] Nenhum túnel ativo encontrado na API local.")
            return

        for t in tuneis:
            nome = t.get("name", "")
            url_delete = f"http://127.0.0.1:4040/api/tunnels/{nome}"
            try:
                del_req = urllib.request.Request(url_delete, method="DELETE")
                urllib.request.urlopen(del_req, timeout=3)
                print(f"[ngrok] Túnel '{nome}' encerrado via API REST.")
            except Exception as e:
                print(f"[ngrok] Erro ao encerrar túnel '{nome}': {e}")

        print("[ngrok] A aguardar libertação do endpoint remoto (4s)...")
        time.sleep(4)

    except Exception as e:
        print(f"[ngrok] API local indisponível (processo não estava ativo): {e}")


def _matar_processo_ngrok():
    try:
        ngrok.kill()
        print("[ngrok] Processo local terminado.")
    except Exception as e:
        print(f"[ngrok] Erro ao matar processo: {e}")
    time.sleep(1)


def link_qr(label_do_ecra):
    global acesso_validado
    acesso_validado = False
    evento_validado.clear()

    ngrok.set_auth_token(NGROK_TOKEN)
    _fechar_tuneis_via_api_rest()
    _matar_processo_ngrok()

    url_publica = None
    esperas = [2, 5, 8]

    for i, espera in enumerate(esperas):
        try:
            print(f"[ngrok] Tentativa {i + 1}/3 de criar túnel...")
            tunel = ngrok.connect(5000)
            url_publica = tunel.public_url
            print(f"[ngrok] ✔ Túnel ativo: {url_publica}")
            break
        except Exception as e:
            print(f"[ngrok] ✖ Falhou: {str(e)[:120]}")
            if i < len(esperas) - 1:
                print(f"[ngrok] A aguardar {espera}s antes de nova tentativa...")
                time.sleep(espera)

    if not url_publica:
        label_do_ecra.configure(
            image="",
            text=(
                "⚠  TÚNEL NGROK OCUPADO\n\n"
                "O endpoint anterior ainda está ativo\n"
                "nos servidores do ngrok.\n\n"
                "SOLUÇÃO:\n"
                "1. Vai a dashboard.ngrok.com\n"
                "2. Clica em 'Cloud Edge' → 'Endpoints'\n"
                "3. Termina o túnel ativo\n"
                "4. Fecha e abre a aplicação novamente"
            )
        )
        return

    qr = pyqrcode.create(url_publica)
    qr.png('Biometria.png', scale=10)

    img_aberta = Image.open('Biometria.png')
    imagem_ctk = ctk.CTkImage(light_image=img_aberta, dark_image=img_aberta, size=(250, 250))
    label_do_ecra.configure(image=imagem_ctk, text="")
    label_do_ecra.image = imagem_ctk

    threading.Thread(
        target=lambda: socketio.run(
            flask_app, port=5000,
            debug=False, use_reloader=False,
            allow_unsafe_werkzeug=True
        ),
        daemon=True
    ).start()


