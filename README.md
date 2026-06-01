
# PROJETO ARES

Simulador de Rover Espacial desenvolvido em Python + Pygame.

# Ferramentas Utilizadas

- Python 3.13
- Pygame

Para executar:
1- Acesse a pasta
    cd rover
2-Instale as dependências
  pip install pygame
3-Execute o projeto
  python main.py

Exemplo de Script
AVANCA 3
RIGHT
AVANCA 2
DETECT

IF OBSTACLE THEN RIGHT

REPEAT 2 {
    AVANCA 1
    LEFT
}

Comandos Disponíveis
Comando	  Função
AVANCA n	Move o rover para frente
RECUA n   Move o rover para trás
LEFT	    Gira para esquerda
RIGHT    	Gira para direita
DETECT	  Detecta obstáculos
REPEAT {}	Repete comandos
IF OBSTACLE THEN RIGHT	Desvia de obstáculos

Status do Projeto

Em desenvolvimento
