import serial

PORT = "/dev/pts/4"   
BAUDRATE = 115200

modem = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    timeout=0.1
)

print("Virtual EC200U started")
print(f"Listening on {PORT}")

while True:
    data = modem.readline()

    if data:
        command = data.decode("utf-8", errors="ignore").strip()

        print(f"Received: {command}")

        if command == "AT":
            modem.write(b"\r\nOK\r\n")