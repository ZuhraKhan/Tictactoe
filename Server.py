import socket
import threading 

# create initial board
def create_grid(): 
    return [[" " for _ in range(3)] for _ in range(3)]

# printing board
def print_board(board):
    b = "---+---+---\n"  
    for row in board:
        b += " | ".join(row) + "\n"  
        b += "---+---+---\n"  
    return b  

# determing if the given symbol won 
def is_winner(board, symbol):
    for i in range(3):
        if all(board[i][j] == symbol for j in range(3)) or all(board[j][i] == symbol for j in range(3)):
            return True
    if all(board[i][i] == symbol for i in range(3)) or all(board[i][2 - i] == symbol for i in range(3)):
        return True
    return False

# checkign if board full
def is_full(board):
    return all(cell != " " for row in board for cell in row)

# game 
def gameplay(client, symbol, game):
    try:
        
        while not game['Game_Over']:
            if game['current turn'] == symbol: # determinig the turn
                while True:
                    try:
                        # getting the move from the client
                        client.send("Your move. Enter row (0-2): ".encode())
                        row = client.recv(1024).decode().strip()
                        client.send("Enter column (0-2): ".encode())
                        col = client.recv(1024).decode().strip()
                        # checking move validity
                        row, col = int(row), int(col)
                        if 0 <= row < 3 and 0 <= col < 3 and game['board'][row][col] == " ":
                            break
                        else:
                            client.send("Invalid move. Try again.\n".encode())
                    except (ValueError, ConnectionResetError, BrokenPipeError):
                        handle_disconnection(client, game)
                        return
                 # placign the symbol in given move
                game['board'][row][col] = symbol
                # updating board status
                board_State = print_board(game['board'])
                # displaying boad status to clients
                for c in game['clients']:
                    try:
                        c.send(board_State.encode())
                    except (ConnectionResetError, BrokenPipeError): # handling disconnect to avoid sending to a closed connection 
                        handle_disconnection(c, game)
                # checkign winner
                if is_winner(game['board'], symbol):
                    for c in game['clients']:
                        c.send(f"Player {symbol} wins!!! Game Over.\n".encode())
                    game['Game_Over'] = True
                # checking if board full
                elif is_full(game['board']):
                    for c in game['clients']:
                        c.send("It's a Tie. Game Over.\n".encode())
                    game['Game_Over'] = True
                # changing the turn
                else:
                    if game['current turn'] == 'X':
                        game['current turn']='O'
                    else:
                        game['current turn']='X'

    except (ConnectionResetError, BrokenPipeError): # client disconnect handling
        handle_disconnection(client, game)

def handle_disconnection(client, game):
    if client in game['clients']:
        game['clients'].remove(client)
    if len(game['clients']) == 1:
        try:
            game['clients'][0].send("Opponent disconnected. You win!\n".encode())
        except (ConnectionResetError, BrokenPipeError):
            pass
    game['Game_Over'] = True

def Server():
    hostName = "localhost"
    port = 5556

    #initializing socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((hostName, port))
    #listening
    server_socket.listen(2)
    print("Server Listening...")

    while True:
        #client 1 conecting
        client1, add1 = server_socket.accept()
        print(f"Player 1 connected from {add1}. Waiting for Player 2...")
        client1.send("Waiting for another player...\n".encode())
        #client 2 connecting
        client2, add2 = server_socket.accept()
        print(f"Player 2 connected from {add2}")
        client2.send("Connected\n".encode())
        # letting client 1 choose symbol
        symbols = ["X", "O"]
        client1.send("Choose your symbol ['X' or 'O']: ".encode())

        while True:
            symbol1 = client1.recv(1024).decode().strip().upper()
            if symbol1 in symbols:
                break
            client1.send("Invalid symbol. Choose again: ".encode())
        # symbol 2 assigning
        if symbol1 == 'X':
            symbol2 = 'O'
        else:
            symbol2 ='X'
        
        client1.send(f"You are {symbol1}\n".encode())
        client2.send(f"Player 1 chose {symbol1}. You are {symbol2}\n".encode())

        # game state to be shared by the threads
        game_state = {
            'board': create_grid(),
            'clients': [client1, client2],
            'current turn': "X",
            'Game_Over': False
        }

        for client in game_state['clients']:
            client.send("Game started! You will receive updates after every move.\n".encode())
         #threads
        threading.Thread(target=gameplay, args=(client1, symbol1, game_state)).start()
        threading.Thread(target=gameplay, args=(client2, symbol2, game_state)).start()

Server()
