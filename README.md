
# PROJETO ARES

Simulador de Rover Espacial desenvolvido em Python + Pygame.

# Ferramentas Utilizadas

- Python 3.13
- Pygame

Para executar:
1- Acesse a pasta
2-Instale as dependências
  pip install pygame
3-Execute o projeto
  python main.py

Exemplo de Script
FRONT 3
RIGHT
FRONT 2
DETECT

IF OBSTACLE THEN RIGHT

REPEAT 2 {
    FRONT 1
    LEFT
}
BACK 1

Comandos Disponíveis
Comando	  Função
FRONT n	Move o rover para frente
BACK n   Move o rover para trás
LEFT	    Gira para esquerda
RIGHT    	Gira para direita
DETECT	  Detecta obstáculos
REPEAT {}	Repete comandos
IF OBSTACLE THEN RIGHT	Desvia de obstáculos

Status do Projeto

CONCLUIDO
