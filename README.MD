# Projeto Stract

Este projeto implementa um servidor Flask que consome dados de uma API de anúncios, processa esses dados e os expõe como relatórios em formato CSV através de endpoints HTTP.

## Endpoints

- `/`: Retorna informações pessoais (nome, email, LinkedIn).
- `/<plataforma>`: Relatório completo para a plataforma especificada (ex: /meta_ads).
- `/<plataforma>/resumo`: Relatório resumido (agregado por conta) para a plataforma.
- `/geral`: Relatório com todos os anúncios de todas as plataformas.
- `/geral/resumo`: Relatório geral resumido (agregado por plataforma).

Todos os endpoints de relatório retornam dados no formato CSV.
O arquivo .csv também pode ser visualizado na pasta `csv`.



1. **Clone o repositório:**

    ```bash
    git clone https://github.com/JoaoVitorCafe/stract-api-platform.git
    cd stract-api-platform
    ```
2. **Clone o repositório:**

Crie um arquivo .env na pasta raiz do projeto e coloque o token de autorização

```
TOKEN_AUTORIZACAO=****************
```

## Instalação - Docker

Caso tenha o docker instalado rode os comandos abaixo no terminal

```
docker build -t stract-api-platform .
```

```
docker run -p 5000:5000 stract-api-platform
```

## Instalação - Manual (Sem Docker)

3. **Crie um ambiente virtual (recomendado):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Linux/macOS
    venv\Scripts\activate    # No Windows
    ```

4. **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Inicie o servidor Flask:**
    ```bash
    python app.py
    ```
