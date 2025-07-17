import streamlit as st
import os
import logging
from datetime import datetime
import time
import json
from conversation_manager import ConversationManager
from vector_store import VectorStore
from document_processor import process_document
from llm_interface import gerar_resposta_assistente
from streamlit_js_eval import get_cookie, set_cookie, streamlit_js_eval
from keycloak_auth import check_keycloak_auth, KeycloakAuth
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JavaScript functions for localStorage
local_storage_js = """
<script>
function saveToLocalStorage(key, value) {
    localStorage.setItem(key, value);
}

function getFromLocalStorage(key) {
    return localStorage.getItem(key);
}

// Função para verificar se é o primeiro carregamento
function isFirstLoad() {
    const key = 'hasLoadedBefore';
    const hasLoaded = localStorage.getItem(key);
    if (!hasLoaded) {
        localStorage.setItem(key, 'true');
        return true;
    }
    return false;
}
</script>
"""

# Inject JavaScript
st.components.v1.html(local_storage_js, height=0)

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "auth_checked" not in st.session_state:
    st.session_state.auth_checked = False

# Initialize Keycloak authentication
keycloak = KeycloakAuth()

# Check if we're already authenticated
if not st.session_state.authenticated:
    # Show logo (opcional)
    st.image("logo.png", width=200)
    # Checa autenticação e redireciona automaticamente se necessário
    if check_keycloak_auth():
        st.session_state.authenticated = True
        st.session_state.auth_checked = True
        st.rerun()
    else:
        st.stop()

# If we get here, we're authenticated
# Show user groups after login
user_groups = keycloak.get_user_groups()
product_data = None
product_name = "MARTA"  # Valor padrão
if user_groups:
    # st.info(f"Grupo(s) do usuário: {user_groups[0][1:]}")
    try:
        group_name = user_groups[0][1:]
        url = f"https://localhost:7186/api/Products/group/{group_name}"
        response = requests.get(url, verify=False)  # Para dev, ignora SSL
        if response.status_code == 200:
            product_data = response.json()
            # Atualiza dinamicamente as variáveis
            assistant_id = product_data.get("assistant_id", "")
            api_key = product_data.get("api_key", "")
            product_name = product_data.get("name", "MARTA")
            # Salva nos cookies
            set_cookie("assistant_id", assistant_id, duration_days=1)
            set_cookie("api_key", api_key, duration_days=1)
            set_cookie("product_name", product_name, duration_days=1)
            # Atualiza session_state
            st.session_state["assistant_id"] = assistant_id
            st.session_state["api_key"] = api_key
            st.session_state["product_name"] = product_name
        else:
            st.warning(
                f"Não foi possível obter dados do produto para o grupo: {group_name}"
            )
    except Exception as e:
        st.warning(f"Erro ao buscar dados do produto: {str(e)}")
else:
    st.info("Usuário não pertence a nenhum grupo.")
    product_name = "MARTA"
    st.session_state["product_name"] = product_name

# Função utilitária para substituir 'MARTA' pelo nome do produto


def replace_marta(text):
    name = st.session_state.get("product_name", "MARTA")
    return text.replace("MARTA", name)


# data = {
#     "grant_type": "authorization_code",
#     "code": code,
#     "client_id": self.client_id,
#     "redirect_uri": self.redirect_uri,
# }
# response = requests.post(self.token_endpoint, data=data)

# Show the main application
title = "RAG System"
st.title(title)

# Initialize session state
if "conversation_manager" not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()
if "session_id" not in st.session_state:
    st.session_state.session_id = st.session_state.conversation_manager.create_session()
if "show_analytics" not in st.session_state:
    st.session_state.show_analytics = False
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False
if "welcome_message_shown" not in st.session_state:
    st.session_state.welcome_message_shown = False

# Load chat history from session state if available
if not st.session_state.history_loaded:
    try:
        # Get history from conversation manager
        history = st.session_state.conversation_manager.get_history(
            st.session_state.session_id
        )
        if history and isinstance(history, list):
            st.session_state.chat_history = history
        st.session_state.history_loaded = True
    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}")

# Add welcome message if not shown yet
if not st.session_state.welcome_message_shown:
    try:
        # Get user info from Keycloak
        user_info = keycloak.get_user_info()
        username = user_info.get("preferred_username", "User")

        # Add welcome message to conversation
        welcome_message = (
            f"👋 Hi {username}! Welcome to MARTA RAG System. How can I help you today?"
        )
        welcome_message = replace_marta(welcome_message)
        st.session_state.conversation_manager.add_message(
            st.session_state.session_id,
            "assistant",
            welcome_message,
            document_context={"timestamp": datetime.now().isoformat()},
        )

        # Update chat history in session state
        st.session_state.chat_history = (
            st.session_state.conversation_manager.get_history(
                st.session_state.session_id
            )
        )
        st.session_state.welcome_message_shown = True
    except Exception as e:
        logger.error(f"Error showing welcome message: {str(e)}")

# Main content based on view state
if st.session_state.show_analytics:
    # Import and render analytics dashboard
    from analytics import render_analytics_dashboard

    render_analytics_dashboard()
else:
    # Left sidebar with sticky MARTA logo
    with st.sidebar:
        try:
            logo_url = None
            if (
                "product_data" in locals()
                and product_data
                and product_data.get("urL_Logo")
            ):
                logo_url = product_data["urL_Logo"]
            elif st.session_state.get("product_data") and st.session_state[
                "product_data"
            ].get("urL_Logo"):
                logo_url = st.session_state["product_data"]["urL_Logo"]
            if not logo_url:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                logo_url = os.path.join(current_dir, "MARTA-Logo.jpg")
            st.image(logo_url, width=200)
        except Exception as e:
            logger.error(f"Error loading logo: {str(e)}")
            st.warning("Unable to load MARTA logo")

        st.subheader(replace_marta("MARTA RAG"))

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Chat", type="primary"):
                st.session_state.show_analytics = False
                st.rerun()
        with col2:
            if st.button("📊 Analytics"):
                st.session_state.show_analytics = True
                st.rerun()

        st.divider()

        # File upload section in sidebar
        uploaded_files = st.file_uploader(
            "📎 Add documents",
            type=["pdf", "txt", "docx", "html", "csv"],
            accept_multiple_files=True,
            help="Upload documents to chat with",
        )

        st.divider()

        # Recuperar cookies
        api_key = (
            get_cookie("api_key") or ""
        )  # Recupera o cookie ou retorna vazio se não existir
        assistant_id = get_cookie("assistant_id") or ""

        # # API key and Assistant ID input fields
        # api_key = st.text_input(
        #     "API Key", value=api_key, type="password", help="Enter your OpenAI API key."
        # )
        # assistant_id = st.text_input(
        #     "Assistant ID", value=assistant_id, help="Enter your Assistant ID."
        # )

        # if st.button("Settings credentials"):
        #     set_cookie(
        #         "api_key", api_key, duration_days=1
        #     )  # Define o cookie para 'api_key'
        #     set_cookie(
        #         "assistant_id", assistant_id, duration_days=1
        #     )  # Define o cookie para 'assistant_id'
        #     st.success("Credentials saved successfully!")

    # Create two columns with 90/10 split for the main content
    col_chat, col_info = st.columns([0.90, 0.10])

    # Main chat area (90% width)
    with col_chat:
        st.title(replace_marta("Neuai RAG"))

        # Upload status container in main area
        if uploaded_files:
            with st.container():
                st.markdown("##### Document Processing Status")
                for uploaded_file in uploaded_files:
                    file_key = f"processed_{uploaded_file.name}"
                    if file_key not in st.session_state:
                        try:
                            with st.spinner("Processing..."):
                                chunks, metadata = process_document(uploaded_file)
                                st.session_state.vector_store.add_documents(
                                    chunks, metadata
                                )
                                st.session_state[file_key] = True

                                try:
                                    st.session_state.conversation_manager.add_message(
                                        st.session_state.session_id,
                                        "system",
                                        f"Document '{metadata['filename']}' processed.",
                                        document_context=metadata,
                                    )
                                except ConnectionError as e:
                                    logger.error(f"Database connection error: {str(e)}")

                            st.success(f"✓ Successfully processed {uploaded_file.name}")
                        except Exception as e:
                            logger.error(f"Error processing document: {str(e)}")
                            st.error(
                                f"❌ Não foi possível processar o arquivo {uploaded_file.name}. O arquivo pode estar protegido ou corrompido."
                            )
                    else:
                        st.info(f"✓ {uploaded_file.name} (already processed)")

        # Recuperar histórico do chat dos cookies
        history = get_cookie("chat_history")
        if history:
            try:
                history = json.loads(history)  # Converte de string para lista
            except json.JSONDecodeError:
                history = []  # Caso não consiga decodificar, inicializa como vazio
        else:
            history = []

        # Chat interface
        st.subheader("Chat Interface")

        # Display chat history
        try:
            if st.session_state.chat_history:
                for message in st.session_state.chat_history:
                    if isinstance(message, dict):
                        role = message.get("role", "system")
                        content = message.get("content", "")

                        with st.chat_message(role):
                            st.write(content)

                            # Display document context if available
                            if doc_context := message.get("document_context"):
                                if isinstance(doc_context, dict):
                                    if (
                                        "documents" in doc_context
                                        and doc_context["documents"]
                                    ):
                                        doc_name = doc_context["documents"][0]
                                        st.caption(f"📄 Document: {doc_name}")
                                    elif "filename" in doc_context:
                                        st.caption(
                                            f"📄 Document: {doc_context['filename']}"
                                        )

                            # Display timestamp
                            if timestamp := message.get("timestamp"):
                                st.caption(f"Sent at: {timestamp}")
        except Exception as e:
            logger.error(f"Error displaying chat history: {str(e)}")

        # Session Information
        try:
            session_info = st.session_state.conversation_manager.get_session_info(
                st.session_state.session_id
            )
            if session_info:
                st.caption(f"Messages: {session_info.get('message_count', 0)}")
        except Exception as e:
            logger.error(f"Error displaying session info: {str(e)}")

    # Chat input and processing controls
    if st.session_state.is_processing:
        # Show processing state with disabled input
        st.text_input(
            "Ask a question about your documents",
            value="Processing previous message... Please wait.",
            disabled=True,
            key="processing_placeholder",
        )
    else:
        # Only show chat input when not processing
        prompt = st.chat_input("Ask a question about your documents")

        # Handle new message
        if prompt and not st.session_state.is_processing:
            # User message
            with st.chat_message("user"):
                st.write(prompt)

            # Set processing state before starting response
            st.session_state.is_processing = True

            # Assistant response
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Thinking..."):
                        context, context_metadata = (
                            st.session_state.vector_store.get_relevant_context(prompt)
                        )
                        response = gerar_resposta_assistente(
                            prompt, context, api_key, assistant_id
                        )

                        # Store messages
                        try:
                            # Add user message
                            st.session_state.conversation_manager.add_message(
                                st.session_state.session_id,
                                "user",
                                prompt,
                                document_context={
                                    "query_time": datetime.now().isoformat()
                                },
                            )

                            # Add assistant response
                            st.session_state.conversation_manager.add_message(
                                st.session_state.session_id,
                                "assistant",
                                response,
                                document_context={
                                    "documents": [
                                        meta.get("filename")
                                        for meta in context_metadata
                                    ],
                                    "timestamp": datetime.now().isoformat(),
                                },
                            )

                            # Update chat history in session state
                            st.session_state.chat_history = (
                                st.session_state.conversation_manager.get_history(
                                    st.session_state.session_id
                                )
                            )

                        except Exception as e:
                            logger.error(f"Error saving messages: {str(e)}")
                            st.warning("Response generated but history not saved")

                        st.write(response)

                except Exception as e:
                    logger.error(f"Error processing query: {str(e)}")
                    st.error(f"Error processing your question: {str(e)}")
                finally:
                    st.session_state.is_processing = False

            # Force rerun to update the chat interface
            if prompt:
                st.rerun()

    # Add spacing before footer
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # Footer with Neuai branding
    st.markdown('<div class="footer-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("© 2025 NeuAI • [neuai.com](https://www.neuai.com)")
    with col2:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "logo.png")
            st.image(logo_path, width=100)
        except Exception as e:
            st.warning("Unable to load Neuai logo")
    st.markdown("</div>", unsafe_allow_html=True)
