"""
falar.py - Motor de voz com gTTS + pygame
- Fala frase a frase (mais natural e rápido a começar)
- Pode ser interrompida a meio com interromper_fala()
"""

from gtts import gTTS
import pygame
import os
import re
import threading
import time
import core.ouvir as ouvir  # Importa o módulo de escuta para monitorizar o microfone

# Flag global de interrupção - quando SET, a fala para
_interrupcao = threading.Event()


def interromper_fala():
    """Para a fala imediatamente. Pode ser chamada de qualquer thread."""
    _interrupcao.set()
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass


def _dividir_em_frases(texto: str) -> list:
    """
    Divide o texto em frases curtas para começar a falar mais cedo
    e soar mais natural. Não espera gerar o áudio de tudo de uma vez.
    """
    # Divide por pontuação forte
    frases = re.split(r'(?<=[.!?])\s+', texto.strip())

    resultado = []
    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue
        # Frases longas divididas por vírgula
        if len(frase) > 90:
            sub = re.split(r'(?<=,)\s+', frase)
            resultado.extend([s.strip() for s in sub if s.strip()])
        else:
            resultado.append(frase)

    return resultado if resultado else [texto.strip()]


def jarvis_falar(texto: str):
    """
    Fala o texto frase a frase com gTTS + pygame.
    Começa a falar mal a primeira frase esteja pronta (baixo delay).
    Interrompível a qualquer momento com interromper_fala().
    """
    _interrupcao.clear()

    # Se o utilizador já começou a falar alto antes de ditar, cancela logo
    if hasattr(ouvir, 'interrompido') and ouvir.interrompido:
        return

    frases = _dividir_em_frases(texto)
    ficheiros_temp = []

    try:
        pygame.mixer.init()

        for i, frase in enumerate(frases):
            # Verifica interrupção por código ou por voz antes de cada frase
            if _interrupcao.is_set() or (hasattr(ouvir, 'interrompido') and ouvir.interrompido):
                _interrupcao.set()
                print("[Jarvis] Fala interrompida.")
                break

            if not frase:
                continue

            # Gera o áudio desta frase
            nome_ficheiro = f"_jarvis_chunk_{i}.mp3"
            ficheiros_temp.append(nome_ficheiro)

            try:
                tts = gTTS(text=frase, lang='pt', tld='pt')
                tts.save(nome_ficheiro)
            except Exception as e:
                print(f"[gTTS] Erro a gerar frase: {e}")
                continue

            # Verifica de novo antes de tocar (pode ter sido interrompido durante o gTTS)
            if _interrupcao.is_set() or (hasattr(ouvir, 'interrompido') and ouvir.interrompido):
                _interrupcao.set()
                break

            # Toca o áudio
            pygame.mixer.music.load(nome_ficheiro)
            pygame.mixer.music.play()

            # Espera que acabe, verificando interrupção a cada 50ms
            while pygame.mixer.music.get_busy():
                if _interrupcao.is_set() or (hasattr(ouvir, 'interrompido') and ouvir.interrompido):
                    pygame.mixer.music.stop()
                    _interrupcao.set()
                    print("[Jarvis] Fala interrompida.")
                    break
                time.sleep(0.05)

            if _interrupcao.is_set():
                break

    except Exception as erro:
        print(f"[Jarvis] Erro na voz: {erro}")

    finally:
        # Limpa sempre os ficheiros temporários
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        for f in ficheiros_temp:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass