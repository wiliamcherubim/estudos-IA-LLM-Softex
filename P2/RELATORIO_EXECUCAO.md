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

Definida previamente à execução dos testes:

| Nota  | Interpretação                                                                                               |
| :---: | :---------------------------------------------------------------------------------------------------------- |
| **0** | Resposta inventada (alucinação), sem relação com a pergunta ou claramente incorreta.                        |
| **1** | Resposta parcialmente relacionada ao tema, mas com erros importantes nos dados.                             |
| **2** | Resposta útil e segura, porém incompleta ou vaga.                                                           |
| **3** | Resposta correta, clara e fiel ao regulamento (ou recusa explícita e correta quando não há acesso ao dado). |

---

## 2. Configurações Avaliadas (Nível Básico — Sem RAG)

Nesta primeira etapa, o modelo respondeu às perguntas **sem acesso ao PDF do regulamento**, utilizando apenas seu conhecimento interno e as instruções de sistema.

- **Fatores mantidos constantes:**
  - Modelo: `gemini-3.5-flash-lite`
  - `system_instruction`: Instrução para responder com objetividade e declarar ausência de dados caso não tenha certeza factual.
  - `max_output_tokens`: `300`
- **Fator deliberadamente variado (`temperature`):**
  - **Config A (`config_A_baseline_temp0`):** `temperature = 0.0` (Linha de base determinística, focada em precisão e baixa variação).
  - **Config B (`config_B_criativa_temp09`):** `temperature = 0.9` (Configuração alternativa com maior aleatoriedade para observar risco de invenção de dados).

---

## 3. Resultados da Comparação Inicial (Nível Básico)

|  Caso   | Configuração          | Qualidade (0–3) | Latência (s) | Consumo (Tokens In / Out) | Observações               |
| :-----: | :-------------------- | :-------------: | :----------: | :-----------------------: | :------------------------ |
| **C01** | Config A (`temp=0.0`) |     [Nota]      | [Ex: 0.85s]  |       [Ex: 65 / 42]       | [Resumo do comportamento] |
| **C01** | Config B (`temp=0.9`) |     [Nota]      | [Ex: 0.92s]  |       [Ex: 65 / 78]       | [Resumo do comportamento] |
| **C02** | Config A (`temp=0.0`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C02** | Config B (`temp=0.9`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C03** | Config A (`temp=0.0`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C03** | Config B (`temp=0.9`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C04** | Config A (`temp=0.0`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C04** | Config B (`temp=0.9`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C05** | Config A (`temp=0.0`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C05** | Config B (`temp=0.9`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C06** | Config A (`temp=0.0`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |
| **C06** | Config B (`temp=0.9`) |     [Nota]      |     [s]      |        [In / Out]         | [Observação]              |

---

## 4. Evolução por Nível

### Conclusão Inicial — Nível Básico (`p2-basico`)

- **Desempenho comparativo:** [Escreva aqui qual configuração foi melhor — ex: A Config A com `temperature=0.0` apresentou respostas mais concisas e consistentes, enquanto a Config B gerou textos mais longos / tentou supor detalhes].
- **Latência e Consumo:** [Compare a média de tempo e tokens de saída entre A e B].
- **Limitação principal:** Como nenhum dos modelos teve acesso ao documento oficial (condição sem RAG), ambos não puderam informar valores exatos de bolsa, datas do cronograma ou regras específicas de pontuação, confirmando a necessidade de implementar **RAG** nas próximas etapas.

_(As seções de Fluxo Rastreável, Uso de IDE Agêntica, Implementação de RAG, Recomendação Final e Piloto serão adicionadas nos níveis Intermediário e Avançado)._
