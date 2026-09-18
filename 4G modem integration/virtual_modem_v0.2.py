import serial


class VirtualModem:
    def __init__(self, port):
        self.port = port
        self.baudrate = 115200

        # Internal modem state
        self.sim_ready = True
        self.network_registered = True
        self.data_connected = False

        self.signal_quality = 20
        self.operator = "MTN"

        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=0.1
        )

    def send_response(self, response):
        message = f"\r\n{response}\r\n"
        self.serial.write(message.encode())

    def handle_command(self, command):
        match command:

            case "AT":
                self.send_response("OK")

            case "AT+CPIN?":
                if self.sim_ready:
                    self.send_response("+CPIN: READY\r\n\r\nOK")
                else:
                    self.send_response("+CPIN: SIM PIN")

            case "AT+CSQ":
                self.send_response(
                    f"+CSQ: {self.signal_quality},99\r\n\r\nOK"
                )

            case "AT+COPS?":
                self.send_response(
                    f'+COPS: 0,0,"{self.operator}"\r\n\r\nOK'
                )

            case "AT+CEREG?":
                if self.network_registered:
                    self.send_response("+CEREG: 0,1\r\n\r\nOK")
                else:
                    self.send_response("+CEREG: 0,0\r\n\r\nOK")

            case _:
                self.send_response("ERROR")

    def run(self):
        print("Virtual EC200U started")
        print(f"Listening on {self.port}")

        while True:
            data = self.serial.readline()

            if not data:
                continue

            command = data.decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if command:
                print(f"ESP32 -> {command}")
                self.handle_command(command)


if __name__ == "__main__":
    PORT = "/dev/pts/1"  # Change this to your actual PTY

    modem = VirtualModem(PORT)
    modem.run()