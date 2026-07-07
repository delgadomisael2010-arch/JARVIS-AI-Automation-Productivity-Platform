import os
import sys
import subprocess
import threading
import time
import datetime
import requests
import webbrowser
import re
from dotenv import load_dotenv
import os

load_dotenv()
AGUARDANDO_CONFIRMACAO_FICHA = False
TEMA_ESTUDO_REMANESCENTE = ""


def aumentar_volume():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    atual = volume.GetMasterVolumeLevelScalar()
    novo = min(1.0, atual + 0.1)
    volume.SetMasterVolumeLevelScalar(novo, None)
    return f"Volume aumentado para {int(novo * 100)}%"


def diminuir_volume():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    atual = volume.GetMasterVolumeLevelScalar()
    novo = max(0.0, atual - 0.1)
    volume.SetMasterVolumeLevelScalar(novo, None)
    return f"Volume diminuído para {int(novo * 100)}%"


def silenciar():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    muted = volume.GetMute()
    volume.SetMute(not muted, None)
    return "Som desativado." if not muted else "Som ativado."


def obter_volume():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    atual = volume.GetMasterVolumeLevelScalar()
    return f"Volume atual: {int(atual * 100)}%"


def aumentar_brilho():
    try:
        import screen_brightness_control as sbc
        atual = sbc.get_brightness()[0]
        novo = min(100, atual + 10)
        sbc.set_brightness(novo)
        return f"Brilho aumentado para {novo}%"
    except:
        return "Não foi possível controlar o brilho neste dispositivo."


def diminuir_brilho():
    try:
        import screen_brightness_control as sbc
        atual = sbc.get_brightness()[0]
        novo = max(0, atual - 10)
        sbc.set_brightness(novo)
        return f"Brilho diminuído para {novo}%"
    except:
        return "Não foi possível controlar o brilho neste dispositivo."


APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "notepad": "notepad.exe",
    "calculadora": "calc.exe",
    "explorador": "explorer.exe",
    "vscode": r"C:\Users\aluno\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "spotify": r"C:\Users\aluno\AppData\Roaming\Spotify\Spotify.exe",
    "discord": r"C:\Users\aluno\AppData\Local\Discord\app-*\Discord.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "paint": "mspaint.exe",
    "terminal": "cmd.exe",
    "pycharm": r"C:\Program Files\JetBrains\PyCharm Community Edition*\bin\pycharm64.exe",
}


def abrir_aplicacao(nome):
    nome = nome.lower().strip()
    for chave, caminho in APPS.items():
        if chave in nome:
            try:
                subprocess.Popen(caminho, shell=True)
                return f"A abrir {chave}, senhor."
            except Exception as e:
                return f"Erro ao abrir {chave}: {e}"
    return f"Aplicação '{nome}' não encontrada na lista."


def listar_aplicacoes():
    lista = ", ".join(APPS.keys())
    return f"Posso abrir: {lista}."


def pesquisar_google(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"A pesquisar '{query}' no Google."


def pesquisar_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"A pesquisar '{query}' no YouTube."


def abrir_url(url):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"A abrir {url}."


def previsao_tempo(cidade="Lisboa"):
    try:
        url = f"https://wttr.in/{cidade}?format=4"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
        return "Não consegui obter a previsão do tempo."
    except:
        return "Erro ao aceder ao serviço de meteorologia."


def previsao_tempo_detalhada(cidade="Lisboa"):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt"
        geo = requests.get(geo_url, timeout=5).json()
        if not geo.get("results"):
            return f"Cidade '{cidade}' não encontrada."

        res = geo["results"][0]
        lat, lon = res["latitude"], res["longitude"]
        nome_cidade = res["name"]

        meteo_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&timezone=auto&forecast_days=3"
        )
        meteo = requests.get(meteo_url, timeout=5).json()
        atual = meteo["current"]
        diario = meteo["daily"]

        codigos = {
            0: "Céu limpo", 1: "Principalmente limpo", 2: "Parcialmente nublado",
            3: "Nublado", 45: "Nevoeiro", 61: "Chuva leve", 63: "Chuva moderada",
            65: "Chuva forte", 80: "Aguaceiros", 95: "Trovoada"
        }
        cond = codigos.get(atual["weathercode"], "Condição desconhecida")

        resposta = (
            f"🌍 {nome_cidade}\n"
            f"🌡 Temperatura: {atual['temperature_2m']}°C\n"
            f"💧 Humidade: {atual['relative_humidity_2m']}%\n"
            f"💨 Vento: {atual['wind_speed_10m']} km/h\n"
            f"☁ Condição: {cond}\n\n"
            f"📅 Próximos 3 dias:\n"
        )
        for i in range(3):
            data = diario["time"][i]
            tmax = diario["temperature_2m_max"][i]
            tmin = diario["temperature_2m_min"][i]
            chuva = diario["precipitation_sum"][i]
            resposta += f"  {data}: {tmin}°C — {tmax}°C  |  Chuva: {chuva}mm\n"

        return resposta.strip()
    except Exception as e:
        return f"Erro na previsão detalhada: {e}"


lembretes = []


def adicionar_lembrete(texto, minutes, callback_falar=None):
    def disparar():
        time.sleep(minutes * 60)
        msg = f"Lembrete: {texto}"
        lembretes_ativos = [l for l in lembretes if l["texto"] != texto]
        lembretes.clear()
        lembretes.extend(lembretes_ativos)
        if callback_falar:
            callback_falar(msg)
        print(f"⏰ {msg}")

    lembretes.append({"texto": texto, "minutos": minutes})
    threading.Thread(target=disparar, daemon=True).start()
    return f"Lembrete definido: '{texto}' em {minutes} minuto(s)."


def listar_lembretes():
    if not lembretes:
        return "Não há lembretes ativos, senhor."
    lista = "\n".join([f"• {l['texto']} (em {l['minutos']} min)" for l in lembretes])
    return f"Lembretes ativos:\n{lista}"


def cancelar_lembretes():
    lembretes.clear()
    return "Todos os lembretes foram cancelados."


def cancelar_lembrete_por_indice(indice):
    if not lembretes:
        return "Não há lembretes ativos para cancelar."
    try:
        indice = int(indice)
    except (ValueError, TypeError):
        return "Índice inválido. Diz um número, por exemplo: 'cancela lembrete 1'."
    if indice < 1 or indice > len(lembretes):
        return f"Índice inválido. Tens {len(lembretes)} lembrete(s) ativo(s)."
    removido = lembretes.pop(indice - 1)
    return f"Lembrete '{removido['texto']}' cancelado."


def info_sistema():
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disco = psutil.disk_usage('/')
    return (
        f"CPU: {cpu}%\n"
        f"RAM: {ram.percent}% ({ram.used // (1024 ** 2)}MB / {ram.total // (1024 ** 2)}MB)\n"
        f"Disco: {disco.percent}% usado ({disco.free // (1024 ** 3)}GB livres)"
    )


def hora_atual():
    agora = datetime.datetime.now()
    return f"São {agora.strftime('%H:%M')} do dia {agora.strftime('%d de %B de %Y')}."


def detetar_e_executar(texto, callback_falar=None):
    global AGUARDANDO_CONFIRMACAO_FICHA, TEMA_ESTUDO_REMANESCENTE
    t = texto.lower().strip()

    from core.cerebro import obter_nivel, limpar_memoria
    from core.relatorio import gerar_relatorio_pt

    nivel_atual = obter_nivel()

    if t == "cls":
        return "◈ TELA LIMPA. PROTOCOLOS DE INTERFACE REINICIADOS. ◈"
    if t == "cls-m":
        limpar_memoria()
        return "◈ MEMÓRIA VOLÁTIL E TELA LIMPAS. SISTEMA EM REPOUSO. ◈"

    if AGUARDANDO_CONFIRMACAO_FICHA:
        AGUARDANDO_CONFIRMACAO_FICHA = False
        if any(p in t for p in ["sim", "quero", "gera", "com certeza", "s", "executa", "podes", "bora", "pode ser"]):
            tema = TEMA_ESTUDO_REMANESCENTE

            if tema.lower() in ["explica", "ficha", "relatorio", "documento", "estudo"]:
                tema = "Introdução ao Python e Variáveis"

            tema_titulo = tema.upper()

            print(f"J.A.R.V.I.S » A contactar a IA para criar uma ficha exclusiva sobre '{tema}'...")

            try:
                from groq import Groq
                client_local = Groq(api_key=os.getenv("GROQ_API_KEY"))

                prompt_ficha = f"""
                Gera o conteúdo textual completo para uma ficha de estudo pedagógica e caderno de atividades sobre o conceito técnico de Programação/Python: '{tema}'.
                CRÍTICO: O foco total tem de ser técnico em Informática e Programação.
                O público-alvo são alunos do 10.º ano do ensino secundário/profissional (Linguagem de Programação Python).
                Usa uma linguagem muito simples, apelativa, acessível e clara.

                Estrutura o documento RIGOROSAMENTE com a seguinte ordem de secções:
                1. Um título mestre no início em MAIÚSCULAS: CADERNO DE ATIVIDADES E ESTUDO PRÁTICO - ASSUNTO: {tema_titulo}
                2. Um título em MAIÚSCULAS: INTRODUÇÃO SIMPLIFICADA (O QUE PRECISAS DE SABER)
                3. Um título em MAIÚSCULAS: RESUMO COMPLETO (EXPLICADO PASSO A PASSO)
                4. Um título em MAIÚSCULAS: EXEMPLO PRÁTICO E FÁCIL DE ENTENDER
                5. Um título em MAIÚSCULAS: O QUE DEVES FAZER VS O QUE DEVES EVITAR
                6. Um título em MAIÚSCULAS: QUESTÕES PARA TREINARES E SUBIRES DE NÍVEL
                   - SECÇÃO A: PERGUNTAS DE ESCOLHA MÚLTIPLA
                   - SECÇÃO B: DESAFIOS PRÁTICOS (PARA FAZERES NO PC)
                7. Termina com a linha exata em maiúsculas: ◈ ACADEMIA J.A.R.V.I.S. — MATERIAL DIDÁTICO DO SECUNDÁRIO ◈

                NOTAS CRÍTICAS DE FORMATAÇÃO:
                - NÃO uses rigorosamente nenhuma formatação em Markdown. O texto deve ser plano.
                - Usa as linhas de título de secção descritas estritamente em MAIÚSCULAS.
                """

                resposta_api = client_local.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt_ficha}],
                    max_tokens=1800
                )
                conteudo_ficha = resposta_api.choices[0].message.content

                nome_gerado = gerar_relatorio_pt(f"Ficha_Estudo_{tema.replace(' ', '_')}_10Ano", conteudo_ficha)
                return f"◈ PROTOCOLO DIDÁTICO DINÂMICO REGENERADO ◈\nO modelo pedagógico real sobre '{tema}' foi estruturado com sucesso no documento '{nome_gerado}'!"
            except Exception as e:
                return f"❌ [ERRO NO MOTOR DE GERAÇÃO]: {e}"
        elif any(p in t for p in ["não", "nao", "cancela", "rejeita", "esquece"]):
            return "Entendido, senhor. Procedimento de geração da ficha cancelado."

    # ======== MENU DE AJUDA ========
    if any(p in t for p in ["ajuda", "help", "comandos", "o que podes fazer", "lista de comandos"]):

        # A magia está aqui: Ele diz esta frase rapidamente em vez de ler o menu!
        if callback_falar:
            callback_falar("A carregar os protocolos e comandos disponíveis no ecrã, senhor.")

        cmds = ["=== COMANDOS J.A.R.V.I.S. ==="]
        cmds.append("• calc: [conta]         -> Calculadora rápida")
        cmds.append("• cls                   -> Limpar a tela")
        cmds.append("• cls-m                 -> Limpar a tela e a memória")
        if nivel_atual >= 2:
            cmds.append("• que horas são         -> Ver hora atual e data")
            cmds.append("• volume [subir/baixar] -> Controlar o som")
            cmds.append("• brilho [subir/baixar] -> Controlar o brilho")
            cmds.append("• abre [app]            -> Iniciar Chrome, VSCode, etc.")
            cmds.append("• lista de apps         -> Ver aplicações registadas")
            cmds.append("• pesquisa [termo]      -> Pesquisar no Google")
            cmds.append("• youtube [termo]       -> Pesquisar no YouTube")
            cmds.append("• tempo em [cidade]     -> Meteorologia real")
            cmds.append("• lembra-me de [algo]   -> Criar um lembrete")
            cmds.append("• estado do sistema     -> Ver CPU, RAM e Disco")
        if nivel_atual >= 3:
            cmds.append("• traduzir: [texto]     -> Tradutor de Idiomas")
            cmds.append("• resumir: [texto]      -> Resumidor de Textos")
            cmds.append("• email: [assunto]      -> Criar rascunho de email")
        if nivel_atual >= 4:
            cmds.append("• analisar: [código]    -> Analisador de Sintaxe")
        if nivel_atual >= 5:
            cmds.append("• relatorio: [tema]     -> Compilar Documento Word")
        cmds.append("=============================")
        return "\n".join(cmds)

    # ======== GERAÇÃO DIRETA DE RELATÓRIO (NOVO) ========
    if t.startswith("relatorio:") or t.startswith("relatório:"):
        tema = t.split(":", 1)[1].strip()
        if callback_falar:
            callback_falar(f"A compilar o documento sobre {tema}, senhor.")
        try:
            from groq import Groq
            client_local = Groq(api_key=os.getenv("GROQ_API_KEY"))
            resp = client_local.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user",
                           "content": f"Escreve um relatório extremamente detalhado sobre: {tema}. Formata com títulos em MAIÚSCULAS e usa tópicos."}],
                max_tokens=1500
            )
            conteudo = resp.choices[0].message.content
            nome_gerado = gerar_relatorio_pt(f"Relatorio_{tema.replace(' ', '_')}", conteudo)
            return f"Relatório técnico sobre '{tema}' gerado e guardado como '{nome_gerado}', senhor."
        except Exception as e:
            return f"Erro ao gerar relatório: {e}"

    # ======== HARDWARE E SISTEMA ========
    if any(p in t for p in ["aumenta o volume", "sobe o volume", "mais volume", "volume subir", "subir volume"]):
        return aumentar_volume()
    if any(p in t for p in ["diminui o volume", "baixa o volume", "menos volume", "volume baixar", "baixar volume"]):
        return diminuir_volume()
    if any(p in t for p in ["silencia", "muda o som", "sem som", "mute"]):
        return silenciar()
    if any(p in t for p in ["que volume", "volume atual", "quanto é o volume"]):
        return obter_volume()

    if any(p in t for p in ["aumenta o brilho", "mais brilho", "sobe o brilho", "brilho subir", "subir brilho"]):
        return aumentar_brilho()
    if any(p in t for p in ["diminui o brilho", "menos brilho", "baixa o brilho", "brilho baixar", "baixar brilho"]):
        return diminuir_brilho()

    if any(p in t for p in ["abre ", "abrir ", "lança ", "inicia "]):
        for app in APPS.keys():
            if app in t:
                return abrir_aplicacao(app)

    if any(p in t for p in ["que aplicações", "o que podes abrir", "lista de apps"]):
        return listar_aplicacoes()

    if any(p in t for p in ["pesquisa no youtube", "procura no youtube", "youtube "]):
        query = t.split("youtube")[-1].replace("sobre", "").strip()
        if query:
            return pesquisar_youtube(query)

    if any(p in t for p in ["pesquisa ", "pesquisar ", "procura ", "google ", "pesquisa sobre "]):
        for prefixo in ["pesquisa ", "pesquisar ", "procura ", "google ", "pesquisa sobre "]:
            if prefixo in t:
                query = t.split(prefixo)[-1].strip()
                if query:
                    return pesquisar_google(query)

    if any(p in t for p in ["abre o site", "vai para", "abre o link"]):
        partes = t.split()
        for p in partes:
            if "." in p and len(p) > 4:
                return abrir_url(p)

    if any(p in t for p in ["tempo em ", "previsão em ", "clima em "]):
        for prefixo in ["tempo em ", "previsão em ", "clima em "]:
            if prefixo in t:
                cidade = t.split(prefixo)[-1].strip()
                return previsao_tempo_detalhada(cidade)

    if any(p in t for p in ["que tempo", "como está o tempo", "previsão do tempo", "vai chover"]):
        return previsao_tempo_detalhada("Lisboa")

    # ======== LEMBRETES ========
    if any(p in t for p in ["cancela lembretes", "apaga lembretes", "remove lembretes"]):
        return cancelar_lembretes()

    if any(p in t for p in ["cancela lembrete", "apaga lembrete", "remove lembrete"]):
        nums = re.findall(r'\d+', t)
        if nums:
            return cancelar_lembrete_por_indice(int(nums[0]))
        else:
            if not lembretes:
                return "Não há lembretes ativos."
            lista = "\n".join([f"{i + 1}. {l['texto']} (em {l['minutos']} min)" for i, l in enumerate(lembretes)])
            return f"Qual lembrete queres cancelar? Diz o número:\n{lista}"

    if any(p in t for p in ["que lembretes", "lembretes ativos", "os meus lembretes"]):
        return listar_lembretes()

    if any(p in t for p in ["lembra-me", "lembrete", "avisa-me daqui"]):
        nums = re.findall(r'\d+', t)
        minutes = int(nums[0]) if nums else 5
        for prefixo in ["lembra-me de ", "lembra-me ", "lembrete para ", "avisa-me daqui a "]:
            if prefixo in t:
                descricao = t.split(prefixo)[-1]
                descricao = re.sub(r'daqui a \d+ minutos?', '', descricao).strip()
                descricao = re.sub(r'em \d+ minutos?', '', descricao).strip()
                if descricao:
                    return adicionar_lembrete(descricao, minutes, callback_falar)
        return adicionar_lembrete("lembrete", minutes, callback_falar)

    if any(p in t for p in ["estado do sistema", "info do sistema", "como está o pc"]):
        return info_sistema()
    if any(p in t for p in ["que horas", "horas são", "que dia é"]):
        return hora_atual()

    return None