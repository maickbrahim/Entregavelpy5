# Sistema de Análise de Dados

Projeto em Python que lê um arquivo CSV com **e-mail, CPF, telefone e data de nascimento**, valida cada campo com **expressões regulares**, trata **exceções** e gera um **relatório formatado**.

## Como executar

```bash
python analise_dados.py              # lê o arquivo dados.csv
python analise_dados.py outro.csv    # lê outro arquivo
```

O relatório é exibido no terminal e salvo em `relatorio.txt`.

## Estrutura

```
analise-dados/
├── analise_dados.py   # script principal
├── dados.csv          # arquivo de exemplo (entrada)
├── relatorio.txt      # gerado ao executar (saída)
└── README.md
```

## Justificativa das validações

| Campo | Regex (raw string) | Por quê |
|---|---|---|
| E-mail | `^[\w.+-]+@[\w-]+(\.[\w-]+)+$` | `\w` aceita letras, números e `_`. Exige `@` e ao menos um ponto no domínio (rejeita `bruno@email`). `^` e `$` garantem que a string inteira siga o padrão. |
| CPF | `^\d{3}\.\d{3}\.\d{3}-\d{2}$` | `\d{3}` = 3 dígitos, `\.` = ponto literal. Depois do formato, o código confere os **dígitos verificadores** e rejeita sequências repetidas como `111.111.111-11`. |
| Telefone | `^\(\d{2}\)\s?9?\d{4}-\d{4}$` | DDD entre parênteses, espaço opcional (`\s?`), nono dígito opcional (`9?`) e hífen. Aceita fixo e celular. |
| Data | `^\d{2}/\d{2}/\d{4}$` | Valida o formato `dd/mm/aaaa`. Depois `datetime.strptime` confirma se a data **existe** (rejeita `31/02/2000`) e a idade é checada. |

Usamos `^` e `$` em todos os padrões porque, sem eles, `re.match` aceitaria lixo depois do trecho correto (ex: `123.456.789-09abc`). Todos os padrões usam *raw strings* (`r"..."`) para o Python não interpretar a barra invertida.

## Exceções tratadas

| Exceção | Onde | O que acontece |
|---|---|---|
| `FileNotFoundError` | Abertura do arquivo | Mostra mensagem amigável em vez de quebrar o programa. |
| `KeyError` | Cabeçalho do CSV | Levantada quando falta uma coluna obrigatória; a mensagem lista quais. |
| `ValueError` | `strptime` na data | Capturada ao validar datas inexistentes (ex: 31/02). |
| `UnicodeDecodeError` | Leitura do arquivo | Avisa quando o arquivo não está em UTF-8. |
| `FormatoInvalidoError` (personalizada) | Validação de e-mail, CPF, telefone e data | Regra de negócio: campo fora do formato esperado. Guarda `campo` e `valor`. |
| `IdadeInvalidaError` (personalizada) | Validação da data | Regra de negócio: idade fora do intervalo de 0 a 120 anos. |

Estrutura do `try/except/else/finally` no `main()`:

- **`try`**: tenta ler o arquivo.
- **`except`**: trata cada tipo de erro de leitura.
- **`else`**: só roda se a leitura deu certo (analisa e gera o relatório).
- **`finally`**: sempre roda e imprime "Análise finalizada.".

## Exemplo de entrada (`dados.csv`)

```csv
nome,email,cpf,telefone,data_nascimento
Ana,ana.silva@email.com,529.982.247-25,(11) 98765-4321,15/03/1995
Bruno,bruno@email,111.444.777-35,(21) 3456-7890,22/07/1988
Carla,carla_souza@empresa.com.br,123.456.789-09,(31) 99999-1234,10/12/2001
Diego,diego@email.com,12345678900,(11) 98765-4321,05/05/1990
Elisa,elisa@email.com,111.111.111-11,11987654321,31/02/2000
Fabio,fabio@email.com,529.982.247-25,(85) 98888-7777,20/10/2090
Gabi,gabi@email.com,111.444.777-35,(41) 97777-6666,01/01/1850
```

## Exemplo de saída (relatório)

```
============================================================
               RELATÓRIO DE ANÁLISE DE DADOS
============================================================
Arquivo analisado : dados.csv
Total de registros: 7
Registros válidos : 2 (28.6%)
Registros inválidos: 5 (71.4%)

--- REGISTROS VÁLIDOS ---
  Linha  2 | Ana          | ana.silva@email.com
  Linha  4 | Carla        | carla_souza@empresa.com.br

--- REGISTROS INVÁLIDOS ---
  Linha  3 | Bruno
      - e-mail em formato inválido: 'bruno@email'
  Linha  5 | Diego
      - CPF em formato inválido: '12345678900'
  Linha  6 | Elisa
      - CPF em formato inválido: '111.111.111-11'
      - telefone em formato inválido: '11987654321'
      - data inexistente no calendário: '31/02/2000'
  Linha  7 | Fabio
      - idade inválida: -65 anos (permitido: 0 a 120)
  Linha  8 | Gabi
      - idade inválida: 176 anos (permitido: 0 a 120)
============================================================
```

> A idade depende da data em que o programa é executado.

## Exemplos de erros tratados

```
$ python analise_dados.py nao_existe.csv
Erro: o arquivo 'nao_existe.csv' não foi encontrado.
Análise finalizada.

$ python analise_dados.py csv_sem_colunas.csv
Erro no formato do CSV: 'coluna(s) ausente(s): cpf, telefone, data_nascimento'
Análise finalizada.
```

## Tecnologias

Python 3 (módulos `re`, `csv`, `datetime`, `sys`) — sem bibliotecas externas.
