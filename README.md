# Curso de IA LLM - Softex Campinas

Este repositório contém as atividades e projetos desenvolvidos durante o curso de IA LLM.

## 📁 Estrutura do Repositório

- `P0/`: Primeiro fluxo com LLM (Extração de Pontos de Ação).
- `requirements.txt`: Dependências do Python necessárias para rodar o projeto.

---

## 🚀 P0 — Primeiro fluxo com LLM

### Visão Geral do Problema

**Problema:** Identificar e extrair pontos de ação (tarefas, responsáveis e prazos) a partir de transcrições textuais de reuniões de forma automatizada.
**Pergunta Motriz:** Como fazer um modelo de linguagem resolver um problema real, do zero, sem depender de um tutorial passo a passo?

### 🛠️ Como Executar o Projeto

#### 1. Pré-requisitos

Certifique-se de ter o Python instalado na sua máquina (recomendado Python 3.10+).

#### 2. Instalação das Dependências

Instale os pacotes necessários utilizando o arquivo de requerimentos:

```bash
pip install -r requirements.txt
```

#### 3. Configuração das Credenciais (Segurança)

O projeto utiliza a API do Google Gemini e protege as credenciais seguindo as boas práticas de desenvolvimento.

1. Crie um arquivo chamado `.env` na raiz do projeto.
2. Adicione sua chave de API gerada no Google AI Studio da seguinte forma:
   ```env
   GEMINI_API_KEY=sua_chave_aqui
   ```
   _(O arquivo `.env` está devidamente listado no `.gitignore` para evitar vazamentos de credenciais)._

#### 4. Execução do Script

Para rodar a aplicação e ver a extração acontecer no terminal, execute:

```bash
python P0/app.py
```
