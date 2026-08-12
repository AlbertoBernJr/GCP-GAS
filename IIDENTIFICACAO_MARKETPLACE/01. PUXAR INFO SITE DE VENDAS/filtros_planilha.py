"""
Módulo de Filtros para Planilhas
Versão: 1.0

Fornece funções para filtrar dados de planilhas XLSX,
incluindo normalização de texto e critérios de busca.
"""

import unicodedata


def normalizar_texto(texto):
    """
    Remove acentos e converte para minúsculas.
    
    Args:
        texto: String a ser normalizada
    
    Returns:
        str: Texto normalizado (sem acentos, minúsculo)
    
    Exemplos:
        normalizar_texto("Colégio Matriz Educação")
        -> "colegio matriz educacao"
    """
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.lower().strip()


def atende_criterios(linha):
    """
    Verifica se uma linha atende ao critério de filtro:
    - Coluna AF (índice 31 - Nome do Marketplace) deve conter "Colegio Matriz"
      (case insensitive, busca com e sem acentos)
    
    Args:
        linha: Lista com os valores da linha da planilha
    
    Returns:
        bool: True se atende ao critério, False caso contrário
    
    Exemplos:
        atende_criterios([..., "Colégio Matriz Educação", ...]) -> True
        atende_criterios([..., "Outra Escola", ...]) -> False
    """
    if len(linha) < 32:
        return False
    
    coluna_af = str(linha[31]) if linha[31] else ''
    
    # Normaliza o texto (remove acentos)
    texto_af_normalizado = normalizar_texto(coluna_af)
    
    # Verifica de várias formas:
    # 1. Texto normalizado (sem acentos, minúsculo)
    # 2. Texto original em minúsculo
    contem_colegio = (
        'matriz' in texto_af_normalizado or
        'matriz' in coluna_af.lower()
    )
    
    return contem_colegio


def filtrar_dados(dados):
    """
    Filtra os dados mantendo apenas linhas que atendem ao critério.
    
    Critério atual:
    - Coluna AF (Nome do Marketplace) contém "Colegio Matriz"
    
    Args:
        dados: Lista de listas com os dados da planilha (inclui cabeçalho)
    
    Returns:
        list: Dados filtrados (cabeçalho + linhas que atendem ao critério)
    
    Exemplo:
        dados = [['Cabeçalho', ...], ['Dados', ..., 'Colégio Matriz', ...], ...]
        filtrados = filtrar_dados(dados)
        # Retorna cabeçalho + apenas linhas com 'Colégio Matriz'
    """
    if not dados or len(dados) < 2:
        print("⚠️ Dados insuficientes para filtrar")
        return dados
    
    print("\n🔍 FILTRANDO DADOS...")
    print("-" * 60)
    print(f"🔍 Critério:")
    print(f"   Coluna AF (Nome do Marketplace) contém 'Colegio Matriz'")
    print(f"   (case insensitive, busca com e sem acentos)")
    
    # Mantém o cabeçalho (primeira linha)
    cabecalho = dados[0]
    linhas_filtradas = [cabecalho]
    
    total_dados = len(dados) - 1  # Exclui cabeçalho
    linhas_com_colegio = 0
    
    # Para debug: exemplos do que foi encontrado
    exemplos_colegio = []
    
    for i, linha in enumerate(dados[1:], start=2):
        if len(linha) < 32:
            continue
            
        coluna_af = str(linha[31]) if linha[31] else ''
        
        texto_af_norm = normalizar_texto(coluna_af)
        tem_colegio = (
            'matriz' in texto_af_norm or
            'matriz' in coluna_af.lower()
        )
        
        if tem_colegio:
            linhas_filtradas.append(linha)
            linhas_com_colegio += 1
            
            # Guarda alguns exemplos
            if len(exemplos_colegio) < 5:
                exemplos_colegio.append((i, coluna_af[:80]))
        
        # Log a cada 2000 linhas
        if i % 2000 == 0:
            print(f"⏳ Processadas {i-1}... (Encontradas: {linhas_com_colegio})")
    
    print(f"\n📊 ESTATÍSTICAS DE FILTRAGEM:")
    print(f"   Total de linhas: {total_dados}")
    print(f"   ✅ Contêm 'Colegio Matriz' na coluna AF: {linhas_com_colegio}")
    print(f"   📤 Linhas a enviar: {len(linhas_filtradas)} (cabeçalho + {linhas_com_colegio} dados)")
    
    if exemplos_colegio:
        print(f"\n📋 EXEMPLOS DE LINHAS FILTRADAS:")
        for idx, (linha_num, af) in enumerate(exemplos_colegio, 1):
            print(f"   {idx}. Linha {linha_num}: '{af}'")
    
    print("-" * 60)
    
    return linhas_filtradas
