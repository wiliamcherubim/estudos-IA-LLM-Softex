# Projeto P2 — Assistente Informativo com RAG (Processo Seletivo HBR 02/2025 - CIIA)

Avaliação experimental de configurações do modelo `gemini-3.5-flash-lite` e implementação de pipeline RAG (_Retrieval-Augmented Generation_) para responder dúvidas objetivas sobre o regulamento do Centro Integrado de Inteligência Artificial (CIIA).

## Estrutura da Pasta `P2/`

- `corpus/`: Documentos Markdown temáticos extraídos do regulamento oficial público (`regulamento-v-2.pdf`).
- `resultados/`: Arquivos JSON com os logs rastreáveis, latência, consumo de tokens e avaliações (`resultados_basico.json`, `logs_intermediario.json`, `resultados_avancado_rag.json`).
- `experimento_basico.py`: Comparação inicial sem RAG (`temperature` 0.0 vs. 0.9) em 6 casos (`p2-basico`).
- `fluxo_intermediario.py`: Fluxo modular em 2 etapas com validação, retry controlado e 8+ casos (`p2-intermediario`).
- `experimento_rag_avancado.py`: Pipeline completo de embeddings (`gemini-embedding-001`), busca por similaridade e comparação Sem RAG vs. Com RAG com 3 repetições (`p2-avancado`).
- `RELATORIO_EXECUCAO.md`: Relatório técnico consolidado com métricas, revisão da IDE agêntica e recomendação final.

## Como Executar

1. Instale as dependências na raiz do repositório: `pip install -r requirements.txt`
2. Configure sua chave `GEMINI_API_KEY` no arquivo `.env` na raiz.
3. Execute as etapas em ordem:
   - Básico: `python P2/experimento_basico.py`
   - Intermediário: `python P2/fluxo_intermediario.py`
   - Avançado (RAG): `python P2/experimento_rag_avancado.py`

## Vídeo de Demonstração

- Link do YouTube (Não listado): [INSERIR LINK DO VÍDEO APÓS GRAVAÇÃO]
  Inicio do projeto P2
