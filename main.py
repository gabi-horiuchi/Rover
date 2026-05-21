from interface import tela_inicial, tela_jogo
import pygame


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