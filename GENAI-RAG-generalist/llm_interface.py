import os
import openai
from typing import Optional
import time


# Carregar chave da OpenAI
def carregar_chave_openai(api_key: Optional[str] = None) -> None:
    if api_key:
        openai.api_key = api_key
        print("Chave API carregada corretamente.")
    elif os.path.exists("openai_key.txt"):
        with open("openai_key.txt") as f:
            openai.api_key = f.read().strip()
            print("Chave API carregada corretamente.")
    else:
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Erro: Nenhuma chave de API encontrada.")


def gerar_resposta_assistente(
    query: str,
    context: Optional[str] = None,
    api_key: Optional[str] = None,
    assistant_id: Optional[str] = None,
) -> str:
    try:
        # Carregar chave de API
        carregar_chave_openai(api_key)

        # Validar o assistant_id
        if not assistant_id:
            return "Erro: 'assistant_id' é obrigatório."

        # Criar um novo thread para a conversa
        thread = openai.beta.threads.create()

        # Construir a mensagem com contexto opcional
        user_message = (
            query if not context else f"Context: {context}\n\nQuestion: {query}"
        )

        # Adicionar a mensagem ao thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )

        # Criar a execução do assistente
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        print("Execução do assistente iniciada:", run)

        # Aguardar a resposta do assistente com timeout e verificações de erro
        start_time = time.time()
        timeout = 60  # Defina um timeout de 60 segundos
        while run.status in ["queued", "in_progress"]:
            time.sleep(1)  # Pequeno delay para evitar chamadas excessivas
            run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # Verificar o tempo decorrido e interromper se o tempo de espera exceder o timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                return "Erro: Timeout excedido enquanto aguardava pela resposta do assistente."

            # Logar o status atual para depuração
            print(f"Status atual do run: {run.status}")

        if run.status == "completed":
            # Acessando corretamente o conteúdo do assistente
            messages = openai.beta.threads.messages.list(thread_id=thread.id)

            # Acessando o conteúdo da resposta, verificando se é uma lista
            message_content = messages.data[0].content
            # Se o conteúdo for uma lista, acesse o primeiro item
            if isinstance(message_content, list):
                return message_content[0].text.value  # Acessando o valor do texto
            else:
                return message_content.text.value  # Caso seja um único objeto

        elif run.status == "failed":
            return "Erro: Execução do assistente falhou."

        else:
            return f"Erro inesperado: Status do run é {run.status}"

    except openai.error.AuthenticationError:
        return "Erro de autenticação. Verifique sua chave de API."
    except openai.error.InvalidRequestError as e:
        return f"Erro de solicitação inválida: {e}"
    except Exception as e:
        return f"Erro: {str(e)}"
