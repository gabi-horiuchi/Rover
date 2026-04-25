import pygame
from math import cos, sin, radians

from simulador import SimuladorRover
from parser_rover import validar_e_compilar, ParseError

pygame.init()
pygame.font.init()

LARGURA = 1300
ALTURA = 700
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Rover Espacial - PROJETO ARES")
CLOCK = pygame.time.Clock()
FPS = 60


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
LEGENDA_H = 88

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
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            rect = pygame.Rect(GRID_X + x * CELL, GRID_Y + y * CELL, CELL, CELL)

            cor = COR_AREIA if (x + y) % 2 == 0 else COR_AREIA_ESCURA
            pygame.draw.rect(tela, cor, rect)
            pygame.draw.rect(tela, COR_GRADE, rect, 1)

            if (x, y) in sim.obstaculos:
                pygame.draw.circle(tela, COR_OBS, rect.center, CELL // 3)
                pygame.draw.circle(tela, (120, 120, 130), rect.center, CELL // 4, 2)

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
        numero = str(scroll_script + i + 1).rjust(2)
        texto = f"{numero} | {linha}"

        render = FONTE_PEQUENA.render(texto[:75], True, COR_TEXTO)
        tela.blit(render, (editor.x + 10, y))

        y += 17

    total_linhas = len(linhas)
    fim = min(scroll_script + max_linhas_visiveis, total_linhas)

    info_scroll = FONTE_MINI.render(
        f"Linhas {scroll_script + 1}-{fim} de {total_linhas}",
        True,
        COR_SUB
    )
    tela.blit(info_scroll, (editor.x + 20, editor.y + editor.h - 18))

    seta = FONTE_MEDIA.render("↑↓", True, COR_LUZ)
    tela.blit(seta, (editor.x + editor.w - 35, editor.y + editor.h - 25))

    status_txt = FONTE_MEDIA.render(sim.status[:58], True, sim.cor_status)
    tela.blit(status_txt, (PAINEL_X + 12, PAINEL_Y + 222))

    estado_box = pygame.Rect(PAINEL_X + 12, PAINEL_Y + 252, PAINEL_W - 24, 82)
    pygame.draw.rect(tela, (18, 20, 28), estado_box, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, estado_box, 1, border_radius=10)

    infos = [
        f"Posição: ({sim.rover.x}, {sim.rover.y})",
        f"Direção: {sim.rover.direcao}",
        f"Próxima instrução: {sim.indice + 1 if sim.indice < len(sim.comandos) else '-'}",
    ]

    for idx, info in enumerate(infos):
        render = FONTE_MEDIA.render(info, True, COR_TEXTO)
        tela.blit(render, (estado_box.x + 10, estado_box.y + 8 + idx * 23))

    log_box = pygame.Rect(PAINEL_X + 12, PAINEL_Y + 344, PAINEL_W - 24, 118)
    pygame.draw.rect(tela, COR_LOG, log_box, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, log_box, 1, border_radius=10)

    log_titulo = FONTE_MEDIA.render("LOG DE EXECUÇÃO", True, COR_TEXTO)
    tela.blit(log_titulo, (log_box.x + 10, log_box.y + 8))

    logs_visiveis = sim.log[-4:]

    for i, linha in enumerate(logs_visiveis):
        render = FONTE_MINI.render(linha[:68], True, COR_SUB)
        tela.blit(render, (log_box.x + 10, log_box.y + 34 + i * 17))


def desenhar_legenda(tela):
    legenda_box = pygame.Rect(GRID_X, LEGENDA_Y, GRID_W, LEGENDA_H)

    pygame.draw.rect(tela, (16, 18, 26), legenda_box, border_radius=10)
    pygame.draw.rect(tela, COR_PAINEL_BORDA, legenda_box, 1, border_radius=10)

    titulo = FONTE_MEDIA.render("Comandos válidos:", True, COR_TEXTO)
    tela.blit(titulo, (legenda_box.x + 12, legenda_box.y + 8))

    linha1 = "AVANCA n   RECUA n   LEFT   RIGHT"
    linha2 = "DETECT   IF OBSTACLE THEN RIGHT"
    linha3 = "REPEAT n { comandos }"

    tela.blit(FONTE_PEQUENA.render(linha1, True, COR_SUB), (legenda_box.x + 12, legenda_box.y + 30))
    tela.blit(FONTE_PEQUENA.render(linha2, True, COR_SUB), (legenda_box.x + 12, legenda_box.y + 48))
    tela.blit(FONTE_PEQUENA.render(linha3, True, COR_SUB), (legenda_box.x + 12, legenda_box.y + 66))


def desenhar_tela_inicial(tela, mouse_pos, btn_iniciar, btn_sair):
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
    ry = 380

    pygame.draw.ellipse(tela, (35, 35, 40), (rx - 55, ry + 38, 110, 20))
    pygame.draw.rect(tela, COR_ROVER, (rx - 35, ry, 70, 30), border_radius=6)
    pygame.draw.rect(tela, (180, 185, 200), (rx - 20, ry - 12, 40, 10), border_radius=3)

    pygame.draw.circle(tela, COR_PRETO, (rx - 42, ry + 38), 10)
    pygame.draw.circle(tela, COR_PRETO, (rx + 42, ry + 38), 10)

    pygame.draw.line(tela, COR_ROVER, (rx, ry), (rx, ry - 34), 3)
    pygame.draw.circle(tela, COR_LUZ, (rx, ry - 34), 5)

    pygame.draw.line(tela, COR_LUZ, (rx + 15, ry + 12), (rx + 70, ry - 6), 3)
    pygame.draw.circle(tela, COR_LUZ, (rx + 70, ry - 6), 4)

    info1 = FONTE_MEDIA.render("• Compile scripts", True, COR_TEXTO)
    info2 = FONTE_MEDIA.render("• Execute automaticamente", True, COR_TEXTO)
    info3 = FONTE_MEDIA.render("• Desvie de obstáculos na Lua", True, COR_TEXTO)

    tela.blit(info1, info1.get_rect(center=(LARGURA // 2, 470)))
    tela.blit(info2, info2.get_rect(center=(LARGURA // 2, 500)))
    tela.blit(info3, info3.get_rect(center=(LARGURA // 2, 530)))

    btn_iniciar.desenhar(tela, mouse_pos)
    btn_sair.desenhar(tela, mouse_pos)


def tela_inicial():
    btn_iniciar = Botao(LARGURA // 2 - 120, 580, 240, 50, "Iniciar Missão")
    btn_sair = Botao(LARGURA // 2 - 120, 640, 240, 42, "Sair")

    rodando = True

    while rodando:
        mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if btn_iniciar.clicou(evento):
                return True

            if btn_sair.clicou(evento):
                rodando = False

        desenhar_tela_inicial(TELA, mouse, btn_iniciar, btn_sair)

        pygame.display.flip()
        CLOCK.tick(FPS)

    return False


def tela_jogo():
    script = SCRIPT_EXEMPLO
    scroll_script = 0
    simulador = SimuladorRover()

    btn_reset = Botao(PAINEL_X, BTN_Y, BTN_W, BTN_H, "Reset")
    btn_compilar = Botao(PAINEL_X + (BTN_W + BTN_GAP), BTN_Y, BTN_W, BTN_H, "Compilar")
    btn_executar = Botao(PAINEL_X + 2 * (BTN_W + BTN_GAP), BTN_Y, BTN_W, BTN_H, "Executar")
    btn_voltar = Botao(PAINEL_X + 3 * (BTN_W + BTN_GAP), BTN_Y, BTN_W, BTN_H, "Voltar")

    rodando = True

    while rodando:
        mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
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
                    script = script[:-1]

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

            elif btn_voltar.clicou(evento):
                return "menu"

            elif btn_reset.clicou(evento):
                simulador.resetar()

        total_linhas = len(script.splitlines())
        max_scroll = max(0, total_linhas - 11)
        scroll_script = min(scroll_script, max_scroll)

        simulador.atualizar()

        TELA.fill(COR_FUNDO)

        desenhar_estrelas(TELA)
        desenhar_grid(TELA, simulador)
        desenhar_legenda(TELA)
        desenhar_painel(TELA, script, simulador, scroll_script)

        btn_reset.desenhar(TELA, mouse)
        btn_compilar.desenhar(TELA, mouse)
        btn_executar.desenhar(TELA, mouse)
        btn_voltar.desenhar(TELA, mouse)

        pygame.display.flip()
        CLOCK.tick(FPS)
def executar_app():
    while True:
        if not tela_inicial():
            break

        resultado = tela_jogo()

        if resultado != "menu":
            break

    pygame.quit()


if __name__ == "__main__":
    executar_app()
