import re

REGEX_AVANCA = re.compile(r"^AVANCA\s+(\d+)$")
REGEX_RECUA = re.compile(r"^RECUA\s+(\d+)$")
REGEX_LEFT = re.compile(r"^LEFT$")
REGEX_RIGHT = re.compile(r"^RIGHT$")
REGEX_DETECT = re.compile(r"^DETECT$")
REGEX_IF = re.compile(r"^IF\s+OBSTACLE\s+THEN\s+RIGHT$")
REGEX_REPEAT = re.compile(r"^REPEAT\s+(\d+)\s*\{$")
REGEX_FECHA = re.compile(r"^\}$")


class ParseError(Exception):
    pass


def normalizar_linhas(script):
    linhas = []

    for i, linha in enumerate(script.splitlines(), start=1):
        limpa = linha.strip()

        if limpa:
            linhas.append((i, limpa))

    return linhas


def parse_bloco(linhas, inicio=0, exige_fechamento=False):
    comandos = []
    i = inicio

    while i < len(linhas):
        num_linha, linha = linhas[i]

        if REGEX_FECHA.match(linha):
            return comandos, i + 1

        m = REGEX_AVANCA.match(linha)
        if m:
            n = int(m.group(1))

            if n <= 0:
                raise ParseError(f"Linha {num_linha}: AVANCA precisa de número maior que 0.")

            comandos.append(("AVANCA", n, num_linha))
            i += 1
            continue

        m = REGEX_RECUA.match(linha)
        if m:
            n = int(m.group(1))

            if n <= 0:
                raise ParseError(f"Linha {num_linha}: RECUA precisa de número maior que 0.")

            comandos.append(("RECUA", n, num_linha))
            i += 1
            continue

        if REGEX_LEFT.match(linha):
            comandos.append(("LEFT", None, num_linha))
            i += 1
            continue

        if REGEX_RIGHT.match(linha):
            comandos.append(("RIGHT", None, num_linha))
            i += 1
            continue

        if REGEX_DETECT.match(linha):
            comandos.append(("DETECT", None, num_linha))
            i += 1
            continue

        if REGEX_IF.match(linha):
            comandos.append(("IF_OBSTACLE_THEN_RIGHT", None, num_linha))
            i += 1
            continue

        m = REGEX_REPEAT.match(linha)
        if m:
            qtd = int(m.group(1))

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
        raise ParseError(f"Linha {num_linha}: fechamento inesperado -> '{linha}'")

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