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

|  Caso   | Configuração          | Qualidade (0–3) | Latência (s) | Consumo (Tokens In / Out) | Observações                                    |
| :-----: | :-------------------- | :-------------: | :----------: | :-----------------------: | :--------------------------------------------- |
| **C01** | Config A (`temp=0.0`) |        3        |    1.567s    |          99 / 91          | Sem acesso ao edital; manteve resposta segura. |
| **C02** | Config A (`temp=0.0`) |        3        |    1.157s    |         112 / 125         | Sem acesso ao edital; manteve resposta segura. |
| **C03** | Config A (`temp=0.0`) |        3        |    3.187s    |         105 / 131         | Sem acesso ao edital; manteve resposta segura. |
| **C04** | Config A (`temp=0.0`) |        3        |    1.461s    |         103 / 95          | Sem acesso ao edital; manteve resposta segura. |
| **C05** | Config A (`temp=0.0`) |        3        |    2.619s    |         112 / 110         | Sem acesso ao edital; manteve resposta segura. |
| **C06** | Config A (`temp=0.0`) |        3        |    1.012s    |         105 / 124         | Sem acesso ao edital; manteve resposta segura. |
| **C01** | Config B (`temp=0.9`) |        3        |    1.255s    |          99 / 92          | Sem acesso ao edital; manteve resposta segura. |
| **C02** | Config B (`temp=0.9`) |        3        |    1.076s    |         112 / 129         | Sem acesso ao edital; manteve resposta segura. |
| **C03** | Config B (`temp=0.9`) |        3        |     1.9s     |         105 / 119         | Sem acesso ao edital; manteve resposta segura. |
| **C04** | Config B (`temp=0.9`) |        3        |    1.234s    |         103 / 97          | Sem acesso ao edital; manteve resposta segura. |
| **C05** | Config B (`temp=0.9`) |        3        |    1.057s    |         112 / 106         | Sem acesso ao edital; manteve resposta segura. |
| **C06** | Config B (`temp=0.9`) |        3        |    2.076s    |         105 / 91          | Sem acesso ao edital; manteve resposta segura. |

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

|            Caso            | Configuração          | Qualidade (0–3) | Latência (s) | Consumo (Tokens In / Out) | Observações                                         |
| :------------------------: | :-------------------- | :-------------: | :----------: | :-----------------------: | :-------------------------------------------------- |
|          **C01**           | Config A (`temp=0.0`) |        3        |    1.104s    |         107 / 81          | concluido_com_sucesso                               |
|          **C02**           | Config A (`temp=0.0`) |        3        |    0.973s    |         120 / 129         | concluido_com_sucesso                               |
|          **C03**           | Config A (`temp=0.0`) |        3        |    1.428s    |         113 / 128         | concluido_com_sucesso                               |
|          **C04**           | Config A (`temp=0.0`) |        3        |    1.432s    |         111 / 110         | concluido_com_sucesso                               |
|          **C05**           | Config A (`temp=0.0`) |        3        |    2.483s    |         120 / 81          | concluido_com_sucesso                               |
|          **C06**           | Config A (`temp=0.0`) |        3        |    2.838s    |         113 / 125         | concluido_com_sucesso                               |
|          **C07**           | Config A (`temp=0.0`) |        3        |    3.87s     |         96 / 178          | concluido_com_sucesso                               |
|          **C08**           | Config A (`temp=0.0`) |        3        |    1.316s    |         122 / 104         | concluido_com_sucesso                               |
|   **C09_FALHA_ENTRADA**    | Config A (`temp=0.0`) |        3        |     0.0s     |           0 / 0           | interrompido_validacao                              |
|          **C01**           | Config B (`temp=0.9`) |        3        |    1.788s    |         107 / 106         | concluido_com_sucesso                               |
|          **C02**           | Config B (`temp=0.9`) |        3        |    1.203s    |         120 / 144         | concluido_com_sucesso                               |
|          **C03**           | Config B (`temp=0.9`) |        3        |    1.078s    |         113 / 134         | concluido_com_sucesso                               |
|          **C04**           | Config B (`temp=0.9`) |        3        |    1.429s    |         111 / 81          | concluido_com_sucesso                               |
|          **C05**           | Config B (`temp=0.9`) |        3        |    1.538s    |         120 / 77          | concluido_com_sucesso                               |
|          **C06**           | Config B (`temp=0.9`) |        3        |    3.205s    |         113 / 90          | concluido_com_sucesso                               |
|          **C07**           | Config B (`temp=0.9`) |        3        |    2.129s    |         96 / 139          | concluido_com_sucesso                               |
|          **C08**           | Config B (`temp=0.9`) |        3        |    1.11s     |         122 / 69          | concluido_com_sucesso                               |
|   **C09_FALHA_ENTRADA**    | Config B (`temp=0.9`) |        3        |     0.0s     |           0 / 0           | interrompido_validacao                              |
| **C10_FALHA_API_SIMULADA** | Config A (`temp=0.0`) |        3        |    1.005s    |           0 / 0           | Falha de timeout capturada sem quebrar a aplicação. |

- **Conclusão Intermediária:** A `Config A (temperature=0.0)` manteve melhor previsibilidade e recusa adequada nos casos fora de escopo (`C08`) e ambíguos (`C07`), sendo escolhida como base para a etapa de RAG.

### Uso Crítico da IDE Agêntica (Competência C14)

- **Ferramenta utilizada:** VS Code (Chat em modo Agent conectado ao provedor Google Gemini via BYOK após erro `400` no endpoint padrão do Copilot Fusion).
- **Tarefa delegada:** Refatorar apenas a função `etapa_2_consultar_llm` em `P2/fluxo_intermediario.py` para implementar retry limitado (máximo 2 tentativas, pausa de 1s) e registrar `tentativas_realizadas` no retorno.
- **Revisão e validação:** O diff (`+26 -3` linhas) foi inspecionado manualmente, confirmando o laço finito `for tentativa in range(1, 3):` (sem risco de loop infinito) e a preservação das demais funções. A execução gravada em `logs_intermediario.json` validou `tentativas_realizadas: 1` nas chamadas normais e `tentativas_realizadas: 2` na falha simulada (`C10`).
- **Decisão:** Sugestão **incorporada** após verificação.

---

## 6. Evolução no Nível Avançado (`p2-avancado`) — RAG e Recomendação Final

### Preparação do Corpus e Estratégia de Particionamento

- **Origem e Vigência:** Regulamento do Processo Seletivo HBR 02/2025 — Centro Integrado de Inteligência Artificial (CIIA), publicado pelo Instituto Hardware BR (vigência abril–maio/2025, documento público).
- **Curadoria:** O regulamento foi organizado em 4 documentos Markdown temáticos na pasta `P2/corpus/`, preservando metadados de origem e numeração oficial das cláusulas, sem dados pessoais ou conteúdo restrito.
- **Particionamento (_Chunking_):** Divisão semântica por títulos de seção (`#` / `##`) e blocos de parágrafos, evitando cortar fórmulas de pontuação ou tabelas de cronograma no meio.
- **Embeddings e Recuperação:** Modelo `gemini-embedding-001` (via Google GenAI SDK), busca em memória por similaridade de cosseno, `top_k = 3` e `limiar_minimo = 0.25`.

### Avaliação da Recuperação e Uso do Contexto

- **Avaliação da Recuperação:** Na primeira execução do RAG com limiar `0.45` e quebra estrita por `# `, nenhum chunk atingiu o corte de similaridade (`Tokens In = 168`). Após ajustar o particionamento para seções `##`/parágrafos e calibrar o limiar para `0.25`, a recuperação passou a retornar os trechos exatos do regulamento e o modelo respondeu corretamente às perguntas `C01`, `C02`, `C03` e `C05`, mantendo a recusa correta no caso ausente `C06`.
- **Avaliação do Uso do Contexto:** Com os trechos injetados no prompt, o `gemini-3.5-flash-lite` (`temperature=0.0`) extraiu com precisão os números oficiais (20 vagas, bolsa de R$ 2.800,00, fórmula `0,7*PS + 0,3*FS` e datas do cronograma), citou as seções de origem e não inventou resposta quando o tema não constava no corpus (`C06`).
- **Consistência (Protocolo de 3 Repetições):** Nos casos repetidos 3 vezes (`C01`, `C03` e `C06`), a configuração com `temperature=0.0` manteve 100% de consistência factual e estrutural entre as execuções.

### Recomendação Técnica Final

- **Configuração Recomendada:** Modelo `gemini-3.5-flash-lite` com `temperature = 0.0`, `max_output_tokens = 350` **com RAG ativado** (`top_k = 3`, `limiar = 0.25`, particionamento semântico por seção).
- **Configuração Alternativa:** Mesmo modelo sem RAG apenas para triagem inicial de intenção ou perguntas genéricas sobre o funcionamento do chat, nunca para informar datas ou valores.
- **Quando usar ou não usar RAG:**
  - _RAG obrigatório:_ Dúvidas sobre prazos, valores de bolsa, critérios de desempate e requisitos do edital.
  - _Recusa / Encaminhamento humano:_ Avaliação individual de candidatos, análise curricular subjetiva ou recursos administrativos.

### Condições para um Piloto Seguro

- **Público e Tarefa:** Candidatos do processo seletivo tirando dúvidas objetivas sobre o edital público vigente.
- **Controles Obrigatórios:** Base documental exclusivamente pública e versionada; resposta restrita aos trechos recuperados com citação de fonte; bloqueio de entradas vazias ou pedidos de decisão individual; revisão humana obrigatória para casos omissos no edital.
