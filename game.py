import pygame
import sys
import random
import time
import sqlite3

# Inicializando o pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jogo de Programação")

# Carregar a fonte PressStart2P.ttf
font = pygame.font.Font("PressStart2P.ttf", 36)

# Carregar sons
collision_sound = pygame.mixer.Sound("collision.wav")
correct_answer_sound = pygame.mixer.Sound("correct_answer.wav")
wrong_answer_sound = pygame.mixer.Sound("wrong_answer.wav")
move = pygame.mixer.Sound("move.wav")
suspense = pygame.mixer.Sound("suspense.wav")

# Ajustar o volume dos sons
collision_sound.set_volume(0.2)
correct_answer_sound.set_volume(0.2)
wrong_answer_sound.set_volume(0.2)
move.set_volume(0.2)
suspense.set_volume(0.2)

# Configurações das cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Configurações do jogador
player_size = 20
player_speed = 5

# Configurações da porta
door_size = [40, 80]

# Configurações do computador
computer_size = [20, 20]

# Banco de dados SQLite
conn = sqlite3.connect('ranking.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS ranking
             (initials TEXT, score INTEGER)''')
conn.commit()

# Perguntas e respostas
questions = {
    "matematica": [
        ("2 + 2", "4"),
        ("3 * 3", "9"),
        ("5 + 5", "10"),
        ("5 - 2", "3"),
        ("6 / 2", "3"),
        ("8 + 1", "9"),
        ("10 - 4", "6"),
        ("6 + 6", "12")
    ],
    "futebol": [
        ("Primeira letra do \nmelhor time das Américas?", "f"),
        ("Última letra do \ntime mais rebaixado\ndo rio?", "o")
    ],
    "programacao": [
        ("Extensão de arquivo \nPython?", "py"),
        ("Palavra-chave para \ndefinir uma função?", "def")
    ],
    "desenhos_animados": [
        ("Qual é o amigo do \nMickey?", "pluto"),
        ("Nome do Bob \nEsponja?", "bob")
    ],
    "historia": [
        ("Ano da Independência \ndo Brasil?", "1822"),
        ("Quem descobriu \na América?", "colombo")
    ]
}

# Variáveis de controle do jogo
current_question = 0
entered_password = ""
password_parts = []
password_correct = False
game_over = False
computer_flash = False
time_limit = 10  # Tempo inicial para responder a pergunta
countdown = time_limit
difficulty_level = 1
current_score = 0
correct_answers = 0

# Configurações de texto
font = pygame.font.Font("PressStart2P.ttf", 20)

# Carregar sprites
player_img = pygame.image.load("player.png").convert_alpha()
door_img = pygame.image.load("door.png").convert_alpha()
computer_img = pygame.image.load("computer.png").convert_alpha()
background_image = pygame.image.load("background.jpg").convert()

# Classes de sprites
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (220, 395)

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= player_speed
            if self.rect.x < -5:
                self.rect.x = -5
            move.play()
        if keys[pygame.K_RIGHT]:
            self.rect.x += player_speed
            if self.rect.x > 660:
                self.rect.x = 660
            move.play()
        if keys[pygame.K_UP]:
            self.rect.y -= player_speed
            if self.rect.y < 395:
                self.rect.y = 395
            move.play()
        if keys[pygame.K_DOWN]:
            self.rect.y += player_speed
            if self.rect.y > 515:
                self.rect.y = 515
            move.play()

class Door(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = door_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (50, 450)

class Computer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = computer_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (220, 395)

    def move(self):
        min_x = 220
        max_x = 660
        min_y = 395
        max_y = 515
        self.rect.topleft = (random.randint(min_x, max_x), random.randint(min_y, max_y))

# Função para exibir texto na tela ou em uma superfície específica
def draw_text(text, pos, color=WHITE, surface=None):
    if surface is None:
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, pos)
    else:
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, pos)
def draw_multiline_text(text, pos, color=WHITE):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        draw_text(line, (pos[0], pos[1] + i * 30), color)

# Função para reiniciar o jogo
def reset_game():
    global current_question, current_score, entered_password, password_parts, password_correct, game_over, time_limit, countdown, correct_answers
    player.rect.topleft = (220, 395)
    password_parts = []
    current_question = 0
    entered_password = ""
    password_correct = False
    game_over = False
    computer.move()
    time_limit = 10
    countdown = time_limit
    current_score = 0
    correct_answers = 0

# Função para perguntar e responder
def ask_question(category):
    global current_question, password_correct, password_parts, countdown, game_over, current_score, correct_answers
    start_time = time.time()
    
    question_list = questions[category]
    
    if current_question == len(question_list):
        draw_text("Vá até a porta", (50, 50), YELLOW)
        pygame.display.flip()
        suspense.play()
        return
    else:
        question, correct_answer = question_list[current_question]
        user_answer = ""
        answer_done = False
        while not answer_done:
            elapsed_time = time.time() - start_time
            countdown = time_limit - elapsed_time
            if countdown <= 0:
                game_over = True
                return

            screen.fill(BLACK)
            all_sprites.draw(screen)
            draw_multiline_text(f"Pergunta: {question} =", (50, 50))
            draw_text(user_answer, (50, 100))
            draw_text(f"Tempo restante: {int(countdown)}", (250, 570), RED)
            pygame.display.flip()
            suspense.play()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        answer_done = True
                    elif event.key == pygame.K_BACKSPACE:
                        user_answer = user_answer[:-1]
                    else:
                        user_answer += event.unicode

        if user_answer == correct_answer:
            password_parts.append(user_answer)
            current_question += 1
            correct_answers += 1
            current_score += 1 + int(time_limit - elapsed_time)
            computer.move()
            correct_answer_sound.play()
        else:
            game_over = True
            wrong_answer_sound.play()

# Função para exibir o ranking
def display_ranking():
    screen.fill(BLACK)
    draw_text("Ranking", (280, 50), YELLOW)
    c.execute("SELECT * FROM ranking ORDER BY score DESC LIMIT 5")
    rankings = c.fetchall()
    for i, (initials, score) in enumerate(rankings):
        draw_text(f"{i+1}. {initials} - {score}", (280, 150 + i * 50), WHITE)
    draw_text("Pressione Enter para voltar", (200, 500), WHITE)
    pygame.display.flip()
    wait_for_enter()

# Função para exibir a tela de menu sobre a imagem do jogo
def display_menu_over_game():
    # Criar uma superfície temporária com transparência
    menu_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    menu_surface.fill((0, 0, 0, 128))  # 128 é a transparência

    # Desenhar a tela do menu na superfície
    draw_text("Menu Inicial", (280, 50), YELLOW, surface=menu_surface)
    draw_text("1. Jogar", (280, 150), WHITE, surface=menu_surface)
    draw_text("2. Ver Ranking", (280, 200), WHITE, surface=menu_surface)
    draw_text("3. Sobre", (280, 250), WHITE, surface=menu_surface)
    draw_text("4. Sair", (280, 300), WHITE, surface=menu_surface)

    # Desenhar a superfície sobre a imagem de fundo do jogo
    screen.blit(background_image, (0, 0))
    screen.blit(menu_surface, (0, 0))

    pygame.display.flip()

# Função para exibir o menu inicial
def display_menu():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    display_category_menu()  # Removendo a definição de 'running = False' para exibir o menu de categorias
                elif event.key == pygame.K_2:
                    display_ranking()
                elif event.key == pygame.K_3:
                    display_about()
                elif event.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()
        
        # Exibir o menu sobre a imagem do jogo
        display_menu_over_game()



# Função para exibir o menu de categorias
def display_category_menu():
    running = True
    while running:
        screen.blit(background_image, (0, 0))  # Desenhar a imagem de fundo do jogo
        draw_text("Menu de Categorias", (280, 50), YELLOW)  # Desenhar o título do menu
        draw_text("1. Matemática", (280, 150), WHITE)  # Desenhar as opções de categoria
        draw_text("2. Futebol", (280, 200), WHITE)
        draw_text("3. Programação", (280, 250), WHITE)
        draw_text("4. Desenhos Animados", (280, 300), WHITE)
        draw_text("5. História", (280, 350), WHITE)
        pygame.display.flip()  # Atualizar a tela

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    running = False
                    main_game_loop("matematica")
                elif event.key == pygame.K_2:
                    running = False
                    main_game_loop("futebol")
                elif event.key == pygame.K_3:
                    running = False
                    main_game_loop("programacao")
                elif event.key == pygame.K_4:
                    running = False
                    main_game_loop("desenhos_animados")
                elif event.key == pygame.K_5:
                    running = False
                    main_game_loop("historia")

# Função para exibir a tela de "About"
def display_about():
    screen.fill(BLACK)
    draw_text("Sobre", (350, 50), YELLOW)
    draw_multiline_text("Este jogo foi criado para\npraticar programação\nusando Pygame.\nDivirta-se!", (200, 150), WHITE)
    draw_text("Pressione Enter para voltar", (200, 500), WHITE)
    pygame.display.flip()
    wait_for_enter()

# Função para esperar pelo pressionamento da tecla Enter
def wait_for_enter():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    display_menu()

# Função principal do jogo
def main_game_loop(category):
    global game_over, password_correct, start_time, time_limit,clock
    reset_game()
    running = True
    clock = pygame.time.Clock()
    start_time = time.time()

    while running:
        screen.blit(background_image, (0, 0))

        elapsed_time = time.time() - start_time
        countdown = time_limit - elapsed_time

        if countdown <= 0:
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys)

        if keys[pygame.K_RETURN]:
            if pygame.sprite.collide_rect(player, computer):
                ask_question(category)
                start_time = time.time()

            if pygame.sprite.collide_rect(player, door):
                password_correct = True

        all_sprites = pygame.sprite.Group()
        all_sprites.add(computer)
        all_sprites.add(door)
        all_sprites.add(player)

        all_sprites.draw(screen)

        if game_over:
            draw_text("Game Over", (350, 300), RED)
            pygame.display.flip()
            time.sleep(2)
            if current_score > 0:
                save_score()
                display_ranking()
            reset_game()
            display_menu()
            start_time = time.time()
            continue

        if current_question == 6 and password_correct:
            if password_correct:

                if pygame.sprite.collide_rect(player, door):
                    draw_text("Senha correta!", (50, 100), GREEN)
                    pygame.display.flip()
                    time.sleep(2)

                    if difficulty_level < 5:
                        difficulty_level += 1
                        time_limit -= 1
                    if current_score > 0:
                        save_score()
                    reset_game()
                    display_menu()
                    start_time = time.time()

        if password_correct:
            for _ in range(6):
                screen.fill(BLACK)
                draw_text("Acesso liberado!", (250, 300), GREEN)
                pygame.display.flip()
                time.sleep(0.5)
                screen.fill(BLACK)
                pygame.display.flip()
                time.sleep(0.5)
            draw_text("Vá até a porta para vencer o jogo", (200, 400), GREEN)

        draw_text(" ".join(password_parts), (50, 100))
        draw_text(f"Score: {current_score}", (50, 550))
        draw_text(f"Tempo restante: {int(countdown)}", (420, 550), YELLOW)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()
# Função para solicitar as iniciais do jogador na tela do jogo
def ask_initials():
    initials = ""
    input_active = True
    while input_active:
        screen.fill(BLACK)
        draw_text("Digite suas iniciais (3 letras):", (50, 250), WHITE)
        draw_text(initials, (350, 300), YELLOW)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                else:
                    if len(initials) < 3 and event.unicode.isalpha():
                        initials += event.unicode.upper()
    return initials
# Função para salvar a pontuação no banco de dados
# Modificação da função save_score() para usar ask_initials() e mostrar o ranking com a posição do jogador piscando
def save_score():
    initials = ask_initials()
    c.execute("INSERT INTO ranking (initials, score) VALUES (?, ?)", (initials, current_score))
    conn.commit()


# Variáveis de controle do jogo
all_sprites = pygame.sprite.Group()
player = Player()
door = Door()
computer = Computer()
all_sprites.add(computer)
all_sprites.add(door)
all_sprites.add(player)

display_menu()