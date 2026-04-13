---
title: |-
  
  AI Engineering — Complete Concept Guide
author: Claude (Anthropic)
created: 2026-04-06
tags:
  - ai-engineering
  - llm
  - concepts
  - reference
  - obsidian
type: masterguide
status: complete
---

# 🧠 AI Engineering — Master Concept Guide

> A complete reference for every core concept an AI Engineer must know — with real input/output examples, mental models, and implementation notes.

---

## 📑 Table of Contents

1. [[#01 · Tokens & Tokenization]]
2. [[#02 · Context Window]]
3. [[#03 · Embeddings]]
4. [[#04 · Vector Databases]]
5. [[#05 · RAG — Retrieval Augmented Generation]]
6. [[#06 · Prompt Engineering]]
7. [[#07 · System Prompt]]
8. [[#08 · Temperature & Sampling Parameters]]
9. [[#09 · Few-Shot & Zero-Shot Learning]]
10. [[#10 · Chain of Thought (CoT)]]
11. [[#11 · Function Calling / Tool Use]]
12. [[#12 · Structured Output / JSON Mode]]
13. [[#13 · Streaming]]
14. [[#14 · Fine-Tuning]]
15. [[#15 · Agents & Agentic Loops]]
16. [[#16 · Multi-Agent Systems]]
17. [[#17 · Memory (Short, Long, Episodic)]]
18. [[#18 · Chunking Strategies]]
19. [[#19 · Semantic Search]]
20. [[#20 · Evaluation (Evals)]]
21. [[#21 · Guardrails & Safety Layers]]
22. [[#22 · Model Context Protocol (MCP)]]
23. [[#23 · Latency, Cost & Throughput Tradeoffs]]
24. [[#24 · Multimodality]]

---

## 01 · Tokens & Tokenization

```yaml
concept: Tokenization
category: fundamentals
difficulty: beginner
related: [context-window, embeddings, cost-optimization]
```

### 📖 What is it?

LLMs don't read words — they read **tokens**. A token is a chunk of text that the model's vocabulary recognizes. Tokens are neither characters nor words; they're learned sub-word units via algorithms like **BPE (Byte Pair Encoding)**.

### 🔢 Rules of Thumb

```yaml
english_word: ~1.3 tokens average
code: ~1 token per character (denser)
chinese_japanese: ~2–3 chars per token
whitespace_and_punctuation: separate tokens
```

### 📥 Input → 📤 Output Example

```yaml
input_text: "Hello, how are you?"
tokenized:
  - "Hello"     # token_id: 15339
  - ","         # token_id: 11
  - " how"      # token_id: 703
  - " are"      # token_id: 527
  - " you"      # token_id: 499
  - "?"         # token_id: 30
token_count: 6
```

```python
# Using tiktoken (OpenAI tokenizer) — same concept applies to Claude
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")

text = "Hello, how are you?"
tokens = enc.encode(text)
print(tokens)        # [15339, 11, 703, 527, 499, 30]
print(len(tokens))   # 6
```

### ⚠️ Why Engineers Care

```yaml
cost_model: pay_per_token (input + output)
context_limit: measured_in_tokens_not_words
performance: fewer_tokens = faster_response
prompt_engineering: compress_prompts_to_save_tokens
```

---

## 02 · Context Window

```yaml
concept: Context Window
category: fundamentals
difficulty: beginner
related: [tokens, memory, RAG, chunking]
```

### 📖 What is it?

The **context window** is the total number of tokens the model can "see" at once — both input (your prompt + history) and output (the response). Think of it as the model's working memory for a single call.

### 📊 Model Comparison

```yaml
models:
  GPT-4o:          128_000 tokens  (~96k words)
  Claude-3.7:      200_000 tokens  (~150k words)
  Gemini-1.5-Pro:  1_000_000 tokens
  Llama-3.1-405B:  128_000 tokens

token_to_word_ratio: ~0.75 (1 word ≈ 1.3 tokens)
```

### 📥 Input → 📤 Output Example

```yaml
scenario: "Exceeding context window"

input:
  system_prompt_tokens: 500
  conversation_history_tokens: 180_000
  new_user_message_tokens: 300
  total: 181_000

model_limit: 200_000

remaining_for_output: 19_000 tokens (~14k words)

# If total input > model_limit → Error or truncation
error_if_exceeded: "context_length_exceeded"
```

### 🛠️ Engineering Patterns

```yaml
strategies_when_context_is_full:
  1_sliding_window:    keep_last_N_messages_only
  2_summarization:     compress_old_turns_into_summary
  3_RAG:               don't_stuff_docs_in_context_retrieve_only_relevant
  4_trim_system_prompt: keep_system_prompt_concise
```

---

## 03 · Embeddings

```yaml
concept: Embeddings
category: representations
difficulty: intermediate
related: [vector-databases, semantic-search, RAG]
```

### 📖 What is it?

An **embedding** is a dense numerical vector that represents the *semantic meaning* of text. Similar meanings → similar vectors → small distance in vector space.

### 📥 Input → 📤 Output Example

```yaml
input: "The cat sat on the mat"

output_embedding:  # 1536-dimensional vector (text-embedding-3-small)
  - [0.0023, -0.0412, 0.0891, 0.0033, -0.1204, ..., 0.0067]
  # 1536 floats total

# Similarity comparison:
sentence_A: "The feline rested on the rug"
sentence_B: "Stock markets crashed yesterday"

cosine_similarity_A: 0.91  # Very similar meaning → close vectors
cosine_similarity_B: 0.07  # Very different meaning → far apart
```

```python
# Generate embedding using Anthropic / OpenAI
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="The cat sat on the mat"
)

vector = response.data[0].embedding
print(len(vector))   # 1536
print(vector[:5])    # [0.0023, -0.0412, 0.0891, ...]
```

### 🧮 Distance Metrics

```yaml
cosine_similarity:
  formula: "cos(θ) = A·B / (|A||B|)"
  range: [-1, 1]
  1:    identical_meaning
  0:    no_relation
  -1:   opposite_meaning
  use_case: semantic_search (most common)

euclidean_distance:
  use_case: clustering, k-means

dot_product:
  use_case: when vectors are normalized (same as cosine)
```

---

## 04 · Vector Databases

```yaml
concept: Vector Databases
category: infrastructure
difficulty: intermediate
related: [embeddings, RAG, semantic-search]
```

### 📖 What is it?

A **vector database** stores embeddings and enables fast **Approximate Nearest Neighbor (ANN)** search to find semantically similar content at scale. Regular SQL `WHERE` clauses don't work on 1536-dimensional vectors.

### 🏗️ Popular Options

```yaml
databases:
  Pinecone:
    type: fully_managed_cloud
    best_for: production, no_ops
    query_latency: ~10ms

  Weaviate:
    type: open_source + cloud
    best_for: hybrid_search (vector + keyword)

  pgvector:
    type: postgres_extension
    best_for: teams_already_on_postgres, simplicity
    query_latency: ~50ms (for millions of rows)

  Chroma:
    type: open_source, embeddable
    best_for: local_dev, prototypes

  Qdrant:
    type: open_source + cloud
    best_for: performance, rust_native
```

### 📥 Input → 📤 Output Example

```yaml
# --- WRITE ---
operation: upsert
input:
  id: "doc_001"
  vector: [0.0023, -0.0412, 0.0891, ...]  # 1536 dims
  metadata:
    text: "India charges 18% GST on SaaS services"
    source: "gst_guide_2024.pdf"
    page: 14

# --- READ (Semantic Search) ---
query_vector: [0.0021, -0.0398, 0.0876, ...]  # embedding of "What is GST on software?"
top_k: 3

output:
  results:
    - id: "doc_001"
      score: 0.94
      metadata:
        text: "India charges 18% GST on SaaS services"
    - id: "doc_089"
      score: 0.87
      metadata:
        text: "GST exemptions for export of software services"
    - id: "doc_034"
      score: 0.81
      metadata:
        text: "B2B SaaS invoicing requirements under GST"
```

```python
# pgvector example (Postgres)
# After: CREATE EXTENSION vector; and column type vector(1536)

query_vector = embed("What is GST on software?")

results = db.execute("""
  SELECT id, text, 1 - (embedding <=> %s::vector) AS similarity
  FROM documents
  ORDER BY embedding <=> %s::vector
  LIMIT 3
""", [query_vector, query_vector])
```

---

## 05 · RAG — Retrieval Augmented Generation

```yaml
concept: RAG (Retrieval Augmented Generation)
category: architecture_pattern
difficulty: intermediate
related: [embeddings, vector-databases, chunking, context-window]
```

### 📖 What is it?

**RAG** solves the problem of LLMs not knowing your private or recent data. Instead of fine-tuning, you:
1. **Retrieve** relevant chunks from a knowledge base at query time
2. **Augment** the prompt with those chunks
3. **Generate** a grounded response

### 🔄 RAG Pipeline

```yaml
pipeline:
  step_1_ingest:
    - load documents (PDF, HTML, MD, DB)
    - chunk into pieces (300–500 tokens)
    - embed each chunk
    - store in vector DB

  step_2_query:
    - embed user question
    - vector search → top-K chunks
    - inject chunks into prompt as context
    - call LLM → grounded response
```

### 📥 Input → 📤 Output Example

```yaml
user_question: "What is the tax rate for Indian salary income above ₹15L?"

# Step 1: Embed question, search vector DB
retrieved_chunks:
  - chunk_1: "Under new tax regime, income above ₹15 lakh is taxed at 30% flat."
  - chunk_2: "Old regime allows deductions under 80C, HRA, etc. reducing taxable base."

# Step 2: Augmented prompt sent to LLM
augmented_prompt: |
  You are a tax assistant. Use only the context below to answer.

  Context:
  [1] Under new tax regime, income above ₹15 lakh is taxed at 30% flat.
  [2] Old regime allows deductions under 80C, HRA, etc. reducing taxable base.

  Question: What is the tax rate for Indian salary income above ₹15L?

# Step 3: LLM Output
llm_response: |
  Under the new tax regime, income above ₹15 lakh is taxed at 30%.
  Under the old regime, the effective rate can be lower depending on
  deductions you claim under sections like 80C and HRA.
  Source: [1], [2]
```

### ⚡ RAG vs Fine-Tuning

```yaml
comparison:
  RAG:
    update_knowledge: real_time (just re-index)
    cost: low (no training)
    transparency: can_cite_sources
    best_for: dynamic / private knowledge bases

  Fine_Tuning:
    update_knowledge: requires_retraining
    cost: high (GPU compute)
    transparency: black_box
    best_for: teaching_style / format / domain_vocabulary
```

---

## 06 · Prompt Engineering

```yaml
concept: Prompt Engineering
category: core_skill
difficulty: beginner_to_advanced
related: [system-prompt, few-shot, chain-of-thought, structured-output]
```

### 📖 What is it?

**Prompt Engineering** is the craft of structuring text inputs to reliably get high-quality, specific outputs from an LLM. The model's behavior is almost entirely controlled by its input.

### 🧱 Anatomy of a Good Prompt

```yaml
structure:
  role:        "You are a senior Indian tax advisor..."
  context:     "The user is a startup founder with US C-Corp + India subsidiary..."
  task:        "Calculate TDS liability on salary of ₹25L/year"
  constraints: "Use only new tax regime. Show step-by-step workings."
  format:      "Return as JSON with fields: gross, tds_rate, tds_amount, net"
  examples:    (few-shot — see Section 09)
```

### 📥 Input → 📤 Output Examples

#### ❌ Bad Prompt

```yaml
input: "tell me about taxes"
output: |
  Taxes are mandatory financial charges imposed by governments...
  [3 generic paragraphs that help no one]
problem: vague → vague
```

#### ✅ Good Prompt

```yaml
input: |
  You are a CA specializing in Indian startup taxation.
  A founder pays an Indian employee ₹25,00,000 annual CTC.
  Calculate the monthly TDS to be deducted under the new tax regime.
  Show: slab breakdown, annual TDS, monthly TDS.
  Format: markdown table.

output: |
  | Income Slab        | Rate | Tax Amount  |
  |--------------------|------|-------------|
  | ₹0 – ₹3L          | 0%   | ₹0          |
  | ₹3L – ₹7L         | 5%   | ₹20,000     |
  | ₹7L – ₹10L        | 10%  | ₹30,000     |
  | ₹10L – ₹12L       | 15%  | ₹30,000     |
  | ₹12L – ₹15L       | 20%  | ₹60,000     |
  | ₹15L – ₹25L       | 30%  | ₹3,00,000   |
  | **Total Annual TDS** |    | **₹4,10,000** |
  | **Monthly TDS**      |    | **₹34,167**   |

  *Standard deduction of ₹75,000 applied. No surcharge (income < ₹50L).*
```

### 🔧 Key Techniques

```yaml
techniques:
  role_prompting:     "You are an expert in X" → activates domain knowledge
  positive_framing:   "Do X" better than "Don't do Y"
  output_anchoring:   "Return JSON with keys: a, b, c" → constrains format
  step_by_step:       "Think step by step" → improves reasoning accuracy
  persona_lock:       keep role consistent throughout system prompt
  delimiters:         use XML tags <context></context> to separate sections
```

---

## 07 · System Prompt

```yaml
concept: System Prompt
category: prompt_engineering
difficulty: beginner
related: [prompt-engineering, guardrails, persona]
```

### 📖 What is it?

The **system prompt** is a special, privileged message sent before the conversation begins. It sets the model's **persona, rules, capabilities, and constraints** for the entire session. Users typically cannot see it.

### 📥 Input → 📤 Output Example

```yaml
system_prompt: |
  You are TaxOS, an AI tax advisor for Indian startup founders.
  You specialize in US-India dual-jurisdiction tax compliance.

  Rules:
  - Always cite the relevant section of Income Tax Act or IRC
  - Never give a definitive legal opinion; recommend a CA for final sign-off
  - If asked about unrelated topics, redirect to tax and compliance
  - Respond in the same language the user writes in (Hindi or English)
  - Format monetary amounts in Indian notation (₹10,00,000 not ₹1,000,000)

user_message: "What is the TDS rate on salary?"

model_output: |
  Under Section 192 of the Income Tax Act, 1961, TDS on salary is
  computed at the applicable slab rates for the financial year.
  For FY 2025-26 under the new tax regime:
  - Up to ₹3L: Nil
  - ₹3L–₹7L: 5%
  - ₹7L–₹10L: 10%
  ...
  I'd recommend your CA verify this for your specific case.
```

### 🔐 System Prompt Best Practices

```yaml
do:
  - be_specific_about_persona_and_scope
  - define_output_format_expectations
  - list_explicit_rules_as_bullet_points
  - include_edge_case_handling
  - version_control_your_system_prompts

dont:
  - overload_with_conflicting_rules
  - assume_model_remembers_between_sessions
  - put_sensitive_secrets_in_system_prompt (not 100% safe)
  - make_it_too_long_without_testing (diminishing returns)
```

---

## 08 · Temperature & Sampling Parameters

```yaml
concept: Temperature & Sampling
category: model_parameters
difficulty: beginner
related: [prompt-engineering, structured-output, agents]
```

### 📖 What is it?

These parameters control the **randomness and diversity** of the model's output. They adjust how the model samples from its probability distribution over the next token.

### 🌡️ Temperature

```yaml
temperature:
  range: 0.0 → 2.0
  default: 1.0

  0.0:
    behavior: deterministic, always picks highest probability token
    use_case: structured_output, math, code, extraction
    example_output: "The TDS rate is 10% under Section 194J."

  0.3-0.5:
    behavior: focused but some variation
    use_case: factual Q&A, summarization

  0.7-0.9:
    behavior: balanced creativity
    use_case: writing, explanations, chatbots

  1.2-1.5:
    behavior: creative and diverse
    use_case: brainstorming, creative_writing

  2.0:
    behavior: near random, often incoherent
    use_case: rarely useful in production
```

### 📥 Input → 📤 Output Example

```yaml
prompt: "Name a creative startup idea"

temperature_0.0_output:
  - "An AI-powered personal finance manager"
  - "An AI-powered personal finance manager"   # same every time
  - "An AI-powered personal finance manager"

temperature_1.5_output:
  - "A subscription service that sends you rare fungi samples monthly"
  - "A peer-to-peer skill rental marketplace for 15-minute consultations"
  - "A micro-dosing tracker integrated with your wearable and therapist"
```

### Other Sampling Parameters

```yaml
top_p:
  aka: nucleus_sampling
  how: sample from tokens comprising top P% probability mass
  value_0.1: very focused (only high-prob tokens)
  value_0.9: broad sampling
  tip: tune temperature OR top_p, rarely both

top_k:
  how: sample from only top K tokens
  value_1: same as temperature=0 (greedy)
  value_40: common default

max_tokens:
  what: hard cap on output length
  tip: always set this to avoid runaway outputs + cost overruns

stop_sequences:
  what: tokens that stop generation when encountered
  example: ["</answer>", "###", "\n\nUser:"]
  use_case: structured_generation, multi-turn_control
```

---

## 09 · Few-Shot & Zero-Shot Learning

```yaml
concept: Few-Shot & Zero-Shot
category: prompt_engineering
difficulty: beginner
related: [prompt-engineering, fine-tuning]
```

### 📖 What is it?

- **Zero-shot**: Ask the model to do a task with no examples
- **Few-shot**: Show the model 2–5 examples of input→output, then give the real input

### 📥 Input → 📤 Output Examples

#### Zero-Shot

```yaml
input: |
  Classify the sentiment of this text as POSITIVE, NEGATIVE, or NEUTRAL.
  Text: "The product arrived late but the quality was excellent."

output: "POSITIVE"   # (reasonable, no examples needed)
```

#### Few-Shot

```yaml
input: |
  Classify the income type as: SALARY, BUSINESS, CAPITAL_GAINS, OTHER

  Examples:
  Text: "Monthly paycheck from TechCorp" → SALARY
  Text: "Sold 100 shares of Infosys" → CAPITAL_GAINS
  Text: "Invoice from my freelance client" → BUSINESS
  Text: "Rental income from my flat in Pune" → OTHER

  Now classify:
  Text: "Annual bonus from employer"

output: "SALARY"
```

### 📊 When to Use Each

```yaml
zero_shot:
  use_when: task is common / well-known to model
  examples: summarize, translate, explain

few_shot:
  use_when:
    - task has custom format or taxonomy
    - model keeps getting it wrong zero-shot
    - you have a specific output style requirement
  n_examples: 2–5 (more is often diminishing returns)

fine_tuning:
  use_when:
    - few-shot still not reliable enough
    - you have 100+ labeled examples
    - latency/cost of long few-shot prompts is a problem
```

---

## 10 · Chain of Thought (CoT)

```yaml
concept: Chain of Thought
category: reasoning
difficulty: intermediate
related: [prompt-engineering, agents, evaluation]
```

### 📖 What is it?

**Chain of Thought** is a prompting technique where you ask the model to *reason step-by-step* before giving a final answer. It dramatically improves accuracy on math, logic, and multi-step problems.

### 📥 Input → 📤 Output Example

#### Without CoT ❌

```yaml
input: |
  An employee earns ₹80,000/month. PF is 12% of basic (basic = 50% of CTC).
  What is the monthly PF contribution by employer?

output: "₹9,600"   # WRONG — rushed calculation
```

#### With CoT ✅

```yaml
input: |
  An employee earns ₹80,000/month. PF is 12% of basic (basic = 50% of CTC).
  What is the monthly PF contribution by employer?
  Think step by step.

output: |
  Step 1: Monthly CTC = ₹80,000
  Step 2: Basic salary = 50% of CTC = ₹80,000 × 0.50 = ₹40,000
  Step 3: Employer PF = 12% of Basic = ₹40,000 × 0.12 = ₹4,800
  Answer: The monthly employer PF contribution is ₹4,800.
```

### 🔧 CoT Variants

```yaml
variants:
  standard_CoT:
    trigger: "Think step by step" or "Let's reason through this"

  zero_shot_CoT:
    trigger: Just adding "Think step by step" — no examples needed

  few_shot_CoT:
    provide: 2-3 full worked examples with reasoning steps shown

  self_consistency_CoT:
    method: run same prompt N times → majority vote on final answer
    use_case: high-stakes decisions where one run isn't enough

  tree_of_thought:
    method: explore multiple reasoning branches, prune weak ones
    use_case: complex planning, creative problem solving
```

---

## 11 · Function Calling / Tool Use

```yaml
concept: Function Calling / Tool Use
category: agentic_AI
difficulty: intermediate
related: [agents, structured-output, MCP]
```

### 📖 What is it?

**Tool use** lets the LLM decide when to call an external function (API, database query, calculator) and with what arguments. The model doesn't *run* the function — it returns structured JSON telling *your code* what to call.

### 🔄 Flow

```yaml
flow:
  1: user asks question
  2: LLM decides → needs tool → returns tool_call JSON
  3: your code → executes the real function
  4: result → sent back to LLM as tool_result
  5: LLM → uses result to compose final answer
```

### 📥 Input → 📤 Output Example

```yaml
tools_defined:
  - name: get_gst_rate
    description: "Returns GST rate for a given product/service category"
    parameters:
      category:
        type: string
        description: "Product or service category (e.g., 'SaaS', 'Food', 'Pharma')"

user_message: "What GST do I charge on my SaaS product sold to Indian customers?"

# --- LLM Response (Turn 1) ---
llm_output:
  type: tool_call
  tool_name: get_gst_rate
  arguments:
    category: "SaaS"

# --- Your Code Executes ---
function_result:
  category: "SaaS"
  gst_rate: 18
  hsn_code: "9983"
  notes: "IT and ITES services under GST"

# --- LLM Response (Turn 2, with tool result) ---
final_output: |
  You should charge 18% GST on your SaaS product sold to Indian customers.
  This falls under HSN code 9983 (IT and ITES services).
  Add GST separately to your invoice: if your subscription is ₹10,000,
  the invoice total would be ₹11,800.
```

```python
# Anthropic Claude Tool Use
import anthropic

client = anthropic.Anthropic()

tools = [{
    "name": "get_gst_rate",
    "description": "Returns GST rate for a given category",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {"type": "string"}
        },
        "required": ["category"]
    }
}]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "GST on SaaS?"}]
)

# response.stop_reason == "tool_use" → extract and execute
```

---

## 12 · Structured Output / JSON Mode

```yaml
concept: Structured Output
category: output_control
difficulty: beginner
related: [function-calling, prompt-engineering, agents]
```

### 📖 What is it?

Force the model to return valid, parseable JSON (or XML/YAML) so your code can reliably process it. Essential for agents, pipelines, and any app that needs machine-readable output.

### 📥 Input → 📤 Output Example

```yaml
input_prompt: |
  Extract the following from this payslip text and return as JSON only.
  Fields: employee_name, gross_salary, tds_deducted, net_salary, month

  Text: "Payslip for Priya Sharma, July 2025. Gross: ₹85,000.
  TDS: ₹8,200. Net Pay: ₹76,800."

  Return ONLY valid JSON. No explanation. No markdown.

output: |
  {
    "employee_name": "Priya Sharma",
    "gross_salary": 85000,
    "tds_deducted": 8200,
    "net_salary": 76800,
    "month": "July 2025"
  }
```

### 🛠️ Implementation Patterns

```yaml
method_1_prompt_instruction:
  add_to_prompt: "Return ONLY valid JSON. No markdown. No explanation."
  reliability: ~85-90%
  limitation: model sometimes adds prose before/after JSON

method_2_json_mode:
  api_param: response_format = { type: "json_object" }  # OpenAI
  reliability: ~99%
  note: Claude uses tool_use pattern for guaranteed structure

method_3_tool_use_trick:
  define_tool: with your desired schema
  force_call: tool_choice = { type: "tool", name: "extract_data" }
  result: model MUST fill your exact schema
  reliability: ~100%

post_processing:
  - strip markdown fences: text.replace(/```json|```/g, '')
  - try/catch JSON.parse()
  - validate with Zod / Pydantic schema
```

---

## 13 · Streaming

```yaml
concept: Streaming
category: UX_and_performance
difficulty: beginner
related: [latency, agents, UI]
```

### 📖 What is it?

Instead of waiting for the full response (high latency), **streaming** sends tokens to the client as they're generated — like a typewriter effect. Critical for good UX.

### 📥 Input → 📤 Output Example

```yaml
without_streaming:
  user_sends_request: t=0ms
  model_generates_500_tokens: t=0ms to t=4000ms
  user_sees_anything: t=4000ms   ← 4 second blank wait

with_streaming:
  user_sends_request: t=0ms
  first_token_appears: t=300ms   ← user sees immediate response
  tokens_stream_in: every 20-50ms
  complete: t=4000ms
  perceived_latency: 300ms (10x better UX)
```

```javascript
// Anthropic streaming example
const stream = await anthropic.messages.stream({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Explain GST in India' }]
});

for await (const chunk of stream) {
  if (chunk.type === 'content_block_delta') {
    process.stdout.write(chunk.delta.text);  // print as it arrives
  }
}
```

### 📡 SSE (Server-Sent Events) Pattern

```yaml
client_to_server: POST /api/chat  (one request)
server_to_client: SSE stream  (chunked response)

SSE_event_format: |
  data: {"type":"content_block_delta","delta":{"text":"The"}}
  data: {"type":"content_block_delta","delta":{"text":" GST"}}
  data: {"type":"content_block_delta","delta":{"text":" rate"}}
  data: [DONE]

frontend_handling:
  - EventSource API (browser)
  - fetch() with ReadableStream
  - React: useState + useEffect to append tokens
```

---

## 14 · Fine-Tuning

```yaml
concept: Fine-Tuning
category: model_training
difficulty: advanced
related: [few-shot, RAG, evaluation]
```

### 📖 What is it?

**Fine-tuning** continues training a pre-trained model on your custom dataset to adapt it to your domain, style, or task. The model's weights are updated — unlike RAG or prompting which keep weights frozen.

### 📊 When to Fine-Tune

```yaml
fine_tune_when:
  - prompt_engineering_alone_not_reliable_enough
  - need_specific_output_style_consistently
  - domain_vocabulary_not_in_base_model
  - latency_cost_of_long_prompts_is_problem
  - classification_task_with_1000s_of_examples
  - have_100-10000_high_quality_labeled_examples

do_NOT_fine_tune_when:
  - knowledge_needs_to_stay_current (use RAG)
  - you_have_fewer_than_50_examples
  - the_task_works_fine_with_prompting
  - you_cant_afford_GPU_compute
```

### 📥 Input → 📤 Output (Training Data Format)

```yaml
# JSONL format — one example per line
training_data_example:

  row_1: |
    {
      "messages": [
        {"role": "system", "content": "You extract GST details from invoices"},
        {"role": "user", "content": "Invoice: TechCorp Pvt Ltd, ₹50,000 + 18% GST"},
        {"role": "assistant", "content": "{\"vendor\": \"TechCorp Pvt Ltd\", \"base\": 50000, \"gst_rate\": 18, \"gst_amount\": 9000, \"total\": 59000}"}
      ]
    }

  row_2: |
    {
      "messages": [
        {"role": "system", "content": "You extract GST details from invoices"},
        {"role": "user", "content": "Bill from WebHost India: ₹12,000 + IGST 18%"},
        {"role": "assistant", "content": "{\"vendor\": \"WebHost India\", \"base\": 12000, \"gst_rate\": 18, \"gst_amount\": 2160, \"total\": 14160}"}
      ]
    }

minimum_rows: 50  (recommended: 200–500 for reliable results)
```

### ⚙️ Fine-Tuning Parameters

```yaml
hyperparameters:
  learning_rate: 1e-5 to 1e-4  (lower = safer, less forgetting)
  epochs: 3-5  (more = overfitting risk)
  batch_size: 4-32

techniques:
  full_fine_tuning: update all weights (expensive)
  LoRA: update small adapter matrices only (cheap, popular)
  QLoRA: LoRA on quantized model (runs on consumer GPU)

cost_estimate_openai_gpt4o_mini:
  training: $0.003 per 1k tokens
  10k_examples_avg_200_tokens: ~$6 total
```

---

## 15 · Agents & Agentic Loops

```yaml
concept: AI Agents
category: agentic_AI
difficulty: advanced
related: [tool-use, memory, multi-agent, MCP]
```

### 📖 What is it?

An **agent** is an LLM that operates in a **loop**: it perceives, decides which tool to call, executes (via your code), observes the result, and continues until the task is complete. Unlike a single Q&A, agents handle multi-step tasks autonomously.

### 🔄 The ReAct Loop

```yaml
pattern: ReAct (Reason + Act)

loop:
  1_observe:  current state + user goal
  2_think:    "I need to check the GST rate first, then calculate the invoice total"
  3_act:      call tool (get_gst_rate, category="SaaS")
  4_observe:  tool returns 18%
  5_think:    "Now I can calculate: 50000 × 1.18 = 59000"
  6_respond:  final answer OR loop again if more steps needed
```

### 📥 Input → 📤 Output Example (Multi-step)

```yaml
user_goal: "File a zero-return GST for my company for October 2025"

agent_trace:
  turn_1:
    think: "I need to check if there are any invoices for October"
    act: search_invoices(month="Oct-2025")
    observe: "No invoices found for Oct 2025"

  turn_2:
    think: "Zero invoices → zero return. I need company GSTIN to proceed."
    act: get_company_details()
    observe: {gstin: "29ABCDE1234F1Z5", name: "AcmeTech Pvt Ltd"}

  turn_3:
    think: "All info ready. File the GSTR-1 nil return via GST portal API."
    act: file_gstr1(gstin="29ABCDE1234F1Z5", month="10-2025", invoices=[])
    observe: {arn: "AA290600123456", status: "Filed", timestamp: "2025-11-10T14:32:00"}

  final_response: |
    ✅ Nil GSTR-1 filed successfully for October 2025.
    ARN: AA290600123456 | Filed at: 2:32 PM, Nov 10, 2025.
```

### ⚠️ Agent Failure Modes

```yaml
failure_modes:
  infinite_loop:      agent keeps calling tools without converging
  tool_hallucination: agent calls non-existent tool names
  context_overflow:   long agentic run exhausts context window
  wrong_tool_args:    agent passes malformed arguments

mitigations:
  max_iterations: hard_cap (e.g., 15 turns)
  structured_tool_schemas: precise descriptions + types
  checkpointing: save state so user can inspect + resume
  human_in_the_loop: confirm before irreversible actions
```

---

## 16 · Multi-Agent Systems

```yaml
concept: Multi-Agent Systems
category: agentic_AI
difficulty: advanced
related: [agents, orchestration, MCP]
```

### 📖 What is it?

Instead of one LLM doing everything, **multi-agent systems** use specialized sub-agents coordinated by an orchestrator. Each agent has a focused role, tools, and system prompt.

### 🏗️ Architecture Patterns

```yaml
patterns:
  orchestrator_worker:
    orchestrator: decomposes task, routes to sub-agents
    workers: specialist agents (Researcher, Writer, Validator)

  pipeline:
    agent_1_output → agent_2_input → agent_3_input
    example: Extract → Validate → Format → File

  debate:
    agent_A: argues position 1
    agent_B: argues position 2
    judge_agent: evaluates and decides
    use_case: high-stakes decisions

  parallel:
    orchestrator: splits task into N independent subtasks
    N_agents: run simultaneously
    orchestrator: merges results
    use_case: research across multiple data sources
```

### 📥 Input → 📤 Output Example

```yaml
user_goal: "Prepare my company's annual tax compliance report"

orchestrator_plan:
  - agent_US_tax:    "Analyze US C-Corp obligations (1120, payroll)"
  - agent_India_tax: "Analyze India subsidiary obligations (ITR, TDS, GST)"
  - agent_transfer_pricing: "Check TP documentation requirements"
  - agent_formatter: "Merge all outputs into final PDF report"

parallel_execution:
  agent_US_tax_output:
    form_1120_due: "April 15, 2026"
    estimated_tax: "$12,400"
    state_filings: ["Delaware", "California"]

  agent_India_tax_output:
    itr_due: "October 31, 2025"
    tds_q3_due: "January 31, 2026"
    gst_monthly_filings: "current"

  agent_transfer_pricing_output:
    threshold_met: true
    form_3CEB_required: true
    deadline: "November 30, 2025"

orchestrator_merges_and_passes_to_formatter → PDF report generated
```

---

## 17 · Memory (Short, Long, Episodic)

```yaml
concept: LLM Memory Types
category: architecture
difficulty: intermediate
related: [context-window, RAG, agents, vector-databases]
```

### 📖 What is it?

LLMs are **stateless** — each API call starts fresh. "Memory" must be engineered explicitly using different storage strategies depending on what you want to remember and for how long.

### 🗂️ Four Memory Types

```yaml
memory_types:

  1_in_context_memory:
    what: conversation history injected into each prompt
    duration: current session only
    limit: context window size
    example: "Earlier you said you're a startup with 5 employees..."
    cost: tokens per turn

  2_external_memory_database:
    what: facts stored in DB, retrieved via semantic search (RAG)
    duration: persistent across sessions
    limit: storage size
    example: user preferences, past tax filings, entity details
    cost: embedding + vector search per query

  3_summarization_memory:
    what: compress old turns into summary, keep summary in context
    duration: session + across sessions if saved
    example: "In our last 3 conversations, you've asked about GST filings"
    tool: call LLM to summarize, store summary, inject at session start

  4_episodic_memory:
    what: key events/decisions stored with timestamps
    example: "Filed GSTR-1 for Q2 on 2025-10-12 | Result: Success"
    retrieval: recent N episodes OR semantic search
```

### 📥 Input → 📤 Output Example

```yaml
# Session Start — inject memory
system_prompt_with_memory: |
  You are TaxOS for Arpit Choudhary.

  Remembered context:
  - Company: AcmeTech Pvt Ltd (India subsidiary of US C-Corp)
  - GSTIN: 29ABCDE1234F1Z5
  - Last session: Filed GSTR-1 nil return for Oct 2025
  - Pending: TDS Q3 return due Jan 31, 2026
  - Preferred response style: concise with tables

user_message: "What should I do next for tax compliance?"

output: |
  Based on your profile, your most urgent item is:

  | Task               | Due Date       | Status  |
  |--------------------|----------------|---------|
  | TDS Q3 Return      | Jan 31, 2026   | Pending |
  | GSTR-3B (Dec)      | Jan 20, 2026   | Pending |

  Should I help you prepare the TDS Q3 workings?
```

---

## 18 · Chunking Strategies

```yaml
concept: Chunking
category: RAG_pipeline
difficulty: intermediate
related: [RAG, embeddings, vector-databases, context-window]
```

### 📖 What is it?

Before embedding documents, you must split them into chunks. **Chunk size and overlap** dramatically affect RAG quality — too small loses context, too large dilutes relevance.

### 📊 Chunking Strategies

```yaml
strategies:

  fixed_size:
    method: split every N characters/tokens
    chunk_size: 500 tokens
    overlap: 50 tokens  # prevents cutting mid-sentence
    pro: simple, predictable
    con: may cut mid-sentence, mid-thought

  recursive_character:
    method: split by paragraph → sentence → word (fallback)
    separators: ["\n\n", "\n", ". ", " "]
    pro: respects natural structure
    con: variable chunk sizes

  semantic:
    method: embed sentences, split when cosine similarity drops sharply
    pro: chunks are semantically coherent
    con: slower, more complex

  document_structure:
    method: use headers (H1/H2/H3) as chunk boundaries
    pro: preserves document logic
    con: requires structured documents (MD, HTML)

  agentic_chunking:
    method: ask LLM "what's the key proposition of this paragraph?"
    pro: highest quality, context-aware
    con: expensive (LLM call per paragraph)
```

### 📥 Input → 📤 Output Example

```yaml
input_document: |
  Section 3.2 — Employer PF Obligations
  Under the Employees' Provident Funds Act, 1952, every employer with 20+
  employees must register with EPFO. The employer contributes 12% of basic
  salary to EPF. Of this, 8.33% goes to EPS (pension) and 3.67% to EPF.
  Employee also contributes 12% of basic to EPF.

  Section 3.3 — ESIC Registration
  Employers with 10+ employees where any earns below ₹21,000/month must
  register with ESIC. Employer contributes 3.25% and employee 0.75% of
  gross wages.

chunked_output_recursive:
  chunk_1:
    text: |
      Section 3.2 — Employer PF Obligations
      Under the Employees' Provident Funds Act, 1952, every employer with 20+
      employees must register with EPFO. The employer contributes 12% of basic
      salary to EPF. Of this, 8.33% goes to EPS (pension) and 3.67% to EPF.
      Employee also contributes 12% of basic to EPF.
    tokens: 68
    metadata: {section: "3.2", topic: "PF"}

  chunk_2:
    text: |
      Section 3.3 — ESIC Registration
      Employers with 10+ employees where any earns below ₹21,000/month must
      register with ESIC. Employer contributes 3.25% and employee 0.75% of
      gross wages.
    tokens: 44
    metadata: {section: "3.3", topic: "ESIC"}
```

---

## 19 · Semantic Search

```yaml
concept: Semantic Search
category: retrieval
difficulty: intermediate
related: [embeddings, vector-databases, RAG]
```

### 📖 What is it?

**Semantic search** finds results based on *meaning*, not keyword matching. "Income tax on salary" and "TDS on employment" are semantically similar but share no keywords.

### 🔍 Semantic vs Keyword vs Hybrid

```yaml
keyword_search:
  method: BM25, TF-IDF, exact match
  query: "GST invoice"
  matches: documents containing the words "GST" and "invoice"
  misses: docs saying "goods & services tax bill" or "GSTIN receipt"

semantic_search:
  method: embed query → find nearest vectors
  query: "GST invoice"
  matches: documents about GST invoices even if worded differently
  misses: sometimes misses exact technical terms / codes

hybrid_search:
  method: weighted combination of BM25 + vector similarity
  formula: score = α × BM25_score + (1-α) × semantic_score
  α_typical: 0.5 to 0.7
  best_for: production RAG (catches both keyword + semantic matches)
```

### 📥 Input → 📤 Output Example

```yaml
query: "How much does the employer pay for social security in India?"

keyword_search_results:
  - "Social Security benefits for NRIs"    # keyword match but irrelevant
  - "Employee social security number"      # irrelevant

semantic_search_results:
  - "Employer PF contribution: 12% of basic salary"      # score: 0.91
  - "ESIC: Employer pays 3.25% of gross wages"           # score: 0.87
  - "Gratuity provision: 4.81% of basic salary"          # score: 0.79

# Semantic search correctly understands PF + ESIC = Indian social security
```

---

## 20 · Evaluation (Evals)

```yaml
concept: Evals (Evaluation)
category: quality_assurance
difficulty: intermediate
related: [fine-tuning, prompt-engineering, agents]
```

### 📖 What is it?

**Evals** are systematic tests to measure LLM output quality. Without evals, you're flying blind — you don't know if a prompt change made things better or worse.

### 📊 Eval Types

```yaml
eval_types:

  1_exact_match:
    method: output == expected_output
    use_case: classification, extraction, structured data
    example:
      input: "What is the TDS rate under 194J?"
      expected: "10%"
      pass_if: output.strip() == "10%"

  2_contains:
    method: expected_substring in output
    use_case: fact checking in long responses

  3_LLM_as_judge:
    method: ask another LLM to score the output 1-5
    use_case: open-ended responses, quality, tone
    judge_prompt: |
      Rate this tax advice for accuracy (1-5):
      Question: {question}
      Answer: {answer}
      Scoring rubric: 5=perfectly accurate, 1=factually wrong

  4_human_eval:
    method: human reviewers rate outputs
    gold_standard: true
    cost: highest
    use_case: final validation before production

  5_regression_suite:
    method: run N test cases before every deploy
    goal: ensure changes don't break existing functionality
```

### 📥 Input → 📤 Output Example

```yaml
eval_suite_example:

  test_cases:
    - id: tc_001
      input: "TDS rate on professional fees?"
      expected_contains: "10%"
      expected_section: "194J"
      result: PASS

    - id: tc_002
      input: "GST rate on SaaS"
      expected_contains: "18%"
      result: PASS

    - id: tc_003
      input: "Is PF mandatory for 15 employees?"
      expected: "No, mandatory above 20 employees"
      result: FAIL  ← model said "Yes" — prompt needs fixing

  summary:
    total: 50
    passed: 47
    failed: 3
    accuracy: 94%
    regression_vs_last_version: +2%
```

---

## 21 · Guardrails & Safety Layers

```yaml
concept: Guardrails
category: safety_and_reliability
difficulty: intermediate
related: [system-prompt, evaluation, agents]
```

### 📖 What is it?

**Guardrails** are programmatic or model-based checks that validate LLM inputs and outputs to prevent harmful, off-topic, or incorrect responses in production.

### 🏗️ Guardrail Architecture

```yaml
layers:
  L1_input_guardrail:
    runs: before LLM call
    checks:
      - topic relevance (is this a tax question?)
      - PII detection (don't log sensitive data)
      - prompt injection detection ("ignore previous instructions")
    action_on_fail: reject with message

  L2_LLM_system_prompt:
    runs: during LLM call
    checks: persona, scope, formatting rules
    action_on_fail: model self-corrects or refuses

  L3_output_guardrail:
    runs: after LLM call
    checks:
      - JSON schema validation
      - hallucination detection (does answer cite a real section?)
      - PII in output (mask before logging)
      - confidence threshold
    action_on_fail: retry OR fallback response

  L4_human_review:
    runs: async, for flagged outputs
    checks: spot review of low-confidence answers
```

### 📥 Input → 📤 Output Example

```yaml
# Input Guardrail — Topic Filter
input: "Write me a poem about love"
guardrail_check:
  topic_relevant: false
  category_detected: "creative_writing"
response: "I'm TaxOS, your tax compliance assistant. I can only help with tax, GST, payroll, and compliance questions. How can I help you with those today?"

# Output Guardrail — Schema Validation
llm_raw_output: |
  {
    "tds_rate": "ten percent",   ← string instead of number!
    "section": "194J"
  }
schema_check: FAIL (tds_rate must be number)
action: retry with note "Return tds_rate as a numeric value"
```

---

## 22 · Model Context Protocol (MCP)

```yaml
concept: Model Context Protocol (MCP)
category: integration_standard
difficulty: intermediate
related: [tool-use, agents, multi-agent]
```

### 📖 What is it?

**MCP** (by Anthropic) is an open standard that lets LLMs connect to external tools and data sources through a standardized protocol — like USB-C but for AI tools. Instead of custom integrations per tool, one MCP client connects to any MCP server.

### 🔌 Architecture

```yaml
components:
  MCP_Host:     your app / Claude Desktop / AI agent
  MCP_Client:   library that speaks MCP protocol
  MCP_Server:   exposes tools + resources (your database, Notion, GitHub, etc.)

communication: JSON-RPC 2.0 over stdio or HTTP/SSE

MCP_Server_exposes:
  tools:      callable functions (like tool_use)
  resources:  readable data sources (files, DB rows, API endpoints)
  prompts:    reusable prompt templates
```

### 📥 Input → 📤 Output Example

```yaml
# MCP Server: gst-portal-mcp
tools_exposed:
  - name: get_gst_filings
    description: "Fetch all GST filings for a GSTIN"
    params: {gstin: string, fy: string}

  - name: file_gstr1
    description: "File GSTR-1 return"
    params: {gstin: string, period: string, invoices: array}

# Claude calls via MCP:
mcp_request:
  tool: get_gst_filings
  params:
    gstin: "29ABCDE1234F1Z5"
    fy: "2025-26"

mcp_response:
  filings:
    - period: "Apr-25"
      status: "Filed"
      arn: "AA2904..."
    - period: "May-25"
      status: "Filed"
      arn: "AA2905..."
    - period: "Jun-25"
      status: "Not Filed"  ← flagged!
```

---

## 23 · Latency, Cost & Throughput Tradeoffs

```yaml
concept: Latency / Cost / Throughput
category: production_engineering
difficulty: intermediate
related: [streaming, fine-tuning, model-selection]
```

### 📊 Model Selection Matrix

```yaml
models_comparison:

  Claude_Haiku:
    latency: ~300ms first token
    cost: $0.25 / 1M input tokens
    quality: good
    use_case: classification, extraction, simple Q&A

  Claude_Sonnet:
    latency: ~500ms first token
    cost: $3 / 1M input tokens
    quality: very_good
    use_case: most production tasks, agents

  Claude_Opus:
    latency: ~1s first token
    cost: $15 / 1M input tokens
    quality: best
    use_case: complex reasoning, high-stakes decisions

  cost_optimization_strategies:
    - cache_static_system_prompts (prompt caching saves 90% on repeated prompts)
    - use_smaller_model_for_routing_and_classification
    - use_larger_model_only_for_final_answer
    - batch_API_for_non_realtime_workloads (50% discount, async)
    - compress_prompts (fewer tokens = lower cost)
```

### 📥 Input → 📤 Output: Cost Calculation

```yaml
scenario: "Process 10,000 tax invoices per day with extraction"

input_tokens_per_invoice: 300
output_tokens_per_invoice: 100
total_tokens_per_day: 10_000 × 400 = 4_000_000

cost_haiku:   4M × ($0.25/1M + $1.25/1M output) = ~$6/day
cost_sonnet:  4M × ($3/1M + $15/1M output) = ~$72/day
cost_opus:    4M × ($15/1M + $75/1M output) = ~$360/day

recommendation: Use Haiku for extraction (structured task) → $6/day
                Use Sonnet for complex advisory → selectively
```

---

## 24 · Multimodality

```yaml
concept: Multimodality
category: model_capabilities
difficulty: intermediate
related: [embeddings, RAG, structured-output]
```

### 📖 What is it?

Modern LLMs can process **multiple input types** beyond text: images, PDFs, audio, video. This opens up use cases like reading scanned documents, analyzing charts, or processing handwritten invoices.

### 🎯 Input Modalities

```yaml
modalities:
  text:    universal, all models
  images:  GPT-4o, Claude 3+, Gemini (JPEG, PNG, GIF, WebP)
  PDF:     Claude 3+ (natively), others via extraction
  audio:   Gemini 1.5, Whisper (transcription then text)
  video:   Gemini 1.5 Pro (frame sampling)
```

### 📥 Input → 📤 Output Example

```yaml
# Reading a scanned GST invoice image
input:
  type: image
  content: [base64 encoded scan of handwritten invoice]
  prompt: |
    Extract the following from this invoice image:
    - Vendor name
    - Invoice date
    - GSTIN of vendor
    - Line items with amounts
    - Total GST
    Return as JSON.

output: |
  {
    "vendor_name": "Raj Office Supplies",
    "invoice_date": "2025-11-05",
    "vendor_gstin": "27AABCR1234A1Z5",
    "line_items": [
      {"description": "A4 Paper Reams", "qty": 10, "rate": 250, "amount": 2500},
      {"description": "Ink Cartridges", "qty": 5, "rate": 800, "amount": 4000}
    ],
    "subtotal": 6500,
    "gst_rate": 18,
    "gst_amount": 1170,
    "total": 7670
  }

# This eliminates manual data entry from physical invoices!
```

---

## 🗺️ Concept Dependency Map

```yaml
learning_path:
  week_1_foundations:
    - tokens_and_tokenization
    - context_window
    - temperature_and_sampling
    - prompt_engineering
    - system_prompt

  week_2_retrieval:
    - embeddings
    - vector_databases
    - chunking_strategies
    - semantic_search
    - RAG

  week_3_reliability:
    - few_shot_learning
    - chain_of_thought
    - structured_output
    - streaming
    - evaluation

  week_4_production:
    - function_calling
    - fine_tuning
    - guardrails
    - latency_cost_tradeoffs
    - multimodality

  week_5_advanced:
    - agents
    - multi_agent_systems
    - memory
    - MCP
```

---

## 🔗 Quick Reference Card

```yaml
quick_reference:

  make_output_deterministic:   temperature: 0.0
  improve_reasoning:           add "think step by step"
  get_structured_JSON:         use tool_use + force schema
  handle_large_docs:           chunk → embed → RAG
  reduce_cost:                 use smaller model + cache prompts
  reduce_latency:              enable streaming
  add_realtime_knowledge:      RAG over updated vector DB
  customize_behavior:          system_prompt + fine-tuning
  connect_external_tools:      function_calling / MCP
  measure_quality:             build eval suite before deploying
  memory_across_sessions:      external DB + inject at session start
  run_complex_tasks:           agents with tool loop + max_iterations cap
```

---

*Generated by Claude · Anthropic · April 2026*
*For use in Obsidian — paste into any .md file*