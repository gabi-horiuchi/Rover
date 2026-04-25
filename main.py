import pygame
import sys
from interface import tela_inicial, tela_jogo

pygame.init()

def main():
    if tela_inicial():
        tela_jogo()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()