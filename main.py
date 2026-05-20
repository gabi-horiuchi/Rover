import pygame

from interface import tela_inicial, tela_jogo

pygame.init()

def executar_app():
    rodando = True

    while rodando:
        iniciar = tela_inicial()

        if not iniciar:
            break 

        tela_jogo() 

if __name__ == "__main__":
    executar_app()