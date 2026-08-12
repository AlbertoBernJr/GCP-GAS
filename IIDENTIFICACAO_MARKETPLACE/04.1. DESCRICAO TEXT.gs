/** 
 * =============================================================================
 * SISTEMA DE CONCILIAÇÃO FUZZY - DOCUMENTAÇÃO COMPLETA
 * =============================================================================
 * Versão: F16 - Otimizada (Performance F12 + Correções F15)
 * Objetivo: Identificar alunos no banco de dados externo utilizando busca
 *           aproximada (fuzzy) com CPF, nomes, telefones e data de nascimento,
 *           incluindo diferenciação robusta de irmãos e priorização de
 *           responsáveis financeiros.
 * 
 * Autor: Sistema de Conciliação Automatizada
 * Última Atualização: 2026
 * =============================================================================
 * 
 * SUMÁRIO:
 * 1. Visão Geral do Sistema
 * 2. Arquitetura e Gerenciamento de Recursos
 * 3. Normalização e Limpeza de Dados
 * 4. Detecção Inteligente de Tipos de Dados
 * 5. Algoritmo de Similaridade Fuzzy
 * 6. Sistema de Pontuação e Tiers (Atualizado)
 * 7. Mecanismo de Diferenciação de Irmãos (Reforçado)
 * 8. Processamento em Chunks (com Limpeza Inicial)
 * 9. Estrutura de Dados
 * 10. Geração de Relatório Final
 * 11. Fluxo Completo de Execução
 * 12. Exemplos Práticos (Incluindo Data de Nascimento)
 * 
 * =============================================================================
 * 1. VISÃO GERAL DO SISTEMA
 * =============================================================================
 * 
 * O script resolve a correspondência entre uma planilha de origem (aba "F3")
 * e um banco externo de alunos ("IDENTIFICACAO_MARKETPLACE"). Além das
 * funcionalidades anteriores, esta versão incorpora a DATA DE NASCIMENTO
 * como critério de desempate, reconhece CPFs diretamente no intervalo de
 * dados (I:N) e estabelece uma hierarquia clara entre CPF do responsável
 * financeiro e CPF do aluno.
 * 
 * NOVIDADES DA VERSÃO F16:
 * - Limpeza automática do intervalo Q2:Y antes da primeira execução.
 * - Cópia das colunas E→X e D→Y (antes apenas A→V e F→W).
 * - Separação e uso de CPFs encontrados no intervalo I:N.
 * - Comparação com a coluna X (data de nascimento) do banco externo.
 * - Nova função de similaridade de sobrenomes (calcularSimilaridadeSobrenome).
 * - Tiers reorganizados com subdivisões para CPF de responsável, irmãos por
 *   sobrenome e match por data de nascimento.
 * 
 * =============================================================================
 * 2. ARQUITETURA E GERENCIAMENTO DE RECURSOS
 * =============================================================================
 * 
 * 2.1 ORIENTAÇÃO A OBJETOS
 * Toda a lógica está encapsulada na classe `ConciliadorFuzzy`, garantindo
 * isolamento de estado e evitando conflitos com outros scripts.
 * 
 * 2.2 PROCESSAMENTO EM CHUNKS
 * Para contornar o limite de 6 minutos do Apps Script:
 * - Tempo máximo configurado: 4,5 minutos.
 * - Estado salvo via `PropertiesService`.
 * - Gatilho automático (`continuarProcessamentoF3`) agenda nova execução
 *   após 30 segundos de pausa.
 * 
 * 2.3 MEMÓRIA DE ESTADO
 * Propriedades utilizadas:
 * - `F3_LINHA_ATUAL`        : última linha processada.
 * - `F3_COPIAS_REALIZADAS`  : evita recopiar colunas.
 * - `F3_LIMPEZA_REALIZADA`  : evita limpar Q2:Y repetidamente.
 * 
 * 2.4 LIMPEZA INICIAL DO INTERVALO DE SAÍDA
 * Na primeira execução (quando a flag `F3_LIMPEZA_REALIZADA` não existe),
 * o intervalo Q2:Y é totalmente limpo, garantindo que resíduos de execuções
 * anteriores não interfiram nos resultados.
 * 
 * =============================================================================
 * 3. NORMALIZAÇÃO E LIMPEZA DE DADOS
 * =============================================================================
 * 
 * 3.1 normalizarTexto(texto)
 * Padroniza nomes:
 * - Converte para minúsculas.
 * - Remove acentos (NFD + regex).
 * - Mantém apenas letras e números.
 * - Remove preposições ('da','de','do','das','dos').
 * - Remove espaços extras.
 * 
 * 3.2 normalizarNumero(valor)
 * Extrai apenas dígitos. Ignora valores como "0" ou "00".
 * 
 * 3.3 normalizarData(valor)
 * Remove todos os caracteres não numéricos da data, gerando uma string
 * pura de dígitos (ex.: "1234567") para comparação exata.
 * 
 * =============================================================================
 * 4. DETECÇÃO INTELIGENTE DE TIPOS DE DADOS
 * =============================================================================
 * 
 * O intervalo I:N da aba F3 pode conter nomes, telefones, CPFs e datas de
 * aniversário misturados. As funções de classificação agora incluem CPF:
 * 
 * 4.1 isCPF(valor)
 * Retorna verdadeiro se o valor contiver exatamente 11 dígitos (CPF sem
 * formatação ou mascarado).
 * 
 * 4.2 isTelefone(valor)
 * Verdadeiro para valores com 8 a 11 dígitos, desde que não sejam CPF
 * (a verificação de CPF é feita antes).
 * 
 * 4.3 isDataAniversario(valor)
 * Detecta datas por:
 * - Presença de "/" ou "-" e padrão DD/MM/AAAA (flexível).
 * - Sequência de 7 ou 8 dígitos sem separadores (ex.: 15031990).
 * 
 * 4.4 isNome(valor)
 * Verdadeiro se houver letras, não for uma sequência puramente numérica
 * e não contiver barras.
 * 
 * 4.5 separarDadosIntervalo(intervalo)
 * Processa as 6 células (I a N) e retorna:
 * {
 *   nomes:     [...],   // palavras classificadas como nome
 *   telefones: [...],   // números de 8-11 dígitos (excluindo CPF)
 *   cpfs:      [...],   // números com exatamente 11 dígitos
 *   datas:     [...],   // padrões de data
 *   ignorados: [...]    // demais valores (ex.: "vestibular")
 * }
 * 
 * =============================================================================
 * 5. ALGORITMO DE SIMILARIDADE FUZZY
 * =============================================================================
 * 
 * Além dos métodos já existentes (Jaccard de palavras, Bigramas e Inclusão
 * Parcial), a versão F16 introduz uma nova métrica focada em sobrenomes.
 * 
 * 5.1 ÍNDICE DE JACCARD (PALAVRAS COMUNS)
 * Exemplo: "davi XXX" vs "alicia DDDD" → 1 palavra comum de 2 → score 0.5
 * 
 * 5.2 COMPARAÇÃO DE BIGRAMAS (SORENSEN-DICE)
 * Eficaz para capturar pequenos erros de digitação.
 * 
 * 5.3 INCLUSÃO PARCIAL
 * Se um nome é substring do outro, atribui 0.95.
 * 
 * 5.4 PENALIZAÇÃO POR PRIMEIRO NOME (mantida da F13)
 * Se a primeira palavra do nome buscado não tem correspondência razoável
 * (exata, mesmo prefixo ou bigramas ≥ 0.7) no banco, o score é multiplicado
 * por 0.3. Essa penalização continua sendo crucial para evitar confundir
 * irmãos com o mesmo sobrenome.
 * 
 * 5.5 SIMILARIDADE DE SOBRENOMES (NOVA)
 * `calcularSimilaridadeSobrenome(str1, str2)`:
 * - Extrai todas as palavras após a primeira, ignorando preposições.
 * - Calcula a proporção de sobrenomes comuns em relação ao total de
 *   sobrenomes distintos.
 * - Ex.: "davi reis pantoja" vs "alicia reis pantoja" → sobrenomes ["reis","pantoja"]
 *   em ambos → score 1.0.
 * 
 * =============================================================================
 * 6. SISTEMA DE PONTUAÇÃO E TIERS (ATUALIZADO)
 * =============================================================================
 * 
 * 6.1 COMPOSIÇÃO DA PONTUAÇÃO
 * scoreCombinadoNomes = (scoreAluno * 10) + scoreResp
 *                       + (50 se bateu telefone)
 *                       + (30 se bateu data de nascimento)
 * 
 * 6.2 TABELA DE TIERS
 * 
 * ┌─────────┬───────────────────────────────────────────┬───────────────┐
 * │  Tier   │ Condição                                  │ Pontuação Base│
 * ├─────────┼───────────────────────────────────────────┼───────────────┤
 * │ 1       │ CPF bateu + Nome Aluno ≥ 0.65             │ 10000         │
 * │ 1B      │ CPF Responsável bateu + Nome Resp ≥ 0.65  │ 9000          │
 * │ 2       │ CPF bateu + Sobrenome ≥ 0.70 + Aluno<0.65 │ 2000          │
 * │ 2B      │ CPF Responsável bateu (match fraco)       │ 1800          │
 * │ 2C      │ CPF Aluno bateu (match fraco)             │ 1500          │
 * │ 2D      │ CPF bateu + nomes muito diferentes        │ 1000          │
 * │ 3       │ Sem CPF, Aluno≥0.75 e Resp≥0.75           │ 5000          │
 * │ 3B      │ Sem CPF, Aluno≥0.75 + Data nasc. bateu    │ 4800          │
 * │ 4       │ Sem CPF, só Nome Aluno ≥ 0.75             │ 500           │
 * │ 4B      │ Sem CPF, Sobrenome≥0.70 + Data bateu      │ 450           │
 * │ 4C      │ Sem CPF, Sobrenome ≥ 0.70                 │ 400           │
 * │ 5       │ Sem CPF, Nome Responsável ≥ 0.85          │ 50            │
 * │ 6       │ Sem CPF, apenas Telefone bateu            │ 25            │
 * └─────────┴───────────────────────────────────────────┴───────────────┘
 * 
 * A pontuação final sempre adiciona o `scoreCombinadoNomes`, garantindo
 * desempate fino entre registros do mesmo tier.
 * 
 * =============================================================================
 * 7. MECANISMO DE DIFERENCIAÇÃO DE IRMÃOS (REFORÇADO)
 * =============================================================================
 * 
 * Problema: Um CPF de responsável financeiro pode pertencer a vários irmãos.
 * A versão F16 agora combina três camadas de proteção:
 * 
 * 7.1 Penalização do Primeiro Nome
 * Se o primeiro nome não é compatível, o score cai drasticamente (×0.3),
 * impedindo que sobrenomes em comum levem a um falso Tier 1.
 * 
 * 7.2 Similaridade de Sobrenome
 * Quando a penalização age, o sistema ainda pode identificar que são irmãos
 * por meio da alta similaridade de sobrenomes. Nesse caso, o match é
 * classificado como Tier 2 ou 4B/4C, dependendo da presença de CPF.
 * 
 * 7.3 Hierarquia de CPFs
 * Na busca, o CPF do responsável financeiro (coluna K do banco) tem
 * prioridade sobre o CPF do aluno. Assim, se um registro trouxer o CPF do
 * responsável, o sistema primeiro tenta associá-lo ao aluno correto via
 * nome; se falhar, ainda reconhece que pertence à família (Tier 2B).
 * 
 * =============================================================================
 * 8. PROCESSAMENTO EM CHUNKS (COM LIMPEZA INICIAL)
 * =============================================================================
 * 
 * 8.1 FLUXO DO CHUNK
 * 1. Verifica se a limpeza do intervalo Q2:Y já foi feita; se não, executa.
 * 2. Realiza a cópia das colunas fixas (A→V, F→W, E→X, D→Y) uma única vez.
 * 3. Carrega o banco externo.
 * 4. Lê as colunas B-N a partir da linha atual.
 * 5. Para cada linha:
 *    a. Extrai CPF da coluna C e valor de fallback da coluna G.
 *    b. Separa os dados do intervalo I:N com `separarDadosIntervalo`.
 *    c. Filtra palavras ignoradas ("vestibular", "ano", "serie").
 *    d. Valida telefones (≥8 dígitos).
 *    e. Combina todos os CPFs disponíveis (coluna C + CPFs do intervalo).
 *    f. Chama `buscarMelhorMatch` passando todos os parâmetros.
 *    g. Escreve o resultado nas colunas Q, R, S, T.
 * 6. Se o tempo limite for atingido, salva a linha atual e agenda continuação.
 * 7. Ao final de todos os dados, gera o relatório final.
 * 
 * 8.2 CONTROLE DE FLAGS
 * - `F3_LIMPEZA_REALIZADA`: evita limpar Q:Y repetidamente.
 * - `F3_COPIAS_REALIZADAS`: evita recopiar colunas.
 * - `F3_LINHA_ATUAL`: retoma o processamento de onde parou.
 * 
 * =============================================================================
 * 9. ESTRUTURA DE DADOS
 * =============================================================================
 * 
 * 9.1 PLANILHA F3 (ENTRADA - Leitura colunas B-N)
 * ┌────────┬──────────────────────────────────────────────┐
 * │ Coluna │ Conteúdo                                     │
 * ├────────┼──────────────────────────────────────────────┤
 * │   B    │ (não utilizado diretamente)                  │
 * │   C    │ CPF principal de busca                       │
 * │   D    │ (será copiado para Y)                        │
 * │   E    │ (será copiado para X)                        │
 * │   F    │ (será copiado para W)                        │
 * │   G    │ Valor de FALLBACK (exibido se nada encaixar) │
 * │   H    │ (não utilizado)                              │
 * │ I - N  │ Nomes, telefones, CPFs e datas misturados    │
 * └────────┴──────────────────────────────────────────────┘
 * 
 * 9.2 PLANILHA F3 (SAÍDA - Escrita colunas Q-T, V-Y)
 * ┌────────┬──────────────────────────────────────────────┐
 * │ Coluna │ Conteúdo                                     │
 * ├────────┼──────────────────────────────────────────────┤
 * │   Q    │ RA do aluno (ou fallback)                    │
 * │   R    │ Nome do aluno                                │
 * │   S    │ CPF do aluno                                 │
 * │   T    │ CPF do Responsável Financeiro                │
 * │   V    │ Cópia da coluna A                            │
 * │   W    │ Cópia da coluna F                            │
 * │   X    │ Cópia da coluna E                            │
 * │   Y    │ Cópia da coluna D                            │
 * └────────┴──────────────────────────────────────────────┘
 * 
 * 9.3 BANCO EXTERNO (IDENTIFICACAO_MARKETPLACE)
 * Além das colunas já mapeadas na versão F13, a coluna X (índice 23)
 * agora é lida como data de nascimento do aluno.
 * 
 * 9.4 OBJETO DE ITEM DO BANCO (atualizado)
 * {
 *   resM, resN, resAL, resT,
 *   alunoNomeNorm,
 *   dataNascimentoNorm,          // ← NOVO
 *   nomesParaBusca,
 *   respNomesNorm,
 *   telefonesParaBusca,
 *   cpfsNorm                    // agora contém CPF aluno + CPF resp fin
 * }
 * 
 * =============================================================================
 * 10. GERAÇÃO DE RELATÓRIO FINAL
 * =============================================================================
 * 
 * A aba "FINAL" é gerada ao término do processamento, consolidando os
 * resultados sem duplicatas. As colunas de origem (Q-AB) incluem agora
 * os campos copiados (V, W, X, Y) além dos resultados principais.
 * 
 * A montagem final seleciona e reorganiza os campos relevantes para
 * gerar uma visão limpa e ordenada.
 * 
 * =============================================================================
 * 11. FLUXO COMPLETO DE EXECUÇÃO (ATUALIZADO)
 * =============================================================================
 * 
 * 1. `iniciarConciliacaoF3()` limpa gatilhos e propriedades.
 * 2. `processarEmChunks()`:
 *    a. Se primeira execução, limpa Q2:Y.
 *    b. Copia colunas fixas (V, W, X, Y) uma vez.
 *    c. Carrega banco externo.
 *    d. Itera sobre as linhas:
 *       - Separa dados do intervalo I:N (nomes, telefones, cpfs, datas).
 *       - Combina CPFs.
 *       - Chama `buscarMelhorMatch` com todos os critérios.
 *       - Preenche Q, R, S, T.
 *       - Controla tempo; se excedido, salva estado e agenda trigger.
 *    e. Ao final, chama `finalizarProcessamento`.
 * 3. `finalizarProcessamento()`:
 *    - Remove flags e gatilhos.
 *    - Chama `gerarRelatorioFinal()` para criar a aba "FINAL".
 * 
 * =============================================================================
 * 12. EXEMPLOS PRÁTICOS (ATUALIZADOS)
 * =============================================================================
 * 
 * EXEMPLO 1: MATCH PERFEITO COM CPF E DATA
 * F3: CPF "XXXXXXX", nome "Davi Pantoja", data "DD/DD/DDDD"
 * Banco: mesmo CPF e nome, data "XXXXX".
 * Resultado: Tier 1 (CPF + nome), com bônus de data incluso no score.
 * 
 * EXEMPLO 2: IRMÃO DETECTADO POR SOBRENOME E CPF DO RESPONSÁVEL
 * F3: CPF do responsável "XXXXXXX", nome "Alícia Pantoja".
 * Banco: CPF responsável igual, nome do aluno "Davi Pantoja".
 * Penalização do primeiro nome reduz score. Similaridade de sobrenome = 1.0.
 * Classificação: Tier 2 (CPF_IRMAO_SOBRENOME).
 * 
 * EXEMPLO 3: MATCH POR DATA DE NASCIMENTO SEM CPF
 * F3: sem CPF, nome "Davi", data "DD/DD/DDDD".
 * Banco: nome "Davi Pantoja", data igual.
 * Score do nome pode não atingir 0.75, mas com data bateu, se o score for
 * suficiente poderá entrar no Tier 3B ou 4B.
 * 
 * EXEMPLO 4: FALLBACK
 * Nenhum critério atinge os thresholds. Valor da coluna G é exibido em Q,
 * e "AAAAAA" nas demais.
 * 
 * =============================================================================
 * FIM DA DOCUMENTAÇÃO - Versão F16
 * =============================================================================
 */
