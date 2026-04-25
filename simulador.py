import pygame
from dataclasses import dataclass
from parser_rover import expandir_comandos


GRID_COLS = 12
GRID_ROWS = 12
EXEC_DELAY = 450

COR_SUB = (205, 190, 175)
COR_OK = (110, 200, 120)
COR_ALERTA = (240, 180, 80)


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
        self.rover_px = float(self.rover.x)
        self.rover_py = float(self.rover.y)
        self.angulo_anim = 0.0
        self.velocidade_animacao = 0.14

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
        nx = self.rover.x + dx
        ny = self.rover.y + dy

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

        self.rover_px += (self.rover.x - self.rover_px) * self.velocidade_animacao
        self.rover_py += (self.rover.y - self.rover_py) * self.velocidade_animacao

        angulos_alvo = {
            "N": -90,
            "E": 0,
            "S": 90,
            "W": 180
        }

        alvo = angulos_alvo[self.rover.direcao]
        diferenca = (alvo - self.angulo_anim + 180) % 360 - 180
        self.angulo_anim += diferenca * 0.16