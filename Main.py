import json
import os
import unicodedata



# O usuário deve entrar com o seu login e senha​ (autenticação) e ter a funcionalidade de cadastrar usuário
# Se o usuário estiver autenticado, continue a execução do programa
# Caso contrário, saia do programa e mostre a mensagem "Usuário ou senha inválidos" na tela
# Um novo usuário cadastrado não deverá ter permissão para nenhum arquivo
# A relação usuário/senha deve estar armazenado em um arquivo (TXT, CSV ou JSON)
# As permissões dos usuários devem estar armazenadas em um arquivo (TXT, CSV ou JSON)
# O sistema deve perguntar ao usuário qual ação ele deseja realizar (ler, escrever ou apagar) sobre um recurso fictício
# No contexto do trabalho, o recurso fictício, no caso, não é um arquivo existente no sistema
# Ele deverá especificar a ação que deseja realizar (ler, escrever, apagar) sobre um recurso
# O sistema deve perguntar ao usuário qual arquivo ele deseja realizar a operação selecionada no item 2​
# O sistema deve imprimir na tela caso o acesso foi concedido ou não​
# “Acesso permitido” caso o acesso foi concedido​
# Se não, “Acesso negado”


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            dados = json.load(file)
            return dados
    except FileNotFoundError:
        return {}  
    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo JSON: {file_path}")
        return {}

def save_json(file_path, dados):
    try:
        with open(file_path, 'w') as file:
            json.dump(dados, file, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON {file_path}: {e}")
        return False

def processar_string(texto):
    if not isinstance(texto, str):
        raise TypeError("A entrada deve ser uma string.")
    texto_limpo = texto.strip()
    texto_maiusculo = texto_limpo.upper()
    texto_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', texto_maiusculo)
                                if unicodedata.category(c) != 'Mn')


def criar_usuario(file_path, nome_usuario, senha):
    
    dados = load_json(file_path)

    if dados is None:
        return None

    proximo_numero = 1
    for usuario in dados.get("usuarios", []):
        login_existente = usuario.get("login")
        if login_existente and login_existente.startswith("user"):
            try:
                numero = int(login_existente[4:])
                proximo_numero = max(proximo_numero, numero + 1)
            except ValueError:
                pass

    novo_login = f"user{proximo_numero}"
    novo_usuario = {
        "login": novo_login,
        "senha": senha,
        "nome": nome_usuario
    }

    dados.setdefault("usuarios", []).append(novo_usuario)

    if save_json(file_path, dados):
        return novo_login
    else:
        return None

    
def criar_permissoes(file_path, nome_completo, novo_usuario):
    
    dados = load_json(file_path)

    if dados is None:
        return False

    permissoes_usuario = {
        "usuario_id": novo_usuario,
        "nome": nome_completo,
        "cargo": "Sem Cargo",
        "permissoes": {"permissao": []}, 
        "status": "ativo"
    }

    
    dados[novo_usuario] = permissoes_usuario 

    if save_json(file_path, dados):
        return True
    else:
        return False


def Login():
    dados_permissoes = load_json("permissoes.json")
    dados_login = load_json("usuarios.json") #carrega o arquivo usuarios.json

    while True:

        if dados_login:
            login_usuario = input("Digite seu login: ")
            
            usuario_encontrado = None 
            for usuario in dados_login.get("usuarios", []): 
                if usuario.get("login") == login_usuario: 
                    usuario_encontrado = usuario 
            
            if not usuario_encontrado:
                print("Login não encontrado.")
                continue
            
            elif dados_permissoes[login_usuario]["status"] == "bloqueado": 
                print("Conta bloqueada. Entre em contato com o administrador.")
                return None, None
            else:
                tentativas = 0
                while tentativas < 5:
                    senha_usuario = input("Digite sua senha: ")
                   
                    if usuario_encontrado["senha"] == senha_usuario: 
                        print("\nLogin autenticado!")
                        print(f"Bem-vindo, {usuario_encontrado['nome']}!")
                        return usuario_encontrado, dados_permissoes[login_usuario]["permissoes"]["permissao"]
                        
                    else:
                        tentativas += 1
                        print(f"Senha incorreta. Você tem {5 - tentativas} tentativas restantes.")
                    if tentativas >= 5:
                        print("Número máximo de tentativas excedido. Conta bloqueada.")
                        dados_permissoes[login_usuario]["status"] = "bloqueado"
                        save_json("permissoes.json", dados_permissoes)
                        break
                else:
                    break 
        else:
            print("Erro ao carregar dados de usuários.") 
            break 





















def main():
    print("\nBem-vindo!")
    while True:
        print("\nMenu:")
        print("1. Login")
        print("2. Criar novo usuário")
        print("3. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            login_usuario, permissoes_usuario = Login() 
            while True:
                if login_usuario:
                    print("\nO que você deseja fazer?")
                    print("1. Ler arquivo")
                    print("2. Escrever arquivo")
                    print("3. Apagar arquivo")
                    print("4. Sair")
                    acao = input("Escolha uma ação: ")

                    acao_para_permissao = {
                        "1": "ler",
                        "2": "escrever",
                        "3": "apagar"
                    }

                    permissao_necessaria = acao_para_permissao.get(acao)

                    if permissao_necessaria:
                        if permissao_necessaria in permissoes_usuario:
                            print("\nAcesso permitido")
                            print(f"Ação realizada: {permissao_necessaria}.")
                            continue
                        else:
                            print(f"Você não possui permissão para {permissao_necessaria} o arquivo.")
                    elif acao == "4":
                        print("\nSaiu!")
                        break
                    else:
                        print("Ação inválida.")
                else:
                    print("Login falhou.")
                    break
       
        elif escolha == "2":
            nome_completo = input("Digite seu nome completo: ")  
            senha = input("Digite sua senha: ")
            nome_completo = processar_string(nome_completo)
            novo_usuario = criar_usuario("usuarios.json", nome_completo, senha)

            if novo_usuario:
                print(f"O cadastro de {nome_completo} foi criado com sucesso!")
                print(f"Seu login é: {novo_usuario}")
                nova_permissao = criar_permissoes("permissoes.json", nome_completo, novo_usuario)
                if nova_permissao:
                    print("Permissões criadas com sucesso!")
                else:
                    print("Falha ao criar as permissões, contate o administrador.")
            else:
                print("Falha ao criar o novo usuário.")
        elif escolha == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
    