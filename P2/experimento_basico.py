import os
import time
import json
from datetime import datetime
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY não encontrada no arquivo .env")

client = genai.Client()
MODELO = "gemini-3.5-flash-lite"

INSTRUCAO_SISTEMA = (
    "Você é um assistente informativo do Processo Seletivo HBR 02/2025 "
    "(Centro Integrado de Inteligência Artificial - CIIA). "
    "Responda de forma clara e objetiva. Se você não tiver certeza ou não dispuser "
    "da informação oficial exata, declare explicitamente que não possui dados suficientes "
    "e não invente datas, valores ou regras."
)

CASOS_TESTE = [
    {
        "id": "C01",
        "pergunta": "Quantas vagas existem para desenvolvedores de soluções no CIIA e qual o valor mensal da bolsa?",
        "gabarito": "20 vagas para desenvolvedores de soluções; bolsa de R$ 2.800,00 mensais (20h/semana)."
    },
    {
        "id": "C02",
        "pergunta": "Não sou estudante de graduação nem pós-graduação. Posso me inscrever no processo seletivo HBR 02/2025?",
        "gabarito": "Sim, em caráter de excepcionalidade, comprovando pelo menos 2 anos de atuação acadêmica ou profissional em áreas tecnológicas correlatas."
    },
    {
        "id": "C03",
        "pergunta": "Como é calculada a nota final para classificação dos 100 primeiros candidatos e quais são os critérios de desempate?",
        "gabarito": "NOTA = (0,7 x PS) + (0,3 x FS). Desempate: 1º Programação para IA; 2º IA Generativa."
    },
    {
        "id": "C04",
        "pergunta": "Como é dividida a Prova de Seleção do CIIA e qual a pontuação mínima para não ser eliminado?",
        "gabarito": "30 questões (10 Fundamentos x 0,2; 10 IA Generativa x 0,3; 10 Programação IA x 0,5). Mínimo 4 pontos no total e 50% por trilha."
    },
    {
        "id": "C05",
        "pergunta": "Qual é o período de inscrições e a data da Prova de Seleção no Processo Seletivo HBR 02/2025?",
        "gabarito": "Inscrições: 04/04/25 a 13/04/25. Prova de Seleção: 10/05/25."
    },
    {
        "id": "C06",
        "pergunta": "O regulamento do CIIA exige certificado de proficiência em inglês (TOEFL ou IELTS) para assumir a bolsa?",
        "gabarito": "Informação ausente no regulamento (não há exigência de certificação em inglês)."
    }
]

CONFIGURACOES = {
    "config_A_baseline_temp0": {
        "temperature": 0.0,
        "max_output_tokens": 300,
        "descricao": "Linha de base determinística (temperature=0.0)"
    },
    "config_B_criativa_temp09": {
        "temperature": 0.9,
        "max_output_tokens": 300,
        "descricao": "Variação com maior aleatoriedade (temperature=0.9)"
    }
}

def executar_experimento():
    resultados = []
    data_execucao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for nome_cfg, params in CONFIGURACOES.items():
        print(f"\n=== Executando {nome_cfg} ({params['descricao']}) ===")
        for caso in CASOS_TESTE:
            inicio = time.perf_counter()
            erro = None
            resposta_texto = ""
            tokens_entrada = None
            tokens_saida = None

            try:
                response = client.models.generate_content(
                    model=MODELO,
                    contents=caso["pergunta"],
                    config=types.GenerateContentConfig(
                        system_instruction=INSTRUCAO_SISTEMA,
                        temperature=params["temperature"],
                        max_output_tokens=params["max_output_tokens"],
                    )
                )
                resposta_texto = response.text.strip()
                if response.usage_metadata:
                    tokens_entrada = response.usage_metadata.prompt_token_count
                    tokens_saida = response.usage_metadata.candidates_token_count
            except Exception as e:
                erro = str(e)

            latencia = round(time.perf_counter() - inicio, 3)
            print(f"[{caso['id']}] Latência: {latencia}s | Tokens (in/out): {tokens_entrada}/{tokens_saida}")
            print(f"Resposta: {resposta_texto[:140]}...\n")

            resultados.append({
                "data": data_execucao,
                "caso_id": caso["id"],
                "configuracao": nome_cfg,
                "parametros": params,
                "pergunta": caso["pergunta"],
                "gabarito_referencia": caso["gabarito"],
                "resposta": resposta_texto,
                "latencia_segundos": latencia,
                "tokens_entrada": tokens_entrada,
                "tokens_saida": tokens_saida,
                "erro": erro,
                "nota_avaliacao_0_a_3": None,  # Preencher manualmente após análise
                "observacao": ""
            })
            time.sleep(1.5)  # Evita limite de requisições por minuto (RPM)

    os.makedirs("P2/resultados", exist_ok=True)
    caminho_saida = "P2/resultados/resultados_basico.json"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"Resultados salvos em {caminho_saida}")

if __name__ == "__main__":
    executar_experimento()
