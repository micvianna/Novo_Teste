import os
import time
from datetime import datetime
from typing import Any, Mapping

import requests
import streamlit as st

REQUEST_TIMEOUT_SECONDS = 30
POLL_RETRIES = 30
POLL_DELAY_SECONDS = 5


class ConfigurationError(RuntimeError):
    """Raised when the local API configuration is incomplete."""


def read_configuration(environ: Mapping[str, str] | None = None) -> tuple[str, str]:
    values = os.environ if environ is None else environ
    base_url = values.get("CREWAI_KICKOFF_URL", "").strip().rstrip("/")
    token = values.get("CREWAI_BEARER_TOKEN", "").strip()

    if not base_url or not token:
        raise ConfigurationError(
            "Defina CREWAI_KICKOFF_URL e CREWAI_BEARER_TOKEN no ambiente local."
        )

    return base_url, token


def endpoint(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def request_json(
    method: str,
    request_url: str,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    try:
        response = requests.request(
            method,
            request_url,
            headers=headers,
            json=body,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        status = exc.response.status_code if exc.response is not None else None
        message = f"Falha na API (HTTP {status})." if status else "Falha de comunicação com a API."
        st.error(message)
        return None
    except ValueError:
        st.error("A API retornou uma resposta que não é JSON válido.")
        return None


def get_inputs(base_url: str, headers: dict[str, str]) -> dict[str, Any] | None:
    return request_json("GET", endpoint(base_url, "inputs"), headers)


def post_kickoff(
    base_url: str,
    headers: dict[str, str],
    body: dict[str, Any],
) -> dict[str, Any] | None:
    return request_json("POST", endpoint(base_url, "kickoff"), headers, body)


def get_status(
    kickoff_id: str,
    base_url: str,
    headers: dict[str, str],
) -> dict[str, Any] | None:
    return request_json("GET", endpoint(base_url, f"status/{kickoff_id}"), headers)


def wait_for_success(
    kickoff_id: str,
    base_url: str,
    headers: dict[str, str],
    max_retries: int = POLL_RETRIES,
    delay: int = POLL_DELAY_SECONDS,
) -> dict[str, Any] | None:
    for _ in range(max_retries):
        status_response = get_status(kickoff_id, base_url, headers)
        if not status_response:
            return None

        state = status_response.get("state")
        if state == "SUCCESS":
            return status_response
        if state == "FAILED":
            st.error("A execução remota terminou com falha.")
            return None

        st.info("Execução remota ainda em andamento.")
        time.sleep(delay)

    st.error("Tempo limite excedido ao aguardar a execução remota.")
    return None


def main() -> None:
    st.title("Cliente Streamlit para kickoff CrewAI")

    try:
        base_url, token = read_configuration()
    except ConfigurationError as exc:
        st.warning(str(exc))
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    st.subheader("Inputs disponíveis")
    inputs_data = get_inputs(base_url, headers)
    if inputs_data:
        st.json(inputs_data)
    else:
        st.info("Os inputs remotos não puderam ser carregados.")

    topic = st.text_input("Tópico", value="AI LLMs")
    current_year = st.number_input("Ano", value=datetime.now().year)

    if not st.button("Iniciar kickoff"):
        return

    body = {"inputs": {"topic": topic, "current_year": int(current_year)}}
    kickoff_response = post_kickoff(base_url, headers, body)
    if not kickoff_response:
        return

    kickoff_id = kickoff_response.get("kickoff_id")
    if not kickoff_id:
        st.error("A resposta não contém um identificador de kickoff.")
        return

    st.success("Kickoff iniciado.")
    status_response = wait_for_success(kickoff_id, base_url, headers)
    if status_response:
        st.subheader("Resultado")
        st.write(status_response.get("result", "Resultado indisponível."))


if __name__ == "__main__":
    main()
