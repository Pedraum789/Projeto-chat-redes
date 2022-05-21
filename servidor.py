import socket
import csv
import pandas as pd
from csv import DictWriter

PORT = ""
SERVERPORT = 8081

FIELD_NAMES = ['LOGIN', 'PASSWORD']

def haveLogin(login):
    file = open('logins.csv')
    csvreader = csv.reader(file)
    next(csvreader)

    for row in csvreader:
        if(row[0] == login):
            file.close()
            return True
    file.close()
    return False

def havePassword(password, login):
    file = open('logins.csv')
    csvreader = csv.reader(file)
    next(csvreader)

    for row in csvreader:
        if(row[0] == login and row[1] == password):
            file.close()
            return True
    file.close()
    return False
    
def registerLogin(login):
    dict={FIELD_NAMES[0]:login, FIELD_NAMES[1]: ""}
    # Open your CSV file in append mode
    # Create a file object for this file
    with open('logins.csv', 'a') as f_object:
        
        # Pass the file object and a list 
        # of column names to DictWriter()
        # You will get a object of DictWriter
        dictwriter_object = DictWriter(f_object, fieldnames=FIELD_NAMES)
    
        #Pass the dictionary as an argument to the Writerow()
        dictwriter_object.writerow(dict)
    
        #Close the file object
        f_object.close()
        
def registerPassword(login, password):
    
    file = open('logins.csv')
    csvreader = csv.reader(file)
    next(csvreader)
    count = 0
    for row in csvreader:
        count+=1
        if(row[0] == login):
            break
    file.close()
    
    # reading the csv file
    df = pd.read_csv("logins.csv")
    # updating the column value/data
    df.loc[count-1, 'PASSWORD'] = password
    # writing into the file
    df.to_csv("logins.csv", index=False)
    print(df)
    
'''
    Funcao que faz o login
'''
def doingLogin(connectionSocket, split_request):
    print("Entrou no metodo LOGIN")
    if(len(split_request) > 1):
        login = split_request[1][split_request[1].find('<') + 1:split_request[1].find('>')]
        
        if(haveLogin(login)):
            print("Seu login e' " + login)
            response = "HTTP/1.1 200 OK\n\nUsuario com login\nPara logar utilizar o comando:\nPASSWORD <SENHA>\n\n"
            connectionSocket.sendall(response.encode())
            doingPassword(connectionSocket, login)
            return True
        else:
            print("Usuario nao tem login cadastrado")
            response = "HTTP/1.1 200 OK\n\nUsuario sem login\nPara se cadastrar utilizar o comando:\nREGISTER_LOGIN <NOME DO USUARIO>\n\n"
            connectionSocket.sendall(response.encode())
            return False
    else:
        print("Chamada errada " + split_request)
        response = "HTTP/1.1 500 Error\n\nFavor utilizar o comando corretamente LOGIN <NOME DO USUARIO>"
        connectionSocket.sendall(response.encode())
        connectionSocket.close()
        return False



def doingRegisterLogin(connectionSocket, split_request):
    print("Entrou no metodo CADASTRO LOGIN")
    if(len(split_request) > 1):
        login = split_request[1][split_request[1].find('<') + 1:split_request[1].find('>')]
        
        if(haveLogin(login)):
            print("Usuario ja cadastrado " + login)
            response = "HTTP/1.1 200 OK\n\nUsuario com login\nPara logar utilizar o comando:\nLOGIN <NOME DO USUARIO>\n\n"
            connectionSocket.sendall(response.encode())
            return False
        else:
            print("Usuario nao tem login cadastrado, cadastrando...")
            registerLogin(login)
            response = "HTTP/1.1 200 OK\n\nLogin cadastrado!\nPara cadastrar uma senha, utilizar o comando:\nREGISTER_PASSWORD <NOME DO USUARIO>\n\n"
            connectionSocket.sendall(response.encode())
            doingRegisterPassword(login, connectionSocket)
            return True
    else:
        print("Chamada errada " + split_request)
        response = "HTTP/1.1 500 Error\n\nFavor utilizar o comando corretamente LOGIN <NOME DO USUARIO>\n\n"
        connectionSocket.sendall(response.encode())
        connectionSocket.close()
        return False

def doingRegisterPassword(login, connectionSocket):
    print("Entrou no metodo CADASTRO PASSWORD")
    while True:
        split_request = connectionAndSplit(connectionSocket)
        if split_request[0] == 'REGISTER_PASSWORD':
            if(len(split_request) > 1):
                password = split_request[1][split_request[1].find('<') + 1:split_request[1].find('>')]
                registerPassword(login, password)
                response = "HTTP/1.1 200 OK\n\nSenha cadastrada\nPara logar utilizar o comando:\nLOGIN <NOME DO USUARIO>\n\n"
                connectionSocket.sendall(response.encode())
                return True
        else:
            print("Chamada errada " + split_request[0])
            response = "HTTP/1.1 500 Error\n\nFavor utilizar o comando corretamente REGISTER_PASSWORD <SENHA>\n\n"
            connectionSocket.sendall(response.encode())


def doingPassword(connectionSocket, login):
    while True:
        split_request = connectionAndSplit(connectionSocket)
        if split_request[0] == 'PASSWORD':
            if verifyingPassword(connectionSocket ,split_request, login):
                response = "HTTP/1.1 200 OK\n\nLogin FEITO!\n\n"
                connectionSocket.sendall(response.encode())
                return True
            else:
                print("Senha errada")
                response = "HTTP/1.1 200 OK\n\nSenha incorreta\nFavor utilizar o comando novamente:\nPASSWORD <SENHA>\n\n"
                connectionSocket.sendall(response.encode())
        else:
            print("Chamada errada " + split_request)
            response = "HTTP/1.1 500 Error\n\nFavor utilizar o comando corretamente PASSWORD <SENHA>\n\n"
            connectionSocket.sendall(response.encode())

def verifyingPassword(connectionSocket, split_request, login):
    print("Entrou no metodo PASSWORD")
    if(len(split_request) > 1):
        password = split_request[1][split_request[1].find('<') + 1:split_request[1].find('>')]
        
        if(havePassword(password, login)):
            print("Sua senha e' " + password)
            return True
        else:
            return False
    else:
        print("Chamada errada " + split_request)
        response = "HTTP/1.1 500 Error\n\nFavor utilizar o comando corretamente PASSWORD <SENHA>\n\n"
        connectionSocket.sendall(response.encode())
        return False

def connectionAndSplit(connectionSocket):
    request = connectionSocket.recv(1024).decode()

    return request.split()

def inicializeServer():

    #cria o socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #atribuir o socket a uma porta especifica
    serverSocket.bind((PORT, SERVERPORT))

    #inicia o "listening"
    serverSocket.listen(1)

    print("Servidor HTTP/1.1 Inicializado")

    connectionSocket, addr = serverSocket.accept()

    while True:
        print("Cliente {} conectado ao servidor".format(addr))
        
        split_request = connectionAndSplit(connectionSocket)
        
        try:
            if split_request[0] == 'LOGIN':
                if doingLogin(connectionSocket ,split_request):
                    pass
            elif split_request[0] == 'REGISTER_LOGIN':
                if doingRegisterLogin(connectionSocket ,split_request):
                    pass
            else:
                print("Comando não pode ser interpretado por esse servidor!")
                response = ("ERRO! Servidor não reconhece esse comando!").encode()
                connectionSocket.send(response)
                connectionSocket.close()
        except:
            pass
        
if __name__ == "__main__":
    inicializeServer()
