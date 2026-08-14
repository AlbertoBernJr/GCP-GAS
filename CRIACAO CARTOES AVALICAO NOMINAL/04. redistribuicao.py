# redistribuicao.py
# Arquivo de configuração para redistribuição dos cartões gerados
# Contém todas as informações de pastas, unidades e mapeamentos

import os

# =============================================================================
# CAMINHO BASE - RAIZ DE TODAS AS PASTAS
# =============================================================================
PASTA_BASE_CARTOES = r"G:\.shortcut-targets-by-id\ --- \Time BI\2. ALUNOS\CARTAO NOTA AV"

# =============================================================================
# PASTA DE BACKUP - Onde TODOS os PDFs são salvos inicialmente
# =============================================================================
PASTA_CARTOES_GERADOS = os.path.join(PASTA_BASE_CARTOES, "0. CARTOES_GERADOS")

# =============================================================================
# MAPEAMENTO DE UNIDADES
# =============================================================================
# Cada unidade tem:
#   - sigla: Abreviação usada no nome do arquivo PDF
#   - pasta: Nome da pasta onde os PDFs serão redistribuídos
#   - caminho_completo: Caminho absoluto da pasta (gerado automaticamente)
# =============================================================================

UNIDADES_CONFIG = {
    "MADUREIRA": {
        "sigla": "MD",
        "pasta": "MADUREIRA (MD)"
    },
    "CAMPO GRANDE": {
        "sigla": "CG",
        "pasta": "CAMPO GRANDE (CG)"
    },
    "BANGU": {
        "sigla": "BG",
        "pasta": "BANGU (BG)"
    },
    "DUQUE DE CAXIAS": {
        "sigla": "CX",
        "pasta": "DUQUE DE CAXIAS (CX)"
    },
    "NOVA IGUACU": {
        "sigla": "NI",
        "pasta": "NOVA IGUACU (NI)"
    },
    "RETIRO DOS ARTISTAS": {
        "sigla": "RA",
        "pasta": "RETIRO DOS ARTISTAS (RA)"
    },
    "ROCHA MIRANDA": {
        "sigla": "RM",
        "pasta": "ROCHA MIRANDA (RM)"
    },
    "SÃO JOÃO DE MERITI": {
        "sigla": "SJ",
        "pasta": "SÃO JOÃO DE MERITI (SJ)"
    },
    "TAQUARA": {
        "sigla": "TQ",
        "pasta": "TAQUARA (TQ)"
    },
    "TIJUCA": {
        "sigla": "TJ",
        "pasta": "TIJUCA (TJ)"
    }
}

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def obter_sigla(unidade):
    """
    Retorna a sigla de uma unidade.
    Exemplo: obter_sigla("MADUREIRA") → "MD"
    """
    return UNIDADES_CONFIG.get(unidade, {}).get('sigla', '--')


def obter_pasta(unidade):
    """
    Retorna o nome da pasta de uma unidade.
    Exemplo: obter_pasta("MADUREIRA") → "MADUREIRA (MD)"
    """
    return UNIDADES_CONFIG.get(unidade, {}).get('pasta', unidade)


def obter_caminho_unidade(unidade):
    """
    Retorna o caminho completo da pasta de uma unidade.
    Exemplo: obter_caminho_unidade("MADUREIRA") → "G:\...\CARTAO NOTA AV\MADUREIRA (MD)"
    """
    pasta = obter_pasta(unidade)
    return os.path.join(PASTA_BASE_CARTOES, pasta)


def obter_caminho_backup():
    """
    Retorna o caminho completo da pasta de backup.
    """
    return PASTA_CARTOES_GERADOS


def listar_unidades():
    """
    Retorna uma lista com os nomes de todas as unidades.
    """
    return list(UNIDADES_CONFIG.keys())


def listar_siglas():
    """
    Retorna uma lista com todas as siglas.
    """
    return [info['sigla'] for info in UNIDADES_CONFIG.values()]


def listar_pastas():
    """
    Retorna uma lista com os caminhos completos de todas as pastas de unidades.
    """
    return [os.path.join(PASTA_BASE_CARTOES, info['pasta']) for info in UNIDADES_CONFIG.values()]


def obter_unidade_por_sigla(sigla):
    """
    Retorna o nome da unidade a partir da sigla.
    Exemplo: obter_unidade_por_sigla("MD") → "MADUREIRA"
    """
    for unidade, info in UNIDADES_CONFIG.items():
        if info['sigla'] == sigla:
            return unidade
    return None


def gerar_nome_arquivo(unidade, turma, grade):
    """
    Gera o nome padronizado do arquivo PDF.
    Exemplo: gerar_nome_arquivo("MADUREIRA", "3º ano A", "2ª/4ª 8h")
             → "MD-3º ano A - MADUREIRA - Grade 2ª4ª 8h.pdf"
    """
    sigla = obter_sigla(unidade)
    return f"{sigla}-{turma} - {unidade} - Grade {grade}.pdf"


def garantir_pastas_existem():
    """
    Cria todas as pastas necessárias se não existirem.
    Retorna uma lista com as pastas criadas.
    """
    pastas_criadas = []
    
    # Pasta de backup
    if not os.path.exists(PASTA_CARTOES_GERADOS):
        os.makedirs(PASTA_CARTOES_GERADOS, exist_ok=True)
        pastas_criadas.append(PASTA_CARTOES_GERADOS)
    
    # Pastas das unidades
    for info in UNIDADES_CONFIG.values():
        caminho = os.path.join(PASTA_BASE_CARTOES, info['pasta'])
        if not os.path.exists(caminho):
            os.makedirs(caminho, exist_ok=True)
            pastas_criadas.append(caminho)
    
    return pastas_criadas


# =============================================================================
# DICIONÁRIO PRINCIPAL (para compatibilidade com importação)
# =============================================================================
CONFIG_REDISTRIBUICAO = {
    'pasta_base_cartoes': PASTA_BASE_CARTOES,
    'pasta_cartoes_gerados': PASTA_CARTOES_GERADOS,
    'unidades_config': UNIDADES_CONFIG,
    'total_unidades': len(UNIDADES_CONFIG),
}

# =============================================================================
# EXIBIR INFORMAÇÕES (apenas quando executado diretamente)
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("📁 CONFIGURAÇÕES DE REDISTRIBUIÇÃO")
    print("=" * 70)
    
    print(f"\n📂 Pasta Base:")
    print(f"   {PASTA_BASE_CARTOES}")
    
    print(f"\n💾 Pasta de Backup:")
    print(f"   {PASTA_CARTOES_GERADOS}")
    
    print(f"\n🏫 Unidades ({len(UNIDADES_CONFIG)}):")
    print("-" * 70)
    print(f"{'Sigla':<8} {'Unidade':<25} {'Pasta':<30}")
    print("-" * 70)
    
    for unidade, info in UNIDADES_CONFIG.items():
        caminho = os.path.join(PASTA_BASE_CARTOES, info['pasta'])
        existe = "✅" if os.path.exists(caminho) else "❌"
        print(f"{info['sigla']:<8} {unidade:<25} {existe} {info['pasta']:<30}")
    
    print("-" * 70)
    
    print(f"\n📝 Exemplo de nome de arquivo:")
    exemplo = gerar_nome_arquivo("MADUREIRA", "3º ano A", "2ª/4ª 8h")
    print(f"   {exemplo}")
    
    print(f"\n🔍 Funções disponíveis:")
    print(f"   obter_sigla(unidade)        → Retorna a sigla")
    print(f"   obter_pasta(unidade)        → Retorna o nome da pasta")
    print(f"   obter_caminho_unidade(unidade) → Retorna o caminho completo")
    print(f"   obter_caminho_backup()      → Retorna o caminho do backup")
    print(f"   listar_unidades()           → Lista todas as unidades")
    print(f"   gerar_nome_arquivo(u, t, g) → Gera nome padronizado do PDF")
    print(f"   garantir_pastas_existem()   → Cria pastas que não existem")
