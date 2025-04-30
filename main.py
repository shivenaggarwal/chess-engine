import pygame as p
import engine, move_ai

BOARD_SIZE = 512  # square board
MOVE_LOG_WIDTH = 188
WIDTH = BOARD_SIZE + MOVE_LOG_WIDTH
HEIGHT = 512
DIMENSION = 8
BOX_SIZE = BOARD_SIZE // DIMENSION
MAX_FPS = 15
IMAGES = {}

THEMES = {
    "Classic": (p.Color('light gray'), p.Color('dark green')),
    "Blue": (p.Color('white'), p.Color('royal blue')),
    "Brown": (p.Color('cornsilk'), p.Color('saddle brown')),
    "Gray": (p.Color('gainsboro'), p.Color('slate gray')),
}

def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("assets/" + piece + ".png"), (BOX_SIZE, BOX_SIZE))

def selectTheme(screen):
    font = p.font.SysFont('Arial', 28, bold=True)
    small_font = p.font.SysFont('Arial', 20)
    options = list(THEMES.keys())
    button_rects = []

    background_color = p.Color('beige')
    button_color = p.Color('lightblue')
    hover_color = p.Color('deepskyblue')
    text_color = p.Color('black')

    running = True

    while running:
        screen.fill(background_color)

        title = font.render('Choose a Board Theme', True, text_color)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        button_width = 200
        button_height = 50
        start_y = 100
        gap = 20
        mouse_pos = p.mouse.get_pos()
        button_rects.clear()

        for idx, option in enumerate(options):
            rect = p.Rect(
                WIDTH // 2 - button_width // 2,
                start_y + idx * (button_height + gap),
                button_width,
                button_height
            )
            button_rects.append((rect, option))
            
            # Change color on hover
            if rect.collidepoint(mouse_pos):
                color = hover_color
            else:
                color = button_color

            p.draw.rect(screen, color, rect, border_radius=12)
            
            text = small_font.render(option, True, text_color)
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        p.display.flip()

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                for rect, option in button_rects:
                    if rect.collidepoint(e.pos):
                        return THEMES[option]

def selectGameMode(screen):
    font = p.font.SysFont('Arial', 28, bold=True)
    small_font = p.font.SysFont('Arial', 20)
    options = [
        ("Player vs Player", True, True),
        ("Player vs AI", True, False),
        ("AI vs AI", False, False)
    ]
    button_rects = []

    background_color = p.Color('beige')
    button_color = p.Color('lightblue')
    hover_color = p.Color('deepskyblue')
    text_color = p.Color('black')

    while True:
        screen.fill(background_color)

        title = font.render('Choose Game Mode', True, text_color)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        button_width = 250
        button_height = 50
        start_y = 100
        gap = 20
        mouse_pos = p.mouse.get_pos()
        button_rects.clear()

        for idx, (label, p1, p2) in enumerate(options):
            rect = p.Rect(
                WIDTH // 2 - button_width // 2,
                start_y + idx * (button_height + gap),
                button_width,
                button_height
            )
            button_rects.append((rect, p1, p2, label))

            color = hover_color if rect.collidepoint(mouse_pos) else button_color
            p.draw.rect(screen, color, rect, border_radius=12)

            text = small_font.render(label, True, text_color)
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        p.display.flip()

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                for rect, p1, p2, _ in button_rects:
                    if rect.collidepoint(e.pos):
                        return p1, p2


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    gs = engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadImages()
    global colors
    colors = selectTheme(screen)
    running = True
    boxSelected = ()
    playerClicks = []
    gameOver = False
    player_one, player_two = selectGameMode(screen)
    ai_algorithm = None
    if not player_one or not player_two:
        ai_algorithm = selectAlgorithm(screen)

    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        events = p.event.get() 

        for e in events:
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and human_turn:
                    location = p.mouse.get_pos()
                    col = location[0] // BOX_SIZE
                    row = location[1] // BOX_SIZE

                    if boxSelected == (row, col):
                        boxSelected = ()
                        playerClicks = []
                    else:
                        boxSelected = (row, col)
                        playerClicks.append(boxSelected)

                    if len(playerClicks) == 2:
                        move = engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                boxSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [boxSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    validMoves = gs.getValidMoves()
                    moveMade = False
                if e.key == p.K_r:
                    gs = engine.GameState()
                    validMoves = gs.getValidMoves()
                    boxSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False

        # if not gameOver and not human_turn:
        if not gameOver and not human_turn and len(validMoves) > 0:
            if ai_algorithm == "AlphaPruning":
                ai_move = move_ai.findBestMove(gs, validMoves)
            elif ai_algorithm == "NegaMax":
                ai_move = move_ai.findBestMoveNegaMax(gs, validMoves)
            elif ai_algorithm == "Minimax":
                ai_move = move_ai.findBestMoveMinMax(gs, validMoves)
            elif ai_algorithm == "Random":
                ai_move = move_ai.findRandomMove(validMoves)
            else:
                ai_move = move_ai.findRandomMove(validMoves)

            if ai_move is not None:
                gs.makeMove(ai_move)
                moveMade = True

        if moveMade:
            if len(gs.move_log) > 0:
                last_move = gs.move_log[-1]
                animateMove(last_move, screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, colors, validMoves, boxSelected)

        if gs.checkmate or gs.stalemate:
            if gs.checkmate:
                text = 'Black wins by checkmate!' if gs.white_to_move else 'White wins by checkmate!'
            else:
                text = 'Stalemate!'
            gameOver = True

        if gameOver:
            button_rect = drawText(screen, text) 
            for e in events:
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN and button_rect and button_rect.collidepoint(e.pos):
                    gs = engine.GameState()
                    validMoves = gs.getValidMoves()
                    boxSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False

        clock.tick(MAX_FPS)
        p.display.flip()

        
def highlightSquares(screen, gs, validMoves, boxSelected):
    if boxSelected != ():
        row, col = boxSelected
        if gs.board[row][col][0] == ('w' if gs.white_to_move else 'b'):
            # highlight the selected square
            selected_surf = p.Surface((BOX_SIZE, BOX_SIZE))
            selected_surf.set_alpha(100)
            selected_surf.fill(p.Color('blue'))
            screen.blit(selected_surf, (col * BOX_SIZE, row * BOX_SIZE))
            # highlight moves from that square
            move_surf = p.Surface((BOX_SIZE, BOX_SIZE))
            move_surf.set_alpha(100)
            move_surf.fill(p.Color('yellow'))
            for move in validMoves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(move_surf, (move.end_col * BOX_SIZE, move.end_row * BOX_SIZE))
                    
def drawGameState(screen, gs, colors, validMoves, boxSelected):
    drawBoard(screen, colors)
    highlightSquares(screen, gs, validMoves, boxSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs)

def drawBoard(screen, colors):
    # Draw 8x8 board
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * BOX_SIZE, row * BOX_SIZE, BOX_SIZE, BOX_SIZE))

    # Draw a thick border around the board
    border_color = p.Color('black')
    border_rect = p.Rect(0, 0, BOARD_SIZE, HEIGHT)
    p.draw.rect(screen, border_color, border_rect, width=4)

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col * BOX_SIZE, row * BOX_SIZE, BOX_SIZE, BOX_SIZE))
                
def animateMove(move, screen, board, clock):
    global colors
    coords = [] # list of coords that the animation will move through
    dR = move.end_row - move.start_row # delta row
    dC = move.end_col - move.start_col # delta col
    frames_per_square = 10
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + dR * frame / frame_count, move.start_col + dC * frame / frame_count)
        drawBoard(screen, colors)
        border_color = p.Color('black')
        border_rect = p.Rect(0, 0, BOARD_SIZE, HEIGHT)
        p.draw.rect(screen, border_color, border_rect, width=4)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * BOX_SIZE, move.end_row * BOX_SIZE, BOX_SIZE, BOX_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * BOX_SIZE, enpassant_row * BOX_SIZE, BOX_SIZE, BOX_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * BOX_SIZE, row * BOX_SIZE, BOX_SIZE, BOX_SIZE))
        p.display.flip()
        clock.tick(60)
        
def drawText(screen, text):
    font = p.font.SysFont("Arial", 40, True)
    button_font = p.font.SysFont("Arial", 28, True)

    # Dim background
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Render game over text
    text_surface = font.render(text, True, p.Color("white"))
    shadow_surface = font.render(text, True, p.Color("black"))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(shadow_surface, text_rect.move(2, 2))
    screen.blit(text_surface, text_rect)

    # Draw "Play Again" button
    button_text = button_font.render("Play Again", True, p.Color("white"))
    button_rect = p.Rect(0, 0, 180, 50)
    button_rect.center = (WIDTH // 2, HEIGHT // 2 + 40)

    mouse_pos = p.mouse.get_pos()
    color = p.Color("dodgerblue") if button_rect.collidepoint(mouse_pos) else p.Color("royalblue")
    p.draw.rect(screen, color, button_rect, border_radius=12)
    screen.blit(button_text, button_text.get_rect(center=button_rect.center))
    
    return button_rect  # Return the button rect for interaction

def drawMoveLog(screen, gs):
    move_log_font = p.font.SysFont("Courier New", 18)
    header_font = p.font.SysFont("Arial", 22, bold=True)
    move_log_rect = p.Rect(BOARD_SIZE, 0, MOVE_LOG_WIDTH, HEIGHT)
    p.draw.rect(screen, p.Color("lightgray"), move_log_rect)

    # Draw heading background
    header_bg_rect = p.Rect(BOARD_SIZE, 0, MOVE_LOG_WIDTH, 36)
    p.draw.rect(screen, p.Color("darkgray"), header_bg_rect)

    # Draw heading text
    header_text = header_font.render("Move Log", True, p.Color("white"))
    header_pos = header_text.get_rect(center=(BOARD_SIZE + MOVE_LOG_WIDTH // 2, 18))
    screen.blit(header_text, header_pos)

    move_log = gs.move_log
    padding = 10
    top_offset = 40  # space below header
    line_spacing = 24
    max_rows = (HEIGHT - top_offset - 10) // line_spacing
    move_pairs = []
    for i in range(0, len(move_log), 2):
        move_num = f"{i // 2 + 1:2}."
        white_move = move_log[i].getChessNotation()
        black_move = move_log[i + 1].getChessNotation() if i + 1 < len(move_log) else ""
        move_pairs.append(f"{move_num} {white_move:<6} {black_move:<6}")
        
    # Show only the last moves that fit on screen
    move_pairs = move_pairs[-max_rows:]

    for i, move_str in enumerate(move_pairs):
        y = top_offset + i * line_spacing
        if i % 2 == 0:
            row_bg_rect = p.Rect(BOARD_SIZE, y, MOVE_LOG_WIDTH, line_spacing)
            p.draw.rect(screen, p.Color("whitesmoke"), row_bg_rect)

        move_text = move_log_font.render(move_str, True, p.Color("black"))
        screen.blit(move_text, (BOARD_SIZE + padding, y))

def selectAlgorithm(screen):
    font = p.font.SysFont('Arial', 28, bold=True)
    small_font = p.font.SysFont('Arial', 20)
    options = ["Minimax", "Random", "NegaMax", "AlphaPruning"]
    button_rects = []

    background_color = p.Color('beige')
    button_color = p.Color('lightblue')
    hover_color = p.Color('deepskyblue')
    text_color = p.Color('black')

    while True:
        screen.fill(background_color)

        title = font.render('Select AI Algorithm', True, text_color)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        button_width = 200
        button_height = 50
        start_y = 120
        gap = 20
        mouse_pos = p.mouse.get_pos()
        button_rects.clear()

        for idx, algo in enumerate(options):
            rect = p.Rect(
                WIDTH // 2 - button_width // 2,
                start_y + idx * (button_height + gap),
                button_width,
                button_height
            )
            button_rects.append((rect, algo))

            color = hover_color if rect.collidepoint(mouse_pos) else button_color
            p.draw.rect(screen, color, rect, border_radius=12)

            text = small_font.render(algo, True, text_color)
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        p.display.flip()

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                for rect, algo in button_rects:
                    if rect.collidepoint(e.pos):
                        return algo

if __name__ == "__main__":
    main()
