import serial
import socket
import time


# PTY exposed by socat.
# Change this path to the PTY created for the VirtualModem.
SERIAL_PORT = "/dev/pts/5"

# Serial communication speed.
BAUDRATE = 115200


# Create the serial connection with the ESP32.
modem_serial = serial.Serial(
    SERIAL_PORT,
    BAUDRATE,
    timeout=0.1
)


# TCP socket used by the virtual modem.
tcp_socket = None


def handle_command(command):
    """
    Process one AT command received from the ESP32.
    """

    global tcp_socket

    command = command.strip()

    print(f"ESP32 -> Modem: {command}")


    # Basic modem test
    if command == "AT":

        modem_serial.write(b"\r\nOK\r\n")


    # Open a TCP connection
    elif command.startswith("AT+QIOPEN="):

        print("Opening TCP connection...")

        try:
            # For this first version, we use our local test server.
            server_ip = "127.0.0.1"
            server_port = 5000

            # Create a TCP socket.
            tcp_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            # Connect to the TCP server.
            tcp_socket.connect(
                (server_ip, server_port)
            )

            print(
                f"TCP connection established "
                f"with {server_ip}:{server_port}"
            )

            # Simulate the EC200U asynchronous result.
            #
            # connectID = 0
            # err = 0 means successful connection.
            modem_serial.write(
                b"\r\nOK\r\n"
            )

            time.sleep(0.1)

            modem_serial.write(
                b"\r\n+QIOPEN: 0,0\r\n"
            )

        except Exception as error:

            print(f"TCP connection failed: {error}")

            modem_serial.write(
                b"\r\nOK\r\n"
            )

            time.sleep(0.1)

            # Non-zero error means the connection failed.
            modem_serial.write(
                b"\r\n+QIOPEN: 0,1\r\n"
            )


    # Unknown command
    else:

        modem_serial.write(
            b"\r\nERROR\r\n"
        )


print("Virtual modem started.")
print(f"Listening on {SERIAL_PORT}")


while True:

    # Check whether the ESP32 sent something.
    if modem_serial.in_waiting:

        # Read one line from the serial port.
        command = modem_serial.readline().decode(
            "utf-8",
            errors="replace"
        )

        if command.strip():
            handle_command(command)