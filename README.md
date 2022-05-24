# Projeto-chat-redes
Apos rodar a aplicacao, utilizar o comando: `telnet localhost 8080`


## Metodos para login

| METODO | DESCRICAO | OBSERVACAO |
| ------------------- | ------------------- | ------------------- |
| `LOGIN <NOME DO USUARIO>` | Utilizado para logar o usuario | - |

#### Caso consiga fazer login
`HTTP/1.1 200 OK\n\nUsuario com login\nPara logar utilizar o comando:\nPASSWORD <SENHA>\n\n`

#### Caso o usuario nao tem login cadastrado
`HTTP/1.1 401 Unauthorized\n\nUsuario sem login\nPara se cadastrar utilizar o comando:\nREGISTER_LOGIN <NOME DO USUARIO>\n\n`

#### Caso o usuario tenha utilizado o comando errado
`HTTP/1.1 406 Not Acceptable\n\nFavor utilizar o comando corretamente LOGIN <NOME DO USUARIO>`

***

| METODO | DESCRICAO | OBSERVACAO |
| ------------------- | ------------------- | ------------------- |
| `PASSWORD <SENHA>` | Verifica a senha para logar | Pode ser utilizado apenas depois do LOGIN |

#### Caso o usuario digite corretamente a senha
`HTTP/1.1 200 OK\n\nLogin FEITO!\n\nComandos disponiveis:\n\n
LIST --- Listar Salas\n
CREATE <NOME DA SALA> -- Criar uma sala\n
JOIN <NOME DA SALA> --- Entrar na sala\n
LEAVE_SERVER --- Deixar o servidor\n\n`

#### Caso o usuario digite errado a senha
`HTTP/1.1 401 Unauthorized\n\nSenha incorreta\nFavor utilizar o comando novamente:\nPASSWORD <SENHA>\n\n`

#### Caso o usuário digite o comando errado
`HTTP/1.1 404 Not Found\n\nFavor utilizar o comando corretamente PASSWORD <SENHA>\n\n`

***

| METODO | DESCRICAO | OBSERVACAO |
| ------------------- | ------------------- | ------------------- |
| `REGISTER_LOGIN <NOME DO USUARIO>` | Cadastrar um login | - |

#### Casoo o usuário ja tenha login
`HTTP/1.1 200 OK\n\nUsuario com login\nPara logar utilizar o comando:\nLOGIN <NOME DO USUARIO>\n\n`

#### Caso o usuário cadastre o login
`HTTP/1.1 200 OK\n\nLogin cadastrado!\nPara cadastrar uma senha, utilizar o comando:\nREGISTER_PASSWORD <NOME DO USUARIO>\n\n`

#### Caso o usuário utilize o comando errado
`HTTP/1.1 404 Not Found\n\nFavor utilizar o comando corretamente REGISTER_LOGIN <NOME DO USUARIO>\n\n`

***

| METODO | DESCRICAO | OBSERVACAO |
| ------------------- | ------------------- | ------------------- |
| `REGISTER_PASSWORD <SENHA>` | Cadastrar uma senha | Pode ser utilizado apenas depois do REGISTER_LOGIN |

#### Caso o usuário cadastre a senha corretamente
`HTTP/1.1 200 OK\n\nSenha cadastrada\nPara logar utilizar o comando:\nLOGIN <NOME DO USUARIO>\n\n`

#### Caso o usuário utilize o comando errado
`HTTP/1.1 404 Not Found\n\nFavor utilizar o comando corretamente REGISTER_PASSWORD <SENHA>\n\n`

***

| METODO | DESCRICAO | OBSERVACAO |
| ------------------- | ------------------- | ------------------- |
| `LIST` | Lista os servidores | As salas são apagadas quando o servidor cair |

#### Caso o usuário utilize o comando corretamente
`HTTP/1.1 200 OK\n\nSalas do servidor:\n\n" + rooms + "\n`

***

| METODO | DESCRICAO | OBSERVACAO |
| ------------------- | ------------------- | ------------------- |
| `CREATE <NOME DA SALA>` | Cria uma sala | Ao cair o servidor essa sala não vai mais existir |

#### Caso o nome da sala tenha espacos
`HTTP/1.1 500 Error\n\nNome da sala com espacos!\n\n`

#### Caso consiga criar uma sala
`HTTP/1.1 201 Created\n\nSala CRIADA!\n\n`

#### Caso a sala ja exista
`HTTP/1.1 200 OK\n\nSala ja existe no servidor!\n\n`

***

| METODO | DESCRICAO | OBSERVACAO |
| ------------------- | ------------------- | ------------------- |
| `JOIN <NOME DA SALA>` | Entra na sala | Ao entrar na sala pode enviar qualquer mensagem (COMANDO /EXIT SAI DA SALA) |

#### Caso o nome da sala tenha espacos
`HTTP/1.1 500 Error\n\nNome da sala com espacos!\n\n`

#### Caso consiga entrar na sala
`HTTP/1.1 200 OK\n\nVoce entrou na sala room!\n\n`

#### Caso a sala não exista
`HTTP/1.1 404 Not found\n\nSala nao existe\n\n`

***

| METODO | DESCRICAO | OBSERVACAO |
| ------------------- | ------------------- | ------------------- |
| `LEAVE_SERVER` | Sai do servidor | Usuário sai do servidor (pode ser utilizado apenas depois de logado e nao pode estar em nenhuma sala) |

#### Caso o usuário consiga sair do servidor
`HTTP/1.1 200 OK\n\nSaindo do servidor...\nBye :)\n`

***

#### Caso seja um comando não reconhecido pelo servidor
`ERRO! Servidor não reconhece esse comando!`
