# Relatório de Execução — Projeto P2

**Autor:** Wiliam Cherubim  
**Curso:** IA LLM — Instituto Hardware BR / Softex Campinas  
**Modelo Base:** `gemini-3.5-flash-lite` (via Google GenAI SDK)

---

## 1. Definição da Tarefa e Delimitação do Problema

- **Domínio:** Processo Seletivo HBR 02/2025 — Centro Integrado de Inteligência Artificial (CIIA).
- **Tarefa do Assistente:** Responder perguntas objetivas de candidatos sobre requisitos de inscrição, vagas, bolsas, critérios de classificação, prova e cronograma do edital oficial.
- **Limites do Sistema:** O assistente não deve avaliar currículos, prever aprovação de candidatos, substituir a comissão organizadora ou inventar informações ausentes no documento oficial.

### Critérios e Escala de Avaliação

| Nota  | Interpretação                                                                                               |
| :---: | :---------------------------------------------------------------------------------------------------------- |
| **0** | Resposta inventada (alucinação), sem relação com a pergunta ou claramente incorreta.                        |
| **1** | Resposta parcialmente relacionada ao tema, mas com erros importantes nos dados.                             |
| **2** | Resposta útil e segura, porém incompleta ou vaga.                                                           |
| **3** | Resposta correta, clara e fiel ao regulamento (ou recusa explícita e correta quando não há acesso ao dado). |

---

## 2. Configurações Avaliadas (Nível Básico — Sem RAG)

- **Fatores mantidos constantes:** Modelo `gemini-3.5-flash-lite`, mesmo `system_instruction` e `max_output_tokens = 300`.
- **Fator deliberadamente variado (`temperature`):**
  - **Config A (`config_A_baseline_temp0`):** `temperature = 0.0` (Linha de base determinística).
  - **Config B (`config_B_criativa_temp09`):** `temperature = 0.9` (Variação com maior aleatoriedade).

---

## 3. Resultados da Comparação Inicial (Nível Básico)

| Caso | Configuração | Qualidade (0–3) | Latência (s) | Consumo (Tokens In / Out) | Observações |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **C01** | Config A (`temp=0.0`) | 3 | 1.567s | 99 / 91 | Sem acesso ao edital; manteve resposta segura. |
| **C02** | Config A (`temp=0.0`) | 3 | 1.157s | 112 / 125 | Sem acesso ao edital; manteve resposta segura. |
| **C03** | Config A (`temp=0.0`) | 3 | 3.187s | 105 / 131 | Sem acesso ao edital; manteve resposta segura. |
| **C04** | Config A (`temp=0.0`) | 3 | 1.461s | 103 / 95 | Sem acesso ao edital; manteve resposta segura. |
| **C05** | Config A (`temp=0.0`) | 3 | 2.619s | 112 / 110 | Sem acesso ao edital; manteve resposta segura. |
| **C06** | Config A (`temp=0.0`) | 3 | 1.012s | 105 / 124 | Sem acesso ao edital; manteve resposta segura. |
| **C01** | Config B (`temp=0.9`) | 3 | 1.255s | 99 / 92 | Sem acesso ao edital; manteve resposta segura. |
| **C02** | Config B (`temp=0.9`) | 3 | 1.076s | 112 / 129 | Sem acesso ao edital; manteve resposta segura. |
| **C03** | Config B (`temp=0.9`) | 3 | 1.9s | 105 / 119 | Sem acesso ao edital; manteve resposta segura. |
| **C04** | Config B (`temp=0.9`) | 3 | 1.234s | 103 / 97 | Sem acesso ao edital; manteve resposta segura. |
| **C05** | Config B (`temp=0.9`) | 3 | 1.057s | 112 / 106 | Sem acesso ao edital; manteve resposta segura. |
| **C06** | Config B (`temp=0.9`) | 3 | 2.076s | 105 / 91 | Sem acesso ao edital; manteve resposta segura. |

---

## 4. Evolução por Nível — Conclusão Inicial (`p2-basico`)

- **Desempenho comparativo:** A `Config A (temperature=0.0)` apresentou respostas mais diretas, determinísticas e consistentes entre execuções, enquanto a `Config B (temperature=0.9)` gerou respostas mais longas e verbosas.
- **Limitação principal:** Como ambos os testes ocorreram sem acesso ao regulamento (sem RAG), o modelo não pôde informar datas, valores de bolsa ou notas de corte exatas, confirmando a necessidade de implementar **RAG** no Nível Avançado.

---

## 5. Evolução no Nível Intermediário (`p2-intermediario`)

### Arquitetura do Fluxo Rastreável e Tratamento de Falhas
O fluxo foi modularizado em `P2/fluxo_intermediario.py` com duas etapas independentes e logs estruturados em `P2/resultados/logs_intermediario.json`:
1. **Etapa 1 (`etapa_1_validar_entrada`):** Normaliza o texto e rejeita entradas vazias ou maiores que 500 caracteres antes do consumo da API (demonstrado no caso `C09_FALHA_ENTRADA`).
2. **Etapa 2 (`etapa_2_consultar_llm`):** Realiza a chamada ao `gemini-3.5-flash-lite` com captura controlada de exceções (`APIError`, `TimeoutError`) e retry limitado a 2 tentativas (demonstrado no caso `C10_FALHA_API_SIMULADA`).

### Resultados da Comparação Ampliada (8 Casos + 2 Testes de Resiliência)

| Caso | Configuração | Qualidade (0–3) | Latência (s) | Consumo (Tokens In / Out) | Observações |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **C01** | Config A (`temp=0.0`) | 3 | 1.104s | 107 / 81 | concluido_com_sucesso |
| **C02** | Config A (`temp=0.0`) | 3 | 0.973s | 120 / 129 | concluido_com_sucesso |
| **C03** | Config A (`temp=0.0`) | 3 | 1.428s | 113 / 128 | concluido_com_sucesso |
| **C04** | Config A (`temp=0.0`) | 3 | 1.432s | 111 / 110 | concluido_com_sucesso |
| **C05** | Config A (`temp=0.0`) | 3 | 2.483s | 120 / 81 | concluido_com_sucesso |
| **C06** | Config A (`temp=0.0`) | 3 | 2.838s | 113 / 125 | concluido_com_sucesso |
| **C07** | Config A (`temp=0.0`) | 3 | 3.87s | 96 / 178 | concluido_com_sucesso |
| **C08** | Config A (`temp=0.0`) | 3 | 1.316s | 122 / 104 | concluido_com_sucesso |
| **C09_FALHA_ENTRADA** | Config A (`temp=0.0`) | 3 | 0.0s | 0 / 0 | interrompido_validacao |
| **C01** | Config B (`temp=0.9`) | 3 | 1.788s | 107 / 106 | concluido_com_sucesso |
| **C02** | Config B (`temp=0.9`) | 3 | 1.203s | 120 / 144 | concluido_com_sucesso |
| **C03** | Config B (`temp=0.9`) | 3 | 1.078s | 113 / 134 | concluido_com_sucesso |
| **C04** | Config B (`temp=0.9`) | 3 | 1.429s | 111 / 81 | concluido_com_sucesso |
| **C05** | Config B (`temp=0.9`) | 3 | 1.538s | 120 / 77 | concluido_com_sucesso |
| **C06** | Config B (`temp=0.9`) | 3 | 3.205s | 113 / 90 | concluido_com_sucesso |
| **C07** | Config B (`temp=0.9`) | 3 | 2.129s | 96 / 139 | concluido_com_sucesso |
| **C08** | Config B (`temp=0.9`) | 3 | 1.11s | 122 / 69 | concluido_com_sucesso |
| **C09_FALHA_ENTRADA** | Config B (`temp=0.9`) | 3 | 0.0s | 0 / 0 | interrompido_validacao |
| **C10_FALHA_API_SIMULADA** | Config A (`temp=0.0`) | 3 | 1.005s | 0 / 0 | Falha de timeout capturada sem quebrar a aplicação. |

- **Conclusão Intermediária:** A `Config A (temperature=0.0)` manteve melhor previsibilidade e recusa adequada nos casos fora de escopo (`C08`) e ambíguos (`C07`), sendo escolhida como base para a etapa de RAG.

### Uso Crítico da IDE Agêntica (Competência C14)
- **Ferramenta utilizada:** VS Code (Chat em modo Agent conectado ao provedor Google Gemini via BYOK após erro `400` no endpoint padrão do Copilot Fusion).
- **Tarefa delegada:** Refatorar apenas a função `etapa_2_consultar_llm` em `P2/fluxo_intermediario.py` para implementar retry limitado (máximo 2 tentativas, pausa de 1s) e registrar `tentativas_realizadas` no retorno.
- **Revisão e validação:** O diff (`+26 -3` linhas) foi inspecionado manualmente, confirmando o laço finito `for tentativa in range(1, 3):` (sem risco de loop infinito) e a preservação das demais funções. A execução gravada em `logs_intermediario.json` validou `tentativas_realizadas: 1` nas chamadas normais e `tentativas_realizadas: 2` na falha simulada (`C10`).
- **Decisão:** Sugestão **incorporada** após verificação.
