# Atualize para Python 3.10 ou superior
FROM python:3.10-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copiar apenas o arquivo de requisitos para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Atualizar o pip e instale as dependências
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Cp o restante dos arquivos do projeto para o container
COPY . .
COPY X509-cert-953527341211576668.pem /app/X509-cert-953527341211576668.pem
RUN chmod 600 /app/X509-cert-953527341211576668.pem



# Exponha a porta para o servidor
EXPOSE 8501
# EXPOSE 443

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
# CMD ["streamlit", "run", "main.py", "--server.port=443", "--server.address=0.0.0.0"]
