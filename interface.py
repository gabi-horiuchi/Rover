import pygame
import random
from math import cos, sin, radians

from simulador import SimuladorRover
from parser_rover import validar_e_compilar, ParseError

pygame.init()
pygame.font.init()
pygame.mixer.init()
print("Mixer iniciado")

LARGURA = 1300
ALTURA = 700
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Rover Espacial - PROJETO ARES")
CLOCK = pygame.time.Clock()
FPS = 60

BACKSPACE_DELAY_INICIAL = 350
BACKSPACE_INTERVALO = 45


GRID_COLS = 12
GRID_ROWS = 12
CELL = 38

MARGEM = 40
GRID_X = MARGEM
GRID_Y = 88

GRID_W = GRID_COLS * CELL
GRID_H = GRID_ROWS * CELL

GAP = 30
PAINEL_X = GRID_X + GRID_W + GAP
PAINEL_Y = GRID_Y
PAINEL_W = LARGURA - PAINEL_X - MARGEM
PAINEL_H = 480

LEGENDA_Y = GRID_Y + GRID_H + 14
LEGENDA_H = 120

BTN_Y = PAINEL_Y + PAINEL_H + 18
BTN_W = 150
BTN_H = 42
BTN_GAP = 15


COR_FUNDO = (18, 18, 35)
COR_AREIA = (170, 170, 175)
COR_AREIA_ESCURA = (130, 130, 140)
COR_GRADE = (90, 90, 100)

COR_TEXTO = (230, 230, 235)
COR_SUB = (180, 180, 190)

COR_BOTAO = (70, 90, 140)
COR_BOTAO_HOVER = (100, 130, 180)

COR_OBS = (000, 000, 000)
COR_ROVER = (90, 140, 200)
COR_LUZ = (140, 180, 255)

COR_EDITOR = (18, 20, 30)
COR_LOG = (15, 17, 25)

COR_OK = (120, 200, 160)
COR_ERRO = (220, 90, 90)
COR_ALERTA = (230, 200, 120)

COR_PAINEL = (20, 22, 30)
COR_PAINEL_BORDA = (90, 110, 150)

COR_PRETO = (10, 10, 10)
COR_BRANCO = (240, 240, 240)


FONTE_MEDIA = pygame.font.SysFont("consolas", 18)
FONTE_PEQUENA = pygame.font.SysFont("consolas", 15)
FONTE_MINI = pygame.font.SysFont("consolas", 13)
FONTE_TITULO = pygame.font.SysFont("consolas", 28, bold=True)
FONTE_TITULO_GRANDE = pygame.font.SysFont("consolas", 44, bold=True)

SOM_MOVIMENTO = pygame.mixer.Sound("assets/sounds/move.mp3")
SOM_ERRO = pygame.mixer.Sound("assets/sounds/error.mp3")
SOM_CLICK = pygame.mixer.Sound("assets/sounds/click.mp3")
SOM_VITORIA = pygame.mixer.Sound("assets/sounds/victory.mp3")

SOM_MOVIMENTO.set_volume(0.2)
SOM_ERRO.set_volume(0.4)
SOM_CLICK.set_volume(0.2)
SOM_VITORIA.set_volume(0.5)

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


def apagar_ultimo_caractere(texto):
    if not texto:
        return texto

    return texto[:-1]


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
        return (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.rect.collidepoint(evento.pos)
        )

def desenhar_estrelas(tela):
    estrelas = [
        (70, 25), (120, 50), (210, 35), (320, 20), (470, 40),
        (560, 28), (690, 22), (790, 45), (920, 30), (850, 60),
        (160, 90), (260, 70), (390, 55), (610, 70), (980, 44),
        (1120, 28), (1240, 62), (1290, 36)
    ]

    for x, y in estrelas:
        pygame.draw.circle(tela, COR_BRANCO, (x, y), 2)


def desenhar_grid(tela, sim):

    # coordenadas horizontais
    for x in range(GRID_COLS):
        texto = FONTE_MINI.render(str(x), True, COR_SUB)

        tela.blit(
            texto,
            (
                GRID_X + x * CELL + CELL // 2 - 4,
                GRID_Y - 18
            )
        )

    # coordenadas verticais
    for y in range(GRID_ROWS):
        texto = FONTE_MINI.render(str(y), True, COR_SUB)

        tela.blit(
            texto,
            (
                GRID_X - 18,
                GRID_Y + y * CELL + CELL // 2 - 6
            )
        )

    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            rect = pygame.Rect(GRID_X + x * CELL, GRID_Y + y * CELL, CELL, CELL)

            cor = COR_AREIA if (x + y) % 2 == 0 else COR_AREIA_ESCURA
            pygame.draw.rect(tela, cor, rect)
            pygame.draw.rect(tela, COR_GRADE, rect, 1)

            # destaca posição inicial
            if (x, y) == (0, 0):
                pygame.draw.rect(tela, (100, 180, 120), rect, 3)

            if (x, y) in sim.obstaculos:
                centro_x, centro_y = rect.center

                pygame.draw.ellipse(
                    tela,
                    (40, 40, 45),
                    (centro_x - 14, centro_y + 8, 28, 10)
                    )

                pontos = [
                        (centro_x - 10, centro_y + 6),
                        (centro_x - 14, centro_y - 2),
                        (centro_x - 8, centro_y - 11),
                        (centro_x + 2, centro_y - 13),
                        (centro_x + 12, centro_y - 6),
                        (centro_x + 13, centro_y + 4),
                        (centro_x + 4, centro_y + 11),
                        (centro_x - 6, centro_y + 12),
                    ]

                pygame.draw.polygon(
                        tela,
                        (70, 70, 78),
                        pontos
                    )

                pygame.draw.circle(
                        tela,
                        (120, 120, 130),
                        (centro_x - 3, centro_y - 4),
                        4
                    )

                pygame.draw.line(
                        tela,
                        (45, 45, 50),
                        (centro_x - 4, centro_y - 3),
                        (centro_x + 5, centro_y + 4),
                        2
                    )

    rx = GRID_X + int(sim.rover_px * CELL) + CELL // 2
    ry = GRID_Y + int(sim.rover_py * CELL) + CELL // 2

    pygame.draw.ellipse(tela, (35, 35, 40), (rx - 16, ry + 10, 32, 8))
    pygame.draw.rect(tela, COR_ROVER, (rx - 11, ry - 8, 22, 16), border_radius=4)
    pygame.draw.rect(tela, (180, 185, 200), (rx - 7, ry - 12, 14, 6), border_radius=2)

    pygame.draw.circle(tela, COR_PRETO, (rx - 13, ry + 9), 5)
    pygame.draw.circle(tela, COR_PRETO, (rx + 13, ry + 9), 5)
    pygame.draw.circle(tela, (70, 70, 80), (rx - 13, ry + 9), 2)
    pygame.draw.circle(tela, (70, 70, 80), (rx + 13, ry + 9), 2)

    pygame.draw.line(tela, COR_ROVER, (rx, ry - 8), (rx, ry - 20), 2)
    pygame.draw.circle(tela, COR_LUZ, (rx, ry - 20), 3)

    direcao_suave_x = cos(radians(sim.angulo_anim))
    direcao_suave_y = sin(radians(sim.angulo_anim))

    ponta_x = rx + int(direcao_suave_x * 18)
    ponta_y = ry + int(direcao_suave_y * 18)

    pygame.draw.line(tela, COR_LUZ, (rx, ry), (ponta_x, ponta_y), 2)
    pygame.draw.circle(tela, COR_LUZ, (ponta_x, ponta_y), 3)

    # desenha objetivo do modo desafio
    if sim.objetivo:

        ox, oy = sim.objetivo

        centro_x = GRID_X + ox * CELL + CELL // 2
        centro_y = GRID_Y + oy * CELL + CELL // 2

        pygame.draw.circle(
            tela,
            (255, 215, 0),
            (centro_x, centro_y),
            10
        )

        pygame.draw.circle(
            tela,
            (255, 240, 120),
            (centro_x, centro_y),
            5
        )

    # destaca célula atual do rover
    rover_rect = pygame.Rect(
        GRID_X + sim.rover.x * CELL,
        GRID_Y + sim.rover.y * CELL,
        CELL,
        CELL
    )

    pygame.draw.rect(tela, COR_LUZ, rover_rect, 2)

    titulo = FONTE_TITULO.render("PROJETO ARES - BASE LUNAR 2D", True, COR_TEXTO)
    tela.blit(titulo, (GRID_X, 35))


def desenhar_painel(tela, script, sim, scroll_script=0):
    painel = pygame.Rect(PAINEL_X, PAINEL_Y, PAINEL_W, PAINEL_H)

    pygame.draw.rect(tela, COR_PAINEL, painel, border_radius=12)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, painel, 2, border_radius=12)

    titulo = FONTE_TITULO.render("SCRIPT", True, COR_TEXTO)
    tela.blit(titulo, (PAINEL_X, 35))

    editor = pygame.Rect(PAINEL_X + 12, PAINEL_Y + 12, PAINEL_W - 24, 200)
    pygame.draw.rect(tela, COR_EDITOR, editor, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, editor, 1, border_radius=10)

    linhas = script.splitlines()

    if not linhas:
        linhas = [""]

    max_linhas_visiveis = 11
    linhas_visiveis = linhas[scroll_script:scroll_script + max_linhas_visiveis]

    y = editor.y + 8

    for i, linha in enumerate(linhas_visiveis):

        linha_real = scroll_script + i

        numero = str(linha_real + 1).rjust(2)
        texto = f"{numero} | {linha}"

        cor_texto = COR_TEXTO

        # linha atual sendo executada
        if linha_real == sim.indice and sim.executando:
            
            destaque = pygame.Rect(
                editor.x + 4,
                y - 1,
                editor.w - 8,
                18
            )

            pygame.draw.rect(
                tela,
                (70, 140, 90),
                destaque,
                border_radius=4
            )

            cor_texto = COR_BRANCO

        # linhas já executadas
        elif linha_real < sim.indice:
            cor_texto = (140, 140, 150)

        render = FONTE_PEQUENA.render(texto[:75], True, cor_texto)

        tela.blit(render, (editor.x + 10, y))

        y += 17

    total_linhas = len(linhas)
    fim = min(scroll_script + max_linhas_visiveis, total_linhas)

    info_scroll = FONTE_MINI.render(
        f"Linhas {scroll_script + 1}-{fim} de {total_linhas}",
        True,
        COR_SUB
    )

    tela.blit(
    info_scroll,
    (
         editor.x + editor.w - 175,
        editor.y + editor.h - 20
    )
)

    seta = FONTE_MEDIA.render("↑↓", True, COR_LUZ)
    tela.blit(seta, (editor.x + editor.w - 35, editor.y + editor.h - 25))

    status_txt = FONTE_MEDIA.render(sim.status[:58], True, sim.cor_status)
    tela.blit(status_txt, (PAINEL_X + 12, PAINEL_Y + 222))

    estado_box = pygame.Rect(PAINEL_X + 12, PAINEL_Y + 252, PAINEL_W - 24, 105)

    pygame.draw.rect(tela, (18, 20, 28), estado_box, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, estado_box, 1, border_radius=10)

    infos = [
        f"Posição: ({sim.rover.x}, {sim.rover.y})",
        f"Direção: {sim.rover.direcao}",
        f"Próxima instrução: {sim.indice + 1 if sim.indice < len(sim.comandos) else '-'}",
        f"Comandos executados: {sim.indice}/{len(sim.comandos)}",
    ]

    for idx, info in enumerate(infos):

        # limita tamanho do texto
        texto = info[:42]

        render = FONTE_PEQUENA.render(texto, True, COR_TEXTO)

        tela.blit(
            render,
            (
                estado_box.x + 10,
                estado_box.y + 8 + idx * 22
            )
        )

    log_box = pygame.Rect(PAINEL_X + 12, PAINEL_Y + 344, PAINEL_W - 24, 118)

    pygame.draw.rect(tela, COR_LOG, log_box, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, log_box, 1, border_radius=10)

    log_titulo = FONTE_MEDIA.render("LOG DE EXECUÇÃO", True, COR_TEXTO)
    tela.blit(log_titulo, (log_box.x + 10, log_box.y + 8))

    logs_visiveis = sim.log[-4:]

    for i, linha in enumerate(logs_visiveis):
        render = FONTE_MINI.render(linha[:68], True, COR_SUB)

        tela.blit(
            render,
            (
                log_box.x + 10,
                log_box.y + 34 + i * 17
            )
        )


def desenhar_legenda(tela):
    legenda_box = pygame.Rect(GRID_X, LEGENDA_Y, GRID_W, LEGENDA_H)

    pygame.draw.rect(tela, (16, 18, 26), legenda_box, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, legenda_box, 1, border_radius=10)

    titulo = FONTE_MEDIA.render("Comandos válidos:", True, COR_TEXTO)
    tela.blit(titulo, (legenda_box.x + 12, legenda_box.y + 8))

    comandos = [
        "AVANCA n        -> Move para frente",
        "RECUA n         -> Move para trás",
        "LEFT / RIGHT    -> Rotaciona rover",
        "DETECT          -> Detecta obstáculo",
        "REPEAT n { }    -> Repete comandos"
    ]

    for i, comando in enumerate(comandos):

        render = FONTE_PEQUENA.render(
            comando,
            True,
            COR_SUB
        )

        tela.blit(
            render,
            (
                legenda_box.x + 14,
                legenda_box.y + 30 + i * 16
            )
        )


def desenhar_tela_inicial(tela, mouse_pos, btn_iniciar, btn_desafio, btn_sair):
    tela.fill(COR_FUNDO)
    desenhar_estrelas(tela)

    pygame.draw.circle(tela, (200, 200, 210), (1130, 120), 70)
    pygame.draw.circle(tela, (160, 160, 170), (1105, 100), 18)
    pygame.draw.circle(tela, (140, 140, 150), (1160, 140), 15)
    pygame.draw.circle(tela, (170, 170, 180), (1145, 95), 10)

    pygame.draw.rect(tela, COR_AREIA_ESCURA, (0, ALTURA - 180, LARGURA, 180))
    pygame.draw.circle(tela, (120, 120, 130), (100, ALTURA - 50), 60)
    pygame.draw.circle(tela, (95, 95, 105), (240, ALTURA - 20), 90)
    pygame.draw.circle(tela, (135, 135, 145), (410, ALTURA - 60), 65)
    pygame.draw.circle(tela, (110, 110, 120), (700, ALTURA - 10), 120)

    titulo = FONTE_TITULO_GRANDE.render("ROVER ESPACIAL", True, COR_BRANCO)
    subtitulo = FONTE_TITULO.render("PROJETO ARES - MISSÃO LUNAR", True, COR_LUZ)

    descricao = FONTE_MEDIA.render(
        "Simulador com comandos, regex e exploração em grid 2D",
        True,
        COR_SUB,
    )

    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 150)))
    tela.blit(subtitulo, subtitulo.get_rect(center=(LARGURA // 2, 205)))
    tela.blit(descricao, descricao.get_rect(center=(LARGURA // 2, 250)))

    rx = LARGURA // 2
    ry = 340

    pygame.draw.ellipse(tela, (35, 35, 40), (rx - 55, ry + 38, 110, 20))
    pygame.draw.rect(tela, COR_ROVER, (rx - 35, ry, 70, 30), border_radius=6)
    pygame.draw.rect(tela, (180, 185, 200), (rx - 20, ry - 12, 40, 10), border_radius=3)

    pygame.draw.circle(tela, COR_PRETO, (rx - 42, ry + 38), 10)
    pygame.draw.circle(tela, COR_PRETO, (rx + 42, ry + 38), 10)

    pygame.draw.line(tela, COR_ROVER, (rx, ry), (rx, ry - 34), 3)
    pygame.draw.circle(tela, COR_LUZ, (rx, ry - 34), 5)

    pygame.draw.line(tela, COR_LUZ, (rx + 15, ry + 12), (rx + 70, ry - 6), 3)
    pygame.draw.circle(tela, COR_LUZ, (rx + 70, ry - 6), 4)

    texto_info = FONTE_MEDIA.render(
        "1. Compile scripts  |  2. Execute automaticamente  |  3. Desvie de obstáculos na Lua",
        True,
        COR_TEXTO
    )

    tela.blit(
        texto_info,
        texto_info.get_rect(center=(LARGURA // 2, 455))
)

    btn_iniciar.desenhar(tela, mouse_pos)
    btn_desafio.desenhar(tela, mouse_pos)
    btn_sair.desenhar(tela, mouse_pos)


def tela_inicial():
    btn_iniciar = Botao(LARGURA // 2 - 120, 500, 240, 50, "Iniciar Simulação")
    btn_desafio = Botao(LARGURA // 2 - 120, 560, 240, 50, "Modo missão espacial")
    btn_sair = Botao(LARGURA // 2 - 120, 620, 240, 42, "Sair")
    rodando = True

    while rodando:
        mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            
            if evento.type == pygame.QUIT:
                rodando = False

            if btn_iniciar.clicou(evento):
                SOM_CLICK.play()
                return "normal"

            if btn_desafio.clicou(evento):
                SOM_CLICK.play()
                return "desafio"

            if btn_sair.clicou(evento):
                SOM_CLICK.play()
                rodando = False

        desenhar_tela_inicial(TELA, mouse, btn_iniciar, btn_desafio, btn_sair)

        pygame.display.flip()
        CLOCK.tick(FPS)

    return False
        
def desenhar_tela_vitoria(tela, mouse_pos, btn_reiniciar, btn_menu, confetes):

    overlay = pygame.Surface((LARGURA, ALTURA))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))

    tela.blit(overlay, (0, 0))

    caixa = pygame.Rect(
        LARGURA // 2 - 250,
        ALTURA // 2 - 170,
        500,
        340
    )

    pygame.draw.rect(tela, (25, 28, 40), caixa, border_radius=18)
    pygame.draw.rect(tela, (255, 215, 0), caixa, 3, border_radius=18)

    titulo = FONTE_TITULO_GRANDE.render(
        "MISSÃO CONCLUÍDA",
        True,
        (255, 215, 0)
    )

    subtitulo = FONTE_MEDIA.render(
        "O rover encontrou o objetivo espacial.",
        True,
        COR_BRANCO
    )

    tela.blit(
        titulo,
        titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 70))
    )

    tela.blit(
        subtitulo,
        subtitulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 20))
    )

    btn_reiniciar.desenhar(tela, mouse_pos)
    btn_menu.desenhar(tela, mouse_pos)

    # confetes
    for confete in confetes:

        pygame.draw.rect(
            tela,
            confete["cor"],
            (
                confete["x"],
                confete["y"],
                confete["tam"],
                confete["tam"]
            )
        )

        confete["y"] += confete["vel"]

        if confete["y"] > ALTURA:
            confete["y"] = random.randint(-200, -20)
   
def tela_jogo(modo="normal"):
    script = SCRIPT_EXEMPLO
    scroll_script = 0
    backspace_pressionado = False
    backspace_inicio_tick = 0
    backspace_ultimo_tick = 0

    simulador = SimuladorRover()

    if modo == "desafio":
        script = ""
        simulador.gerar_desafio()

    ultima_posicao = (simulador.rover.x, simulador.rover.y)

    btn_reset = Botao(PAINEL_X, BTN_Y, BTN_W, BTN_H, "Reset")
    btn_compilar = Botao(PAINEL_X + (BTN_W + BTN_GAP), BTN_Y, BTN_W, BTN_H, "Compilar")
    btn_executar = Botao(PAINEL_X + 2 * (BTN_W + BTN_GAP), BTN_Y, BTN_W, BTN_H, "Executar")
    btn_voltar = Botao(PAINEL_X + 3 * (BTN_W + BTN_GAP), BTN_Y, BTN_W, BTN_H, "Voltar")

    vitoria = False

    tempo_vitoria = None

    btn_reiniciar = Botao(
        LARGURA // 2 - 110,
        ALTURA // 2 + 40,
        220,
        50,
        "Nova missão"
    )

    btn_menu_vitoria = Botao(
        LARGURA // 2 - 110,
        ALTURA // 2 + 105,
        220,
        50,
        "Voltar ao menu"
    )

    rodando = True

    confetes = []

    for i in range(120):

        confetes.append({
            "x": random.randint(0, LARGURA),
            "y": random.randint(-ALTURA, 0),
            "vel": random.randint(3, 8),
            "tam": random.randint(4, 8),
            "cor": random.choice([
                (255, 80, 80),
                (80, 255, 120),
                (80, 180, 255),
                (255, 220, 70),
                (255, 120, 255)
            ])
        })

    while rodando:
        mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():

            if vitoria:

                if btn_reiniciar.clicou(evento):

                    SOM_CLICK.play()

                    simulador = SimuladorRover()
                    simulador.gerar_desafio()

                    script = ""
                    vitoria = False

                elif btn_menu_vitoria.clicou(evento):

                    SOM_CLICK.play()
                    return "menu"

                continue

            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.MOUSEWHEEL:
                total_linhas = len(script.splitlines())
                max_scroll = max(0, total_linhas - 11)

                if evento.y > 0:
                    scroll_script = max(0, scroll_script - 1)
                elif evento.y < 0:
                    scroll_script = min(max_scroll, scroll_script + 1)

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_BACKSPACE:
                    script = apagar_ultimo_caractere(script)
                    agora = pygame.time.get_ticks()
                    backspace_pressionado = True
                    backspace_inicio_tick = agora
                    backspace_ultimo_tick = agora

                elif evento.key == pygame.K_TAB:
                    script += "    "

                elif evento.key == pygame.K_RETURN:
                    script += "\n"

                    total_linhas = len(script.splitlines())
                    max_scroll = max(0, total_linhas - 11)
                    scroll_script = max_scroll

                elif evento.key == pygame.K_UP:
                    scroll_script = max(0, scroll_script - 1)

                elif evento.key == pygame.K_DOWN:
                    total_linhas = len(script.splitlines())
                    max_scroll = max(0, total_linhas - 11)
                    scroll_script = min(max_scroll, scroll_script + 1)

                else:
                    if evento.unicode and evento.unicode.isprintable():
                        script += evento.unicode

                        total_linhas = len(script.splitlines())
                        max_scroll = max(0, total_linhas - 11)

                        if len(script.splitlines()) > 11:
                            scroll_script = max_scroll

            elif evento.type == pygame.KEYUP:
                if evento.key == pygame.K_BACKSPACE:
                    backspace_pressionado = False

            elif btn_compilar.clicou(evento):

                SOM_CLICK.play()

                simulador.resetar_estado()
                try:
                    arvore = validar_e_compilar(script)
                    simulador.carregar_programa(arvore)

                except ParseError as e:
                    SOM_ERRO.play()

                    simulador.status = str(e)
                    simulador.cor_status = COR_ERRO
                    simulador.log.append("Erro de compilação.")

            elif btn_executar.clicou(evento):
                if simulador.comandos:
                    simulador.executando = True

                    SOM_CLICK.play()

                    simulador.finalizado = False
                    simulador.status = "Executando..."
                    simulador.cor_status = COR_ALERTA
                    simulador.tempo_ultimo_passo = pygame.time.get_ticks()

                else:
                    simulador.status = "Compile o script antes de executar."
                    simulador.cor_status = COR_ERRO

            elif btn_voltar.clicou(evento):
                SOM_CLICK.play()
                return "menu"

            elif btn_reset.clicou(evento):

                SOM_CLICK.play()

                simulador.resetar_estado()

                if simulador.modo_desafio:
                    script = ""
                else:
                    script = SCRIPT_EXEMPLO

        teclas = pygame.key.get_pressed()

        if backspace_pressionado and not teclas[pygame.K_BACKSPACE]:
            backspace_pressionado = False

        if backspace_pressionado and script:
            agora = pygame.time.get_ticks()
            passou_delay = agora - backspace_inicio_tick >= BACKSPACE_DELAY_INICIAL
            passou_intervalo = agora - backspace_ultimo_tick >= BACKSPACE_INTERVALO

            if passou_delay and passou_intervalo:
                script = apagar_ultimo_caractere(script)
                backspace_ultimo_tick = agora

        total_linhas = len(script.splitlines())
        max_scroll = max(0, total_linhas - 11)
        scroll_script = min(scroll_script, max_scroll)

        simulador.atualizar()

        # vitória modo desafio
        if (
            not vitoria
            and tempo_vitoria is None
            and simulador.modo_desafio
            and simulador.objetivo
            and (simulador.rover.x, simulador.rover.y) == simulador.objetivo
        ):

            simulador.executando = False

            tempo_vitoria = pygame.time.get_ticks()

        if tempo_vitoria is not None and not vitoria:

            agora = pygame.time.get_ticks()

            if agora - tempo_vitoria >= 500:

                SOM_VITORIA.play()

                vitoria = True

        posicao_atual = (simulador.rover.x, simulador.rover.y)

        if posicao_atual != ultima_posicao:


            pygame.time.delay(100)

            SOM_MOVIMENTO.play()

            ultima_posicao = posicao_atual

        TELA.fill(COR_FUNDO)

        desenhar_estrelas(TELA)
        desenhar_grid(TELA, simulador)
        desenhar_legenda(TELA)
        desenhar_painel(TELA, script, simulador, scroll_script)

        btn_reset.desenhar(TELA, mouse)
        btn_compilar.desenhar(TELA, mouse)
        btn_executar.desenhar(TELA, mouse)
        btn_voltar.desenhar(TELA, mouse)

        if vitoria:
            desenhar_tela_vitoria(
                TELA,
                mouse,
                btn_reiniciar,
                btn_menu_vitoria,
                confetes
    )

        pygame.display.flip()
        CLOCK.tick(FPS) 

def executar_app():
    while True:
        modo = tela_inicial()

        if not modo:
            break

        resultado = tela_jogo(modo)

        if resultado != "menu":
            break

    pygame.quit()


if __name__ == "__main__":
    executar_app()
