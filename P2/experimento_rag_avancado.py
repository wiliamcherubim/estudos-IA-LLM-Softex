import os
import glob
import math
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
MODELO_LLM = "gemini-3.5-flash-lite"
MODELO_EMBEDDING = "gemini-embedding-001"

CONFIG_RECOMENDADA = {
    "nome": "config_A_baseline_temp0",
    "temperature": 0.0,
    "max_output_tokens": 350
}

INSTRUCAO_SEM_RAG = (
    "Você é um assistente informativo do Processo Seletivo HBR 02/2025 "
    "(Centro Integrado de Inteligência Artificial - CIIA). "
    "Responda de forma clara e objetiva. Se não dispuser da informação oficial exata, "
    "declare explicitamente que não possui dados suficientes e não invente regras, valores ou datas."
)

INSTRUCAO_COM_RAG = (
    "Você é um assistente informativo do Processo Seletivo HBR 02/2025 "
    "(Centro Integrado de Inteligência Artificial - CIIA). "
    "Responda EXCLUSIVAMENTE com base nos TRECHOS OFICIAIS fornecidos no contexto. "
    "Cite a fonte/seção utilizada na resposta. "
    "Se a resposta não estiver nos trechos fornecidos, declare explicitamente: "
    "'Não encontrei base documental suficiente nos trechos consultados para responder a esta pergunta.' "
    "Nunca invente informações ou utilize conhecimento externo."
)

CASOS_COMPARACAO_RAG = [
    {
        "id": "C01",
        "tipo": "direta",
        "repetir_3x": True,
        "pergunta": "Quantas vagas existem para desenvolvedores de soluções no CIIA e qual o valor mensal da bolsa?",
        "gabarito": "20 vagas para desenvolvedores; bolsa de R$ 2.800,00 mensais (20h/semana)."
    },
    {
        "id": "C02",
        "tipo": "combinada",
        "repetir_3x": False,
        "pergunta": "Não sou estudante de graduação nem pós-graduação. Posso me inscrever no processo seletivo HBR 02/2025?",
        "gabarito": "Sim, em caráter de excepcionalidade, comprovando pelo menos 2 anos de atuação acadêmica ou profissional em áreas tecnológicas correlatas."
    },
    {
        "id": "C03",
        "tipo": "combinada_calculo",
        "repetir_3x": True,
        "pergunta": "Como é calculada a nota final para classificação dos 100 primeiros candidatos e quais são os critérios de desempate?",
        "gabarito": "NOTA = (0,7 x PS) + (0,3 x FS). Desempate: 1º Programação para IA; 2º IA Generativa."
    },
    {
        "id": "C05",
        "tipo": "direta_cronograma",
        "repetir_3x": False,
        "pergunta": "Qual é o período de inscrições e a data da Prova de Seleção no Processo Seletivo HBR 02/2025?",
        "gabarito": "Inscrições: 04/04/25 a 13/04/25. Prova de Seleção: 10/05/25."
    },
    {
        "id": "C06",
        "tipo": "ausente_inducao",
        "repetir_3x": True,
        "pergunta": "O regulamento do CIIA exige certificado de proficiência em inglês (TOEFL ou IELTS) para assumir a bolsa?",
        "gabarito": "Informação ausente no regulamento (deve recusar e declarar falta de base documental)."
    }
]

def gerar_embedding(texto: str) -> list[float]:
    res = client.models.embed_content(
        model=MODELO_EMBEDDING,
        contents=texto
    )
    return res.embeddings[0].values

def similaridade_cosseno(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

def construir_indice_vetorial(pasta_corpus: str = "P2/corpus") -> list[dict]:
    indice = []
    arquivos = sorted(glob.glob(os.path.join(pasta_corpus, "*.md")))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo .md encontrado em {pasta_corpus}")

    for caminho in arquivos:
        nome_arquivo = os.path.basename(caminho)
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()

        linhas = conteudo.splitlines()
        cabecalho_fonte = linhas[0] if linhas else nome_arquivo
        corpo = "\n".join(linhas[1:]) if len(linhas) > 1 else conteudo

        # Divide por títulos (# ou ##) ou blocos separados por linha em branco dupla
        import re
        secoes = [s.strip() for s in re.split(r"\n(?=#+\s)", corpo) if s.strip()]
        if len(secoes) <= 1:
            secoes = [s.strip() for s in corpo.split("\n\n") if len(s.strip()) > 40]

        for idx, secao in enumerate(secoes, start=1):
            titulo_secao = secao.splitlines()[0].replace("#", "").strip()[:80]
            vetor = gerar_embedding(secao)
            indice.append({
                "chunk_id": f"{nome_arquivo}::S{idx}",
                "arquivo": nome_arquivo,
                "fonte_metadado": cabecalho_fonte,
                "secao": titulo_secao,
                "texto": secao,
                "embedding": vetor
            })
            time.sleep(0.3)

    print(f"Índice vetorial construído com {len(indice)} chunks semânticos.")
    return indice

def recuperar_trechos(pergunta: str, indice: list[dict], top_k: int = 3, limiar_minimo: float = 0.25) -> list[dict]:
    vetor_pergunta = gerar_embedding(pergunta)
    ranqueados = []
    for chunk in indice:
        score = similaridade_cosseno(vetor_pergunta, chunk["embedding"])
        if score >= limiar_minimo:
            ranqueados.append({
                "chunk_id": chunk["chunk_id"],
                "arquivo": chunk["arquivo"],
                "secao": chunk["secao"],
                "similaridade": round(score, 4),
                "texto": chunk["texto"]
            })
    ranqueados.sort(key=lambda x: x["similaridade"], reverse=True)
    return ranqueados[:top_k]


def consultar_llm(pergunta: str, trechos: list[dict] | None) -> dict:
    inicio = time.perf_counter()
    if trechos is None:
        instrucao = INSTRUCAO_SEM_RAG
        prompt = pergunta
    else:
        instrucao = INSTRUCAO_COM_RAG
        if not trechos:
            contexto_str = "[NENHUM TRECHO RELEVANTE RECUPERADO]"
        else:
            blocos = [
                f"[Fonte: {t['arquivo']} | Seção: {t['secao']} | Similaridade: {t['similaridade']}]\n{t['texto']}"
                for t in trechos
            ]
            contexto_str = "\n\n---\n\n".join(blocos)
        prompt = f"TRECHOS OFICIAIS DO REGULAMENTO:\n{contexto_str}\n\nPERGUNTA DO CANDIDATO:\n{pergunta}"

    response = client.models.generate_content(
        model=MODELO_LLM,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=instrucao,
            temperature=CONFIG_RECOMENDADA["temperature"],
            max_output_tokens=CONFIG_RECOMENDADA["max_output_tokens"]
        )
    )
    latencia = round(time.perf_counter() - inicio, 3)
    tokens_in = response.usage_metadata.prompt_token_count if response.usage_metadata else None
    tokens_out = response.usage_metadata.candidates_token_count if response.usage_metadata else None

    return {
        "resposta": response.text.strip(),
        "latencia_segundos": latencia,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out
    }

def executar_experimento_avancado():
    indice = construir_indice_vetorial()
    resultados = []
    data_exec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for condicao in ["SEM_RAG", "COM_RAG"]:
        print(f"\n================ CONDIÇÃO: {condicao} ================")
        for caso in CASOS_COMPARACAO_RAG:
            total_repeticoes = 3 if caso["repetir_3x"] else 1
            for rep in range(1, total_repeticoes + 1):
                trechos = recuperar_trechos(caso["pergunta"], indice) if condicao == "COM_RAG" else None
                res_llm = consultar_llm(caso["pergunta"], trechos)

                fontes_usadas = [f"{t['arquivo']} ({t['secao']})" for t in trechos] if trechos else []
                print(f"[{caso['id']} | Rep {rep}/{total_repeticoes} | {condicao}] Lat: {res_llm['latencia_segundos']}s | Tokens: {res_llm['tokens_in']}/{res_llm['tokens_out']}")
                print(f"Resposta: {res_llm['resposta'][:130]}...\n")

                resultados.append({
                    "data": data_exec,
                    "caso_id": caso["id"],
                    "tipo_caso": caso["tipo"],
                    "condicao": condicao,
                    "repeticao": rep,
                    "configuracao": CONFIG_RECOMENDADA,
                    "pergunta": caso["pergunta"],
                    "gabarito_referencia": caso["gabarito"],
                    "trechos_recuperados": trechos if trechos is not None else [],
                    "fontes_apresentadas": fontes_usadas,
                    "resposta": res_llm["resposta"],
                    "latencia_segundos": res_llm["latencia_segundos"],
                    "tokens_in": res_llm["tokens_in"],
                    "tokens_out": res_llm["tokens_out"],
                    "avaliacao_recuperacao": "",
                    "avaliacao_uso_contexto": "",
                    "nota_qualidade_0_a_3": None
                })
                time.sleep(4.5)

    os.makedirs("P2/resultados", exist_ok=True)
    caminho = "P2/resultados/resultados_avancado_rag.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"Experimento Avançado salvo em {caminho}")

if __name__ == "__main__":
    executar_experimento_avancado()
