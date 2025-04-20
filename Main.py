import json
import unicodedata

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
    return texto_sem_acentos


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
    dados_login = load_json("usuarios.json") 

    while True:

        if dados_login:
            login_usuario = input("Digite seu login: ")
            
            usuario_encontrado = None 
            for usuario in dados_login.get("usuarios", []): 
                if usuario.get("login") == login_usuario: 
                    usuario_encontrado = usuario 
            
            if not usuario_encontrado:
                print_mensagem("Login não encontrado. Tente novamente.", tipo="erro")
                continue
            
            elif dados_permissoes[login_usuario]["status"] == "bloqueado":
                print_mensagem("Conta bloqueada. Entre em contato com o administrador.", tipo="erro")
                return None, None
            else:
                tentativas = 0
                while tentativas < 5:
                    senha_usuario = input("\nDigite sua senha: ")
                   
                    if usuario_encontrado["senha"] == senha_usuario: 
                        print_mensagem(f"Bem-vindo(a), {usuario_encontrado['nome']}!", tipo="sucesso")
                        return usuario_encontrado, dados_permissoes[login_usuario]["permissoes"]["permissao"]
                        
                    else:
                        tentativas += 1
                        print_mensagem(f"Senha incorreta. Você tem {5 - tentativas} tentativas restantes", tipo="erro")
                        
                    if tentativas >= 5:
                        print_mensagem("Número máximo de tentativas atingido. Conta bloqueada.", tipo="erro")
                        dados_permissoes[login_usuario]["status"] = "bloqueado"
                        save_json("permissoes.json", dados_permissoes)
                        break
                else:
                    break 
        else:
            print_mensagem("Nenhum usuário encontrado.", tipo="erro")
            break 


def listar_arquivos(permissoes_usuario):
  
    print("Arquivos disponíveis:")
    print("\n1. arquivo1.txt")
    print("2. arquivo2.txt")
    print("3. arquivo3.txt")
    print("\n4. Sair") 

    while True:
        arquivo_escolhido = input("\nDigite o número do arquivo que deseja acessar: ")

        if arquivo_escolhido in ["1", "2", "3"]:
            print(f"\nVocê escolheu o arquivo {arquivo_escolhido}. O que deseja fazer?")
            print("1. Ler arquivo")
            print("2. Escrever arquivo")
            print("3. Apagar arquivo")
            print("4. Sair")
            acao = input("Escolha uma ação: ")

            acao_para_permissao = {
                "1": "ler",
                "2": "escrever",
                "3": "apagar",
            }
            permissao_necessaria = acao_para_permissao.get(acao)

            if acao == "4":
                print_mensagem("Saindo do programa", tipo="info")
                break 
            elif permissao_necessaria:
                if permissao_necessaria in permissoes_usuario:
                    print_mensagem(f"Acesso permitido para {permissao_necessaria} o arquivo {arquivo_escolhido}.", tipo="sucesso")
                
                else:
                    print_mensagem(f"Você não possui permissão para {permissao_necessaria} o arquivo.", tipo="erro")
            else:
                print_mensagem("Ação inválida. Tente novamente.", tipo="erro")
        elif arquivo_escolhido == "4": 
            print_mensagem("Saindo do programa...", tipo="info")
            return 
        else:
            print_mensagem("Arquivo inválido.", tipo="erro") 
        


def print_mensagem(mensagem, tipo="info"):
    
    
    cores = {
        "info": "\033[34m",    # Azul
        "sucesso": "\033[32m", # Verde
        "erro": "\033[31m",   # Vermelho
        "reset": "\033[0m"    # Resetar a cor
    }
    estilo = {
        "inicio": "\033[1m",
        "fim": "\033[0m"
    }

    cor = cores.get(tipo, cores["info"])

    # Versão com caixa
    largura_caixa = len(mensagem) + 6
    print(f"{estilo['inicio']}{cor}" + "-" * largura_caixa + f"{cores['reset']}")
    print(f"{estilo['inicio']}{cor}|  {mensagem}  |{cores['reset']}")
    print(f"{estilo['inicio']}{cor}" + "-" * largura_caixa + f"{cores['reset']}")














def main():
    print_mensagem("Bem-vindo(a), escolha sua opção!", tipo="info")
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
                    listar_arquivos(permissoes_usuario)
                    break
                else:
                    print_mensagem("Login falhou", tipo="erro") 
                    break
       
        elif escolha == "2":
            nome_completo = input("Digite seu nome completo: ")  
            senha = input("Digite sua senha: ")
            nome_completo = processar_string(nome_completo)
            novo_usuario = criar_usuario("usuarios.json", nome_completo, senha)

            if novo_usuario:
                print_mensagem(f"Usuário {nome_completo} criado com sucesso!", tipo="sucesso")
                print_mensagem(f"Seu Login para acessar a conta é: {novo_usuario}", tipo="sucesso")
                nova_permissao = criar_permissoes("permissoes.json", nome_completo, novo_usuario)
                if nova_permissao:
                    print_mensagem("Permissões criadas com sucesso!", tipo="sucesso")
                else:
                    print_mensagem("Falha ao criar permissões para o novo usuário.", tipo="erro")
            else:
                print_mensagem("Falha ao criar o novo usuário.", tipo="erro")
        elif escolha == "3":
            print_mensagem("Saindo do programa. Até logo!", tipo="info")
            break
        else:
            print_mensagem("Opção inválida. Tente novamente.", tipo="erro")

if __name__ == "__main__":
    main()
    