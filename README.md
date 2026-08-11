# Novo Teste — laboratório CrewAI

Repositório de estudo que reúne:

- um scaffold CrewAI configurado em `src/novo_teste/`;
- um cliente Streamlit em `app.py` para iniciar e acompanhar uma execução remota via HTTP.

Este projeto é um laboratório, não uma aplicação finalizada ou um serviço de produção.

## Segurança

O cliente Streamlit exige duas variáveis locais:

```env
CREWAI_KICKOFF_URL=
CREWAI_BEARER_TOKEN=
```

Copie o exemplo e preencha somente no ambiente autorizado:

```bash
cp .env.example .env
```

O código não possui valores padrão e encerra a execução antes de qualquer requisição quando a configuração está ausente.

Um token concreto esteve anteriormente versionado. O valor é tratado como `[REDACTED]` e deve ser revogado ou rotacionado manualmente. A remoção do branch atual não elimina o valor do histórico Git; esse histórico não foi reescrito porque não há autorização para force push neste repositório.

## Instalação

Requer Python 3.10 até 3.13 e `uv`:

```bash
uv sync
```

## Executar o scaffold CrewAI

```bash
uv run crewai run
```

Essa execução depende dos providers e credenciais configurados pelo scaffold e pode gerar custo externo.

## Executar o cliente Streamlit

Exporte as variáveis do arquivo local de forma compatível com seu shell e execute:

```bash
uv run streamlit run app.py
```

O cliente consulta os inputs disponíveis, inicia um kickoff e acompanha seu estado até sucesso, falha ou timeout. Mensagens de erro não exibem corpo de resposta, token ou URL configurada.

## Testes locais

Os testes não fazem chamadas de rede:

```bash
uv run python -m unittest discover -s tests
```

Eles verificam que a configuração vem do ambiente e que nenhuma requisição é feita quando as variáveis obrigatórias estão ausentes.

## Maturidade

- Sem CI.
- O scaffold CrewAI ainda contém conteúdo de exemplo.
- O cliente depende de uma API externa não incluída no repositório.
- Nenhum resultado de execução remota é declarado como validado.
