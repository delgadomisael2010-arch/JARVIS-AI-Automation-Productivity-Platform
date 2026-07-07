import psutil
import requests
from cerebro import pensar
from core.falar import jarvis_falar

def obter_telemetria():

    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        try:
            clima_req = requests.get("https://wttr.in/Lisboa?format=%t+%C", timeout=2)
            clima = clima_req.text.strip() if clima_req.status_code == 200 else "Offline"
        except:
            clima = "Erro de Conexão"
    except:
        cpu, ram, clima = 0, 0, "Erro de Sistema"
    return cpu, ram, clima

def processar_comando_texto(texto, nivel_seguranca, caixa_chat):
    if not texto:
        return

    caixa_chat.insert("end", f"\n  TU (Nível {nivel_seguranca}) » {texto}\n", "user")
    if nivel_seguranca < 3 and any(palavra in texto.lower() for palavra in ["eliminar", "formatar", "acesso"]):
        resposta = "Lamento informar, mas o seu nível de acesso não permite comandos de sistema."
    else:
        resposta = pensar(texto)

    caixa_chat.insert("end", f"\n  JARVIS » {resposta}\n\n", "jarvis")
    caixa_chat.see("end")

def definir_status_seguranca(nivel):
    protocolos = {
        5: ("PROTOCOLO OMNIPOTENTE - ADMIN", "#00E5FF"),
        4: ("PROTOCOLO OPERACIONAL - OPERATOR", "#00FF99"),
        3: ("PROTOCOLO ANALÍTICO - ANALYST", "#FFD700"),
        2: ("PROTOCOLO LIMITADO - GUEST", "#0099DD"),
        1: ("ACESSO RESTRITO - BLOQUEADO", "#FF3366")
    }
    return protocolos.get(nivel, ("DESCONHECIDO", "#FFFFFF"))

