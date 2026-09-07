# 📋 Resumo das Funcionalidades do Script

O script é composto por duas funções principais:

1. **`aoEditarColunaE(e)`** – gatilho que executa automaticamente sempre que uma célula é editada na planilha.
2. **`verificarCorAba(sheet)`** – função auxiliar que verifica o estado das caixas de seleção e ajusta a cor da aba.

---

## 🔹 Função `aoEditarColunaE(e)`

Esta função é disparada a cada edição de célula. Ela identifica em qual coluna ocorreu a alteração e age de acordo.

### ➤ Quando a edição é na **Coluna E** (coluna 5, linha ≥ 3, valor não vazio):

1. **Registra data/hora** na coluna **F** (formato `dd/MM/yyyy HH:mm:ss`), indicando quando a célula E foi modificada.
2. **Garante que a coluna G tenha uma caixa de seleção (checkbox)**:
   - Se ainda não existir, cria a validação de checkbox.
   - Depois, **desmarca** a caixa (define como `FALSE`), indicando que aquela linha ainda não foi conferida.
3. **Não altera a coluna H** – preserva qualquer valor existente (ex.: data de marcação anterior).
4. **Colore a aba da planilha de laranja** (`#FFA500`), sinalizando que há alguma pendência (checkbox não marcado).
5. **Envia um e-mail** para `alberto.bernardo@ ----` com:
   - Nome da planilha e da aba.
   - Linha editada.
   - Novo valor inserido na coluna E.
   - Data/hora da edição.
   - Usuário que realizou a alteração.
   - Link direto para a célula editada.

### ➤ Quando a edição é na **Coluna G** (coluna 7, linha ≥ 3) – ou seja, quando o usuário marca/desmarca a caixa de seleção:

1. **Se a checkbox for marcada (`TRUE`)**:
   - Insere a **data atual** (somente dia, formato `dd/MM/yyyy`) na coluna **H**.
2. **Se a checkbox for desmarcada (`FALSE`)**:
   - **Limpa** o conteúdo da coluna **H** (remove a data).
3. Após alterar a caixa, **chama a função `verificarCorAba(sheet)`** para reavaliar a cor da aba.

---

## 🔹 Função `verificarCorAba(sheet)`

Esta função é chamada sempre que uma checkbox da coluna G é modificada. Ela:

1. Identifica a última linha com dados na planilha.
2. Percorre **todas as células da coluna G** (da linha 3 até a última).
3. Considera apenas as células que possuem **validação do tipo checkbox**.
4. Verifica se **todas essas checkboxes estão marcadas** (`TRUE`):
   - **Se todas estiverem marcadas** → remove a cor da aba (define como `null`), indicando que não há mais pendências.
   - **Se houver pelo menos uma desmarcada** → mantém ou define a cor laranja, indicando que ainda existem itens pendentes.

Se não houver nenhuma checkbox na coluna G, a cor da aba não é alterada.

---

## ✅ Em resumo

- **Coluna E** → gera pendência: registra data/hora, desmarca checkbox, colore a aba de laranja e notifica por e‑mail.
- **Coluna G** → confirma pendência: ao marcar, registra a data em H; ao desmarcar, limpa H. Em seguida, verifica se todas as caixas estão marcadas para decidir se a aba deve voltar à cor normal ou continuar laranja.
