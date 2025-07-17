import streamlit as st
import requests
from urllib.parse import urljoin, urlparse, parse_qs
import json
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class KeycloakAuth:
    def __init__(self):
        self.keycloak_url = os.environ.get("KEYCLOAK_URL", "http://localhost:8080")
        self.keycloak_url_interno = os.environ.get(
            "KEYCLOAK_URL_INTERNO", "http://localhost:8080"
        )
        self.realm = os.environ.get("KEYCLOAK_REALM", "neuai")
        self.client_id = os.environ.get("KEYCLOAK_CLIENT_ID", "genai")
        self.token_endpoint = urljoin(
            self.keycloak_url_interno,
            f"/realms/{self.realm}/protocol/openid-connect/token",
        )
        self.userinfo_endpoint = urljoin(
            self.keycloak_url_interno,
            f"/realms/{self.realm}/protocol/openid-connect/userinfo",
        )
        self.auth_endpoint = urljoin(
            self.keycloak_url, f"/realms/{self.realm}/protocol/openid-connect/auth"
        )
        self.redirect_uri = os.environ.get(
            "KEYCLOAK_REDIRECT_URI", "http://localhost:8501/"
        )
        # Initialize session state if not exists
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "access_token" not in st.session_state:
            st.session_state.access_token = None
        if "user_info" not in st.session_state:
            st.session_state.user_info = None

    def redirect_to_login(self):
        # Monta a URL de autorização
        auth_url = (
            f"{self.auth_endpoint}?client_id={self.client_id}"
            f"&response_type=code&scope=openid profile email"
            f"&redirect_uri={self.redirect_uri}"
        )
        st.markdown(
            f"""
            <meta http-equiv='refresh' content='0; url={auth_url}' />
        """,
            unsafe_allow_html=True,
        )
        st.stop()

    def exchange_code_for_token(self, code):
        # Troca o code pelo access token
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(self.token_endpoint, data=data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            id_token = token_data.get("id_token")
            refresh_token = token_data.get("refresh_token")
            if not access_token:
                logger.error("No access token received")
                return False
            st.session_state.access_token = access_token
            if id_token:
                st.session_state.id_token = id_token
            if refresh_token:
                st.session_state.refresh_token = refresh_token
            # Obter userinfo
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_response = requests.get(self.userinfo_endpoint, headers=headers)
            if userinfo_response.status_code == 200:
                user_info = userinfo_response.json()
                st.session_state.user_info = user_info
                st.session_state.authenticated = True
                # Salva no localStorage
                st.markdown(
                    f"""
                    <script>
                        localStorage.setItem('access_token', '{access_token}');
                        localStorage.setItem('user_info', '{json.dumps(user_info)}');
                        localStorage.setItem('authenticated', 'true');
                    </script>
                    """,
                    unsafe_allow_html=True,
                )
                return True
            else:
                logger.error(f"Failed to get user info: {userinfo_response.text}")
                return False
        else:
            logger.error(f"Failed to exchange code: {response.text}")
            return False

    def check_auth(self):
        # Já autenticado na sessão
        if (
            st.session_state.authenticated
            and st.session_state.access_token
            and st.session_state.user_info
        ):
            return True
        # Tenta restaurar do localStorage
        st.markdown(
            """
            <script>
                const access_token = localStorage.getItem('access_token');
                const user_info = localStorage.getItem('user_info');
                const authenticated = localStorage.getItem('authenticated');
                if (access_token && user_info && authenticated === 'true') {
                    window.parent.postMessage({
                        type: 'restore_session',
                        data: {
                            access_token: access_token,
                            user_info: JSON.parse(user_info),
                            authenticated: true
                        }
                    }, '*');
                }
            </script>
            """,
            unsafe_allow_html=True,
        )
        if (
            st.session_state.authenticated
            and st.session_state.access_token
            and st.session_state.user_info
        ):
            return True
        return False

    def logout(self):
        st.session_state.authenticated = False
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.session_state.id_token = None
        st.session_state.refresh_token = None
        st.markdown(
            """
            <script>
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_info');
                localStorage.removeItem('authenticated');
            </script>
            """,
            unsafe_allow_html=True,
        )
        # Monta a URL de logout do Keycloak
        refresh_token = st.session_state.get("refresh_token")
        logout_url = (
            f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/logout"
            f"?post_logout_redirect_uri={self.redirect_uri}"
        )
        if refresh_token:
            logout_url += f"&refresh_token={refresh_token}"
        # Redireciona para o logout do Keycloak
        st.markdown(
            f"""
            <meta http-equiv='refresh' content='0; url={logout_url}' />
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    def get_user_info(self):
        if st.session_state.user_info:
            return st.session_state.user_info
        return {}

    def get_user_groups(self):
        """
        Retorna a lista de grupos do usuário autenticado, se disponível.
        A claim 'groups' deve estar presente no user_info retornado pelo Keycloak.
        """
        user_info = self.get_user_info()
        return user_info.get("groups", [])


def check_keycloak_auth():
    keycloak = KeycloakAuth()
    # Detecta se há code na URL usando apenas st.query_params
    code = None
    if hasattr(st, "query_params"):
        code = (
            st.query_params.get("code", [None])[0]
            if isinstance(st.query_params.get("code"), list)
            else st.query_params.get("code")
        )
    if code:
        if keycloak.exchange_code_for_token(code):
            st.session_state.authenticated = True
            return True
        else:
            st.error("Erro ao autenticar com Keycloak.")
            return False
    # Se não autenticado, redireciona automaticamente
    if not keycloak.check_auth():
        keycloak.redirect_to_login()
        st.stop()
    return True
