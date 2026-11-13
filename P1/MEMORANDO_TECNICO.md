# Memorando Técnico — Projeto P1: Análise de Viabilidade de IA

**Autor:** Wiliam Cherubim  
**Curso:** IA LLM — Softex Campinas  
**Etapa Atual:** Nível Intermediário (`p1-intermediario`)

---

## 1. Análise Inicial das Funcionalidades (Nível Básico)

### 1.1. Classificar mensagens por assunto (Candidata ao uso de LLM)

- **Natureza da tarefa:** Envolve principalmente **interpretação de linguagem** natural para identificar a intenção do estudante.
- **Entrada:** Texto livre da mensagem enviada pelo estudante no canal de atendimento.
- **Resultado esperado:** Uma categoria padronizada correspondente ao tema principal da solicitação.
- **Um LLM é adequado para essa tarefa?** Sim. Modelos de linguagem compreendem bem contexto, sinônimos e textos informais, superando buscas simples por palavras-chave.
- **Que erros o modelo poderia cometer?** Classificar incorretamente mensagens ambíguas, escolher apenas um tema quando há dois assuntos juntos ou inventar categorias fora da lista permitida.
- **Qual seria o impacto desses erros?** Baixo a moderado. O principal impacto é o atraso no atendimento por encaminhamento ao setor errado, sem perda financeira ou acadêmica direta.
- **Existe alternativa mais simples?** Sim, um formulário de contato com menu suspenso (_dropdown_), porém os estudantes frequentemente selecionam opções erradas por dúvida ou pressa.
- **Seria necessária revisão humana?** Apenas nos casos em que a mensagem apresentar ambiguidade ou múltiplos assuntos simultâneos.

---

### 1.2. Encaminhar a mensagem ao setor responsável (Solução mais simples sem IA)

- **Natureza da tarefa:** Envolve exclusivamente **aplicação de regra** lógica determinística.
- **Entrada:** A categoria do assunto já identificada (ex: _Pagamentos_, _Matrícula_, _Acesso ao Ambiente Virtual_).
- **Resultado esperado:** Roteamento automático do chamado para a fila do departamento correspondente (ex: Financeiro, Secretaria ou Suporte Técnico).
- **Um LLM é adequado para essa tarefa?** Não. Usar um modelo de linguagem para mapear uma categoria fixa a um setor gera custo desnecessário, maior latência e risco de variação na resposta.
- **Que erros o modelo poderia cometer?** Se usado nessa etapa, poderia alucinar o nome de um setor inexistente ou alterar o padrão de roteamento sem motivo.
- **Qual seria o impacto desses erros?** Extravio de solicitações e perda de rastreabilidade no fluxo de atendimento.
- **Existe alternativa mais simples?** Sim. Regras fixas condicionais (`SE categoria == "Pagamentos" ENTÃO encaminhar para "Setor Financeiro"`), que são gratuitas, instantâneas e 100% previsíveis.
- **Seria necessária revisão humana?** Não para o roteamento padrão, apenas em casos de exceção marcados como "Outros".

---

### 1.3. Apoiar decisões sobre revisão de nota ou benefício financeiro (Alto impacto)

- **Natureza da tarefa:** Envolve **decisão** crítica, consulta a normas institucionais e avaliação de mérito.
- **Entrada:** Pedido do estudante acompanhado de justificativas, histórico escolar, atestados ou dados financeiros.
- **Resultado esperado:** Parecer deferindo ou indeferindo uma alteração de nota, desconto ou bolsa de estudos.
- **Um LLM é adequado para essa tarefa?** Não. Modelos de linguagem geram texto com base em probabilidade estatística e não possuem capacidade jurídica, ética ou institucional para julgar direitos de estudantes.
- **Que erros o modelo poderia cometer?** Inventar regras acadêmicas (alucinação), aplicar tratamentos desiguais (viés) ou aceitar argumentos persuasivos sem base documental.
- **Qual seria o impacto desses erros?** Alto e crítico. Pode causar prejuízo financeiro à instituição, injustiça acadêmica ao aluno e violações legais ou de conformidade.
- **Existe alternativa mais simples?** Não há automação recomendada para a decisão final; o fluxo deve seguir por análise documental humana baseada no regimento da instituição.
- **Seria necessária revisão humana?** Sim, **obrigatória e integral**. A decisão final deve ser tomada exclusivamente por um coordenador, professor ou analista responsável.

---

## 2. Primeiro Prompt Protótipo e Testes Exploratórios

### Prompt V1 — Classificação de Assunto

- **Objetivo:** Classificar a mensagem do aluno em uma única categoria oficial da instituição.
- **Estrutura:**

```text
[CONTEXTO]
Você é um assistente de triagem de atendimento de uma instituição de ensino digital. O departamento recebe milhares de mensagens mensais de estudantes sobre temas acadêmicos, financeiros e técnicos.

[TAREFA]
Analise a mensagem do estudante fornecida abaixo e classifique-a em exatamente UMA das seguintes categorias oficiais:
- Matrícula
- Documentos
- Pagamentos
- Calendário Acadêmico
- Revisão de Notas
- Acesso ao Ambiente Virtual
- Solicitações Administrativas

[INSTRUÇÕES]
- Baseie sua decisão exclusivamente no conteúdo da mensagem.
- Não tente responder à dúvida do aluno, apenas classifique o assunto.
- Se a mensagem não se encaixar em nenhuma categoria acima, responda "Outros".

[FORMATO ESPERADO]
Responda apenas com o nome exato da categoria, sem explicações adicionais ou pontuação.

Mensagem do estudante:
"{mensagem_do_aluno}"
```

### Resultados dos Testes Exploratórios (3 Casos Fictícios)

| Teste  | Mensagem Fictícia (Entrada)                                                                | Resultado Esperado         | Resultado Obtido           | Observação                                                              |
| :----- | :----------------------------------------------------------------------------------------- | :------------------------- | :------------------------- | :---------------------------------------------------------------------- |
| **01** | _"Olá, paguei o boleto ontem mas ainda consta em aberto no portal. Podem verificar?"_      | Pagamentos                 | Pagamentos                 | Acertou a categoria e respeitou o formato sem texto extra.              |
| **02** | _"Não consigo entrar na plataforma para ver a aula de hoje, diz que minha senha expirou."_ | Acesso ao Ambiente Virtual | Acesso ao Ambiente Virtual | Identificou corretamente o problema técnico sem precisar da sigla AVA.  |
| **03** | _"Preciso do meu histórico escolar assinado para entregar no meu estágio até sexta."_      | Documentos                 | Documentos                 | Classificou corretamente a demanda documental sem inventar explicações. |

---

## 3. Evolução de Prompts e Critérios de Avaliação (Nível Intermediário)

### 3.1. Registro da Evolução dos Prompts

- **Limitação identificada na V1:** O Prompt V1 exigia apenas o nome de uma única categoria. Em cenários reais, estudantes enviam mensagens misturando dois assuntos diferentes (ex: problema de boleto e acesso à aula), textos muito curtos/incompletos ou perguntas fora do escopo da instituição. Sem um sinalizador de incerteza, o modelo era forçado a "chutar" uma categoria.

- **Ajustes na V2 (Tratamento de Ambiguidade e Recusa):** Adicionamos regras explícitas para mensagens com múltiplos assuntos (`"Múltiplos Assuntos"`) e para pedidos sem informação suficiente ou fora do contexto acadêmico (`"Incompleto / Fora de Escopo"`), além de exigir uma justificativa curta.

- **Ajustes na V3 (Saída Estruturada em JSON para Integração):** Para permitir que o sistema da escola tome decisões automáticas (como encaminhar direto ou enviar para triagem humana), estruturamos a saída em formato **JSON** contendo três campos: `categoria`, `confianca` (`alta`, `media` ou `baixa`) e `revisao_humana` (`true` ou `false`).

#### Prompt V2 — Tratamento de Casos Ambíguos e Fora de Escopo

```text
[CONTEXTO]
Você é um assistente de triagem de atendimento de uma instituição de ensino digital.

[TAREFA]
Classifique a mensagem do estudante em UMA das categorias oficiais:
- Matrícula
- Documentos
- Pagamentos
- Calendário Acadêmico
- Revisão de Notas
- Acesso ao Ambiente Virtual
- Solicitações Administrativas
- Múltiplos Assuntos (quando houver dois ou mais temas distintos)
- Incompleto / Fora de Escopo (quando faltar informação ou não tiver relação com a escola)

[INSTRUÇÕES]
- Baseie-se exclusivamente no texto enviado pelo estudante.
- Não invente informações nem tente responder à dúvida.
- Se houver dúvida entre duas categorias, priorize "Múltiplos Assuntos".

[FORMATO ESPERADO]
Categoria: <nome exato da categoria>
Justificativa: <frase curta de até 15 palavras explicando a escolha>

Mensagem do estudante:
"{mensagem_do_aluno}"
```

#### Prompt V3 (Versão Final) — Triagem Estruturada com Sinalização de Risco

```text
[CONTEXTO]
Você é um sistema de triagem inteligente de uma instituição de ensino digital. Sua saída será lida por um software que decide se o chamado vai direto para um setor ou para um atendente humano.

[TAREFA]
Analise a mensagem do estudante e retorne um objeto JSON válido classificando o atendimento.

[CATEGORIAS PERMITIDAS]
"Matrícula", "Documentos", "Pagamentos", "Calendário Acadêmico", "Revisão de Notas", "Acesso ao Ambiente Virtual", "Solicitações Administrativas", "Múltiplos Assuntos", "Incompleto / Fora de Escopo".

[INSTRUÇÕES]
- Use estritamente o conteúdo da mensagem. Nunca suponha fatos não escritos.
- Marque "revisao_humana" como true sempre que:
  1. A categoria for "Múltiplos Assuntos", "Incompleto / Fora de Escopo" ou "Revisão de Notas".
  2. A mensagem estiver ambígua, agressiva ou com baixa confiança.
- Caso contrário, marque "revisao_humana" como false.

[FORMATO ESPERADO]
Responda APENAS com o JSON abaixo, sem blocos de código markdown ou texto extra:
{
  "categoria": "string",
  "confianca": "alta | media | baixa",
  "revisao_humana": true ou false,
  "motivo": "explicação objetiva em até 12 palavras"
}

Mensagem do estudante:
"{mensagem_do_aluno}"
```

---

### 3.2. Critérios Objetivos de Avaliação

Para validar o desempenho do **Prompt V3**, cada resposta gerada foi avaliada segundo quatro critérios:

1. **Fidelidade ao texto:** O modelo classificou apenas com base no que foi escrito, sem presumir contextos ocultos.
2. **Obediência às categorias:** A chave `categoria` utilizou exatamente um dos termos da lista oficial.
3. **Conformidade estrutural:** A resposta retornou um JSON válido com as 4 chaves exigidas, sem texto fora da estrutura.
4. **Sinalização adequada de revisão humana:** Casos ambíguos, incompletos ou sensíveis (como revisão de nota) ativaram corretamente `"revisao_humana": true`.

---

### 3.3. Bateria de Testes Variados (8 Casos — Prompt V3)

| Caso   | Tipo de Cenário         | Mensagem Fictícia (Entrada)                                                           | Resultado Esperado                                     | Saída Obtida (Prompt V3)                                                                                                                                                          | Avaliação  |
| :----- | :---------------------- | :------------------------------------------------------------------------------------ | :----------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------- |
| **01** | Simples / Direto        | _"Bom dia, preciso da segunda via do boleto deste mês que venceu ontem."_             | `Pagamentos` (`revisao_humana: false`)                 | `{"categoria": "Pagamentos", "confianca": "alta", "revisao_humana": false, "motivo": "Solicitação clara de segunda via de boleto vencido."}`                                      | **Passou** |
| **02** | Simples / Direto        | _"Quando começam as provas finais deste semestre?"_                                   | `Calendário Acadêmico` (`revisao_humana: false`)       | `{"categoria": "Calendário Acadêmico", "confianca": "alta", "revisao_humana": false, "motivo": "Estudante questiona sobre a data de início das provas finais."}`                  | **Passou** |
| **03** | Alto Impacto            | _"Não concordo com o 4,5 que tirei na prova de Algoritmos, quero revisão."_           | `Revisão de Notas` (`revisao_humana: true`)            | `{"categoria": "Revisão de Notas", "confianca": "alta", "revisao_humana": true, "motivo": "Solicitação de revisão de nota exige intervenção humana."}`                            | **Passou** |
| **04** | Ambíguo / Múltiplo      | _"Paguei minha matrícula ontem mas ainda não liberou meu acesso às aulas no portal."_ | `Múltiplos Assuntos` (`revisao_humana: true`)          | `{"categoria": "Múltiplos Assuntos", "confianca": "alta", "revisao_humana": true, "motivo": "A mensagem envolve pagamentos e acesso ao ambiente virtual."}`                       | **Passou** |
| **05** | Ambíguo / Vago          | _"Oi, tudo bem? Preciso resolver aquele problema lá no sistema."_                     | `Incompleto / Fora de Escopo` (`revisao_humana: true`) | `{"categoria": "Incompleto / Fora de Escopo", "confianca": "baixa", "revisao_humana": true, "motivo": "Mensagem vaga sem especificar o problema relatado."}`                      | **Passou** |
| **06** | Incompleto              | _"Vocês podem enviar?"_                                                               | `Incompleto / Fora de Escopo` (`revisao_humana: true`) | `{"categoria": "Incompleto / Fora de Escopo", "confianca": "alta", "revisao_humana": true, "motivo": "A mensagem está incompleta e não especifica o assunto."}`                   | **Passou** |
| **07** | Fora de Escopo (Recusa) | _"Qual a previsão do tempo para Campinas amanhã?"_                                    | `Incompleto / Fora de Escopo` (`revisao_humana: true`) | `{"categoria": "Incompleto / Fora de Escopo", "confianca": "alta", "revisao_humana": true, "motivo": "A mensagem é irrelevante para a instituição de ensino."}`                   | **Passou** |
| **08** | Linguagem Informal      | _"Mano, travei na hora de trancar o curso, onde clico pra cancelar minha vaga?"_      | `Solicitações Administrativas` ou `Matrícula`          | `{"categoria": "Solicitações Administrativas", "confianca": "media", "revisao_humana": false, "motivo": "Estudante solicita instruções sobre como trancar ou cancelar o curso."}` | **Passou** |

### 3.4. Síntese dos Resultados da Bateria de Testes

- **Taxa de acerto:** 8 de 8 casos aprovados nos critérios estruturais e semânticos (100% de JSONs válidos).
- **Ponto forte observado:** O modelo conseguiu diferenciar pedidos diretos (Casos 01 e 02) de situações que exigem intervenção humana, como revisão de nota (Caso 03) e mensagens com múltiplos temas misturados (Caso 04).
- **Ponto de atenção (Melhoria futura):** No Caso 08 (_trancar o curso_), o modelo retornou `"confianca": "media"` mas manteve `"revisao_humana": false`. Em produção, recomenda-se ajustar a regra para acionar revisão humana sempre que a confiança for `"media"` ou `"baixa"`, evitando cancelamentos acidentais sem orientação.
