# Usa a imagem oficial do Python 3.10.11
FROM python:3.10.11

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . /app

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta 5000 para comunicação externa
EXPOSE 5000

# Define o comando para rodar a API Flask
CMD ["python", "app.py"]
