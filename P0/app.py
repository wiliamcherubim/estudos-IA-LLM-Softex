import os
import google.genai as genai
from dotenv import load_dotenv

# 1. Carrega a variável GEMINI_API_KEY salva no arquivo .env
load_dotenv()

# Instancia o cliente de forma segura (ele lê a chave do arquivo .env automaticamente)
client = genai.Client()

# 2. Dados de entrada (Exemplo de transcrição de reunião)
transcricao_reuniao = """
Carlos disse: Pessoal, precisamos atualizar o relatório de vendas até sexta-feira sem falta, senão o diretor vai cobrar. 
Mariana respondeu: Tudo bem, eu puxo os dados do sistema hoje à tarde. Mas preciso que o desenvolvedor, o Lucas, 
corrija o bug do botão de exportar antes disso. Lucas disse: Deixa comigo, até o meio-dia eu subo a correção no sistema.
"""

# 3. Engenharia de Prompt (O comando para a IA)
prompt_sistema = (
    "Você é um assistente de escritório focado em produtividade. "
    "Analise a transcrição da reunião fornecida e extraia uma lista com "
    "exatamente os três principais pontos de ação (action items), indicando "
    "quem é o responsável e o prazo de cada tarefa, se houver."
)

prompt_final = f"{prompt_sistema}\n\nTranscrição:\n{transcricao_reuniao}"

print("Enviando solicitação para o Gemini...")

# 4. Chamar o modelo LLM
response = client.models.generate_content(
    model='gemini-3.5-flash-lite',
    contents=prompt_final,
)

# 5. Exibir o resultado na tela
print("\n--- PONTOS DE AÇÃO EXTRAÍDOS ---")
print(response.text)
