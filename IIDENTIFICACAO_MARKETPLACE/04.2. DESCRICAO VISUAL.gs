/**
 * =============================================================================
 * SISTEMA DE CONCILIAÇÃO FUZZY – VERSÃO F16 (VISUAL + DOCUMENTAÇÃO)
 * =============================================================================
 * 
 * DESCRIÇÃO VISUAL DO PROCESSO (DIAGRAMAS ASCII)
 * 
 *  1. VISÃO GERAL DA ARQUITETURA
 *  ─────────────────────────────
 *  
 *  +----------------------------+       +-----------------------------+       +----------------------------+
 *  |       PLANILHA F3          |       |      GOOGLE APPS SCRIPT     |       |       PLANILHA F3          |
 *  |   (Entrada: colunas B-N)   | ----> |      ConciliadorFuzzy      | ----> |   (Saída: Q,R,S,T,V,W,X,Y) |
 *  |                            |       |   (processamento em chunks) |       |                            |
 *  +----------------------------+       +-----------------------------+       +----------------------------+
 *                                                      |
 *                                                      | leitura
 *                                                      v
 *                                            +----------------------------+
 *                                            |   PLANILHA EXTERNA         |
 *                                            | IDENTIFICACAO_MARKETPLACE  |
 *                                            |       (colunas A:Z)        |
 *                                            +----------------------------+
 *  
 *  
 *  2. FLUXO DE DADOS NA ABA F3
 *  ───────────────────────────
 *  
 *  ENTRADA (B-N)                             PROCESSAMENTO                            SAÍDA (Q,R,S,T,V,W,X,Y)
 *  ┌─────────────────┐                   ┌───────────────────┐                   ┌─────────────────┐
 *  │ B (não usado)   │                   │                   │                   │ Q = RA / Fallback│
 *  │ C = CPF         │──────────────────>│                   │──────────────────>│ R = Nome Aluno   │
 *  │ D               │────────────┐      │                   │     ┌─────────────>│ S = CPF Aluno    │
 *  │ E               │────────┐   │      │   SEPARAÇÃO DOS   │     │ ┌───────────>│ T = CPF Resp Fin │
 *  │ F               │────┐   │   │      │   DADOS DO        │     │ │            │ V = Cópia de A  │
 *  │ G = Fallback    │    │   │   │      │   INTERVALO I:N   │     │ │            │ W = Cópia de F  │
 *  │ H               │    │   │   │      │   +               │     │ │            │ X = Cópia de E  │
 *  │ I,J,K,L,M,N     │────│───│───│──┐   │   FUZZY MATCH     │     │ │            │ Y = Cópia de D  │
 *  │  (nomes, tels,  │    │   │   │  │   │   +               │     │ │            └─────────────────┘
 *  │   CPFs, datas)  │    │   │   │  │   │   SISTEMA DE      │     │ │
 *  └─────────────────┘    │   │   │  │   │   TIERS           │     │ │
 *                         │   │   │  │   │                   │     │ │
 *                         │   │   │  │   └───────────────────┘     │ │
 *                         │   │   │  └─────────────────────────────┘ │
 *                         │   │   └──────────────────────────────────┘
 *                         │   └────────────────────────────────────── (cópia direta para Y)
 *                         └────────────────────────────────────────── (cópia direta para X)
 *                         (cópia direta para W)
 *                         (cópia direta para V)
 *  
 *  
 *  3. MACROFLUXO DO PROCESSAMENTO (CHUNKS + TRIGGERS)
 *  ─────────────────────────────────────────────────
 *  
 *                           INICIAR
 *                              |
 *                              v
 *                 +-------------------------+
 *                 | limpar gatilhos e       |
 *                 | propriedades anteriores |
 *                 +-------------------------+
 *                              |
 *                              v
 *                 +-------------------------+
 *                 |   processarEmChunks()   |
 *                 +-------------------------+
 *                              |
 *                              v
 *                 +-------------------------+
 *                 | Já processou tudo?      |
 *                 | (linhaAtual > ultima)   |
 *                 +-------------------------+
 *                    |               |
 *                  Sim             Não
 *                    |               |
 *                    v               v
 *          finalizarProcessamento   +----------------------------+
 *          (limpa flags,            | Primeira execução?         |
 *           gera aba FINAL)         | (limpeza Q2:Y)             |
 *                    |              +----------------------------+
 *                    v                            |
 *                  FIM                            v
 *                                    +----------------------------+
 *                                    | Copiar colunas fixas       |
 *                                    | (A->V,F->W,E->X,D->Y)     |
 *                                    +----------------------------+
 *                                                 |
 *                                                 v
 *                                    +----------------------------+
 *                                    | Carregar banco externo     |
 *                                    | (IDENTIFICACAO_MARKETPLACE)|
 *                                    +----------------------------+
 *                                                 |
 *                                                 v
 *                                    +----------------------------+
 *                                    | Ler bloco de dados (B-N)   |
 *                                    +----------------------------+
 *                                                 |
 *                                                 v
 *                                 ┌──────────────────────────────┐
 *                                 |  PARA CADA LINHA:            |
 *                                 └──────────────────────────────┘
 *                                                 |
 *                                                 v
 *                                 +-----------------------------+
 *                                 | Linha tem dados?            |
 *                                 +-----------------------------+
 *                                   |                  |
 *                                 Não                Sim
 *                                   |                  |
 *                                   v                  v
 *                        (fim dos dados)    +-----------------------------+
 *                                           | Extrair CPF (C), Fallback  |
 *                                           | (G) e intervalo I:N        |
 *                                           +-----------------------------+
 *                                                        |
 *                                                        v
 *                                           +-----------------------------+
 *                                           | separarDadosIntervalo()    |
 *                                           | → nomes, tels, cpfs, datas |
 *                                           +-----------------------------+
 *                                                        |
 *                                                        v
 *                                           +-----------------------------+
 *                                           | Filtrar palavras ignoradas |
 *                                           | e validar telefones        |
 *                                           +-----------------------------+
 *                                                        |
 *                                                        v
 *                                           +-----------------------------+
 *                                           | buscarMelhorMatch()        |
 *                                           | (compara com todo o banco) |
 *                                           +-----------------------------+
 *                                                        |
 *                                                        v
 *                                           +-----------------------------+
 *                                           | Escrever resultado em Q,R,S,T|
 *                                           +-----------------------------+
 *                                                        |
 *                                                        v
 *                                           +-----------------------------+
 *                                           | Tempo > 4,5 min?           |
 *                                           +-----------------------------+
 *                                             |                  |
 *                                            Não                Sim
 *                                             |                  |
 *                                             v                  v
 *                                       (próxima linha)   +----------------------+
 *                                                          | Salvar linha atual   |
 *                                                          | Agendar trigger 30s  |
 *                                                          +----------------------+
 *                                                                    |
 *                                                                    v
 *                                                          (execução pausa)
 *                                                                    |
 *                                                                    v
 *                                                      continuarProcessamentoF3()
 *                                                                    |
 *                                                                    v
 *                                                       (retoma o loop de linhas)
 *  
 *  
 *  4. ALGORITMO DE CLASSIFICAÇÃO DAS CÉLULAS (I:N)
 *  ─────────────────────────────────────────────
 *  
 *  Célula do intervalo I:N
 *          |
 *          v
 *  +-------------------+
 *  | É DATA?           |
 *  | (contém "/" "-"   |──Sim──>  LISTA DE DATAS
 *  | ou 7-8 dígitos)   |
 *  +-------------------+
 *          |
 *          Não
 *          v
 *  +-------------------+
 *  | É CPF?            |
 *  | (exatamente 11    |──Sim──>  LISTA DE CPFs
 *  |  dígitos)         |
 *  +-------------------+
 *          |
 *          Não
 *          v
 *  +-------------------+
 *  | É TELEFONE?       |
 *  | (8 a 11 dígitos,  |──Sim──>  LISTA DE TELEFONES
 *  | após descartar CPF)|
 *  +-------------------+
 *          |
 *          Não
 *          v
 *  +-------------------+
 *  | É NOME?           |
 *  | (contém letras,   |──Sim──>  LISTA DE NOMES
 *  | não é numérico)   |
 *  +-------------------+
 *          |
 *          Não
 *          v
 *      IGNORADO
 *  
 *  
 *  5. ÁRVORE DE DECISÃO DO MELHOR MATCH (SISTEMA DE TIERS)
 *  ─────────────────────────────────────────────────────
 *  
 *  Para cada item do banco externo:
 *  │
 *  ├─ CPF bateu? (qualquer CPF encontrado: coluna C + intervalo)
 *  │  │
 *  │  ├─ Sim ─ Qual CPF bateu?
 *  │  │   │
 *  │  │   ├─ Score Nome Aluno ≥ 0.65? ────→ Tier 1   "CPF e Aluno"         (base 10000)
 *  │  │   │
 *  │  │   ├─ CPF do Responsável + Score Nome Resp ≥ 0.65? ─→ Tier 1B  "CPF Resp + Nome Resp" (9000)
 *  │  │   │
 *  │  │   ├─ Sobrenome similar ≥ 0.70 e Nome Aluno < 0.65? ─→ Tier 2  "CPF Irmão/Sobrenome" (2000)
 *  │  │   │
 *  │  │   ├─ CPF do Responsável (sem match forte de nome) ─→ Tier 2B "CPF Responsável" (1800)
 *  │  │   │
 *  │  │   ├─ CPF do Aluno (sem match forte de nome) ──────→ Tier 2C "CPF Aluno"        (1500)
 *  │  │   │
 *  │  │   └─ Nenhuma das anteriores ─────────────────────→ Tier 2D "CPF Nomes Diferentes" (1000)
 *  │  │
 *  │  └─ Não (CPF não bateu)
 *  │      │
 *  │      ├─ Nome Aluno ≥ 0.75 e Nome Resp ≥ 0.75? ──→ Tier 3   "Nomes Aluno+Resp"    (5000)
 *  │      │
 *  │      ├─ Nome Aluno ≥ 0.75 e Data Nasc bateu? ────→ Tier 3B  "Nome Aluno + Data"   (4800)
 *  │      │
 *  │      ├─ Nome Aluno ≥ 0.75 (apenas) ──────────────→ Tier 4   "Nome Aluno"          (500)
 *  │      │
 *  │      ├─ Sobrenome ≥ 0.70 e Data bateu? ──────────→ Tier 4B  "Sobrenome + Data"    (450)
 *  │      │
 *  │      ├─ Sobrenome ≥ 0.70 (apenas) ───────────────→ Tier 4C  "Sobrenome"           (400)
 *  │      │
 *  │      ├─ Nome Responsável ≥ 0.85? ────────────────→ Tier 5   "Nome Responsável"    (50)
 *  │      │
 *  │      ├─ Telefone bateu? ─────────────────────────→ Tier 6   "Telefone"             (25)
 *  │      │
 *  │      └─ Nenhum ─────────────────────────────────→ SEM MATCH
 *  │
 *  └─ (escolhe sempre a maior pontuação final,
 *      adicionando bônus: scoreAluno*10 + scoreResp + 50 se tel + 30 se data)
 *  
 *  
 *  6. HIERARQUIA VISUAL DOS TIERS (PONTUAÇÃO BASE)
 *  ─────────────────────────────────────────────
 *  
 *  PONTUAÇÃO
 *     ^
 *     │
 *  10000 ──┐  Tier 1: CPF + Nome Aluno
 *   9000 ──┤  Tier 1B: CPF Resp + Nome Resp
 *   8000 ──┤
 *   7000 ──┤
 *   6000 ──┤
 *   5000 ──┤  Tier 3: Sem CPF, Aluno+Resp
 *   4800 ──┤  Tier 3B: Sem CPF, Aluno+Data
 *   4000 ──┤
 *   3000 ──┤
 *   2000 ──┤  Tier 2: CPF + Sobrenome Irmão
 *   1800 ──┤  Tier 2B: CPF Resp (fraco)
 *   1500 ──┤  Tier 2C: CPF Aluno (fraco)
 *   1000 ──┤  Tier 2D: CPF nomes diferentes
 *    500 ──┤  Tier 4: Sem CPF, só Aluno
 *    450 ──┤  Tier 4B: Sobrenome+Data
 *    400 ──┤  Tier 4C: Sobrenome
 *     50 ──┤  Tier 5: Sem CPF, só Resp
 *     25 ──┤  Tier 6: Só Telefone
 *      0 ──┴  (sem match)
 *  
 *  
 *  7. EXEMPLO VISUAL DE UM MATCH (IRMÃOS: DAVI vs ALÍCIA)
 *  ────────────────────────────────────────────────────
 *  
 *  Dados da F3 (linha única):
 *  ┌────────────────────────────────────────────┐
 *  │ C: CPF do responsável (XXXXXXXXXXX)        │
 *  │ G: "STATUS_OK"                             │
 *  │ I: "Alícia Pantoja"                        │
 *  │ J: "XXXXX"                                 │
 *  │ K: (vazio)                                 │
 *  │ L: (vazio)                                 │
 *  │ M: (vazio)                                 │
 *  │ N: (vazio)                                 │
 *  └────────────────────────────────────────────┘
 *           │
 *           ▼
 *  separarDadosIntervalo(I:N):
 *     nomes: ["Alícia Pantoja"]
 *     telefones: ["XXXXXX"]
 *     cpfs: []   (não há 11 dígitos)
 *     datas: []
 *           │
 *           ▼
 *  buscarMelhorMatch:
 *     CPF coluna C: XXXXX
 *     CPFs intervalo: (nenhum)
 *     CPFs totais: [XXXXXXXXXX]
 *  
 *     Para o item do banco "Davi Pantoja":
 *        CPF do resp (resT) = XXXX → BATE!
 *        Nome aluno: "davi xxxx pantoja"
 *        Nome busca: "alicia xxxx pantoja"
 *        Score similaridade:
 *           palavras comuns: XX, pantoja → 0.67
 *           penalização primeiro nome ("alicia" vs "davi") → 0.67 * 0.3 = 0.20
 *        Score Aluno = 0.20 (< 0.65)
 *        Sobrenome similar = 1.0 (≥ 0.70)
 *        Resultado: Tier 2 "CPF IRMAO SOBRENOME" (base 2000)
 *           + score combinado (0.20*10 + 0 + 50 do telefone) = +52
 *           = 2052
 *  
 *     Resultado final:
 *     ┌───────────────────────┐
 *     │ Q: RA do Davi         │
 *     │ R: "Davi Pantoja"│
 *     │ S: CPF Aluno (Davi)   │
 *     │ T: CPF Resp Financeiro│
 *     └───────────────────────┘
 *  
 * =============================================================================
 * DOCUMENTAÇÃO TEXTUAL COMPLETA (F16)
 * ... (aqui você pode manter ou resumir a explicação já existente)
 * =============================================================================
 */
