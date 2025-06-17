import json                 
import requests  
import os

os.system('cls')


def consultar_endereco_por_cep(cep): #funcao pra consultar o endereco com base no cep
    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        if "erro" in dados:
            return None
        resultado = {
            'cidade': dados.get('localidade'),
            'logradouro': dados.get('logradouro'),
            'UF': dados.get('uf'),
            'bairro': dados.get('bairro')
            }
        return resultado
    except Exception as e:  
        print(f"ocorreu um erro: {e}")
        return None

def consultar_cep_por_endereco(estado, cidade, rua): #funcao pra consultar o cep com base no endereco
    url = f"https://viacep.com.br/ws/{estado}/{cidade}/{rua}/json/"
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        if isinstance(dados, list) and len(dados) > 0:
            return dados
        return None
    except Exception as e:
        print(f"acoteceu um erro: {e}")
        return None
    print(url)


with open('superdb.json','r', encoding='utf-8') as db: #vai ler o json
    dados = json.load(db)

print('bem vindo a tela de login!! ')

decisao = str(input('voce quer entrar ou se registrar?[E/R] ')).upper().strip()[0]   

emailReg = False  #mais pra frente vai entender, serve pra manter o controle se o email existe registrado ou se a senha ta certa
senhaCerta = False

if decisao == 'R': #usuario se registrando
    email = input('me diga seu email para registrar: ')
    nome = str(input('me diga seu nome completo: '))
    senha = input('me diga sua senha: ')
    cepDecisao = str(input('voce sabe seu CEP?? [S/N]: ')).upper().strip()[0]
    if cepDecisao == 'S':
        cep = int(input('me diga seu cep: '))
        endereco = consultar_endereco_por_cep(cep)
        numero = int(input('pode me dar o numero da sua casa por favor?: ')) 
        comp = input('pode me dar o complemento?(opcional): ') or None  #aqui nao tem segredo a API ja da os dados certinhos com base no CEP
    elif cepDecisao == 'N':
        print('ja que voce nao sabe ceu cep, vamos encontra-lo: ')
        while True:
            estado = str(input('me diga a sigla do seu estado(ex: SP, RJ...): ')).upper()
            cidade = str(input('me diga o nome exato da sua cidade: '))
            rua = str(input('me diga o nome exato da sua rua: '))
            numero = int(input('pode me dar o numero da sua casa por favor?: '))
            comp = input('pode me dar o complemento?:(opcional) ') or None 
            enderecos = consultar_cep_por_endereco(estado, cidade, rua)  #como a API geralmente manda um milhao de CEPS disponiveis, o usuario vai escolher um
            if not enderecos:
                print('nenhum CEP encontrado com base nos dados fornecidos, tente novamente.')
                continue
            elif len(enderecos) == 1:
                endereco = enderecos[0]
                cep = endereco['cep']
                print(f'CEP encontrado: {cep}')
                break
            else:
                print('Varios enderecos encotntrados, escolha o seu: ')
                for i, n in enumerate(enderecos, 1):
                    print(f'{i} - {n['logradouro']}, {n['bairro']}, CEP: {n['cep']} ') #isso vai numerar os ceps encontrados pela api pro usuario escolher
                while True:
                    try:
                        decisao = int(input(f'digite o numero referente ao seu endereco correto(1 a {len(enderecos)}): ')) #escolha do usuario
                        if 1<=decisao<=len(enderecos):
                            endereco = enderecos[decisao-1]
                            cep = endereco['cep']
                            print(f'cep escolhido: {cep} ')
                            break
                        else:
                            print('numero invalido tente um valido.')
                    except ValueError: 
                        print("Digite apenas números.")
            break
                

    usuario_novo ={ #criei um dicionario pra depois adicionar no json
        'nome': nome,
        'email': email,
        'senha': senha,
        'numero': numero,
        'Complemento': comp,
        **endereco #funcao nova que descobri. Nao da pra fazer apendd com dicionario, entao se voce fizer ** ele simplesmente vai, se ta funcionando nao mexa =)
    }

    dados['usuarios'].append(usuario_novo)
    print(f'usuario registrado com sucesso, bem vindo {nome}!')

elif decisao == 'E': #pra entrar eh facil, basicamente ele verifica se ha usuario e se a senha ta certa
    while True:
        email = input('me diga seu email de login: ')
        for usuario in dados['usuarios']: #ele vai passar por cada dicionario que significa um usuario
            if usuario['email'] == email: #verifica se ha um email registrado conforme passado pelo usuario
                emailReg = True #email registrado!
                break
            else:
                emailReg = False #nao ha esse email registrado
                continue
        if emailReg == False:
            print('email nao registrado')
            continue
        break
    
    while True:
        senha = input('me diga sua senha de acesso: ')
        for usuario in dados['usuarios']:
            if usuario['email'] == email and usuario['senha'] == senha: #vai passar por todos ate achar um email igual ao falado antes que ja sabemos que existe, e vai verificar se a senha ta certa
                    print('senha correta!')
                    senhaCerta = True #senha certa
                    break
            else:
                senhaCerta = False
        if senhaCerta:
            break
        else:
            print('senha errada, tente novamente. ')
            continue
if senhaCerta and emailReg:
    for usuario in dados['usuarios']:
        if usuario['email'] == email:
            nome = usuario['nome']
    print(f'USUARIO LOGADO COM SUCESSO!! BEM VINDO {nome} ')

with open('superdb.json', 'w', encoding='utf-8') as db: #msm coisa que o outro mas pra escrever
    json.dump(dados, db, indent=4, ensure_ascii=False)   #o indent=4 serve pra ele usar a identacao padrao e pra ficar alinhado, o ensure_ascii=True serve pra aceitar melhor o alfabeto portugues-BR