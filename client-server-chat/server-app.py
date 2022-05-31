from DataClasses.Server.Server import Server


if __name__ == '__main__':
    current_server = Server()
    while True:
        if input("Enter X to close server: ") == "X":
            current_server.__del__()
            exit()

