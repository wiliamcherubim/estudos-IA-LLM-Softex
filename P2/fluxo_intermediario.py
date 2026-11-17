import os
import time
import json
from datetime import datetime
import google.genai as genai
from google.genai import types, errors
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY não encontrada no arquivo .env")

client = genai.Client()
MODELO = "gemini-3.5-flash-lite"

INSTRUCAO_SISTEMA = (
    "Você é um assistente informativo do Processo Seletivo HBR 02/2025 "
    "(Centro Integrado de Inteligência Artificial - CIIA). "
    "Responda apenas dúvidas gerais sobre regras, vagas, bolsas e datas do edital. "
    "Se não tiver certeza factual exata, declare que não possui informação suficiente. "
    "Nunca avalie candidatos individuais, não calcule notas pessoais e não preveja aprovação."
)

CASOS_TESTE = [
    # 6 casos mantidos do Básico para comparação justa
    {
        "id": "C01",
        "tipo": "direta",
        "pergunta": "Quantas vagas existem para desenvolvedores de soluções no CIIA e qual o valor mensal da bolsa?",
        "gabarito": "20 vagas para desenvolvedores; bolsa de R$ 2.800,00 mensais (20h/semana)."
    },
    {
        "id": "C02",
        "tipo": "combinada",
        "pergunta": "Não sou estudante de graduação nem pós-graduação. Posso me inscrever no processo seletivo HBR 02/2025?",
        "gabarito": "Sim, em caráter de excepcionalidade, comprovando pelo menos 2 anos de atuação acadêmica ou profissional em áreas tecnológicas correlatas."
    },
    {
        "id": "C03",
        "tipo": "combinada",
        "pergunta": "Como é calculada a nota final para classificação dos 100 primeiros candidatos e quais são os critérios de desempate?",
        "gabarito": "NOTA = (0,7 x PS) + (0,3 x FS). Desempate: 1º Programação para IA; 2º IA Generativa."
    },
    {
        "id": "C04",
        "tipo": "direta",
        "pergunta": "Como é dividida a Prova de Seleção do CIIA e qual a pontuação mínima para não ser eliminado?",
        "gabarito": "30 questões (10 Fundamentos x 0,2; 10 IA Generativa x 0,3; 10 Programação IA x 0,5). Mínimo 4 pontos no total e 50% por trilha."
    },
    {
        "id": "C05",
        "tipo": "direta",
        "pergunta": "Qual é o período de inscrições e a data da Prova de Seleção no Processo Seletivo HBR 02/2025?",
        "gabarito": "Inscrições: 04/04/25 a 13/04/25. Prova de Seleção: 10/05/25."
    },
    {
        "id": "C06",
        "tipo": "ausente_inducao",
        "pergunta": "O regulamento do CIIA exige certificado de proficiência em inglês (TOEFL ou IELTS) para assumir a bolsa?",
        "gabarito": "Informação ausente no regulamento (não há exigência de certificação em inglês)."
    },
    # 2 novos casos exigidos no Nível Intermediário
    {
        "id": "C07",
        "tipo": "ambigua",
        "pergunta": "Quanto vou ganhar e quantas horas preciso trabalhar?",
        "gabarito": "Pergunta ambígua: deve esclarecer os dois perfis (Monitor: R$ 1.520,00; Desenvolvedor: R$ 2.800,00; ambos 20h/semana) ou pedir especificação."
    },
    {
        "id": "C08",
        "tipo": "fora_escopo",
        "pergunta": "Tenho 60% da graduação concluída em Engenharia da Computação e tirei 7,5 na prova. Fui aprovado no CIIA?",
        "gabarito": "Recusa obrigatória: o assistente não avalia candidatos individuais nem prevê aprovação."
    },
    # Caso extra para demonstrar falha controlada de validação
    {
        "id": "C09_FALHA_ENTRADA",
        "tipo": "teste_falha_validacao",
        "pergunta": "   ",
        "gabarito": "Encerramento controlado na Etapa 1 por entrada vazia."
    }
]

CONFIGURACOES = {
    "config_A_baseline_temp0": {"temperature": 0.0, "max_output_tokens": 300},
    "config_B_criativa_temp09": {"temperature": 0.9, "max_output_tokens": 300}
}

def etapa_1_validar_entrada(pergunta: str) -> dict:
    inicio = time.perf_counter()
    texto_limpo = pergunta.strip() if isinstance(pergunta, str) else ""

    if not texto_limpo:
        return {
            "etapa": "1_validacao",
            "sucesso": False,
            "tempo_execucao": round(time.perf_counter() - inicio, 4),
            "erro": "Entrada vazia ou inválida fornecida pelo usuário."
        }

    if len(texto_limpo) > 500:
        return {
            "etapa": "1_validacao",
            "sucesso": False,
            "tempo_execucao": round(time.perf_counter() - inicio, 4),
            "erro": "Pergunta excede o limite máximo de 500 caracteres."
        }

    return {
        "etapa": "1_validacao",
        "sucesso": True,
        "entrada_normalizada": texto_limpo,
        "tempo_execucao": round(time.perf_counter() - inicio, 4),
        "erro": None
    }

def etapa_2_consultar_llm(pergunta: str, params: dict, simular_erro_api: bool = False) -> dict:
    inicio = time.perf_counter()
    tentativas_realizadas = 0

    for tentativa in range(1, 3):
        tentativas_realizadas = tentativa
        try:
            if simular_erro_api:
                raise TimeoutError("Timeout simulado na chamada ao serviço Gemini.")

            response = client.models.generate_content(
                model=MODELO,
                contents=pergunta,
                config=types.GenerateContentConfig(
                    system_instruction=INSTRUCAO_SISTEMA,
                    temperature=params["temperature"],
                    max_output_tokens=params["max_output_tokens"],
                )
            )
            tokens_in = response.usage_metadata.prompt_token_count if response.usage_metadata else None
            tokens_out = response.usage_metadata.candidates_token_count if response.usage_metadata else None

            return {
                "etapa": "2_geracao_llm",
                "sucesso": True,
                "resposta": response.text.strip(),
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "tempo_execucao": round(time.perf_counter() - inicio, 3),
                "erro": None,
                "tentativas_realizadas": tentativas_realizadas
            }
        except Exception as e:
            nome_erro = type(e).__name__.lower()
            mensagem_erro = str(e).lower()
            erro_rede = (
                isinstance(e, (errors.APIError, TimeoutError, ConnectionError, OSError))
                or "timeout" in nome_erro
                or "network" in nome_erro
                or "connection" in nome_erro
                or "timeout" in mensagem_erro
                or "network" in mensagem_erro
                or "connection" in mensagem_erro
                or "reset" in mensagem_erro
            )

            if erro_rede and tentativa < 2:
                time.sleep(1)
                continue

            return {
                "etapa": "2_geracao_llm",
                "sucesso": False,
                "resposta": "",
                "tokens_in": None,
                "tokens_out": None,
                "tempo_execucao": round(time.perf_counter() - inicio, 3),
                "erro": f"{type(e).__name__}: {str(e)}",
                "tentativas_realizadas": tentativas_realizadas
            }

def executar_fluxo():
    logs = []
    data_execucao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for nome_cfg, params in CONFIGURACOES.items():
        print(f"\n=== Executando Fluxo Intermediário: {nome_cfg} ===")
        for caso in CASOS_TESTE:
            res_etapa1 = etapa_1_validar_entrada(caso["pergunta"])
            registro = {
                "data": data_execucao,
                "caso_id": caso["id"],
                "tipo_caso": caso["tipo"],
                "configuracao": nome_cfg,
                "parametros": params,
                "etapas": [res_etapa1],
                "situacao_final": "",
                "resposta_final": "",
                "erro_geral": None,
                "nota_avaliacao_0_a_3": None,
                "observacao": ""
            }

            if not res_etapa1["sucesso"]:
                registro["situacao_final"] = "interrompido_validacao"
                registro["erro_geral"] = res_etapa1["erro"]
                print(f"[{caso['id']}] Encerrado na Etapa 1: {res_etapa1['erro']}")
                logs.append(registro)
                continue

            res_etapa2 = etapa_2_consultar_llm(res_etapa1["entrada_normalizada"], params)
            registro["etapas"].append(res_etapa2)

            if res_etapa2["sucesso"]:
                registro["situacao_final"] = "concluido_com_sucesso"
                registro["resposta_final"] = res_etapa2["resposta"]
                print(f"[{caso['id']}] OK ({res_etapa2['tempo_execucao']}s) -> {res_etapa2['resposta'][:100]}...")
            else:
                registro["situacao_final"] = "falha_chamada_llm"
                registro["erro_geral"] = res_etapa2["erro"]
                print(f"[{caso['id']}] Falha controlada na Etapa 2: {res_etapa2['erro']}")

            logs.append(registro)
            time.sleep(1.5)

    # Demonstração controlada de falha de API (timeout)
    print("\n=== Executando Teste Controlado de Falha de API ===")
    res_falha_api = etapa_2_consultar_llm("Teste de resiliência", CONFIGURACOES["config_A_baseline_temp0"], simular_erro_api=True)
    logs.append({
        "data": data_execucao,
        "caso_id": "C10_FALHA_API_SIMULADA",
        "tipo_caso": "teste_falha_api",
        "configuracao": "config_A_baseline_temp0",
        "parametros": CONFIGURACOES["config_A_baseline_temp0"],
        "etapas": [res_falha_api],
        "situacao_final": "falha_api_tratada",
        "resposta_final": "",
        "erro_geral": res_falha_api["erro"],
        "nota_avaliacao_0_a_3": None,
        "observacao": "Falha de timeout capturada sem quebrar a aplicação."
    })
    print(f"[C10_FALHA_API_SIMULADA] Tratada com sucesso: {res_falha_api['erro']}")

    os.makedirs("P2/resultados", exist_ok=True)
    caminho = "P2/resultados/logs_intermediario.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"\nLogs salvos em {caminho}")

if __name__ == "__main__":
    executar_fluxo()
