"""
Sistema de Análise de Dados

Lê um arquivo CSV com e-mail, CPF, telefone e data de nascimento, valida cada
campo com expressões regulares (módulo re), trata exceções e gera um relatório.

Uso:
    python analise_dados.py              (lê dados.csv)
    python analise_dados.py outro.csv    (lê outro arquivo)
"""

import csv
import re
import sys
from datetime import datetime

# ----------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------

COLUNAS_OBRIGATORIAS = ["nome", "email", "cpf", "telefone", "data_nascimento"]
IDADE_MINIMA = 0
IDADE_MAXIMA = 120
ARQUIVO_RELATORIO = "relatorio.txt"

# Padrões em raw strings (r"...") para o Python não interpretar a "\"
# ^ início da string | $ fim da string | \d dígito | \w letra/número/_ | \s espaço
PADRAO_EMAIL = r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$"
PADRAO_CPF = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
PADRAO_TELEFONE = r"^\(\d{2}\)\s?9?\d{4}-\d{4}$"
PADRAO_DATA = r"^\d{2}/\d{2}/\d{4}$"


# ----------------------------------------------------------------------
# EXCEÇÕES PERSONALIZADAS (regras de negócio)
# ----------------------------------------------------------------------

class FormatoInvalidoError(Exception):
    """Campo que não segue o formato esperado."""

    def __init__(self, campo, valor):
        self.campo = campo
        self.valor = valor
        super().__init__(f"{campo} em formato inválido: '{valor}'")


class IdadeInvalidaError(Exception):
    """Data de nascimento que resulta em idade fora do intervalo aceito."""

    def __init__(self, idade):
        self.idade = idade
        super().__init__(
            f"idade inválida: {idade} anos "
            f"(permitido: {IDADE_MINIMA} a {IDADE_MAXIMA})"
        )


# ----------------------------------------------------------------------
# VALIDAÇÕES COM REGEX
# ----------------------------------------------------------------------

def validar_email(email):
    if not re.match(PADRAO_EMAIL, email):
        raise FormatoInvalidoError("e-mail", email)


def validar_cpf(cpf):
    """Valida o formato (regex) e depois os dígitos verificadores."""
    if not re.match(PADRAO_CPF, cpf):
        raise FormatoInvalidoError("CPF", cpf)

    numeros = re.sub(r"\D", "", cpf)  # \D = tudo que NÃO é dígito
    if numeros == numeros[0] * 11:    # ex: 111.111.111-11
        raise FormatoInvalidoError("CPF", cpf)

    for tamanho in (9, 10):
        soma = sum(
            int(numeros[i]) * (tamanho + 1 - i) for i in range(tamanho)
        )
        digito = (soma * 10) % 11 % 10
        if digito != int(numeros[tamanho]):
            raise FormatoInvalidoError("CPF", cpf)


def validar_telefone(telefone):
    if not re.match(PADRAO_TELEFONE, telefone):
        raise FormatoInvalidoError("telefone", telefone)


def validar_data(data_texto):
    """
    Regex valida o formato dd/mm/aaaa; strptime valida se a data existe
    (levanta ValueError para 31/02/2000, por exemplo); depois checa a idade.
    """
    if not re.match(PADRAO_DATA, data_texto):
        raise FormatoInvalidoError("data", data_texto)

    nascimento = datetime.strptime(data_texto, "%d/%m/%Y")  # pode dar ValueError
    hoje = datetime.today()
    idade = hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )
    if idade < IDADE_MINIMA or idade > IDADE_MAXIMA:
        raise IdadeInvalidaError(idade)


# ----------------------------------------------------------------------
# LEITURA E ANÁLISE
# ----------------------------------------------------------------------

def validar_registro(registro):
    """Valida todos os campos e devolve a lista de problemas encontrados."""
    validacoes = [
        ("email", validar_email),
        ("cpf", validar_cpf),
        ("telefone", validar_telefone),
        ("data_nascimento", validar_data),
    ]
    problemas = []

    for coluna, funcao_validacao in validacoes:
        valor = registro[coluna].strip()
        try:
            funcao_validacao(valor)
        except (FormatoInvalidoError, IdadeInvalidaError) as erro:
            problemas.append(str(erro))
        except ValueError:
            problemas.append(f"data inexistente no calendário: '{valor}'")

    return problemas


def ler_arquivo(caminho):
    """Lê o CSV e devolve a lista de registros (dicionários)."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)

        colunas_faltando = [
            coluna for coluna in COLUNAS_OBRIGATORIAS
            if coluna not in (leitor.fieldnames or [])
        ]
        if colunas_faltando:
            raise KeyError(f"coluna(s) ausente(s): {', '.join(colunas_faltando)}")

        return list(leitor)


def analisar_registros(registros):
    """Separa registros válidos e inválidos."""
    validos = []
    invalidos = []

    for numero_linha, registro in enumerate(registros, start=2):  # linha 1 = cabeçalho
        problemas = validar_registro(registro)
        if problemas:
            invalidos.append((numero_linha, registro, problemas))
        else:
            validos.append((numero_linha, registro))

    return validos, invalidos


# ----------------------------------------------------------------------
# RELATÓRIO (f-strings)
# ----------------------------------------------------------------------

def montar_relatorio(caminho, total, validos, invalidos):
    percentual = (len(validos) / total * 100) if total else 0
    linhas = []

    linhas.append("=" * 60)
    linhas.append(f"{'RELATÓRIO DE ANÁLISE DE DADOS':^60}")
    linhas.append("=" * 60)
    linhas.append(f"Arquivo analisado : {caminho}")
    linhas.append(f"Total de registros: {total}")
    linhas.append(f"Registros válidos : {len(validos)} ({percentual:.1f}%)")
    linhas.append(f"Registros inválidos: {len(invalidos)} ({100 - percentual:.1f}%)")

    linhas.append("\n--- REGISTROS VÁLIDOS ---")
    if not validos:
        linhas.append("  (nenhum)")
    for numero_linha, registro in validos:
        linhas.append(
            f"  Linha {numero_linha:>2} | {registro['nome']:<12} | "
            f"{registro['email']}"
        )

    linhas.append("\n--- REGISTROS INVÁLIDOS ---")
    if not invalidos:
        linhas.append("  (nenhum)")
    for numero_linha, registro, problemas in invalidos:
        linhas.append(f"  Linha {numero_linha:>2} | {registro['nome']}")
        for problema in problemas:
            linhas.append(f"      - {problema}")

    linhas.append("=" * 60)
    return "\n".join(linhas)


def salvar_relatorio(texto, caminho_saida):
    with open(caminho_saida, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)


# ----------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ----------------------------------------------------------------------

def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "dados.csv"

    try:
        registros = ler_arquivo(caminho)
    except FileNotFoundError:
        print(f"Erro: o arquivo '{caminho}' não foi encontrado.")
    except KeyError as erro:
        print(f"Erro no formato do CSV: {erro}")
    except UnicodeDecodeError:
        print("Erro: o arquivo não está em UTF-8.")
    else:
        # só executa se NÃO houve exceção na leitura
        validos, invalidos = analisar_registros(registros)
        relatorio = montar_relatorio(caminho, len(registros), validos, invalidos)
        print(relatorio)
        salvar_relatorio(relatorio, ARQUIVO_RELATORIO)
        print(f"\nRelatório salvo em '{ARQUIVO_RELATORIO}'.")
    finally:
        # sempre executa, com erro ou sem erro
        print("Análise finalizada.")


if __name__ == "__main__":
    main()
