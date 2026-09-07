function aoEditarColunaE(e) {
  var range = e.range;
  var sheet = range.getSheet();
  var row = range.getRow();
  var col = range.getColumn();

  // =====================
  // EDIÇÃO NA COLUNA E
  // =====================
  if (col === 5 && row >= 3) {
    var novoValor = range.getValue();
    if (novoValor !== "" && novoValor != null) {
      try {
        // 1. Inserir data/hora na coluna F
        sheet.getRange(row, 6)
          .setValue(new Date())
          .setNumberFormat("dd/MM/yyyy HH:mm:ss");

        // 2. Criar/atualizar checkbox na coluna G
        var celulaG = sheet.getRange(row, 7);
        var validacao = celulaG.getDataValidation();
        var temCheckbox = false;

        if (validacao) {
          var criterio = validacao.getCriteriaType();
          if (criterio === SpreadsheetApp.DataValidationCriteria.CHECKBOX) {
            temCheckbox = true;
          }
        }

        if (!temCheckbox) {
          var regraCheckbox = SpreadsheetApp.newDataValidation()
            .requireCheckbox()
            .build();
          celulaG.setDataValidation(regraCheckbox);
        }

        // Desmarca o checkbox (define como FALSE), mas NÃO altera a coluna H
        celulaG.setValue(false);

        // 3. Altera a cor da aba para laranja (indica pendência)
        sheet.setTabColor("#FFA500");

        // 4. Envia e-mail de notificação
        var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
        var nomePlanilha = spreadsheet.getName();
        var nomeAba = sheet.getName();
        var dataHora = new Date();
        var usuario = e.user || "Desconhecido";
        var linkCelula = spreadsheet.getUrl() + "#gid=" + sheet.getSheetId() + "&range=E" + row;

        var assunto = "Atualização SOE - PEI's: " + nomeAba;
        var corpo = "Edição realizada:\n\n" +
                    "Planilha: " + nomePlanilha + "\n" +
                    "Aba/Página: " + nomeAba + "\n" +
                    "Linha: " + row + "\n" +
                    "Novo valor: " + novoValor + "\n" +
                    "Data/Hora: " + dataHora.toLocaleString("pt-BR") + "\n" +
                    "Usuário: " + usuario + "\n" +
                    "Link para a célula: " + linkCelula;

        MailApp.sendEmail({
          to: "alberto.bernardo@-----",
          subject: assunto,
          body: corpo
        });

        console.log(
          "Alteração em " + nomeAba +
          " - E" + row +
          " - Data/Hora em F" + row +
          " - Checkbox desmarcado em G" + row +
          " - Coluna H preservada" +
          " - Cor da aba alterada para laranja" +
          " - E-mail enviado" +
          " - " + new Date()
        );

      } catch (error) {
        console.log("Erro na linha " + row + ": " + error.toString());
      }
    }
  }

  // =====================
  // EDIÇÃO NA COLUNA G (checkboxes)
  // =====================
  if (col === 7 && row >= 3) {
    try {
      var valorCheckbox = range.getValue(); // true ou false
      var colunaH = sheet.getRange(row, 8);

      if (valorCheckbox === true) {
        // Checkbox marcado → registra a data (somente dia) na coluna H
        var hoje = new Date();
        var dataFormatada = Utilities.formatDate(hoje, Session.getScriptTimeZone(), "dd/MM/yyyy");
        colunaH.setValue(dataFormatada);
      } else if (valorCheckbox === false) {
        // Checkbox desmarcado → remove a data da coluna H
        colunaH.clearContent();
      }

      // Após alterar o checkbox, verifica se todas as caixas estão marcadas
      verificarCorAba(sheet);

      console.log(
        "Checkbox alterado em " + sheet.getName() +
        " - G" + row +
        " - Valor: " + valorCheckbox +
        " - " + new Date()
      );

    } catch (error) {
      console.log("Erro ao processar coluna G, linha " + row + ": " + error.toString());
    }
  }
}

/**
 * Verifica todas as caixas de seleção da coluna G (a partir da linha 3).
 * Se todas estiverem marcadas (TRUE), remove a cor laranja da aba.
 * Caso contrário, mantém ou define a cor laranja.
 */
function verificarCorAba(sheet) {
  var lastRow = sheet.getLastRow();
  if (lastRow < 3) return; // não há linhas suficientes

  // Intervalo da coluna G, linhas 3 até lastRow
  var rangeG = sheet.getRange(3, 7, lastRow - 2, 1);
  var valoresG = rangeG.getValues();
  var validacoesG = rangeG.getDataValidations();

  var todasMarcadas = true;
  var existeCheckbox = false;

  for (var i = 0; i < valoresG.length; i++) {
    var valor = valoresG[i][0];
    var validacao = validacoesG[i][0];

    // Verifica se a célula possui validação do tipo CHECKBOX
    if (validacao && validacao.getCriteriaType() === SpreadsheetApp.DataValidationCriteria.CHECKBOX) {
      existeCheckbox = true;
      // Se alguma não estiver marcada (TRUE), então não estão todas
      if (valor !== true) {
        todasMarcadas = false;
        break;
      }
    }
  }

  if (existeCheckbox) {
    if (todasMarcadas) {
      // Remove a cor (sem cor = sem pendências)
      sheet.setTabColor(null);
      console.log("Todas as checkboxes marcadas. Cor removida da aba " + sheet.getName());
    } else {
      // Mantém a cor laranja (ainda há pendências)
      sheet.setTabColor("#FFA500");
      console.log("Ainda há checkboxes não marcadas. Cor laranja mantida na aba " + sheet.getName());
    }
  }
  // Se não houver checkboxes, não altera a cor
}
