import streamlit as st
import requests
import time  # Importando a biblioteca para adicionar delays

# Função para fazer a requisição de status
def get_status(kickoff_id, url, headers):
    try:
        response = requests.get(f"{url}/status/{kickoff_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao obter status. Código de status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro na requisição: {str(e)}")
        return None

# Função para fazer a requisição de kickoff
def post_kickoff(url, headers, body):
    try:
        response = requests.post(f"{url}/kickoff", 
                                 headers=headers, json=body)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao enviar kickoff. Código de status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro na requisição: {str(e)}")
        return None

# Função para fazer a requisição de inputs
def get_inputs(url, headers):
    try:
        response = requests.get(f"{url}/inputs", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao obter inputs. Código de status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro na requisição: {str(e)}")
        return None

# Função para verificar periodicamente o status até que a tarefa seja concluída
def wait_for_success(kickoff_id, url, headers, max_retries=30, delay=5):
    retries = 0
    while retries < max_retries:
        status_response = get_status(kickoff_id, url, headers)
        if status_response:
            state = status_response.get("state")
            if state == "SUCCESS":
                return status_response
            elif state == "FAILED":
                st.error("A tarefa falhou.")
                return None
            else:
                st.write(f"Tarefa ainda em andamento. Estado atual: {state}. Tentando novamente...")
        retries += 1
        time.sleep(delay)  # Espera de 5 segundos antes de tentar novamente

    st.error("Tempo limite excedido para obter sucesso.")
    return None

# Configuração da URL e token
url = "https://novo-teste-fff0e815-98f9-4e7f-a181-cf179414-10bb7562.crewai.com"
token = "eb5f8f7d7b42"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Interface do usuário no Streamlit
st.title("Aplicação de Integração com CrewAI")

# Exibir os inputs disponíveis
st.subheader("Inputs Disponíveis")
inputs_data = get_inputs(url, headers)
if inputs_data:
    st.json(inputs_data)
else:
    st.error("Não foi possível carregar os inputs.")

# Campo de texto para o tópico e ano
topic = st.text_input("Informe o tópico", value="CrewAI")
current_year = st.number_input("Informe o ano atual", value=2025)

# Botão para iniciar o kickoff
if st.button("Iniciar Kickoff"):
    body = {"inputs": {"topic": topic, "current_year": current_year}}
    kickoff_response = post_kickoff(url, headers, body)
    
    if kickoff_response:
        st.json(kickoff_response)
        kickoff_id = kickoff_response.get("kickoff_id", "")
        
        # Verificar o status até atingir "SUCCESS"
        if kickoff_id:
            st.subheader("Verificando Status do Kickoff")
            status_response = wait_for_success(kickoff_id, url, headers)
            
            if status_response:
                result = status_response.get("result",
                                             "Nenhum resultado disponível.")
                st.write(f"Resultado final: {result}")
            else:
                st.error("Não foi possível obter sucesso após múltiplas tentativas.")
    else:
        st.error("Falha ao iniciar o kickoff.")
