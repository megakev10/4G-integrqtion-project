import serial
import socket

class VirtualModem:
    def __init__(self, port):
        self.port = port
        self.baudrate = 115200

        # =========================
        # Internal modem state
        # =========================

        # SIM state
        self.sim_ready = True

        # Mobile network state
        self.network_registered = True
        self.signal_quality = 20
        self.operator = "MTN"

        # Data connection state
        self.data_connected = False

        # Data context configuration
        self.apn = None

        # TCP connection state
        self.tcp_connected = False
        self.tcp_socket = None
        self.connection_id = None

        # Send data state
        self.send_mode = False
        self.send_length = 0

        # Serial interface
        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=0.1
        )


    def send_response(self, response):
        """
        Send a response to the ESP32.
        """

        message = f"\r\n{response}\r\n"

        self.serial.write(
            message.encode()
        )


    def handle_command(self, command):
        """
        Process one AT command.
        """

        match command:

            # =========================
            # Basic modem test
            # =========================

            case "AT":

                self.send_response("OK")


            # =========================
            # SIM status
            # =========================

            case "AT+CPIN?":

                if self.sim_ready:

                    self.send_response(
                        "+CPIN: READY\r\n\r\nOK"
                    )

                else:

                    self.send_response(
                        "+CPIN: SIM PIN"
                    )


            # =========================
            # Signal quality
            # =========================

            case "AT+CSQ":

                self.send_response(
                    f"+CSQ: {self.signal_quality},99\r\n\r\nOK"
                )


            # =========================
            # Operator information
            # =========================

            case "AT+COPS?":

                self.send_response(
                    f'+COPS: 0,0,"{self.operator}"\r\n\r\nOK'
                )


            # =========================
            # Network registration
            # =========================

            case "AT+CEREG?":

                if self.network_registered:

                    self.send_response(
                        "+CEREG: 0,1\r\n\r\nOK"
                    )

                else:

                    self.send_response(
                        "+CEREG: 0,0\r\n\r\nOK"
                    )

            case _ if command.startswith("AT+QICSGP="):

                print("Configuring PDP context...")
                self.apn = "internet"
                self.send_response("OK")

            case _ if command.startswith("AT+QIACT="):

                print("Activating data context...")

                if not self.sim_ready:

                    print("Cannot activate data context: SIM not ready.")
                    self.send_response("ERROR")

                elif not self.network_registered:

                    print("Cannot activate data context: network not registered.")
                    self.send_response("ERROR")

                elif self.apn is None:

                    print("Cannot activate data context: APN not configured.")
                    self.send_response("ERROR")

                else:

                    self.data_connected = True
                    print("Data context activated.")
                    self.send_response("OK")

            case _ if command.startswith("AT+QIOPEN="):

                print("Opening TCP connection...")

                if not self.data_connected:

                    print(
                        "Cannot open TCP connection: "
                        "data context is inactive."
                    )

                    self.send_response("ERROR")

                else:

                    try:

                        # For this first version, use our local TCP server.
                        server_ip = "127.0.0.1"
                        server_port = 5000

                        self.tcp_socket = socket.socket(
                            socket.AF_INET,
                            socket.SOCK_STREAM
                        )

                        self.tcp_socket.connect(
                            (server_ip, server_port)
                        )

                        self.tcp_connected = True
                        self.connection_id = 0

                        print(
                            f"TCP connection established "
                            f"with {server_ip}:{server_port}"
                        )

                        # QIOPEN command accepted
                        self.send_response("OK")

                        # Asynchronous connection result
                        self.send_response("+QIOPEN: 0,0")

                    except Exception as error:

                        print(
                            f"TCP connection failed: {error}"
                        )

                        self.tcp_connected = False
                        self.connection_id = None

                        self.send_response("OK")
                        self.send_response("+QIOPEN: 0,1")

            case _ if command.startswith("AT+QISEND="):

                print("Preparing to send data...")

                if not self.tcp_connected:
                    print("Cannot send data: TCP connection not active.")
                    self.send_response("ERROR")
                    return

                try:
                    parts = command.split("=")[1].split(",")
                    connection_id = int(parts[0])
                    data_length = int(parts[1])

                    if connection_id != self.connection_id:
                        self.send_response("ERROR")
                        return

                    self.send_mode = True
                    self.send_length = data_length
                    print(f"Waiting for {data_length} bytes of data...")
                    self.send_response(">")

                except Exception as error:
                    print(f"QISEND parsing failed: {error}")
                    self.send_response("ERROR")

            case _ if command.startswith("AT+QICLOSE="):

                print("Closing TCP connection...")

                if not self.tcp_connected:
                    self.send_response("ERROR")
                    return

                try:
                    self.tcp_socket.close()

                    self.tcp_socket = None
                    self.tcp_connected = False
                    self.connection_id = None

                    print("TCP connection closed.")

                    self.send_response("OK")

                except Exception as error:
                    print(f"TCP close failed: {error}")
                    self.send_response("ERROR")

            case _ if command.startswith("AT+QIDEACT="):

                print("Deactivating data context...")

                if not self.data_connected:
                    self.send_response("ERROR")
                    return

                self.data_connected = False

                print("Data context deactivated.")

                self.send_response("OK")

            # =========================
            # Unknown command
            # =========================

            case _:

                self.send_response("ERROR")


    def run(self):

        print("Virtual EC200U started.")
        print(f"Listening on {self.port}")

        while True:

            if self.send_mode:

                data = self.serial.read(self.send_length)

                if len(data) < self.send_length:
                    continue

                payload = data

                print(f"ESP32 -> TCP: {payload}")

                try:
                    self.tcp_socket.send(payload)

                    print("Data sent successfully.")

                    self.send_mode = False
                    self.send_length = 0

                    self.send_response("SEND OK")

                except Exception as error:
                    print(f"TCP send failed: {error}")

                    self.send_mode = False
                    self.send_length = 0

                    self.send_response("ERROR")

                continue

            # Read one line from the serial port.
            command = self.serial.readline().decode(
                "utf-8",
                errors="replace"
            )
            if command.strip():
                self.handle_command(command)


if __name__ == "__main__":

    PORT = "/dev/pts/4"

    modem = VirtualModem(PORT)

    modem.run()