import socket 

hostName = "localhost"
port= 5556

client_socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((hostName,port))

while True:
    msg = client_socket.recv(1024).decode()
    print(msg)
    if "Choose your symbol ['X' or 'O']: " in msg:
        symbol =input ("X or O ")
        client_socket.send(symbol.encode())
    elif "Your move. Enter row (0-2): " in msg:
        row = input("row ")
        client_socket.send(row.encode())
    elif "Enter column (0-2): " in msg:
        col = input("col ")
        client_socket.send(col.encode())

