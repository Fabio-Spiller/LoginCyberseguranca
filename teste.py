import json
import os
import unicodedata

def processar_string(texto):
    if not isinstance(texto, str):
        raise TypeError("A entrada deve ser uma string.")
    texto_limpo = texto.strip()
    texto_maiusculo = texto_limpo.upper()
    texto_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', texto_maiusculo)
                                if unicodedata.category(c) != 'Mn')

    return texto_sem_acentos

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