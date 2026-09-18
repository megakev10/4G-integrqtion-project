import socket


# IP address on which the server will listen.
# 0.0.0.0 means: accept connections coming through any
# network interface of this computer.
HOST = "0.0.0.0"

# TCP port used by our test server.
PORT = 5000


# Create a TCP socket.
# AF_INET  -> IPv4
# SOCK_STREAM -> TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Bind the socket to the chosen IP address and port.
# This reserves 0.0.0.0:5000 for our server.
server.bind((HOST, PORT))


# Put the socket into listening mode.
# The argument 1 means that one pending connection can wait
# in the connection queue.
server.listen(1)

print(f"TCP server listening on {HOST}:{PORT}")


# Wait for a client to connect.
# This line blocks the program until a connection is received.
#
# client  -> socket used to communicate with the connected client
# address -> client's IP address and port
client, address = server.accept()

print(f"Client connected: {address}")


# Keep receiving data while the client remains connected.
while True:

    # Receive up to 1024 bytes from the client.
    data = client.recv(1024)


    # If recv() returns empty data, the client has disconnected.
    if not data:
        print("Client disconnected")
        break


    # Convert the received bytes into a Python string.
    # errors="replace" prevents the program from crashing if
    # some received bytes are not valid UTF-8.
    message = data.decode("utf-8", errors="replace")

    print(f"Received: {message}")


    # Send an acknowledgement back to the client.
    # b"ACK\n" is a bytes object because sockets transmit bytes.
    client.sendall(b"ACK\n")


# Close the client connection.
client.close()

# Close the server socket.
server.close()