import re
from difflib import get_close_matches

REGEX_FLAGS = re.IGNORECASE

REGEX_AVANCA = re.compile(r"^AVANCA\s+(?P<passos>\d+)$", REGEX_FLAGS)
REGEX_RECUA = re.compile(r"^RECUA\s+(?P<passos>\d+)$", REGEX_FLAGS)
REGEX_LEFT = re.compile(r"^LEFT$", REGEX_FLAGS)
REGEX_RIGHT = re.compile(r"^RIGHT$", REGEX_FLAGS)
REGEX_DETECT = re.compile(r"^DETECT$", REGEX_FLAGS)
REGEX_IF = re.compile(r"^IF\s+OBSTACLE\s+THEN\s+RIGHT$", REGEX_FLAGS)
REGEX_REPEAT = re.compile(r"^REPEAT\s+(?P<qtd>\d+)\s*\{$", REGEX_FLAGS)
REGEX_FECHA = re.compile(r"^\}$")


class ParseError(Exception):
    pass
COMANDOS_VALIDOS = [
    "AVANCA",
    "RECUA",
    "LEFT",
    "RIGHT",
    "DETECT",
    "IF",
    "REPEAT"
]

def remover_comentario(linha):
    linha = linha.split("#", 1)[0]
    linha = linha.split("//", 1)[0]

    return linha.strip()


def normalizar_linhas(script):
    linhas = []

    for i, linha in enumerate(script.splitlines(), start=1):
        limpa = remover_comentario(linha)

        # normaliza tabs e múltiplos espaços
        limpa = re.sub(r"\s+", " ", limpa)

        if limpa:
            linhas.append((i, limpa))

    return linhas


def parse_bloco(linhas, inicio=0, exige_fechamento=False):
    comandos = []
    i = inicio

    while i < len(linhas):
        num_linha, linha = linhas[i]

        if REGEX_FECHA.fullmatch(linha):
            if exige_fechamento:
                return comandos, i + 1

            raise ParseError(f"Linha {num_linha}: fechamento inesperado -> '{linha}'")

        m = REGEX_AVANCA.fullmatch(linha)
        if m:
            n = int(m.group("passos"))

            if n <= 0:
                raise ParseError(f"Linha {num_linha}: AVANCA precisa de número maior que 0.")

            comandos.append(("AVANCA", n, num_linha))
            i += 1
            continue

        m = REGEX_RECUA.fullmatch(linha)
        if m:
            n = int(m.group("passos"))

            if n <= 0:
                raise ParseError(f"Linha {num_linha}: RECUA precisa de número maior que 0.")

            comandos.append(("RECUA", n, num_linha))
            i += 1
            continue

        if REGEX_LEFT.fullmatch(linha):
            comandos.append(("LEFT", None, num_linha))
            i += 1
            continue

        if REGEX_RIGHT.fullmatch(linha):
            comandos.append(("RIGHT", None, num_linha))
            i += 1
            continue

        if REGEX_DETECT.fullmatch(linha):
            comandos.append(("DETECT", None, num_linha))
            i += 1
            continue

        if REGEX_IF.fullmatch(linha):
            comandos.append(("IF_OBSTACLE_THEN_RIGHT", None, num_linha))
            i += 1
            continue

        m = REGEX_REPEAT.fullmatch(linha)
        if m:
            qtd = int(m.group("qtd"))

            if qtd <= 0:
                raise ParseError(f"Linha {num_linha}: REPEAT precisa de número maior que 0.")

            bloco, novo_i = parse_bloco(linhas, i + 1, True)
            comandos.append(("REPEAT", qtd, bloco, num_linha))
            i = novo_i
            continue

        raise ParseError(f"Linha {num_linha}: sintaxe inválida -> '{linha}'")

    if exige_fechamento:
        raise ParseError("Bloco REPEAT aberto e não fechado com '}'.")

    return comandos, i


def validar_e_compilar(script):
    linhas = normalizar_linhas(script)

    if not linhas:
        raise ParseError("O script está vazio.")

    comandos, idx = parse_bloco(linhas, 0)

    if idx != len(linhas):
        num_linha, linha = linhas[idx]
        raise ParseError(f"Linha {num_linha}: sintaxe inválida -> '{linha}'")

    return comandos


def expandir_comandos(comandos):
    saida = []

    for cmd in comandos:
        if cmd[0] == "REPEAT":
            _, qtd, bloco, _ = cmd

            for _ in range(qtd):
                saida.extend(expandir_comandos(bloco))
        else:
            saida.append(cmd)

    return saida
