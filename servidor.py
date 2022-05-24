import socket
import csv
import pandas as pd
import threading
import time
from csv import DictWriter

PORT = ""
SERVERPORT = 8081

MENSAGES = []
CONNECTIONS = []
FIELD_NAMES = ['LOGIN', 'PASSWORD']

def connectionAndSplit(connectionSocket):
    request = connectionSocket.recv(1024).decode()

    return request.split()

def enviar_mensagem_individual(conexao):
    for i in range(conexao['last'], len(MENSAGES)):
        conexao['connectionSocket'].send(MENSAGES[i])
        conexao['last'] = i + 1
        time.sleep(0.2)

#{'sala': room, 'users': [{"addr": "", "conn": "", "last": 0, "username": ""}], 'mensagens': []}
def sendMessage(room, msg, login):
    for i in CONNECTIONS:
        if i['sala'] == room:
            if msg == '/EXIT\r\n':
                if removeUserRoom(i, login):
                    return False
            i['mensagens'].append(msg)
            for user in i['users']:
                for m in range(user['last'], len(i['mensagens'])):
                    if (user['username'] == login and len(i['mensagens'])-1 == m):
                        pass
                    else:
                        user['conn'].sendall(i['mensagens'][m].encode())
                    user['last'] += 1
                    time.sleep(0.1)
    return True

def removeUserRoom(objeto, login):
    for i in range(len(objeto['users'])):
        if objeto['users'][i]['username'] == login:
            objeto['users'].pop(i)
            return True
    return False
                
      
def sendMessageAfterJoin(room, connectionSocket, addr, login):
    while True:
        receive = connectionSocket.recv(1024).decode() 
        if sendMessage(room, receive, login) == False:
            print("Saiu da sala user: " + login)
            response = "HTTP/1.1 200 OK\n\nUsuario saiu da sala\n\n"
            connectionSocket.sendall(response.encode())
            break
            

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

def haveRoom(room):
    for i in CONNECTIONS:
        if i['sala'] == room:
            return True
    return False

def createRoom(room):
    if haveRoom(room):
        return False
    
    CONNECTIONS.append({'sala': room, 'users': [], 'mensagens': []})
    return True

def joinOnRoom(room, connectionSocket, addr, login):
    for i in CONNECTIONS:
        if i['sala'] == room:
            i['users'].append({"addr": addr, "conn": connectionSocket, "last": 0, "username": login})

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
def doingLogin(connectionSocket, split_request, addr):
    print("Entrou no metodo LOGIN")
    if(len(split_request) > 1):
        login = split_request[1][split_request[1].find('<') + 1:split_request[1].find('>')]
        
        if(haveLogin(login)):
            print("Seu login e' " + login)
            response = "HTTP/1.1 200 OK\n\nUsuario com login\nPara logar utilizar o comando:\nPASSWORD <SENHA>\n\n"
            connectionSocket.sendall(response.encode())
            doingPassword(connectionSocket, login)
            return [True, login]
        else:
            print("Usuario nao tem login cadastrado")
            response = "HTTP/1.1 200 OK\n\nUsuario sem login\nPara se cadastrar utilizar o comando:\nREGISTER_LOGIN <NOME DO USUARIO>\n\n"
            connectionSocket.sendall(response.encode())
            return [False, login]
    else:
        print("Chamada errada " + split_request[0])
        response = "HTTP/1.1 500 Error\n\nFavor utilizar o comando corretamente LOGIN <NOME DO USUARIO>"
        connectionSocket.sendall(response.encode())
        connectionSocket.close()
        return [False, login]



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
        print("Chamada errada " + split_request[0])
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
                response  = "HTTP/1.1 200 OK\n\nLogin FEITO!\n\nComandos disponiveis:\n\n"
                response += "LIST --- Listar Salas\n"
                response += "CREATE <NOME DA SALA> -- Criar uma sala\n"
                response += "JOIN <NOME DA SALA> --- Entrar na sala\n"
                response += "LEAVE_SERVER --- Deixar o servidor\n\n"
                
                connectionSocket.sendall(response.encode())
                break
            else:
                print("Senha errada")
                response = "HTTP/1.1 200 OK\n\nSenha incorreta\nFavor utilizar o comando novamente:\nPASSWORD <SENHA>\n\n"
                connectionSocket.sendall(response.encode())
        else:
            print("Chamada errada " + split_request[0])
            response = "HTTP/1.1 500 Error\n\nFavor utilizar o comando corretamente PASSWORD <SENHA>\n\n"
            connectionSocket.sendall(response.encode())
    return True

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
        print("Chamada errada " + split_request[0])
        response = "HTTP/1.1 500 Error\n\nFavor utilizar o comando corretamente PASSWORD <SENHA>\n\n"
        connectionSocket.sendall(response.encode())
        return False



#{'sala': room, 'users': [{"addr": "", "conn": "", "last": 0, "username": ""}], 'mensagens': []}
def listRooms():
    rooms = ''
    for i in CONNECTIONS:
        rooms += (i['sala'] + '\n\n')
        
    return rooms

def rooms(connectionSocket, addr, login):
    while True:
        split_request = connectionAndSplit(connectionSocket)
        
        if split_request[0] == 'LIST':
            rooms = listRooms()
            response = "HTTP/1.1 200 OK\n\nSalas do servidor:\n\n" + rooms + "\n"
            connectionSocket.sendall(response.encode())
            
        elif split_request[0] == 'CREATE':
            room = split_request[1][split_request[1].find('<') + 1:split_request[1].find('>')]
            if room == "":
                response = "HTTP/1.1 500 Error\n\nNome da sala com espacos!\n\n"
                connectionSocket.sendall(response.encode())
            elif createRoom(room):
                response = "HTTP/1.1 200 OK\n\nSala CRIADA!\n\n"
                connectionSocket.sendall(response.encode())
            else:
                response = "HTTP/1.1 200 OK\n\nSala ja existe no servidor!\n\n"
                connectionSocket.sendall(response.encode())
        
        elif split_request[0] == 'JOIN':
            room = split_request[1][split_request[1].find('<') + 1:split_request[1].find('>')]
            if room == "":
                response = "HTTP/1.1 500 Error\n\nNome da sala com espacos!\n\n"
                connectionSocket.sendall(response.encode())
            elif haveRoom(room):
                response = "HTTP/1.1 200 OK\n\nVoce entrou na sala {}!\n\n".format(room)
                joinOnRoom(room, connectionSocket, addr, login)
                connectionSocket.sendall(response.encode())
                sendMessageAfterJoin(room, connectionSocket, addr, login)
            else:
                response = "HTTP/1.1 500 Error\n\nSala nao existe\n\n"
                connectionSocket.sendall(response.encode())
            
        
        elif split_request[0] == 'LEAVE_SERVER':
            print("Saindo do servidor")
            response = "HTTP/1.1 200 OK\n\nSaindo do servidor...\nBye :)\n"
            connectionSocket.sendall(response.encode())
            connectionSocket.close()
            break
        else:
            response  = "HTTP/1.1 200 OK\n\nComando nao existe\n"
            response += "Comandos disponiveis:\n\n"
            response += "LIST --- Listar Salas\n"
            response += "CREATE <NOME DA SALA> -- Criar uma sala\n"
            response += "JOIN <NOME DA SALA> --- Entrar na sala\n"
            response += "LEAVE_SERVER --- Deixar o servidor\n\n"
            connectionSocket.sendall(response.encode())
    return True

def handle_client(connectionSocket, addr):
    print("Nova coneccao feita, endereco: {}".format(addr))
    
    while True:
        split_request = connectionAndSplit(connectionSocket)
        try:
            if split_request[0] == 'LOGIN':
                resp = doingLogin(connectionSocket ,split_request, addr)
                if resp[0]:
                    rooms(connectionSocket, addr, resp[1])
                    
            elif split_request[0] == 'REGISTER_LOGIN':
                if doingRegisterLogin(connectionSocket ,split_request):
                    pass
            else:
                print("Comando não pode ser interpretado por esse servidor!")
                response = "ERRO! Servidor não reconhece esse comando!"
                connectionSocket.sendall(response.encode())
                connectionSocket.close()
        except:
            pass

def inicializeServer():

    #cria o socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #atribuir o socket a uma porta especifica
    serverSocket.bind((PORT, SERVERPORT))

    #inicia o "listening"
    serverSocket.listen(1)

    print("Servidor HTTP/1.1 Inicializado")
    while True:
        connectionSocket, addr = serverSocket.accept()      
        thread = threading.Thread(target=handle_client, args=(connectionSocket, addr))
        thread.start()
        
if __name__ == "__main__":
    inicializeServer()
