import os
import time
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

prompt_v3 = """[CONTEXTO]
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
"""

casos_teste = [
    "Bom dia, preciso da segunda via do boleto deste mês que venceu ontem.",
    "Quando começam as provas finais deste semestre?",
    "Não concordo com o 4,5 que tirei na prova de Algoritmos, quero revisão.",
    "Paguei minha matrícula ontem mas ainda não liberou meu acesso às aulas no portal.",
    "Oi, tudo bem? Preciso resolver aquele problema lá no sistema.",
    "Vocês podem enviar?",
    "Qual a previsão do tempo para Campinas amanhã?",
    "Mano, travei na hora de trancar o curso, onde clico pra cancelar minha vaga?"
]

print("Iniciando bateria de 8 testes do Prompt V3...\n")

for i, mensagem in enumerate(casos_teste, start=1):
    prompt_final = prompt_v3.replace("{mensagem_do_aluno}", mensagem)
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt_final,
    )
    saida_limpa = response.text.strip().replace("\n", " ")
    print(f"Caso 0{i}: {saida_limpa}\n")
    time.sleep(2)
