FROM quay.io/keycloak/keycloak:25.0.0 AS builder


# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
ENV KC_LOG_LEVEL=DEBUG


# Configure a database vendor
ENV KC_DB=postgres
ENV KC_DB_PASSWORD=MASTER_DB_PASSWORD
ENV KEYCLOAK_ADMIN_PASSWORD=admin
ENV KEYCLOAK_HOSTNAME=auth-sandbox.neuai.com.br
ENV KC_DB_USERNAME=MASTER_DB_USERNAME
ENV KC_HOSTNAME=auth-sandbox.neuai.com.br
ENV KEYCLOAK_ADMIN=admin
ENV KC_DB_URL=jdbc:postgresql://postgres-sandbox.cly4oquyimkk.us-east-1.rds.amazonaws.com:5432/INITIAL_DB_NAME
ENV KEYCLOAK_FRONTEND_URL=https://auth-sandbox.neuai.com.br
# ENV KC_HOSTNAME_ADMIN_URL=https://auth.neuai.com.br
ENV KC_HOSTNAME_STRICT=false
ENV KC_PROXY=edge
# ENV KC_PROXY=reencrypt
#Ou 'edge', dependendo do proxy reverso utilizado

WORKDIR /opt/keycloak
# for demonstration purposes only, please make sure to use proper certificates in production instead
# RUN keytool -genkeypair -storepass password -storetype PKCS12 -keyalg RSA -keysize 2048 -dname "CN=server" -alias server -ext "SAN:c=DNS:localhost,IP:127.0.0.1" -keystore conf/server.keystore
COPY ./conf/server.keystore /opt/keycloak/conf/server.keystore
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:25.0.0
USER keycloak

COPY --from=builder /opt/keycloak /opt/keycloak

COPY ./template-theme /opt/keycloak/themes/template

# Copia os arquivos do realm para o diretório de importação do Keycloak
COPY ./realm-import-dev-env /opt/keycloak/data/import


# Define a variável de ambiente para importar o realm
# ENV KC_IMPORT=/opt/keycloak/data/import

# ENV KC_HOSTNAME=localhost
# ENV KC_HOSTNAME=auth.neuai.com.br
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
# CMD [ "start-dev"]
CMD [ "start-dev", "--import-realm", "--features=preview"]
# CMD [ "start-dev", "--health-enabled=true", "--import-realm" ]
# docker run -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin -p 8080:8080 keycloak