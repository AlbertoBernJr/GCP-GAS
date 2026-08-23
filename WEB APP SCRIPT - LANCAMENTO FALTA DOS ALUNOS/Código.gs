function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Controle de Faltas')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function listarAlunos() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName('BD ALUNOS');
  const data = sheet.getDataRange().getValues();
  const alunos = [];

  for (let i = 1; i < data.length; i++) {
    const [ra, nome, turma, grade] = data[i];
    if (!ra) continue;

    alunos.push({
      ra: ra.toString(),
      nome: nome,
      turma: turma,
      grade: grade
    });
  }

  return alunos;
}

function registrarFaltas(listaRA) {
  if (!listaRA || listaRA.length === 0) {
    throw new Error('Nenhum aluno selecionado.');
  }

  const lock = LockService.getScriptLock();
  lock.waitLock(30000);

  try {
    const ss = SpreadsheetApp.getActive();
    const bdSheet = ss.getSheetByName('BD ALUNOS');
    const regSheet = ss.getSheetByName('REGISTROS');

    // Lê dados dos alunos
    const bdData = bdSheet.getDataRange().getValues();
    const mapaAlunos = new Map();

    for (let i = 1; i < bdData.length; i++) {
      const [ra, nome, turma, grade] = bdData[i];
      if (ra) {
        mapaAlunos.set(ra.toString(), {
          ra: ra.toString(),
          nome: nome,
          turma: turma,
          grade: grade
        });
      }
    }

    // Lê registros existentes para verificar duplicidade
    const regData = regSheet.getDataRange().getValues();
    const registrosExistentes = new Set();

    for (let i = 1; i < regData.length; i++) {
      const ra = regData[i][0] ? regData[i][0].toString() : '';
      const dia = regData[i][4];
      const mes = regData[i][5];
      const ano = regData[i][6];
      if (ra && dia && mes && ano) {
        registrosExistentes.add(`${ra}|${ano}-${mes}-${dia}`);
      }
    }

    // Captura data e hora atuais (servidor)
    const agora = new Date();
    const dia = agora.getDate();
    const mes = agora.getMonth() + 1;
    const ano = agora.getFullYear();
    const email = Session.getActiveUser().getEmail();
    const dataHoraRegistro = agora;

    const novasLinhas = [];
    const duplicados = [];

    listaRA.forEach(raOriginal => {
      const ra = raOriginal.toString();
      if (!mapaAlunos.has(ra)) {
        return; // RA não encontrado
      }

      const chave = `${ra}|${ano}-${mes}-${dia}`;
      if (registrosExistentes.has(chave)) {
        duplicados.push(ra);
        return;
      }

      const aluno = mapaAlunos.get(ra);
      novasLinhas.push([
        aluno.ra,
        aluno.nome,
        aluno.turma,
        aluno.grade,
        dia,
        mes,
        ano,
        email,
        dataHoraRegistro
      ]);
      registrosExistentes.add(chave);
    });

    if (novasLinhas.length > 0) {
      // ---- CORREÇÃO AQUI ----
      const linhasNecessarias = novasLinhas.length;
      const ultimaLinhaPreenchida = regSheet.getLastRow();
      const totalLinhasAtuais = regSheet.getMaxRows();
      const linhasVazias = totalLinhasAtuais - ultimaLinhaPreenchida;

      if (linhasVazias < linhasNecessarias) {
        const linhasFaltantes = linhasNecessarias - linhasVazias;
        // Insere linhas após a última linha preenchida
        regSheet.insertRowsAfter(ultimaLinhaPreenchida, linhasFaltantes);
      }

      // Agora a planilha tem espaço suficiente; grava tudo de uma vez
      const primeiraLinhaParaGravar = regSheet.getLastRow() + 1;
      regSheet
        .getRange(primeiraLinhaParaGravar, 1, novasLinhas.length, novasLinhas[0].length)
        .setValues(novasLinhas);
    }

    return {
      registrados: novasLinhas.length,
      duplicados: duplicados.length,
      totalSelecionados: listaRA.length
    };
  } finally {
    lock.releaseLock();
  }
}
