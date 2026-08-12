/**
 * CLASSE: ConciliadorFuzzy
 * Versão: F16 - Otimizada (Performance F12 + Correções F15)
 */
class ConciliadorFuzzy {
  constructor() {
    this.ss = SpreadsheetApp.getActiveSpreadsheet();
    this.idPlanilhaExterna = "----";
    this.tempoMaximoMS = 4.5 * 60 * 1000; 
    this.inicioExecucao = Date.now();
  }

  normalizarTexto(texto) {
    if (!texto) return "";
    let textoProcessado = texto.toString().toLowerCase().normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]/g, " ").replace(/\s+/g, " ").trim();
    const preposicoes = ['da', 'de', 'do', 'das', 'dos'];
    return textoProcessado.split(' ').filter(p => !preposicoes.includes(p) && p.length > 0).join(' ');
  }

  normalizarNumero(valor) {
    if (!valor) return "";
    let apenasNumeros = valor.toString().replace(/\D/g, '').trim();
    if (apenasNumeros === "0" || apenasNumeros === "00" || apenasNumeros === "") return "";
    return apenasNumeros; 
  }

  // OTIMIZADO: isCPF rápido
  isCPF(valor) {
    if (!valor) return false;
    const numeros = valor.toString().replace(/\D/g, '');
    return numeros.length === 11;
  }

  // OTIMIZADO: isTelefone rápido (sem chamar isCPF internamente)
  isTelefone(valor) {
    if (!valor) return false;
    const numeros = valor.toString().replace(/\D/g, '');
    return numeros.length >= 8 && numeros.length <= 11;
  }

  // OTIMIZADO: isDataAniversario simplificado
  isDataAniversario(valor) {
    if (!valor) return false;
    const str = valor.toString().trim();
    
    // Verificação rápida: tem separador de data?
    if (str.includes('/') || str.includes('-')) {
      const padraoData = /^\d{1,2}[\/\-]\d{1,2}([\/\-]\d{2,4})?$/;
      return padraoData.test(str);
    }
    
    // Data sem separador: 7 ou 8 dígitos
    const numeros = str.replace(/\D/g, '');
    return numeros.length === 7 || numeros.length === 8;
  }

  // Mantido para comparação com coluna X
  normalizarData(valor) {
    if (!valor) return "";
    return valor.toString().replace(/\D/g, '');
  }

  isNome(valor) {
    if (!valor) return false;
    const str = valor.toString().trim();
    
    if (/^\d+$/.test(str.replace(/\s/g, ''))) return false;
    if (str.includes('/') || str.includes('\\')) return false;
    if (/[a-zA-ZÀ-ú]/.test(str)) return true;
    
    return false;
  }

  calcularSimBigramas(s1, s2) {
    if (!s1 || !s2 || s1.length < 2 || s2.length < 2) return 0.0;
    if (s1 === s2) return 1.0;
    let pares1 = [], pares2 = [];
    for (let i = 0; i < s1.length - 1; i++) pares1.push(s1.substring(i, i + 2));
    for (let i = 0; i < s2.length - 1; i++) pares2.push(s2.substring(i, i + 2));
    let inter = 0; let p2B = [...pares2];
    for (let b of pares1) {
      let idx = p2B.indexOf(b);
      if (idx !== -1) { inter++; p2B.splice(idx, 1); }
    }
    return (pares1.length + pares2.length) > 0 ? (2.0 * inter) / (pares1.length + pares2.length) : 0;
  }

  calcularSimilaridade(str1, str2) {
    if (str1 === str2) return 1.0;
    const p1 = str1.split(' '), p2 = str2.split(' ');
    
    let comuns = 0, p2Copia = [...p2];
    for (let w of p1) {
      let idx = p2Copia.indexOf(w);
      if (idx !== -1) { comuns++; p2Copia.splice(idx, 1); }
    }
    const scorePalavras = (2.0 * comuns) / (p1.length + p2.length);
    const scoreBigramas = this.calcularSimBigramas(str1, str2);

    let pontuacaoParcial = 0;
    if (str1.length >= 3 && str2.length >= 3) {
      const s1 = " " + str1 + " ", s2 = " " + str2 + " ";
      if (s2.includes(s1) || s1.includes(s2)) pontuacaoParcial = 0.95; 
    }

    let notaFinal = Math.max(scorePalavras, scoreBigramas, pontuacaoParcial);

    let primeiraPalavraBusca = p1[0];
    let identificadorExisteNoBanco = false;
    for (let w of p2) {
      if (w === primeiraPalavraBusca || 
         (primeiraPalavraBusca.length >= 3 && w.startsWith(primeiraPalavraBusca.substring(0, 3))) || 
         this.calcularSimBigramas(primeiraPalavraBusca, w) >= 0.7) {
        identificadorExisteNoBanco = true;
        break;
      }
    }
    if (!identificadorExisteNoBanco) notaFinal *= 0.3; 

    return notaFinal;
  }

  calcularSimilaridadeSobrenome(str1, str2) {
    if (!str1 || !str2) return 0.0;
    
    const palavras1 = str1.split(' ');
    const palavras2 = str2.split(' ');
    
    const preposicoes = ['da', 'de', 'do', 'das', 'dos'];
    
    const sobrenomes1 = palavras1.slice(1).filter(p => !preposicoes.includes(p));
    const sobrenomes2 = palavras2.slice(1).filter(p => !preposicoes.includes(p));
    
    if (sobrenomes1.length === 0 || sobrenomes2.length === 0) return 0.0;
    
    let sobrenomesComuns = 0;
    let sobrenomes2Copia = [...sobrenomes2];
    
    for (let s of sobrenomes1) {
      let idx = sobrenomes2Copia.indexOf(s);
      if (idx !== -1) {
        sobrenomesComuns++;
        sobrenomes2Copia.splice(idx, 1);
      }
    }
    
    const totalSobrenomes = Math.max(sobrenomes1.length, sobrenomes2.length);
    return sobrenomesComuns / totalSobrenomes;
  }

  carregarBancoExterno() {
    try {
      const ssExterna = SpreadsheetApp.openById(this.idPlanilhaExterna);
      const aba = ssExterna.getSheetByName("IDENTIFICACAO_MARKETPLACE");
      if (!aba) throw new Error("Aba IDENTIFICACAO_MARKETPLACE não encontrada");
      
      const dados = aba.getRange("A:Z").getValues();
      
      return dados.map(linha => ({
        resM: linha[0],  // A - RA
        resN: linha[1],  // B - NOME ALUNO
        resAL: linha[3], // D - CPF ALUNO
        resT: linha[10], // K - CPF RESP. FIN
        
        alunoNomeNorm: this.normalizarTexto(linha[1]),
        dataNascimentoNorm: this.normalizarData(linha[23]), // X
        
        nomesParaBusca: [
          this.normalizarTexto(linha[1]),  // B - NOME ALUNO
          this.normalizarTexto(linha[4]),  // E - RESP. FIN
          this.normalizarTexto(linha[11]), // L - NOME RESP. ACAD
          this.normalizarTexto(linha[15]), // P - NOME PAI
          this.normalizarTexto(linha[18])  // S - NOME MAE
        ].filter(n => n !== ""),
        
        respNomesNorm: [
          this.normalizarTexto(linha[4]),  // E - RESP. FIN
          this.normalizarTexto(linha[11]), // L - NOME RESP. ACAD
          this.normalizarTexto(linha[15]), // P - NOME PAI
          this.normalizarTexto(linha[18])  // S - NOME MAE
        ].filter(n => n !== ""),
        
        telefonesParaBusca: [
          this.normalizarNumero(linha[6]),  // G - Tel/Cel Resp Fin
          this.normalizarNumero(linha[7]),  // H - Tel/Cel Resp Fin
          this.normalizarNumero(linha[8]),  // I - Tel/Cel Resp Fin
          this.normalizarNumero(linha[12]), // M - Tel/Cel Resp Acad
          this.normalizarNumero(linha[13]), // N - Tel/Cel Resp Acad
          this.normalizarNumero(linha[14]), // O - Tel/Cel Resp Acad
          this.normalizarNumero(linha[24]), // Y - Tel/Cel Aluno
          this.normalizarNumero(linha[25])  // Z - Tel/Cel Aluno
        ].filter(t => t !== ""),
        
        cpfsNorm: [
          this.normalizarNumero(linha[3]),  // D - CPF ALUNO
          this.normalizarNumero(linha[10])  // K - CPF RESP. FIN
        ].filter(c => c !== "")
        
      })).filter(item => item.alunoNomeNorm !== "" || item.cpfsNorm.length > 0);
      
    } catch (error) {
      console.error("Erro ao carregar banco externo:", error);
      throw error;
    }
  }

  // Separa dados com regras de CPF/Telefone/Data (ordem não importa)
  separarDadosIntervalo(intervalo) {
    const nomes = [];
    const telefones = [];
    const cpfs = [];
    const datas = [];
    const ignorados = [];
    
    for (let celula of intervalo) {
      if (!celula || celula.toString().trim() === "") continue;
      
      const valor = celula.toString().trim();
      
      // 1. Primeiro verifica se é data de nascimento
      if (this.isDataAniversario(valor)) {
        datas.push(valor);
        continue;
      }
      
      // 2. Verifica se é CPF (11 dígitos - tem prioridade sobre telefone)
      if (this.isCPF(valor)) {
        cpfs.push(valor);
        continue;
      }
      
      // 3. Verifica se é telefone (após descartar CPF)
      if (this.isTelefone(valor)) {
        telefones.push(valor);
        continue;
      }
      
      // 4. Verifica se é nome
      if (this.isNome(valor)) {
        nomes.push(valor);
        continue;
      }
      
      // 5. Se chegou aqui, ignora
      ignorados.push({ valor, tipo: 'desconhecido' });
    }
    
    return { nomes, telefones, cpfs, datas, ignorados };
  }

  // Busca melhor match com prioridade: CPF responsável > CPF aluno
  buscarMelhorMatch(vCpf, vNomesOriginais, vTelefonesOriginais, vCpfsIntervalo, vDatasIntervalo, bancoExterno) {
    const cpfBusca = this.normalizarNumero(vCpf);
    const nomesBuscaNorm = vNomesOriginais.map(n => this.normalizarTexto(n)).filter(n => n !== "");
    const telefonesBuscaNorm = vTelefonesOriginais.map(t => this.normalizarNumero(t)).filter(t => t !== "");
    const cpfsIntervaloNorm = vCpfsIntervalo.map(c => this.normalizarNumero(c)).filter(c => c !== "");
    const datasNorm = vDatasIntervalo.map(d => this.normalizarData(d)).filter(d => d !== "");
    
    // Combina todos os CPFs (coluna C + intervalo), priorizando o do responsável
    let todosCpfs = [...cpfsIntervaloNorm];
    
    // Adiciona CPF da coluna C se existir
    if (cpfBusca && !todosCpfs.includes(cpfBusca)) {
      todosCpfs.push(cpfBusca);
    }
    
    let melhorMatch = { item: null, pontuacao: 0, tipo: "NENHUM" };

    for (let item of bancoExterno) {
      // Verifica se bateu CPF (qualquer um dos CPFs encontrados)
      let bateuCpf = false;
      let tipoCpf = "NENHUM";
      
      if (todosCpfs.length > 0) {
        for (let cpf of todosCpfs) {
          // Verifica se é CPF do responsável (coluna K da base) - PRIORIDADE MÁXIMA
          if (this.normalizarNumero(item.resT) === cpf) {
            bateuCpf = true;
            tipoCpf = "RESPONSAVEL";
            break;
          }
          // Verifica se é CPF do aluno (coluna D da base)
          if (this.normalizarNumero(item.resAL) === cpf) {
            bateuCpf = true;
            tipoCpf = "ALUNO";
          }
        }
      }
      
      // Verifica data de nascimento
      let bateuData = false;
      if (datasNorm.length > 0 && item.dataNascimentoNorm) {
        bateuData = datasNorm.includes(item.dataNascimentoNorm);
      }
      
      // ===== ANÁLISE DE NOMES =====
      let maxScoreAluno = 0;
      let maxScoreResp = 0;
      let maxScoreSobrenome = 0;

      if (nomesBuscaNorm.length > 0) {
        for (let nBusca of nomesBuscaNorm) {
          // 1. Compara com nome do ALUNO
          let simAluno = this.calcularSimilaridade(nBusca, item.alunoNomeNorm);
          if (simAluno > maxScoreAluno) maxScoreAluno = simAluno;
          
          // 2. Compara com nomes dos RESPONSÁVEIS
          for (let nResp of item.respNomesNorm) {
            let simResp = this.calcularSimilaridade(nBusca, nResp);
            if (simResp > maxScoreResp) maxScoreResp = simResp;
          }
          
          // 3. Calcula similaridade de SOBRENOME (para detectar irmãos)
          let simSobrenome = this.calcularSimilaridadeSobrenome(nBusca, item.alunoNomeNorm);
          if (simSobrenome > maxScoreSobrenome) maxScoreSobrenome = simSobrenome;
        }
      }
      
      // Verifica match de telefone
      let bateuTelefone = false;
      if (telefonesBuscaNorm.length > 0 && item.telefonesParaBusca.length > 0) {
        for (let tBusca of telefonesBuscaNorm) {
          if (item.telefonesParaBusca.includes(tBusca)) {
            bateuTelefone = true;
            break;
          }
        }
      }

      let pontuacaoAtual = 0;
      let tipoAtual = "NENHUM";
      
      // Peso de desempate: Nome do aluno vale 10x mais que o nome do responsável
      let scoreCombinadoNomes = (maxScoreAluno * 10) + maxScoreResp;
      if (bateuTelefone) scoreCombinadoNomes += 50;
      if (bateuData) scoreCombinadoNomes += 30;

      // ===== SISTEMA DE TIERS =====
      if (bateuCpf) {
        if (maxScoreAluno >= 0.65) {
          // TIER 1: CPF Bateu e Aluno Bateu
          pontuacaoAtual = 10000 + scoreCombinadoNomes;
          tipoAtual = "1_CPF_E_ALUNO";
        } else if (tipoCpf === "RESPONSAVEL" && maxScoreResp >= 0.65) {
          // TIER 1B: CPF do responsável bateu e nome do responsável bateu
          pontuacaoAtual = 9000 + scoreCombinadoNomes;
          tipoAtual = "1B_CPF_RESP_E_NOME_RESP";
        } else if (maxScoreSobrenome >= 0.70 && maxScoreAluno < 0.65) {
          // TIER 2: CPF Bateu, nomes diferentes mas MESMO SOBRENOME (IRMÃO!)
          pontuacaoAtual = 2000 + (maxScoreSobrenome * 100) + scoreCombinadoNomes;
          tipoAtual = "2_CPF_IRMAO_SOBRENOME";
        } else if (tipoCpf === "RESPONSAVEL") {
          // TIER 2B: CPF do responsável bateu (mas sem match forte de nome)
          pontuacaoAtual = 1800 + scoreCombinadoNomes;
          tipoAtual = "2B_CPF_RESPONSAVEL";
        } else if (tipoCpf === "ALUNO") {
          // TIER 2C: CPF do aluno bateu (mas sem match forte de nome)
          pontuacaoAtual = 1500 + scoreCombinadoNomes;
          tipoAtual = "2C_CPF_ALUNO";
        } else {
          // TIER 2D: CPF Bateu, mas nomes muito diferentes
          pontuacaoAtual = 1000 + scoreCombinadoNomes;
          tipoAtual = "2D_CPF_NOMES_DIFERENTES";
        }
      } else {
        // CPF NÃO bateu - busca por similaridade
        if (maxScoreAluno >= 0.75 && maxScoreResp >= 0.75) {
          // TIER 3: Nomes do Aluno e Responsável batem bem
          pontuacaoAtual = 5000 + scoreCombinadoNomes;
          tipoAtual = "3_NOMES_ALUNO_E_RESP";
        } else if (maxScoreAluno >= 0.75 && bateuData) {
          // TIER 3B: Nome do aluno + data de nascimento
          pontuacaoAtual = 4800 + scoreCombinadoNomes;
          tipoAtual = "3B_NOME_ALUNO_E_DATA";
        } else if (maxScoreAluno >= 0.75) {
          // TIER 4: Apenas nome do Aluno bate bem
          pontuacaoAtual = 500 + scoreCombinadoNomes;
          tipoAtual = "4_NOME_ALUNO";
        } else if (maxScoreSobrenome >= 0.70 && bateuData) {
          // TIER 4B: Sobrenome similar + data (possível irmão com data)
          pontuacaoAtual = 450 + (maxScoreSobrenome * 100) + scoreCombinadoNomes;
          tipoAtual = "4B_SOBRENOME_E_DATA";
        } else if (maxScoreSobrenome >= 0.70) {
          // TIER 4C: Sobrenome similar (possível irmão sem CPF)
          pontuacaoAtual = 400 + (maxScoreSobrenome * 100) + scoreCombinadoNomes;
          tipoAtual = "4C_SOBRENOME_SEM_CPF";
        } else if (maxScoreResp >= 0.85) {
          // TIER 5: Apenas nome do Responsável bate bem
          pontuacaoAtual = 50 + scoreCombinadoNomes;
          tipoAtual = "5_NOME_RESPONSAVEL";
        } else if (bateuTelefone) {
          // TIER 6: Match apenas por telefone
          pontuacaoAtual = 25 + scoreCombinadoNomes;
          tipoAtual = "6_TELEFONE";
        }
      }

      if (pontuacaoAtual > melhorMatch.pontuacao) {
        melhorMatch.pontuacao = pontuacaoAtual;
        melhorMatch.item = item;
        melhorMatch.tipo = tipoAtual;
      }
    }
    return melhorMatch;
  }

  copiarColunasFixas(abaOrigem, linhaInicial, numLinhas) {
    if (numLinhas <= 0) return;
    
    // A -> V (índice 1 -> 22)
    abaOrigem.getRange(linhaInicial, 22, numLinhas, 1).setValues(
      abaOrigem.getRange(linhaInicial, 1, numLinhas, 1).getValues()
    );
    // F -> W (índice 6 -> 23)
    abaOrigem.getRange(linhaInicial, 23, numLinhas, 1).setValues(
      abaOrigem.getRange(linhaInicial, 6, numLinhas, 1).getValues()
    );
    // E -> X (índice 5 -> 24)
    abaOrigem.getRange(linhaInicial, 24, numLinhas, 1).setValues(
      abaOrigem.getRange(linhaInicial, 5, numLinhas, 1).getValues()
    );
    // D -> Y (índice 4 -> 25)
    abaOrigem.getRange(linhaInicial, 25, numLinhas, 1).setValues(
      abaOrigem.getRange(linhaInicial, 4, numLinhas, 1).getValues()
    );
    
    console.log(`✅ Cópias realizadas: A→V, F→W, E→X, D→Y (${numLinhas} linhas)`);
  }

  processarEmChunks() {
    const abaOrigem = this.ss.getSheetByName("F3");
    if (!abaOrigem) throw new Error("Aba F3 não encontrada");
    
    const ultimaLinhaPlanilha = abaOrigem.getLastRow();
    const props = PropertiesService.getScriptProperties();
    
    let linhaAtual = parseInt(props.getProperty('F3_LINHA_ATUAL')) || 2;
    
    if (linhaAtual > ultimaLinhaPlanilha) {
      this.finalizarProcessamento(props);
      return;
    }

    // Limpa intervalo Q2:Y antes de iniciar (apenas na primeira execução)
    const limpezaRealizada = props.getProperty('F3_LIMPEZA_REALIZADA');
    if (!limpezaRealizada || limpezaRealizada !== 'true') {
      console.log("🧹 Limpando intervalo Q2:Y antes do processamento...");
      
      if (ultimaLinhaPlanilha >= 2) {
        const numLinhasParaLimpar = ultimaLinhaPlanilha - 1;
        if (numLinhasParaLimpar > 0) {
          abaOrigem.getRange(2, 17, numLinhasParaLimpar, 9).clearContent(); // Q=17, Y=25 (9 colunas)
          console.log(`✅ Intervalo Q2:Y${ultimaLinhaPlanilha} limpo com sucesso`);
        }
      }
      
      props.setProperty('F3_LIMPEZA_REALIZADA', 'true');
    }

    const numLinhasPendentes = ultimaLinhaPlanilha - linhaAtual + 1;
    const bancoExterno = this.carregarBancoExterno();
    
    const copiasRealizadas = props.getProperty('F3_COPIAS_REALIZADAS');
    if (!copiasRealizadas || copiasRealizadas !== 'true') {
      this.copiarColunasFixas(abaOrigem, linhaAtual, numLinhasPendentes);
      props.setProperty('F3_COPIAS_REALIZADAS', 'true');
    }
    
    // Lê colunas B até N (colunas 2 a 14)
    const dadosOrigem = abaOrigem.getRange(linhaAtual, 2, numLinhasPendentes, 13).getValues();
    const resultadosChunk = [];

    let tempoEsgotado = false;
    let encontrouFimDeDados = false;
    let contador = 0;

    for (let i = 0; i < dadosOrigem.length; i++) {
      const cpfColC = dadosOrigem[i][1];
      const valorFallbackG = dadosOrigem[i][5];
      
      // Intervalo I:N (índices 7 a 12 dentro do range B-N)
      const intervaloIN = [
        dadosOrigem[i][7],  // Coluna I
        dadosOrigem[i][8],  // Coluna J
        dadosOrigem[i][9],  // Coluna K
        dadosOrigem[i][10], // Coluna L
        dadosOrigem[i][11], // Coluna M
        dadosOrigem[i][12]  // Coluna N
      ];
      
      const temDados = cpfColC || intervaloIN.some(cel => cel) || valorFallbackG;
      
      if (!temDados) {
        encontrouFimDeDados = true;
        break;
      }

      if (Date.now() - this.inicioExecucao > this.tempoMaximoMS) {
        tempoEsgotado = true;
        break;
      }

      // Separa os dados do intervalo I:N independente da ordem
      const { nomes, telefones, cpfs, datas } = this.separarDadosIntervalo(intervaloIN);
      
      const palavrasIgnoradas = ["vestibular", "ano", "serie"];
      const nomesValidos = nomes.filter(nome => {
        const nomeNorm = nome.toString().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        return !palavrasIgnoradas.some(palavra => nomeNorm.includes(palavra));
      });
      
      const telefonesValidos = telefones.filter(tel => {
        const numLimpo = tel.toString().replace(/\D/g, '');
        return numLimpo.length >= 8;
      });

      let match = null;
      if (cpfColC || nomesValidos.length > 0 || telefonesValidos.length > 0 || cpfs.length > 0) {
        match = this.buscarMelhorMatch(cpfColC, nomesValidos, telefonesValidos, cpfs, datas, bancoExterno);
      }

      if (match && match.item && match.tipo !== "NENHUM") {
        resultadosChunk.push([
          match.item.resM,
          match.item.resN,
          match.item.resAL,
          match.item.resT
        ]);
      } else {
        let valorFallback = (valorFallbackG !== "" && valorFallbackG !== undefined) ? valorFallbackG : "---";
        resultadosChunk.push([
          valorFallback,
          "---",
          "---",
          "---"
        ]);
      }
      contador++;
    }

    if (resultadosChunk.length > 0) {
      abaOrigem.getRange(linhaAtual, 17, resultadosChunk.length, 4).setValues(resultadosChunk);
    }

    if (encontrouFimDeDados) {
      this.finalizarProcessamento(props);
    } else if (tempoEsgotado) {
      props.setProperty('F3_LINHA_ATUAL', (linhaAtual + contador).toString());
      limparGatilhos();
      ScriptApp.newTrigger('continuarProcessamentoF3').timeBased().after(30 * 1000).create();
    }
  }

  gerarRelatorioFinal() {
    const abaOrigem = this.ss.getSheetByName("F3");
    let abaFinal = this.ss.getSheetByName("FINAL");

    if (!abaOrigem) return;
    if (!abaFinal) {
      abaFinal = this.ss.insertSheet("FINAL"); 
    }

    const ultimaLinha = abaOrigem.getLastRow();
    if (ultimaLinha < 2) return; 

    const dados = abaOrigem.getRange(2, 17, ultimaLinha - 1, 12).getValues();
    const dadosUnicos = new Set();
    const arrayFinal = [];

    for (let i = 0; i < dados.length; i++) {
      const linha = dados[i];
      
      const linhaSelecionada = [
        linha[10], 
        linha[0],  
        linha[1],  
        linha[2],  
        linha[11], 
        linha[6],  
        linha[5]   
      ];

      if (linhaSelecionada.join("").trim() === "") continue;

      const chaveUnique = JSON.stringify(linhaSelecionada);
      
      if (!dadosUnicos.has(chaveUnique)) {
        dadosUnicos.add(chaveUnique);
        arrayFinal.push(linhaSelecionada);
      }
    }

    abaFinal.getRange("A2:G").clearContent();

    if (arrayFinal.length > 0) {
      abaFinal.getRange(2, 1, arrayFinal.length, arrayFinal[0].length).setValues(arrayFinal);
    }
  }

  finalizarProcessamento(props) {
    console.log("✨ Processamento F3 finalizado. Gerando aba FINAL...");
    props.deleteProperty('F3_LINHA_ATUAL');
    props.deleteProperty('F3_COPIAS_REALIZADAS');
    props.deleteProperty('F3_LIMPEZA_REALIZADA');
    limparGatilhos();
    this.gerarRelatorioFinal(); 
    console.log("✅ Rotina totalmente concluída.");
  }
}

function limparGatilhos() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let t of triggers) {
    const func = t.getHandlerFunction();
    if (func === 'continuarProcessamentoF3') ScriptApp.deleteTrigger(t);
  }
}

function continuarProcessamentoF3() {
  new ConciliadorFuzzy().processarEmChunks();
}

function iniciarConciliacaoF3() {
  limparGatilhos();
  PropertiesService.getScriptProperties().deleteProperty('F3_LINHA_ATUAL');
  PropertiesService.getScriptProperties().deleteProperty('F3_COPIAS_REALIZADAS');
  PropertiesService.getScriptProperties().deleteProperty('F3_LIMPEZA_REALIZADA');
  new ConciliadorFuzzy().processarEmChunks();
}
