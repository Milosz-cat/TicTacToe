import time
import os
import random


class TicTacToe:

    def __init__(self, board_size, win_length):
        self.board_size = board_size
        self.win_length = win_length
        self.board = [[" " for x in range(board_size)] for y in range(board_size)]
        self.corners = [
            (0, 0),
            (0, self.board_size - 1),
            (self.board_size - 1, 0),
            (self.board_size - 1, self.board_size - 1),
        ]
        self.center = (
            [
                (self.board_size // 2 - 1, self.board_size // 2 - 1),
                (self.board_size // 2, self.board_size // 2 - 1),
                (self.board_size // 2 - 1, self.board_size // 2),
                (self.board_size // 2, self.board_size // 2),
            ]
            if self.board_size % 2 == 0
            else [(self.board_size // 2, self.board_size // 2)]
        )
        self.num_moves = 0

    def display_board(self):
        """
        Prints the current state of the board in a readable format on the console.
        """
        os.system("cls" if os.name == "nt" else "clear")
        for row in self.board:
            print("| " + " | ".join(row) + " |")

    def is_valid_move(self, row, col):
        """
        Returns a boolean indicating whether a given move is valid or not, i.e., whether it is within the board's bounds and the cell is empty.
        """
        return (
            0 <= row < self.board_size
            and 0 <= col < self.board_size
            and self.board[row][col] == " "
        )

    def make_move(self, row, col, player):
        """
        Places the player's symbol on the given cell.
        """
        self.board[row][col] = player
        self.num_moves += 1

    def undo_move(self, row, col):
        """
        Removes the player's symbol from the given cell.
        """
        self.board[row][col] = " "
        self.num_moves -= 1

    def check_win(self, player, length):
        """
        Checks whether the player has won the game, by checking all possible combinations of given length on the board.
        Return number of wins combinantion.
        """
        score = 0
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == " ":
                    continue

                horizontal = self.check_win_horizontal(i, j, player, length)
                vertical = self.check_win_vertical(i, j, player, length)
                diagonal = self.check_win_diagonal(i, j, player, length)

                if horizontal:
                    score += horizontal
                if vertical:
                    score += vertical
                if diagonal:
                    score += diagonal

        return score

    def check_win_horizontal(self, row, col, player, length):
        """
        Helper function to check for a win horizontally.
        """
        count = 0
        for j in range(col, col + length):
            if j >= self.board_size or self.board[row][j] != player:
                return 0
            count += 1
        return count

    def check_win_vertical(self, row, col, player, length):
        count = 0
        for i in range(row, row + length):
            if i >= self.board_size or self.board[i][col] != player:
                return 0
            count += 1
        return count

    def check_win_diagonal(self, row, col, player, length):
        count = 0
        # check diagonal from top-left to bottom-right
        for i in range(length):
            if (
                row + i >= length
                or col + i >= self.board_size
                or self.board[row + i][col + i] != player
            ):
                break
            count += 1
        else:
            return count

        # check diagonal from bottom-left to top-right
        for i in range(length):
            if (
                row - i < 0
                or col + i >= self.board_size
                or self.board[row - i][col + i] != player
            ):
                break
            count += 1
        else:
            return count

        return 0

    def is_full(self):
        """
        Returns a boolean indicating whether the board is full or not.
        """
        for row in self.board:
            if " " in row:
                return False

        return True

    def evaluate(self, player):
        """
        Evaluates the current state of the board from the perspective of the player, by assigning a score based on the number of marks in a row, column or diagonal. 
        Corners and Center moves are prioritized based on board size.
        Positive points are subtracted from the opponent's perspective points.
        """
        score = 0

        if player in self.corners:
            score += 5 if self.board_size > 3 else 10
        elif player in self.center:
            score += 10 if self.board_size > 3 else 5

        for i in range(2, self.win_length + 1):
            count = self.check_win(player, i)
            if count > 0:
                score += count * (10**i)  # weight factor based on the number of pieces in the line

        for i in range(2, self.win_length + 1):
            count = self.check_win("X" if player == "O" else "O", i)
            if count > 0:
                score -= count * (10**i)  

        return score

    def get_possible_moves(self):
        """
        Returns a list of all possible moves for the current state of the board. 
        Moves are ordered, because center and corener moves are usually better and minmax algorithm can prun worse combinantions and works faster.
        """
        moves = []
        for m in self.center if self.board_size > 3 else self.corners:
            r, c = m
            if self.is_valid_move(r, c):
                moves.append(m)

        for m in self.corners if self.board_size > 3 else self.center:
            r, c = m
            if self.is_valid_move(r, c):
                moves.append(m)

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.is_valid_move(i, j) and (i, j) not in moves:
                    moves.append((i, j))

        return moves

    def get_best_move(self, depth):
        """
        This function returns the best move based on the minimax algorithm with alpha-beta pruning and transposition tables.
        Iterative deepening is used to search state tree more efficent and stop it at depth limit.

        Parameters:
            depth (int): The depth to search for in the minimax algorithm.
        """
        best_score = float("-inf")
        best_move = None
        alpha = float("-inf")
        beta = float("inf")

        transposition_table = {}

        if self.board_size > 3 and self.num_moves == 0:
            return random.choice(self.center)

        for move in self.get_possible_moves():
            row, col = move
            self.make_move(row, col, "O")
            score = self.minimax(depth, alpha, beta, False, transposition_table)
            # print(move, score, alpha, beta)
            self.undo_move(row, col)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        return best_move

    def minimax(self, depth, alpha, beta, is_maximizing, transposition_table):
        """
        This function implements the minimax algorithm with alpha-beta pruning.
        It evaluates the best possible score that can be obtained from a given game state,
        by recursively evaluating all possible future moves and their resulting game states.
        The function keeps track of already evaluated game states using a transposition table.

        Parameters:
            depth: the maximum depth of the search tree to explore (an integer)
            alpha: the current best score of the maximizing player (a floating point number)
            beta: the current best score of the minimizing player (a floating point number)
            is_maximizing: whether the current player is maximizing or not (a boolean)
            transposition_table: a dictionary to keep track of already evaluated game states (a dictionary)

        :return: the best possible score that can be obtained from the current game state (a floating point number)
        """
        board_hash = self.get_board_hash()
        if board_hash in transposition_table:
            return transposition_table[board_hash]

        if self.check_win("O", self.win_length) > 0:
            return 100**self.win_length - self.num_moves
        elif self.check_win("X", self.win_length) > 0:
            return -(100**self.win_length) + self.num_moves
        elif depth == 0 or self.is_full():
            return self.evaluate("O")

        if is_maximizing:
            best_score = float("-inf")
            for move in self.get_possible_moves():
                row, col = move
                self.make_move(row, col, "O")
                score = self.minimax(depth - 1, alpha, beta, False, transposition_table)
                self.undo_move(row, col)
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
            transposition_table[board_hash] = best_score
            return best_score
        else:
            best_score = float("inf")
            for move in self.get_possible_moves():
                row, col = move
                self.make_move(row, col, "X")
                score = self.minimax(depth - 1, alpha, beta, True, transposition_table)
                self.undo_move(row, col)
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if alpha >= beta:
                    break

            transposition_table[board_hash] = best_score
            return best_score

    def get_board_hash(self):
        """
        The get_board_hash() function returns a hash string representation of the current state of a tic-tac-toe board for transposition tables.
        The hash string is constructed by iterating over each cell in the board and adding the character 'X' for player X's moves, 'O' for player O's moves, and '-' for empty cells.
        """
        hash_str = ""
        for row in self.board:
            for cell in row:
                if cell == "X":
                    hash_str += "X"
                elif cell == "O":
                    hash_str += "O"
                else:
                    hash_str += "-"
        return hash_str

    def play(self, choice):
        """
        Function represents a single player turn in a tic-tac-toe game. It takes a choice parameter that indicates the starting player, either 1 (for the human player, X) or 2 (for the computer player, O).
        The function then enters a loop that continues until a win or tie condition is met. In each iteration of the loop, the current state of the board is displayed, and the current player is prompted to make a move.
        The human player's move is obtained through user input, while the computer player's move is obtained by calling the get_best_move() function. Once a valid move is made, the make_move() function is called to update
        the board with the new move. After each move, the player is switched and the loop continues.
        Once the game is over, the final state of the board is displayed, and a message is printed indicating whether the human player or the computer player won, or if the game ended in a tie.

        Parameters:
            choice: An integer that indicates the starting player. The value should be either 1 (for the human player, X) or 2 (for the computer player, O).

        """
        player = "X" if choice == 1 else "O"

        while (
            not self.check_win("X", self.win_length) > 0
            and not self.check_win("O", self.win_length) > 0
            and not self.is_full()
        ):
            self.display_board()

            if player == "X":
                print("Your turn (X): ")
                row = int(input("Enter row (1-{}): ".format(self.board_size))) - 1
                col = int(input("Enter column (1-{}): ".format(self.board_size))) - 1

                while not self.is_valid_move(row, col):
                    print("Invalid move. Try again.")
                    row = int(input("Enter row (1-{}): ".format(self.board_size))) - 1
                    col = (
                        int(input("Enter column (1-{}): ".format(self.board_size))) - 1
                    )

                self.make_move(row, col, player)
            else:
                print("Computer's turn (O): ")
                start_time = time.time()
                row, col = self.get_best_move(5 if self.board_size == 3 else 3)
                end_time = time.time()
                duration = end_time - start_time
                print("Function execution time: ", duration, "seconds.\n")
                self.make_move(row, col, player)

            player = "O" if player == "X" else "X"

        self.display_board()

        if self.check_win("X", self.win_length) > 0:
            print("You win!")
        elif self.check_win("O", self.win_length) > 0:
            print("Computer wins!")
        else:
            print("Tie.")


board_size = int(input("Enter board size: "))
win_length = int(input("Enter win length: "))
game = TicTacToe(board_size, win_length)
choice = 1 if input("Do you want to start a game? [Y/N]\t") == ("y" or "Y") else 0
game.play(choice)
