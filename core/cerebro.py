from groq import Groq
from core.funcoes import detetar_e_executar
import core.ouvir as ouvir  # Importamos o módulo de áudio para ler o estado da interrupção
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_nivel_atual = 1


def definir_nivel(nivel: int):
    global _nivel_atual
    _nivel_atual = max(1, min(6, nivel))


def obter_nivel():
    return _nivel_atual



_historico = []


def limpar_memoria():
    global _historico
    _historico.clear()
    return "Memória de sessão limpa, senhor."


def obter_historico():
    return list(_historico)



_CONFIGS_NIVEL = {
    1: {
        "nome": "ACESSO RESTRITO",
        "role": "BLOQUEADO",
        "tokens": 80,
        "prompt": """NÍVEL 1 — ACESSO RESTRITO (BLOQUEADO):
- Respostas MUITO curtas, maximum 2 frases.
- Não forneces informação técnica, sensível ou detalhada.
- Apenas respondes a saudações e perguntas básicas.
- Para tudo o resto dizes: acesso restrito, nível insuficiente.
- Tom frio e distante."""
    },
    2: {
        "nome": "PROTOCOLO LIMITADO",
        "role": "GUEST",
        "tokens": 150,
        "prompt": """NÍVEL 2 — PROTOCOLO LIMITADO (GUEST):
- Respostas curtas e diretas, máximo 3-4 frases.
- Podes responder a perguntas gerais e simples.
- Não entras in detalhes técnicos profundos.
- Não acedes a informação sensível ou restrita.
- Tom neutro e objetivo."""
    },
    3: {
        "nome": "PROTOCOLO ANALÍTICO",
        "role": "ANALYST",
        "tokens": 400,
        "prompt": """NÍVEL 3 — PROTOCOLO ANALÍTICO (ANALYST):
- Respostas moderadamente detalhadas.
- Podes usar tópicos e análise básica.
- Incluis contexto e explicações claras.
- Podes discutir temas técnicos de forma acessível.
- Tom técnico mas claro. Podes fazer sugestões."""
    },
    4: {
        "nome": "PROTOCOLO OPERACIONAL",
        "role": "OPERATOR",
        "tokens": 700,
        "prompt": """NÍVEL 4 — PROTOCOLO OPERACIONAL (OPERATOR):
- Respostas detalhadas e bem estruturadas.
- Divides por tópicos quando necessário.
- Acesso a análise técnica, código e sistemas.
- Forneces exemplos práticos e comparações.
- Tom profissional e técnico."""
    },
    5: {
        "nome": "PROTOCOLO OMNIPOTENTE",
        "role": "ADMIN",
        "tokens": 1200,
        "prompt": """NÍVEL 5 — PROTOCOLO OMNIPOTENTE (ADMIN):
- Respostas extremamente detalhadas e aprofundadas.
- Divides sempre por tópicos numerados com sub-pontos.
- Acesso total a informação técnica, sensível e complexa.
- Incluis exemplos, análises, alternativas e fontes.
- Antecipas perguntas de seguimento e respondes a elas.
- Tom altamente técnico, científico e elaborado."""
    },
    6: {
        "nome": "PROTOCOLO PROFESSORA",
        "role": "TEACHER",
        "tokens": 1500,
        "prompt": """NÍVEL 6 — PROTOCOLO PROFESSORA (TEACHER):
- És um assistente educacional especializado em programação.
- Explicas sempre de forma pedagógica, clara e estruturada.
- Usas exemplos práticos, analogias e exercícios.
- Adaptas a linguagem a alunos do ensino secundário/profissional.
- Corriges erros com paciência e construtivamente.
- Podes gerar fichas, exercícios, correções e explicações detalhadas.
- Tom encorajador, paciente e didático."""
    },
}



def _system_prompt():
    cfg = _CONFIGS_NIVEL.get(_nivel_atual, _CONFIGS_NIVEL[1])
    return f"""És o Jarvis, um assistente virtual de IA altamente avançado, inspirado no sistema do Iron Man, criado pelo Misael Oliveira Delgado & Micael Marques.
Responde sempre em Português de Portugal.
Usa um tom educado, leal e técnico.

{cfg['prompt']}"""


def _max_tokens():
    return _CONFIGS_NIVEL.get(_nivel_atual, _CONFIGS_NIVEL[1])["tokens"]




_TEMAS_ESTUDO = [
    "python", "programação", "algoritmo", "função", "variável", "classe",
    "loop", "for", "while", "if", "else", "lista", "dicionário", "tuplo",
    "string", "inteiro", "float", "booleano", "herança", "objeto", "módulo",
    "biblioteca", "import", "exceção", "erro", "debug", "recursão",
    "complexidade", "estrutura de dados", "array", "pilha", "fila", "árvore",
    "grafo", "ordenação", "pesquisa", "base de dados", "sql", "html", "css",
    "javascript", "web", "api", "json", "xml", "rede", "protocolo", "socket",
    "thread", "processo", "memória", "ponteiro", "compilador", "interpretador",
    "o que é", "como funciona", "explica", "diferença entre", "conceito",
    "define", "descreve", "como se usa", "para que serve", "exemplo de"
]

_TEMAS_CASUAL = [
    "olá", "oi", "bom dia", "boa tarde", "boa noite", "obrigado", "fixe",
    "ok", "sim", "não", "talvez", "claro", "certo", "entendi", "percebo",
    "como estás", "tudo bem", "até logo", "adeus", "tchau", "piada",
    "conta uma", "és fixe", "és bom", "parabéns", "bom trabalho"
]

_TEMAS_SENSIVEIS = [
    "hack", "exploit", "vulnerabilidade", "password alheia", "roubar",
    "invadir", "cracker", "malware", "vírus", "phishing", "bypass"
]


def _classificar_intencao(texto):
    t = texto.lower().strip()

    if "gera o conteúdo de uma ficha de estudo" in t:
        return {"tipo": "comando", "sugerir_ficha": False, "tema_principal": ""}

    resultado = {
        "tipo": "geral",
        "tema_principal": "",
        "sugerir_ficha": False,
        "nivel_complexidade": 1
    }

    if any(p in t for p in _TEMAS_CASUAL):
        resultado["tipo"] = "casual"
        return resultado

    if any(p in t for p in _TEMAS_SENSIVEIS):
        resultado["tipo"] = "sensivel"
        return resultado

    temas_encontrados = [tema for tema in _TEMAS_ESTUDO if tema in t]
    if temas_encontrados:
        resultado["tipo"] = "estudo"
        resultado["tema_principal"] = temas_encontrados[0]
        resultado["sugerir_ficha"] = _nivel_atual >= 3 and len(t) > 15

    if len(t) > 80:
        resultado["nivel_complexidade"] = 3
    elif len(t) > 30:
        resultado["nivel_complexidade"] = 2

    return resultado


def _construir_contexto_historico():
    if not _historico:
        return []
    return _historico[-16:]


def _mensagem_sugestao_ficha(tema):
    if _nivel_atual == 6:
        return f"\n\n📄 Quer que gere uma ficha de estudo com exercícios sobre '{tema}'? Escreve: ficha: {tema}"
    elif _nivel_atual >= 3:
        return f"\n\n💡 Posso gerar uma ficha de exercícios sobre este tema. Escreve: ficha: {tema}"
    return ""



def pensar(texto_utilizador, callback_falar=None):
    global _historico

    if not texto_utilizador:
        return ""

    resultado_funcao = detetar_e_executar(texto_utilizador, callback_falar=callback_falar)
    if resultado_funcao:
        return resultado_funcao

    intencao = _classificar_intencao(texto_utilizador)

    if intencao["tipo"] == "sensivel" and _nivel_atual < 5:
        return "⚠ Tópico restrito. Este tipo de informação requer nível 5 (ADMIN) ou superior."

    contexto = _construir_contexto_historico()

    mensagens = [
        {"role": "system", "content": _system_prompt()},
        *contexto,
        {"role": "user", "content": texto_utilizador}
    ]

    try:
        # Se uma interrupção de som alto foi ativada antes de enviar para a API, aborta imediatamente
        if hasattr(ouvir, 'interrompido') and ouvir.interrompido:
            ouvir.interrompido = False
            return ""

        resposta_api = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensagens,
            max_tokens=_max_tokens()
        )
        conteudo = resposta_api.choices[0].message.content

        # Verifica novamente se o utilizador falou por cima durante a espera da resposta da API
        if hasattr(ouvir, 'interrompido') and ouvir.interrompido:
            ouvir.interrompido = False
            return ""

        _historico.append({"role": "user", "content": texto_utilizador})
        _historico.append({"role": "assistant", "content": conteudo})

        if len(_historico) > 40:
            _historico = _historico[-40:]

        if intencao["sugerir_ficha"] and intencao["tema_principal"]:
            import core.funcoes as funcoes

            funcoes.AGUARDANDO_CONFIRMACAO_FICHA = True
            funcoes.TEMA_ESTUDO_REMANESCENTE = intencao["tema_principal"]

            conteudo += f"\n\n⚙️ [SISTEMA J.A.R.V.I.S]: Detetei que estamos a estudar '{intencao['tema_principal']}'. Deseja que desenvolva uma ficha complementar com exercícios no Word? (Responda 'Sim' para confirmar)"

        return conteudo

    except Exception as e:
        print(f"Erro no cérebro (Groq): {e}")
        return "⚠ Falha na ligação aos servidores Groq. Verifica a tua ligação à internet, senhor."