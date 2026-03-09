# 🤖 Byte — Assistente Virtual com Memória

Chatbot em Python integrado à API Groq, com controle de memória, persona definida, funções utilitárias e persistência de histórico.

---

## ▶️ Como Executar

### 1. Instale as dependências

```bash
pip install anthropic python-dotenv
```

### 2. Configure a chave da API

Crie um arquivo `.env` na raiz do projeto:

```
GROQ_API_KEY=sua_chave_aqui
```

### 3. Execute

```bash
python main.py
```

---

## 💡 Funcionalidades Implementadas

### Parte 1 — Controle de Memória
- Digite `/limpar` para apagar todo o histórico da conversa
- O assistente confirma: `"Memória da conversa apagada."`

### Parte 2 — Persona do Assistente
- O assistente se chama **Byte**
- Personalidade: descontraído, direto, levemente humorístico e sempre útil
- Definido via `system prompt` a cada chamada à API

### Parte 3 — Limite de Memória
- O histórico é limitado às **últimas 10 mensagens**
- Mensagens mais antigas são removidas automaticamente ao ultrapassar o limite

### Parte 4 — Integração de Funções Python
O LLM detecta a intenção do usuário e aciona automaticamente a função correta:

| Função | Exemplo de uso |
|---|---|
| `calcular_idade` | "Qual minha idade se nasci em 1995-03-20?" |
| `converter_temperatura` | "Converta 100 celsius para fahrenheit" |
| `calcular_imc` | "Meu IMC com 70kg e 1.75m?" |
| `gerar_senha` | "Gere uma senha de 16 caracteres" |

### Parte 5 — Persistência de Dados
- O histórico é salvo automaticamente em `historico.json` após cada mensagem
- Ao reiniciar o programa, o histórico anterior é carregado automaticamente

---

## 🗂️ Estrutura do Projeto

```
├── main.py          # Lógica principal do chatbot
├── tools.py         # Funções utilitárias Python
├── historico.json   # Histórico persistido (gerado automaticamente)
├── .env             # Chave da API (não versionar)
└── README.md
```

---

## 💭 Reflexões

### Se o histórico crescer muito, quais problemas podem ocorrer no uso de LLMs?

LLMs têm uma **janela de contexto limitada** (medida em tokens). Quando o histórico cresce demais:
- A API pode **rejeitar a requisição** por exceder o limite de tokens
- O **custo aumenta** proporcionalmente ao tamanho do contexto enviado
- A **latência** da resposta cresce, pois mais texto precisa ser processado
- O modelo pode ter dificuldade em **focar nas informações relevantes** (fenômeno de "lost in the middle")
- Em conversas muito longas, as instruções do system prompt podem ser "esquecidas" na prática

Por isso, estratégias como resumo de histórico, janela deslizante (as N últimas mensagens) ou embeddings para memória de longo prazo são essenciais em produção.

---

### Por que algumas tarefas são melhores resolvidas por funções Python do que pelo próprio LLM?

LLMs são modelos probabilísticos — eles **aproximam** respostas com base em padrões aprendidos, não executam cálculos deterministicamente. Isso significa:

- **Cálculos numéricos** (IMC, idade, conversões) podem conter erros de arredondamento ou enganos sutis quando feitos pelo LLM
- **Geração de senhas** requer aleatoriedade real — o LLM não tem acesso a um PRNG criptográfico
- **Datas e horários** dependem do momento real de execução, que o LLM não conhece
- Funções Python são **determinísticas, auditáveis e testáveis** — o LLM não é

A combinação ideal é: LLM para linguagem natural e tomada de decisão, funções Python para execução precisa.

---

### Quais riscos existem ao deixar que o LLM tome decisões sobre quando usar uma função?

- **Falsos positivos**: o LLM pode acionar uma função mesmo quando não foi pedido, interpretando mal a intenção
- **Falsos negativos**: o LLM pode tentar responder por conta própria em vez de acionar a função correta
- **Injeção de prompt**: usuários mal-intencionados podem tentar manipular o LLM para acionar funções com parâmetros indesejados
- **Extração incorreta de parâmetros**: o LLM pode extrair valores errados da mensagem (ex: confundir peso com altura)
- **Dependência de formato**: se o LLM não seguir exatamente o formato esperado (`[FUNÇÃO: ...]`), o parser falha silenciosamente

Mitigações: validação rigorosa dos parâmetros antes da execução, testes com casos-limite, e uso de `tool use` nativo da API quando disponível (mais confiável que parsing manual).
