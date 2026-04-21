import pygame
import re
import sys
from dataclasses import dataclass

# ============================================================
# SIMULADOR DO ROVER ESPACIAL - MISSÃO MARTE
# Projeto A3 com:
# - linguagem de comandos
# - validação com regex
# - interpretador simples
# - grid 2D com obstáculos
# - execução automática e passo a passo
# - visual estilo rover espacial / Marte
# - bônus: IF OBSTACLE THEN RIGHT e REPEAT n { ... }
# - tela inicial
# ============================================================

pygame.init()

# ---------------------------
# CONFIGURAÇÕES DA JANELA
# ---------------------------
LARGURA = 1000
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Rover Espacial - Missão Marte")
CLOCK = pygame.time.Clock()
FPS = 60

# ---------------------------
# GRID / MAPA
# ---------------------------
GRID_COLS = 12
GRID_ROWS = 12
CELL = 45
GRID_X = 40
GRID_Y = 90

PAINEL_X = GRID_X + GRID_COLS * CELL + 30
PAINEL_Y = 90
PAINEL_W = 350
PAINEL_H = 560

EXEC_DELAY = 450

# ---------------------------
# CORES - TEMA MARTE / NASA
# ---------------------------
COR_FUNDO = (10, 10, 15)
COR_AREIA = (120, 70, 40)
COR_AREIA_ESCURA = (90, 50, 30)
COR_GRADE = (60, 40, 30)
COR_TEXTO = (240, 240, 240)
COR_SUB = (205, 190, 175)
COR_BOTAO = (156, 84, 40)
COR_BOTAO_HOVER = (186, 104, 52)
COR_OBS = (80, 30, 20)
COR_ROVER = (205, 205, 215)
COR_LUZ = (120, 200, 255)
COR_EDITOR = (20, 18, 22)
COR_LOG = (18, 16, 20)
COR_OK = (110, 200, 120)
COR_ERRO = (225, 95, 95)
COR_ALERTA = (240, 180, 80)
COR_PAINEL = (28, 20, 20)
COR_PAINEL_BORDA = (110, 80, 60)
COR_PRETO = (20, 20, 20)
COR_BRANCO = (255, 255, 255)

# ---------------------------
# FONTES
# ---------------------------
FONTE = pygame.font.SysFont("consolas", 22)
FONTE_MEDIA = pygame.font.SysFont("consolas", 18)
FONTE_PEQUENA = pygame.font.SysFont("consolas", 15)
FONTE_TITULO = pygame.font.SysFont("consolas", 28, bold=True)
FONTE_TITULO_GRANDE = pygame.font.SysFont("consolas", 44, bold=True)

# ---------------------------
# SCRIPT DE EXEMPLO
# ---------------------------
SCRIPT_EXEMPLO = """AVANCA 2
RIGHT
AVANCA 3
IF OBSTACLE THEN RIGHT
AVANCA 2
REPEAT 2 {
    LEFT
    AVANCA 1
    RIGHT
}
DETECT
RECUA 1
"""

# ---------------------------
# REGEX DA LINGUAGEM
# ---------------------------
REGEX_AVANCA = re.compile(r"^AVANCA\s+(\d+)$")
REGEX_RECUA = re.compile(r"^RECUA\s+(\d+)$")
REGEX_LEFT = re.compile(r"^LEFT$")
REGEX_RIGHT = re.compile(r"^RIGHT$")
REGEX_DETECT = re.compile(r"^DETECT$")
REGEX_IF = re.compile(r"^IF\s+OBSTACLE\s+THEN\s+RIGHT$")
REGEX_REPEAT = re.compile(r"^REPEAT\s+(\d+)\s*\{$")
REGEX_FECHA = re.compile(r"^\}$")


# ---------------------------
# MODELOS
# ---------------------------
@dataclass
class Rover:
    x: int
    y: int
    direcao: str


DIRECOES = ["N", "E", "S", "W"]
VETORES = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}


class Botao:
    def __init__(self, x, y, w, h, texto):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto

    def desenhar(self, tela, mouse_pos):
        cor = COR_BOTAO_HOVER if self.rect.collidepoint(mouse_pos) else COR_BOTAO
        pygame.draw.rect(tela, cor, self.rect, border_radius=10)
        pygame.draw.rect(tela, COR_BRANCO, self.rect, 2, border_radius=10)
        render = FONTE_MEDIA.render(self.texto, True, COR_BRANCO)
        tela.blit(render, render.get_rect(center=self.rect.center))

    def clicou(self, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos)


# ---------------------------
# PARSER / INTERPRETADOR
# ---------------------------
class ParseError(Exception):
    pass


def normalizar_linhas(script):
    linhas = []
    for i, linha in enumerate(script.splitlines(), start=1):
        limpa = linha.strip()
        if limpa:
            linhas.append((i, limpa))
    return linhas


def parse_bloco(linhas, inicio=0):
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
            bloco, novo_i = parse_bloco(linhas, i + 1)
            comandos.append(("REPEAT", qtd, bloco, num_linha))
            i = novo_i
            continue

        raise ParseError(f"Linha {num_linha}: sintaxe inválida -> '{linha}'")

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


# ---------------------------
# SIMULAÇÃO
# ---------------------------
class SimuladorRover:
    def __init__(self):
        self.obstaculos = {
            (3, 1), (4, 1), (7, 2), (7, 3), (2, 5), (3, 5),
            (8, 6), (1, 8), (5, 8), (9, 9), (10, 4)
        }
        self.resetar()

    def resetar(self):
        self.rover = Rover(0, 0, "E")
        self.log = ["Sistema pronto."]
        self.comandos = []
        self.indice = 0
        self.executando = False
        self.finalizado = False
        self.tempo_ultimo_passo = 0
        self.status = "Aguardando compilação..."
        self.cor_status = COR_SUB

    def carregar_programa(self, comandos):
        self.comandos = expandir_comandos(comandos)
        self.indice = 0
        self.executando = False
        self.finalizado = False
        self.log = [f"Programa compilado com {len(self.comandos)} instruções."]
        self.status = "Compilado com sucesso."
        self.cor_status = COR_OK

    def dentro_grid(self, x, y):
        return 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS

    def obstaculo_a_frente(self):
        dx, dy = VETORES[self.rover.direcao]
        nx, ny = self.rover.x + dx, self.rover.y + dy
        if not self.dentro_grid(nx, ny):
            return True
        return (nx, ny) in self.obstaculos

    def girar_esquerda(self):
        idx = DIRECOES.index(self.rover.direcao)
        self.rover.direcao = DIRECOES[(idx - 1) % 4]

    def girar_direita(self):
        idx = DIRECOES.index(self.rover.direcao)
        self.rover.direcao = DIRECOES[(idx + 1) % 4]

    def mover(self, passos, frente=True):
        for _ in range(passos):
            dx, dy = VETORES[self.rover.direcao]
            if not frente:
                dx, dy = -dx, -dy

            nx = self.rover.x + dx
            ny = self.rover.y + dy

            if not self.dentro_grid(nx, ny):
                self.log.append("Movimento cancelado: limite do mapa.")
                return False

            if (nx, ny) in self.obstaculos:
                self.log.append("Movimento cancelado: obstáculo encontrado.")
                return False

            self.rover.x = nx
            self.rover.y = ny

        return True

    def executar_passo(self):
        if self.indice >= len(self.comandos):
            self.executando = False
            self.finalizado = True
            self.status = "Execução finalizada."
            self.cor_status = COR_OK
            self.log.append("Fim do programa.")
            return

        cmd = self.comandos[self.indice]
        nome = cmd[0]
        linha = cmd[-1]

        if nome == "AVANCA":
            n = cmd[1]
            ok = self.mover(n, True)
            self.log.append(f"Linha {linha}: AVANCA {n} -> {'OK' if ok else 'BLOQUEADO'}")

        elif nome == "RECUA":
            n = cmd[1]
            ok = self.mover(n, False)
            self.log.append(f"Linha {linha}: RECUA {n} -> {'OK' if ok else 'BLOQUEADO'}")

        elif nome == "LEFT":
            self.girar_esquerda()
            self.log.append(f"Linha {linha}: LEFT -> direção {self.rover.direcao}")

        elif nome == "RIGHT":
            self.girar_direita()
            self.log.append(f"Linha {linha}: RIGHT -> direção {self.rover.direcao}")

        elif nome == "DETECT":
            tem = self.obstaculo_a_frente()
            self.log.append(f"Linha {linha}: DETECT -> {'OBSTÁCULO' if tem else 'LIVRE'}")

        elif nome == "IF_OBSTACLE_THEN_RIGHT":
            if self.obstaculo_a_frente():
                self.girar_direita()
                self.log.append(f"Linha {linha}: obstáculo detectado, girou para {self.rover.direcao}")
            else:
                self.log.append(f"Linha {linha}: caminho livre, não girou")

        self.indice += 1

    def atualizar(self):
        if self.executando:
            agora = pygame.time.get_ticks()
            if agora - self.tempo_ultimo_passo >= EXEC_DELAY:
                self.executar_passo()
                self.tempo_ultimo_passo = agora


# ---------------------------
# FUNÇÕES DE TEXTO
# ---------------------------
def quebrar_linhas(texto, fonte, largura_max):
    palavras = texto.split(" ")
    linhas = []
    atual = ""

    for palavra in palavras:
        teste = palavra if atual == "" else atual + " " + palavra
        if fonte.size(teste)[0] <= largura_max:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra

    if atual:
        linhas.append(atual)
    return linhas


def desenhar_texto_multilinha(tela, texto, fonte, cor, rect, espacamento=4, max_linhas=None):
    y = rect.y
    linhas_total = []

    for bloco in texto.split("\n"):
        if bloco:
            linhas_total.extend(quebrar_linhas(bloco, fonte, rect.w))
        else:
            linhas_total.append("")

    if max_linhas is not None:
        linhas_total = linhas_total[:max_linhas]

    for linha in linhas_total:
        render = fonte.render(linha, True, cor)
        tela.blit(render, (rect.x, y))
        y += render.get_height() + espacamento


# ---------------------------
# DESENHO DO CENÁRIO
# ---------------------------
def desenhar_estrelas(tela):
    estrelas = [
        (70, 25), (120, 50), (210, 35), (320, 20), (470, 40),
        (560, 28), (690, 22), (790, 45), (920, 30), (850, 60),
        (160, 90), (260, 70), (390, 55), (610, 70)
    ]
    for x, y in estrelas:
        pygame.draw.circle(tela, COR_BRANCO, (x, y), 2)


def desenhar_grid(tela, sim):
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            rect = pygame.Rect(GRID_X + x * CELL, GRID_Y + y * CELL, CELL, CELL)

            cor = COR_AREIA if (x + y) % 2 == 0 else COR_AREIA_ESCURA
            pygame.draw.rect(tela, cor, rect)
            pygame.draw.rect(tela, COR_GRADE, rect, 1)

            if (x, y) in sim.obstaculos:
                pygame.draw.circle(tela, COR_OBS, rect.center, CELL // 3)
                pygame.draw.circle(tela, (110, 55, 35), rect.center, CELL // 4, 2)

    rx = GRID_X + sim.rover.x * CELL + CELL // 2
    ry = GRID_Y + sim.rover.y * CELL + CELL // 2

    pygame.draw.ellipse(tela, (40, 20, 15), (rx - 16, ry + 8, 32, 10))
    pygame.draw.rect(tela, COR_ROVER, (rx - 11, ry - 8, 22, 16), border_radius=4)
    pygame.draw.rect(tela, (180, 185, 200), (rx - 7, ry - 12, 14, 6), border_radius=2)
    pygame.draw.circle(tela, COR_PRETO, (rx - 13, ry + 10), 5)
    pygame.draw.circle(tela, COR_PRETO, (rx + 13, ry + 10), 5)
    pygame.draw.circle(tela, (70, 70, 70), (rx - 13, ry + 10), 2)
    pygame.draw.circle(tela, (70, 70, 70), (rx + 13, ry + 10), 2)
    pygame.draw.line(tela, COR_ROVER, (rx, ry - 8), (rx, ry - 20), 2)
    pygame.draw.circle(tela, COR_LUZ, (rx, ry - 20), 3)

    dx, dy = VETORES[sim.rover.direcao]
    pygame.draw.line(tela, COR_LUZ, (rx, ry), (rx + dx * 20, ry + dy * 20), 2)
    pygame.draw.circle(tela, COR_LUZ, (rx + dx * 20, ry + dy * 20), 2)

    titulo = FONTE_TITULO.render("MISSÃO MARTE - GRID 2D", True, COR_TEXTO)
    tela.blit(titulo, (GRID_X, 35))


def desenhar_painel(tela, script, sim):
    painel = pygame.Rect(PAINEL_X, PAINEL_Y, PAINEL_W, PAINEL_H)
    pygame.draw.rect(tela, COR_PAINEL, painel, border_radius=12)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, painel, 2, border_radius=12)

    titulo = FONTE_TITULO.render("SCRIPT", True, COR_TEXTO)
    tela.blit(titulo, (PAINEL_X, 35))

    editor = pygame.Rect(PAINEL_X + 12, PAINEL_Y + 12, PAINEL_W - 24, 240)
    pygame.draw.rect(tela, COR_EDITOR, editor, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, editor, 1, border_radius=10)
    desenhar_texto_multilinha(
        tela,
        script,
        FONTE_PEQUENA,
        COR_TEXTO,
        editor.inflate(-10, -10),
        espacamento=2,
        max_linhas=15,
    )

    status_txt = FONTE_MEDIA.render(sim.status, True, sim.cor_status)
    tela.blit(status_txt, (PAINEL_X + 12, PAINEL_Y + 265))

    estado_box = pygame.Rect(PAINEL_X + 12, PAINEL_Y + 300, PAINEL_W - 24, 90)
    pygame.draw.rect(tela, (18, 14, 16), estado_box, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, estado_box, 1, border_radius=10)

    infos = [
        f"Posição: ({sim.rover.x}, {sim.rover.y})",
        f"Direção: {sim.rover.direcao}",
        f"Próxima instrução: {sim.indice + 1 if sim.indice < len(sim.comandos) else '-'}",
    ]

    for idx, info in enumerate(infos):
        render = FONTE_MEDIA.render(info, True, COR_TEXTO)
        tela.blit(render, (estado_box.x + 10, estado_box.y + 10 + idx * 24))

    log_box = pygame.Rect(PAINEL_X + 12, PAINEL_Y + 405, PAINEL_W - 24, 140)
    pygame.draw.rect(tela, COR_LOG, log_box, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, log_box, 1, border_radius=10)

    log_titulo = FONTE_MEDIA.render("LOG DE EXECUÇÃO", True, COR_TEXTO)
    tela.blit(log_titulo, (log_box.x + 10, log_box.y + 8))

    logs_visiveis = sim.log[-6:]
    for i, linha in enumerate(logs_visiveis):
        render = FONTE_PEQUENA.render(linha[:42], True, COR_SUB)
        tela.blit(render, (log_box.x + 10, log_box.y + 34 + i * 16))


def desenhar_legenda(tela):
    legenda = [
        "Comandos válidos:",
        "AVANCA n",
        "RECUA n",
        "LEFT",
        "RIGHT",
        "DETECT",
        "IF OBSTACLE THEN RIGHT",
        "REPEAT n { ... }",
    ]

    x = GRID_X
    y = GRID_Y + GRID_ROWS * CELL + 15

    for i, txt in enumerate(legenda):
        fonte = FONTE_MEDIA if i == 0 else FONTE_PEQUENA
        cor = COR_TEXTO if i == 0 else COR_SUB
        render = fonte.render(txt, True, cor)
        tela.blit(render, (x, y + i * 20))


# ---------------------------
# TELA INICIAL
# ---------------------------
def desenhar_tela_inicial(tela, mouse_pos, btn_iniciar, btn_sair):
    tela.fill(COR_FUNDO)
    desenhar_estrelas(tela)

    pygame.draw.circle(tela, (180, 80, 50), (850, 120), 70)
    pygame.draw.circle(tela, (210, 110, 70), (825, 100), 18)
    pygame.draw.circle(tela, (140, 65, 40), (880, 140), 15)
    pygame.draw.circle(tela, (160, 75, 45), (865, 95), 10)

    pygame.draw.rect(tela, COR_AREIA_ESCURA, (0, ALTURA - 180, LARGURA, 180))
    pygame.draw.circle(tela, (145, 80, 45), (100, ALTURA - 50), 60)
    pygame.draw.circle(tela, (105, 55, 30), (240, ALTURA - 20), 90)
    pygame.draw.circle(tela, (125, 70, 40), (410, ALTURA - 60), 65)
    pygame.draw.circle(tela, (100, 50, 28), (700, ALTURA - 10), 120)

    titulo = FONTE_TITULO_GRANDE.render("ROVER ESPACIAL", True, COR_BRANCO)
    subtitulo = FONTE_TITULO.render("MISSÃO MARTE", True, COR_LUZ)
    descricao = FONTE_MEDIA.render("Simulador com comandos, regex e exploração em grid 2D", True, COR_SUB)

    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 150)))
    tela.blit(subtitulo, subtitulo.get_rect(center=(LARGURA // 2, 205)))
    tela.blit(descricao, descricao.get_rect(center=(LARGURA // 2, 250)))

    rx, ry = LARGURA // 2, 380
    pygame.draw.ellipse(tela, (40, 20, 15), (rx - 55, ry + 38, 110, 20))
    pygame.draw.rect(tela, COR_ROVER, (rx - 35, ry, 70, 30), border_radius=6)
    pygame.draw.rect(tela, (180, 185, 200), (rx - 20, ry - 12, 40, 10), border_radius=3)
    pygame.draw.circle(tela, COR_PRETO, (rx - 42, ry + 38), 10)
    pygame.draw.circle(tela, COR_PRETO, (rx + 42, ry + 38), 10)
    pygame.draw.circle(tela, (70, 70, 70), (rx - 42, ry + 38), 3)
    pygame.draw.circle(tela, (70, 70, 70), (rx + 42, ry + 38), 3)
    pygame.draw.line(tela, COR_ROVER, (rx, ry), (rx, ry - 34), 3)
    pygame.draw.circle(tela, COR_LUZ, (rx, ry - 34), 5)
    pygame.draw.line(tela, COR_LUZ, (rx + 15, ry + 12), (rx + 70, ry - 6), 3)
    pygame.draw.circle(tela, COR_LUZ, (rx + 70, ry - 6), 4)

    info1 = FONTE_MEDIA.render("• Compile scripts", True, COR_TEXTO)
    info2 = FONTE_MEDIA.render("• Controle o rover", True, COR_TEXTO)
    info3 = FONTE_MEDIA.render("• Desvie de obstáculos em Marte", True, COR_TEXTO)

    tela.blit(info1, info1.get_rect(center=(LARGURA // 2, 470)))
    tela.blit(info2, info2.get_rect(center=(LARGURA // 2, 500)))
    tela.blit(info3, info3.get_rect(center=(LARGURA // 2, 530)))

    btn_iniciar.desenhar(tela, mouse_pos)
    btn_sair.desenhar(tela, mouse_pos)


def tela_inicial():
    btn_iniciar = Botao(LARGURA // 2 - 120, 580, 240, 55, "Iniciar Missão")
    btn_sair = Botao(LARGURA // 2 - 120, 645, 240, 45, "Sair")

    while True:
        mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if btn_iniciar.clicou(evento):
                return

            if btn_sair.clicou(evento):
                pygame.quit()
                sys.exit()

        desenhar_tela_inicial(TELA, mouse, btn_iniciar, btn_sair)
        pygame.display.flip()
        CLOCK.tick(FPS)


# ---------------------------
# LOOP PRINCIPAL
# ---------------------------
def main():
    tela_inicial()

    script = SCRIPT_EXEMPLO
    simulador = SimuladorRover()

    btn_compilar = Botao(PAINEL_X + 10, ALTURA - 78, 100, 46, "Compilar")
    btn_executar = Botao(PAINEL_X + 120, ALTURA - 78, 100, 46, "Executar")
    btn_passo = Botao(PAINEL_X + 230, ALTURA - 78, 100, 46, "1 Passo")
    btn_reset = Botao(PAINEL_X + 10, ALTURA - 130, 100, 40, "Reset")
    btn_exemplo = Botao(PAINEL_X + 120, ALTURA - 130, 210, 40, "Carregar Exemplo")

    while True:
        mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_BACKSPACE:
                    script = script[:-1]
                elif evento.key == pygame.K_TAB:
                    script += "    "
                elif evento.key == pygame.K_RETURN:
                    script += "\n"
                else:
                    if evento.unicode and evento.unicode.isprintable():
                        script += evento.unicode

            elif btn_compilar.clicou(evento):
                simulador.resetar()
                try:
                    arvore = validar_e_compilar(script)
                    simulador.carregar_programa(arvore)
                except ParseError as e:
                    simulador.status = str(e)
                    simulador.cor_status = COR_ERRO
                    simulador.log.append("Erro de compilação.")

            elif btn_executar.clicou(evento):
                if simulador.comandos:
                    simulador.executando = True
                    simulador.finalizado = False
                    simulador.status = "Executando..."
                    simulador.cor_status = COR_ALERTA
                    simulador.tempo_ultimo_passo = pygame.time.get_ticks()
                else:
                    simulador.status = "Compile o script antes de executar."
                    simulador.cor_status = COR_ERRO

            elif btn_passo.clicou(evento):
                if simulador.comandos:
                    simulador.executar_passo()
                else:
                    simulador.status = "Compile o script antes de executar."
                    simulador.cor_status = COR_ERRO

            elif btn_reset.clicou(evento):
                simulador.resetar()

            elif btn_exemplo.clicou(evento):
                script = SCRIPT_EXEMPLO
                simulador.status = "Exemplo carregado."
                simulador.cor_status = COR_SUB

        simulador.atualizar()

        TELA.fill(COR_FUNDO)
        desenhar_estrelas(TELA)
        desenhar_grid(TELA, simulador)
        desenhar_painel(TELA, script, simulador)
        desenhar_legenda(TELA)

        btn_reset.desenhar(TELA, mouse)
        btn_exemplo.desenhar(TELA, mouse)
        btn_compilar.desenhar(TELA, mouse)
        btn_executar.desenhar(TELA, mouse)
        btn_passo.desenhar(TELA, mouse)

        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()