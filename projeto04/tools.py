import datetime
import random
import string


def calcular_idade(data_nascimento: str) -> str:
    """
    Calcula a idade a partir da data de nascimento.
    Formato esperado: YYYY-MM-DD
    """
    try:
        nascimento = datetime.date.fromisoformat(data_nascimento)
        hoje = datetime.date.today()
        idade = hoje.year - nascimento.year - (
            (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
        )
        return f"{idade} anos (nascido em {nascimento.strftime('%d/%m/%Y')})"
    except ValueError:
        return "Data inválida. Use o formato YYYY-MM-DD (ex: 1990-05-15)"


def converter_temperatura(valor: float, escala_origem: str, escala_destino: str) -> str:
    """
    Converte temperatura entre Celsius, Fahrenheit e Kelvin.
    """
    escala_origem = escala_origem.lower().strip()
    escala_destino = escala_destino.lower().strip()

    # Normaliza aliases
    aliases = {"c": "celsius", "f": "fahrenheit", "k": "kelvin"}
    escala_origem = aliases.get(escala_origem, escala_origem)
    escala_destino = aliases.get(escala_destino, escala_destino)

    # Converte para Celsius primeiro
    if escala_origem == "celsius":
        celsius = valor
    elif escala_origem == "fahrenheit":
        celsius = (valor - 32) * 5 / 9
    elif escala_origem == "kelvin":
        celsius = valor - 273.15
    else:
        return f"Escala '{escala_origem}' não reconhecida."

    # Converte de Celsius para destino
    if escala_destino == "celsius":
        resultado = celsius
    elif escala_destino == "fahrenheit":
        resultado = celsius * 9 / 5 + 32
    elif escala_destino == "kelvin":
        resultado = celsius + 273.15
    else:
        return f"Escala '{escala_destino}' não reconhecida."

    simbolos = {"celsius": "°C", "fahrenheit": "°F", "kelvin": "K"}
    s_origem = simbolos.get(escala_origem, "")
    s_destino = simbolos.get(escala_destino, "")

    return f"{valor}{s_origem} = {resultado:.2f}{s_destino}"


def calcular_imc(peso: float, altura: float) -> str:
    """
    Calcula o IMC (Índice de Massa Corporal).
    peso em kg, altura em metros.
    """
    if altura <= 0 or peso <= 0:
        return "Peso e altura devem ser valores positivos."

    imc = peso / (altura ** 2)

    if imc < 18.5:
        classificacao = "Abaixo do peso"
    elif imc < 25:
        classificacao = "Peso normal"
    elif imc < 30:
        classificacao = "Sobrepeso"
    elif imc < 35:
        classificacao = "Obesidade grau I"
    elif imc < 40:
        classificacao = "Obesidade grau II"
    else:
        classificacao = "Obesidade grau III"

    return f"IMC: {imc:.1f} — {classificacao} (peso: {peso}kg, altura: {altura}m)"


def gerar_senha(tamanho: int = 12) -> str:
    """
    Gera uma senha aleatória segura com letras, números e símbolos.
    """
    if tamanho < 4:
        tamanho = 4
    if tamanho > 64:
        tamanho = 64

    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    # Garante ao menos um de cada tipo
    senha = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%&*"),
    ]
    senha += random.choices(caracteres, k=tamanho - 4)
    random.shuffle(senha)
    return "".join(senha)


def data_atual() -> str:
    """Retorna a data atual formatada."""
    return datetime.date.today().strftime("%d/%m/%Y")