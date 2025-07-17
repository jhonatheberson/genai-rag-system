# Build stage
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Install EF Core tools
RUN dotnet tool install --global dotnet-ef

# Copy solution and project files
COPY ["DDDTemplate.sln", "./"]
COPY ["src/API/API.csproj", "src/API/"]
COPY ["src/Application/Application.csproj", "src/Application/"]
COPY ["src/Domain/Domain.csproj", "src/Domain/"]
COPY ["src/Infrastructure/Infrastructure.csproj", "src/Infrastructure/"]
COPY ["tests/Domain.UnitTests/Domain.UnitTests.csproj", "tests/Domain.UnitTests/"]
COPY ["tests/Application.UnitTests/Application.UnitTests.csproj", "tests/Application.UnitTests/"]
COPY ["tests/Controller.UnitTests/Controller.UnitTests.csproj", "tests/Controller.UnitTests/"]
COPY ["tests/Service.UnitTests/Service.UnitTests.csproj", "tests/Service.UnitTests/"]

# Restore dependencies
RUN dotnet restore

# Copy the rest of the source code
COPY src/ ./src/
COPY tests/ ./tests/

# Build and publish
RUN dotnet build "src/API/API.csproj" -c Release -o /app/build
RUN dotnet publish "src/API/API.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Final stage
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS final
WORKDIR /app

# Install certificates, netcat and EF Core tools
RUN apt-get update && \
    apt-get install -y ca-certificates netcat-traditional && \
    rm -rf /var/lib/apt/lists/* && \
    dotnet tool install --global dotnet-ef

# Create directory for HTTPS certificates
RUN mkdir -p /https

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copie os arquivos de projeto e código-fonte para a imagem final
COPY src/ ./src/
COPY DDDTemplate.sln .

COPY --from=build /app/publish .

# Expose ports for HTTP and HTTPS
EXPOSE 80
EXPOSE 443

# Set the entry point
ENTRYPOINT ["/app/entrypoint.sh"]

# docker build -t ddd-template-api .
# docker run -d -p 5254:80 -p 7186:443 -e ASPNETCORE_ENVIRONMENT=Development -e ASPNETCORE_URLS="http://+:80;https://+:443" -e ASPNETCORE_Kestrel__Certificates__Default__Path=/https/aspnetapp.pfx -e ASPNETCORE_Kestrel__Certificates__Default__Password=YourSecurePassword123! -v $(pwd)/certificates:/https:ro --name ddd-template-api ddd-template-api
# docker logs ddd-template-api
# http://localhost:5254/swagger/index.html
#https://localhost:7186/swagger/index.html

# dotnet ef migrations add InitialCreate --project src/Infrastructure --startup-project src/API
# dotnet ef database update --project src/Infrastructure --startup-project src/API

# comando para criar novas migrações
# dotnet ef migrations add NomeDaMigracao --project src/Infrastructure --startup-project src/API

# comando para aplicar as migrações
# dotnet ef database update --project src/Infrastructure --startup-project src/API