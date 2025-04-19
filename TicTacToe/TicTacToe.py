import time
import pygame


# Utility function to copy the game state
def copy_game(game):
    """Create a deep copy of the game state"""
    new_game = UltimateTicTacToe()

    # Copy board
    for big_row in range(3):
        for big_col in range(3):
            for small_row in range(3):
                for small_col in range(3):
                    new_game.board[(big_row, big_col)][(small_row, small_col)] = \
                        game.board[(big_row, big_col)][(small_row, small_col)]

    # Copy small board status
    for big_row in range(3):
        for big_col in range(3):
            new_game.small_board_status[(big_row, big_col)] = game.small_board_status[(big_row, big_col)]

    # Copy other game state
    new_game.current_player = game.current_player
    new_game.next_small_board = game.next_small_board
    new_game.game_result = game.game_result

    return new_game

# Function to count potential wins for a player
def count_potential_wins(game, player):
    """Count potential win opportunities for a player"""
    potential_wins = 0

    # Check rows
    for row in range(3):
        row_status = [game.small_board_status[(row, col)] for col in range(3)]
        if row_status.count(player) == 2 and row_status.count(' ') == 1:
            potential_wins += 1

    # Check columns
    for col in range(3):
        col_status = [game.small_board_status[(row, col)] for row in range(3)]
        if col_status.count(player) == 2 and col_status.count(' ') == 1:
            potential_wins += 1

    # Check diagonals
    diag1 = [game.small_board_status[(i, i)] for i in range(3)]
    if diag1.count(player) == 2 and diag1.count(' ') == 1:
        potential_wins += 1

    diag2 = [game.small_board_status[(i, 2 - i)] for i in range(3)]
    if diag2.count(player) == 2 and diag2.count(' ') == 1:
        potential_wins += 1

    return potential_wins

# Function to count empty cells in a small board
class UltimateTicTacToe:
    def __init__(self):
        # Initialize 3x3 grid of 3x3 boards
        self.board = {}
        for big_row in range(3):
            for big_col in range(3):
                self.board[(big_row, big_col)] = {}
                for small_row in range(3):
                    for small_col in range(3):
                        self.board[(big_row, big_col)][(small_row, small_col)] = " "

        # Track the state of each small board: ' ' (in play), 'X' (X won), 'O' (O won), 'D' (draw)
        self.small_board_status = {(i, j): ' ' for i in range(3) for j in range(3)}

        # Current player
        self.current_player = 'X'

        # Next small board to play (None means any board)
        self.next_small_board = None

        # Game status
        self.game_result = None

    def available_moves(self):
        """Returns a list of valid moves as (big_row, big_col, small_row, small_col)"""
        moves = []

        # If next_small_board is specified and not completed
        if self.next_small_board and self.small_board_status[self.next_small_board] == ' ':
            big_row, big_col = self.next_small_board
            for small_row in range(3):
                for small_col in range(3):
                    if self.board[(big_row, big_col)][(small_row, small_col)] == " ":
                        moves.append((big_row, big_col, small_row, small_col))

        # If no specific small board or the specified board is completed
        elif self.next_small_board is None or self.small_board_status[self.next_small_board] != ' ':
            for big_row in range(3):
                for big_col in range(3):
                    # Only consider small boards that aren't completed
                    if self.small_board_status[(big_row, big_col)] == ' ':
                        for small_row in range(3):
                            for small_col in range(3):
                                if self.board[(big_row, big_col)][(small_row, small_col)] == " ":
                                    moves.append((big_row, big_col, small_row, small_col))

        return moves

    def make_move(self, big_row, big_col, small_row, small_col):
        """Make a move and update the game state"""
        # Check if move is valid
        if self.next_small_board is not None:
            if (big_row, big_col) != self.next_small_board and self.small_board_status[self.next_small_board] == ' ':
                return False  # Invalid move - wrong small board

        if self.small_board_status[(big_row, big_col)] != ' ':
            return False  # Invalid move - completed small board

        if self.board[(big_row, big_col)][(small_row, small_col)] != " ":
            return False  # Invalid move - cell already taken

        # Make the move
        self.board[(big_row, big_col)][(small_row, small_col)] = self.current_player

        # Check if the small board is now won
        if self.check_small_board_win(big_row, big_col, self.current_player):
            self.small_board_status[(big_row, big_col)] = self.current_player

            # Check if the game is now won
            if self.check_game_win(self.current_player):
                self.game_result = self.current_player
                return True

        # Check if the small board is now a draw
        elif self.is_small_board_full(big_row, big_col):
            self.small_board_status[(big_row, big_col)] = 'D'

        # Set the next small board
        next_board = (small_row, small_col)
        if self.small_board_status[next_board] == ' ':
            self.next_small_board = next_board
        else:
            self.next_small_board = None  # Player can choose any board

        # Switch player
        self.current_player = 'O' if self.current_player == 'X' else 'X'

        return True

    def check_small_board_win(self, big_row, big_col, player):
        """Check if a small board is won by the player"""
        board = self.board[(big_row, big_col)]

        # Check rows
        for row in range(3):
            if all(board[(row, col)] == player for col in range(3)):
                return True

        # Check columns
        for col in range(3):
            if all(board[(row, col)] == player for row in range(3)):
                return True

        # Check diagonals
        if all(board[(i, i)] == player for i in range(3)):
            return True
        if all(board[(i, 2 - i)] == player for i in range(3)):
            return True

        return False

    def is_small_board_full(self, big_row, big_col):
        """Check if a small board is full"""
        for small_row in range(3):
            for small_col in range(3):
                if self.board[(big_row, big_col)][(small_row, small_col)] == " ":
                    return False
        return True

    def check_game_win(self, player):
        """Check if the game is won by the player"""
        # Check rows
        for row in range(3):
            if all(self.small_board_status[(row, col)] == player for col in range(3)):
                return True

        # Check columns
        for col in range(3):
            if all(self.small_board_status[(row, col)] == player for row in range(3)):
                return True

        # Check diagonals
        if all(self.small_board_status[(i, i)] == player for i in range(3)):
            return True
        if all(self.small_board_status[(i, 2 - i)] == player for i in range(3)):
            return True

        return False

    def is_game_over(self):
        """Check if the game is over"""
        if self.game_result is not None:
            return True

        # Check if all small boards are completed
        for big_row in range(3):
            for big_col in range(3):
                if self.small_board_status[(big_row, big_col)] == ' ':
                    return False

        # All boards are completed
        self.game_result = 'Draw'
        return True

    def print_board(self):
        """Print the current state of the board"""
        for big_row in range(3):
            # Print each row of small boards
            for small_row in range(3):
                line = ""
                for big_col in range(3):
                    for small_col in range(3):
                        line += self.board[(big_row, big_col)][(small_row, small_col)] + " "
                    # Add separator between small boards
                    if big_col < 2:
                        line += "| "
                print(line)
            # Add separator between rows of small boards
            if big_row < 2:
                print("-" * 21)

        # Print small board status
        print("\nSmall Board Status:")
        for big_row in range(3):
            line = ""
            for big_col in range(3):
                status = self.small_board_status[(big_row, big_col)]
                line += status if status != ' ' else '-'
                line += " "
            print(line)

        # Print next small board
        if self.next_small_board:
            print(f"Next small board: {self.next_small_board}")
        else:
            print("Next small board: Any available")

        print(f"Current player: {self.current_player}")


# Base class for Ultimate Tic-Tac-Toe strategies
class BaseUltimateTTTStrategy:
    def __init__(self, game):
        self.game = game
        self.name = "Base Strategy"
        self.positions_evaluated = 0
        self.moves_considered = 0

    def get_next_move(self, depth=3):
        """Base method to be implemented by subclasses"""
        pass

    def evaluate_board(self, game):
        """Basic board evaluation function"""
        self.positions_evaluated += 1
        score = 0

        # Score based on small boards won
        for big_row in range(3):
            for big_col in range(3):
                if game.small_board_status[(big_row, big_col)] == 'X':
                    score += 10
                elif game.small_board_status[(big_row, big_col)] == 'O':
                    score -= 10

        # Score based on potential wins (two in a row with third spot open)
        for player, multiplier in [('X', 1), ('O', -1)]:
            # Check potential wins in rows, columns, and diagonals of the big board
            score += multiplier * count_potential_wins(game, player)

        # Factor in control of the center big board
        center_status = game.small_board_status[(1, 1)]
        if center_status == 'X':
            score += 5
        elif center_status == 'O':
            score -= 5

        return score

    def count_empty_cells(self, big_row, big_col):
        """Count empty cells in a small board (for MRV heuristic)"""
        count = 0
        for small_row in range(3):
            for small_col in range(3):
                if self.game.board[(big_row, big_col)][(small_row, small_col)] == " ":
                    count += 1
        return count

# Strategy 1: CSP with Minimax and Alpha-Beta Pruning
class CSPAlphaBetaStrategy(BaseUltimateTTTStrategy):
    def __init__(self, game, use_mrv=True):
        super().__init__(game)
        self.name = f"CSP + Alpha-Beta {'with' if use_mrv else 'without'} MRV"
        self.use_mrv = use_mrv

    def get_next_move(self, depth=3):
        """Get the best move using a CSP approach with constraints and alpha-beta pruning"""
        self.positions_evaluated = 0
        self.moves_considered = 0

        player = self.game.current_player
        best_move = None
        best_value = float('-inf') if player == 'X' else float('inf')

        # Get all valid moves
        valid_moves = self.game.available_moves()
        self.moves_considered = len(valid_moves)

        # Apply MRV (Minimum Remaining Values) heuristic if enabled
        if self.use_mrv and len(valid_moves) > 1:
            valid_moves.sort(key=lambda move: self.count_empty_cells(move[0], move[1]))

        # Try each move and evaluate
        for move in valid_moves:
            # Create a copy of the game to simulate the move
            game_copy = copy_game(self.game)
            game_copy.make_move(*move)

            # Evaluate the move using minimax with alpha-beta pruning
            if player == 'X':
                value = self.minimax(game_copy, depth - 1, float('-inf'), float('inf'), False)
                if value > best_value:
                    best_value = value
                    best_move = move
            else:
                value = self.minimax(game_copy, depth - 1, float('-inf'), float('inf'), True)
                if value < best_value:
                    best_value = value
                    best_move = move

        return best_move

    def minimax(self, game, depth, alpha, beta, maximizing):
        """Minimax algorithm with alpha-beta pruning and CSP constraints"""
        # Terminal conditions
        if game.is_game_over():
            if game.game_result == 'X':
                return 100 + depth  # Bonus for winning faster
            elif game.game_result == 'O':
                return -100 - depth  # Bonus for winning faster
            else:
                return 0

        if depth == 0:
            return self.evaluate_board(game)

        valid_moves = game.available_moves()

        # Apply forward checking - prioritize moves that lead to wins
        prioritized_moves = []
        for move in valid_moves:
            big_row, big_col, small_row, small_col = move
            game_copy = copy_game(game)

            # Check if this move would win a small board
            game_copy.make_move(*move)

            # If the move wins a small board, prioritize it
            priority = 0
            if game_copy.small_board_status[(big_row, big_col)] == game.current_player:
                priority = 2
                # If it also wins the game, give it highest priority
                if game_copy.game_result == game.current_player:
                    priority = 3

            # If the move sends opponent to a full or won board, it's also good
            next_board = (small_row, small_col)
            if game_copy.small_board_status[next_board] != ' ':
                priority = max(priority, 1)

            prioritized_moves.append((move, priority))

        # Sort moves by priority (highest first)
        prioritized_moves.sort(key=lambda x: x[1], reverse=True)
        valid_moves = [move for move, _ in prioritized_moves]

        if maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                game_copy = copy_game(game)
                game_copy.make_move(*move)
                eval = self.minimax(game_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                game_copy = copy_game(game)
                game_copy.make_move(*move)
                eval = self.minimax(game_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

# Strategy 2: CSP with Minimax but NO Alpha-Beta Pruning
class CSPMinimaxStrategy(BaseUltimateTTTStrategy):
    def __init__(self, game, use_mrv=True):
        super().__init__(game)
        self.name = f"CSP + Minimax {'with' if use_mrv else 'without'} MRV"
        self.use_mrv = use_mrv

    def get_next_move(self, depth=3):
        """Get the best move using a CSP approach with constraints but no alpha-beta pruning"""
        self.positions_evaluated = 0
        self.moves_considered = 0

        player = self.game.current_player
        best_move = None
        best_value = float('-inf') if player == 'X' else float('inf')

        # Get all valid moves
        valid_moves = self.game.available_moves()
        self.moves_considered = len(valid_moves)

        # Apply MRV (Minimum Remaining Values) heuristic if enabled
        if self.use_mrv and len(valid_moves) > 1:
            valid_moves.sort(key=lambda move: self.count_empty_cells(move[0], move[1]))

        # Try each move and evaluate
        for move in valid_moves:
            # Create a copy of the game to simulate the move
            game_copy = copy_game(self.game)
            game_copy.make_move(*move)

            # Evaluate the move using minimax without alpha-beta pruning
            if player == 'X':
                value = self.minimax(game_copy, depth - 1, False)
                if value > best_value:
                    best_value = value
                    best_move = move
            else:
                value = self.minimax(game_copy, depth - 1, True)
                if value < best_value:
                    best_value = value
                    best_move = move

        return best_move

    def minimax(self, game, depth, maximizing):
        """Minimax algorithm without alpha-beta pruning"""
        # Terminal conditions
        if game.is_game_over():
            if game.game_result == 'X':
                return 100 + depth
            elif game.game_result == 'O':
                return -100 - depth
            else:
                return 0

        if depth == 0:
            return self.evaluate_board(game)

        valid_moves = game.available_moves()

        # Apply forward checking - prioritize moves that lead to wins
        prioritized_moves = []
        for move in valid_moves:
            big_row, big_col, small_row, small_col = move
            game_copy = copy_game(game)

            # Check if this move would win a small board
            game_copy.make_move(*move)

            # If the move wins a small board, prioritize it
            priority = 0
            if game_copy.small_board_status[(big_row, big_col)] == game.current_player:
                priority = 2
                # If it also wins the game, give it highest priority
                if game_copy.game_result == game.current_player:
                    priority = 3

            # If the move sends opponent to a full or won board, it's also good
            next_board = (small_row, small_col)
            if game_copy.small_board_status[next_board] != ' ':
                priority = max(priority, 1)

            prioritized_moves.append((move, priority))

        # Sort moves by priority (highest first)
        prioritized_moves.sort(key=lambda x: x[1], reverse=True)
        valid_moves = [move for move, _ in prioritized_moves]

        if maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                game_copy = copy_game(game)
                game_copy.make_move(*move)
                eval = self.minimax(game_copy, depth - 1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                game_copy = copy_game(game)
                game_copy.make_move(*move)
                eval = self.minimax(game_copy, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval


# Run experimental analysis comparing different strategies
def run_experiments():
    print("Running experiments to compare AI strategies...")

    strategies = [
        ("CSP + Alpha-Beta with MRV", lambda g: CSPAlphaBetaStrategy(g, True)),
        ("CSP + Alpha-Beta without MRV", lambda g: CSPAlphaBetaStrategy(g, False)),
        ("CSP + Minimax with MRV", lambda g: CSPMinimaxStrategy(g, True)),
        ("CSP + Minimax without MRV", lambda g: CSPMinimaxStrategy(g, False))
    ]

    num_games = 5
    results = {}
    matchups = []

    # Set up all possible matchups
    for i in range(len(strategies)):
        for j in range(i + 1, len(strategies)):
            matchups.append((i, j))

    # Initialize results
    for name, _ in strategies:
        results[name] = {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'avg_time_per_move': 0,
            'total_moves': 0,
            'total_time': 0,
            'avg_positions_evaluated': 0,
            'positions_evaluated': 0
        }

    # Play games for each matchup
    for matchup in matchups:
        strat1_idx, strat2_idx = matchup
        strat1_name, strat1_factory = strategies[strat1_idx]
        strat2_name, strat2_factory = strategies[strat2_idx]

        print(f"\nMatchup: {strat1_name} vs {strat2_name}")

        for game_num in range(num_games):
            print(f"Game {game_num + 1}/{num_games}...")
            game = UltimateTicTacToe()

            # Create new strategy instances for this game
            strat1 = strat1_factory(game)
            strat2 = strat2_factory(game)

            current_strat = strat1  # X goes first
            moves = 0

            while not game.is_game_over() and moves < 81:  # Max 81 moves possible
                start_time = time.time()

                # Get next move from current strategy
                ai_move = current_strat.get_next_move(depth=2)  # Reduced depth for faster experiments

                end_time = time.time()
                move_time = end_time - start_time

                # Update statistics
                current_strat_name = strat1_name if game.current_player == 'X' else strat2_name
                results[current_strat_name]['total_time'] += move_time
                results[current_strat_name]['total_moves'] += 1
                results[current_strat_name]['positions_evaluated'] += current_strat.positions_evaluated

                # Make the move
                if ai_move:
                    game.make_move(*ai_move)
                    moves += 1
                else:
                    break

                # Switch strategy for next move
                current_strat = strat2 if game.current_player == 'O' else strat1

            # Record game result
            if game.game_result == 'X':
                results[strat1_name]['wins'] += 1
                results[strat2_name]['losses'] += 1
                print(f"X ({strat1_name}) wins!")
            elif game.game_result == 'O':
                results[strat1_name]['losses'] += 1
                results[strat2_name]['wins'] += 1
                print(f"O ({strat2_name}) wins!")
            else:
                results[strat1_name]['draws'] += 1
                results[strat2_name]['draws'] += 1
                print("Draw!")

    # Calculate averages for each strategy
    for name in results:
        total_moves = results[name]['total_moves']
        if total_moves > 0:
            results[name]['avg_time_per_move'] = results[name]['total_time'] / total_moves
            results[name]['avg_positions_evaluated'] = results[name]['positions_evaluated'] / total_moves

    # Print results
    print("\n==================== RESULTS ====================")
    for name, stats in results.items():
        print(f"\n{name}:")
        print(f"  Wins: {stats['wins']}")
        print(f"  Losses: {stats['losses']}")
        print(f"  Draws: {stats['draws']}")
        print(f"  Win Rate: {stats['wins'] / (stats['wins'] + stats['losses'] + stats['draws']) * 100:.1f}%")
        print(f"  Avg. Time per Move: {stats['avg_time_per_move'] * 1000:.2f} ms")
        print(f"  Avg. Positions Evaluated: {stats['avg_positions_evaluated']:.1f}")


# Play a game of Ultimate Tic-Tac-Toe with the AI
def play_game():
    game = UltimateTicTacToe()

    # Choose strategy
    print("Available AI Strategies:")
    print("1. CSP + Alpha-Beta with MRV")
    print("2. CSP + Alpha-Beta without MRV")
    print("3. CSP + Minimax with MRV")
    print("4. CSP + Minimax without MRV")

    strategy_choice = int(input("Choose AI strategy (1-4): "))

    if strategy_choice == 1:
        solver = CSPAlphaBetaStrategy(game, True)
    elif strategy_choice == 2:
        solver = CSPAlphaBetaStrategy(game, False)
    elif strategy_choice == 3:
        solver = CSPMinimaxStrategy(game, True)
    else:
        solver = CSPMinimaxStrategy(game, False)

    print(f"\nSelected strategy: {solver.name}")
    print("Welcome to Ultimate Tic-Tac-Toe!")
    print("Enter moves as: big_row big_col small_row small_col")
    print("Example: 0 0 1 1 places your mark in the center of the top-left small board")

    human_player = input("Do you want to play as X or O? (X goes first): ").upper()
    while human_player not in ['X', 'O']:
        human_player = input("Please enter X or O: ").upper()

    ai_player = 'O' if human_player == 'X' else 'X'

    # Main game loop
    while not game.is_game_over():
        # Display the current board
        game.print_board()

        # AI or human turn
        if game.current_player == human_player:
            print("\nYour turn")
            valid_move = False
            while not valid_move:
                try:
                    move = input("Enter your move (big_row big_col small_row small_col): ")
                    big_row, big_col, small_row, small_col = map(int, move.split())
                    valid_move = game.make_move(big_row, big_col, small_row, small_col)
                    if not valid_move:
                        print("Invalid move. Try again.")
                except (ValueError, IndexError):
                    print("Invalid input. Use format: big_row big_col small_row small_col")
        else:
            print(f"\nAI ({ai_player}) is thinking...")
            start_time = time.time()
            ai_move = solver.get_next_move()
            end_time = time.time()

            if ai_move:
                print(f"AI moves: {ai_move}")
                print(f"Time taken: {(end_time - start_time) * 1000:.2f} ms")
                print(f"Positions evaluated: {solver.positions_evaluated}")
                game.make_move(*ai_move)
            else:
                print("AI couldn't find a valid move. Game draw.")
                break

    # Game over
    game.print_board()
    print("\nGame Over!")
    if game.game_result == 'Draw':
        print("It's a draw!")
    else:
        if game.game_result == human_player:
            print("You win!")
        else:
            print("AI wins!")


# Initialize pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
BOARD_SIZE = WINDOW_SIZE
SMALL_BOARD_SIZE = BOARD_SIZE // 3
CELL_SIZE = SMALL_BOARD_SIZE // 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 0)


# GUI class for Ultimate Tic-Tac-Toe
class UltimateTTTGUI:
    def __init__(self):
        self.game = UltimateTicTacToe()

        # Set up the display
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 100))  # Extra height for stats
        pygame.display.set_caption("Ultimate Tic-Tac-Toe")

        # Font setup
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 36)

        # Select the AI strategy
        print("Available AI Strategies:")
        print("1. CSP + Alpha-Beta with MRV")
        print("2. CSP + Alpha-Beta without MRV")
        print("3. CSP + Minimax with MRV")
        print("4. CSP + Minimax without MRV")

        strategy_choice = input("Choose AI strategy (1-4): ")

        if strategy_choice == '1':
            self.ai = CSPAlphaBetaStrategy(self.game, True)
        elif strategy_choice == '2':
            self.ai = CSPAlphaBetaStrategy(self.game, False)
        elif strategy_choice == '3':
            self.ai = CSPMinimaxStrategy(self.game, True)
        else:
            self.ai = CSPMinimaxStrategy(self.game, False)

        print(f"\nSelected strategy: {self.ai.name}")

        # Choose player's mark
        human_player = input("Do you want to play as X or O? (X goes first): ").upper()
        while human_player not in ['X', 'O']:
            human_player = input("Please enter X or O: ").upper()

        self.human_player = human_player
        self.ai_player = 'O' if human_player == 'X' else 'X'

        # Stats for AI
        self.ai_time = 0
        self.ai_positions = 0
        self.ai_moves = 0

        # If AI goes first, make its first move
        if self.game.current_player == self.ai_player:
            self.make_ai_move()

    def run_game(self):
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game.is_game_over():
                    if self.game.current_player == self.human_player:
                        self.handle_mouse_click(event.pos)

            # Draw the game board
            self.draw()

            # Update the display
            pygame.display.flip()

        pygame.quit()

    def handle_mouse_click(self, pos):
        """Handle a mouse click on the board"""
        x, y = pos

        # Make sure the click is within the board area
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            # Calculate which big board and small cell was clicked
            big_col = x // SMALL_BOARD_SIZE
            big_row = y // SMALL_BOARD_SIZE

            # Calculate the cell within the small board
            small_col = (x % SMALL_BOARD_SIZE) // CELL_SIZE
            small_row = (y % SMALL_BOARD_SIZE) // CELL_SIZE

            # Try to make the move
            if self.game.make_move(big_row, big_col, small_row, small_col):
                # If the move was successful and the game isn't over, make the AI move
                if not self.game.is_game_over():
                    self.make_ai_move()

    def make_ai_move(self):
        """Make a move for the AI"""
        print(f"AI ({self.ai_player}) is thinking...")
        start_time = time.time()
        ai_move = self.ai.get_next_move()
        end_time = time.time()

        # Update AI statistics
        move_time = end_time - start_time
        self.ai_time += move_time
        self.ai_positions += self.ai.positions_evaluated
        self.ai_moves += 1

        if ai_move:
            print(f"AI moves: {ai_move}")
            print(f"Time taken: {move_time * 1000:.2f} ms")
            print(f"Positions evaluated: {self.ai.positions_evaluated}")
            self.game.make_move(*ai_move)

    def draw(self):
        """Draw the game board and information"""
        # Fill the background
        self.screen.fill(WHITE)

        # Draw the big board grid
        for i in range(1, 3):
            pygame.draw.line(self.screen, BLACK, (0, i * SMALL_BOARD_SIZE),
                             (BOARD_SIZE, i * SMALL_BOARD_SIZE), 4)
            pygame.draw.line(self.screen, BLACK, (i * SMALL_BOARD_SIZE, 0),
                             (i * SMALL_BOARD_SIZE, BOARD_SIZE), 4)

        # Draw small board grids and marks
        for big_row in range(3):
            for big_col in range(3):
                # Highlight active small board
                if self.game.next_small_board == (big_row, big_col) and not self.game.is_game_over():
                    pygame.draw.rect(self.screen, YELLOW,
                                     (big_col * SMALL_BOARD_SIZE, big_row * SMALL_BOARD_SIZE,
                                      SMALL_BOARD_SIZE, SMALL_BOARD_SIZE), 4)

                # Highlight completed small boards
                if self.game.small_board_status[(big_row, big_col)] != ' ':
                    color = RED if self.game.small_board_status[(big_row, big_col)] == 'X' else BLUE
                    if self.game.small_board_status[(big_row, big_col)] == 'D':
                        color = GRAY

                    pygame.draw.rect(self.screen, color,
                                     (big_col * SMALL_BOARD_SIZE + 2, big_row * SMALL_BOARD_SIZE + 2,
                                      SMALL_BOARD_SIZE - 4, SMALL_BOARD_SIZE - 4), 0)

                    # Draw the winner symbol of the small board
                    if self.game.small_board_status[(big_row, big_col)] in ['X', 'O']:
                        text = self.large_font.render(self.game.small_board_status[(big_row, big_col)], True, WHITE)
                        text_rect = text.get_rect(center=(big_col * SMALL_BOARD_SIZE + SMALL_BOARD_SIZE // 2,
                                                          big_row * SMALL_BOARD_SIZE + SMALL_BOARD_SIZE // 2))
                        self.screen.blit(text, text_rect)

                # Draw small grid lines
                for i in range(1, 3):
                    pygame.draw.line(self.screen, BLACK,
                                     (big_col * SMALL_BOARD_SIZE, big_row * SMALL_BOARD_SIZE + i * CELL_SIZE),
                                     (big_col * SMALL_BOARD_SIZE + SMALL_BOARD_SIZE,
                                      big_row * SMALL_BOARD_SIZE + i * CELL_SIZE), 2)
                    pygame.draw.line(self.screen, BLACK,
                                     (big_col * SMALL_BOARD_SIZE + i * CELL_SIZE, big_row * SMALL_BOARD_SIZE),
                                     (big_col * SMALL_BOARD_SIZE + i * CELL_SIZE,
                                      big_row * SMALL_BOARD_SIZE + SMALL_BOARD_SIZE), 2)

                # Draw X's and O's
                for small_row in range(3):
                    for small_col in range(3):
                        cell_content = self.game.board[(big_row, big_col)][(small_row, small_col)]
                        if cell_content != " ":
                            # Draw X or O
                            color = BLACK if self.game.small_board_status[(big_row, big_col)] in [' ', 'D'] else WHITE
                            text = self.font.render(cell_content, True, color)
                            x = big_col * SMALL_BOARD_SIZE + small_col * CELL_SIZE + CELL_SIZE // 2
                            y = big_row * SMALL_BOARD_SIZE + small_row * CELL_SIZE + CELL_SIZE // 2
                            text_rect = text.get_rect(center=(x, y))
                            self.screen.blit(text, text_rect)

        # Draw information at the bottom
        info_y = BOARD_SIZE + 10

        # Draw current player and next board info
        if not self.game.is_game_over():
            current_player_text = f"Current Player: {self.game.current_player}"
            text = self.font.render(current_player_text, True, BLACK)
            self.screen.blit(text, (20, info_y))

            if self.game.next_small_board:
                next_board_text = f"Next Board: {self.game.next_small_board}"
            else:
                next_board_text = "Next Board: Any available"
            text = self.font.render(next_board_text, True, BLACK)
            self.screen.blit(text, (20, info_y + 25))
        else:
            # Game over message - Bold, Yellow, and Centered
            if self.game.game_result == 'Draw':
                result_text = "GAME OVER: IT'S A DRAW!"
            else:
                result_text = f"GAME OVER: {self.game.game_result} WINS!"

            # Create a bold font for the game over message
            bold_font = pygame.font.SysFont(None, 48, bold=True)

            # Draw a semi-transparent background for better visibility
            overlay = pygame.Surface((WINDOW_SIZE, 70))
            overlay.set_alpha(180)
            overlay.fill((50, 50, 50))
            self.screen.blit(overlay, (0, BOARD_SIZE // 2 - 35))

            # Render the text in yellow and center it on the screen
            text = bold_font.render(result_text, True, YELLOW)
            text_rect = text.get_rect(center=(WINDOW_SIZE // 2, BOARD_SIZE // 2))
            self.screen.blit(text, text_rect)

        # Draw AI stats
        if self.ai_moves > 0:
            avg_time = self.ai_time / self.ai_moves * 1000  # Convert to ms
            avg_positions = self.ai_positions / self.ai_moves

            ai_text = f"AI: {self.ai.name}"
            text = self.font.render(ai_text, True, BLACK)
            self.screen.blit(text, (WINDOW_SIZE - 300, info_y))

            time_text = f"Avg time: {avg_time:.2f} ms"
            text = self.font.render(time_text, True, BLACK)
            self.screen.blit(text, (WINDOW_SIZE - 300, info_y + 25))

            pos_text = f"Avg positions: {avg_positions:.1f}"
            text = self.font.render(pos_text, True, BLACK)
            self.screen.blit(text, (WINDOW_SIZE - 300, info_y + 50))

# Function to play the game with GUI
def play_game_gui():
    game_gui = UltimateTTTGUI()
    game_gui.run_game()

if __name__ == "__main__":
    choice = input(
        "1. Play against AI in console\n2. Play against AI with GUI\n3. Run experiments\nEnter your choice (1-3): ")

    if choice == '1':
        play_game()
    elif choice == '2':
        play_game_gui()
    elif choice == '3':
        run_experiments()
    else:
        print("Invalid choice. Exiting.")
