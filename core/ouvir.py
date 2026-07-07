import speech_recognition as sr
import time

# Inicialização dos componentes globais do Reconhecedor de Voz
r = sr.Recognizer()
r.pause_threshold = 0.8  # Resposta mais rápida após o utilizador parar de falar
r.energy_threshold = 300  # Sensibilidade do microfone (bom som)
mic = sr.Microphone()

# Flags globais de controlo de estado
interrompido = False
ultimo_comando = ""


def callback_escuta_ativa(recognizer, audio):
    global interrompido, ultimo_comando
    try:
        texto = recognizer.recognize_google(audio, language='pt-PT').lower()
        if texto.strip():
            print(f"\n[Interrupção Detetada]: '{texto}'") # << EXECUTAS ESTA LINHA?
            ultimo_comando = texto
            interrompido = True
    except (sr.UnknownValueError, sr.RequestError):
        pass


def iniciar_escuta_continua():
    """Ativa o motor de escuta em segundo plano. Deve ser chamado no arranque do programa."""
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.5)

    stop_listening = r.listen_in_background(mic, callback_escuta_ativa)
    print("[Jarvis: Escuta contínua ativa. Pronto para receber ordens!]")
    return stop_listening


def verificar_e_consumir_comando():
    """Verifica e consome comandos gerados por interrupção de voz."""
    global interrompido, ultimo_comando
    if interrompido:
        cmd = ultimo_comando
        interrompido = False
        ultimo_comando = ""
        return cmd
    return ""


def ouvir_mic():
    """
    Função principal exigida pela interface.
    Escuta o utilizador de forma síncrona mantendo a compatibilidade do ecossistema.
    """
    global interrompido, ultimo_comando

    print("[Jarvis está atento (Modo Contínuo)...]")

    # Aguarda que o segundo plano capture alguma fala (máximo 15 segundos para não congelar)
    tentativas = 0
    while not interrompido and tentativas < 150:  # 150 * 0.1s = 15 segundos
        time.sleep(0.1)
        tentativas += 1

    # Se o background guardou ou acabou de guardar alguma fala, entrega-a logo à interface
    if interrompido:
        cmd = ultimo_comando
        interrompido = False
        ultimo_comando = ""
        print(f"[A processar voz]: {cmd}")
        return cmd

    # Caso contrário, se passou o tempo limite sem som detetado, devolve string vazia
    return ""