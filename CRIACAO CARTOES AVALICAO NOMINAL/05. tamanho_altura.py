# tamanho_altura.py
# Arquivo de configuração para o Gerador de Cartões
# ATUALIZADO com as NOVAS coordenadas validadas + interpolação

import os
import numpy as np

# =============================================================================
# NOVAS COORDENADAS FORNECIDAS (7 linhas validadas)
# =============================================================================

COORDENADAS_CONHECIDAS = {
    1:  {'ra': (74, 410, 238, 476), 'nome': (252, 407, 555, 477)},
    2:  {'ra': (72, 488, 237, 557), 'nome': (251, 489, 556, 558)},
    3:  {'ra': (77, 572, 237, 641), 'nome': (250, 571, 555, 641)},
    7:  {'ra': (75, 917, 238, 976), 'nome': (250, 916, 557, 976)},
    17: {'ra': (75, 1716, 237, 1778), 'nome': (252, 1716, 556, 1778)},
    18: {'ra': (76, 1791, 229, 1858), 'nome': (254, 1793, 553, 1858)},
    19: {'ra': (77, 1875, 236, 1935), 'nome': (253, 1874, 555, 1938)},
}

# =============================================================================
# INTERPOLAÇÃO DAS LINHAS FALTANTES
# =============================================================================

def interpolar_linhas_faltantes():
    """
    Interpola linearmente as coordenadas para as linhas faltantes.
    Segmentos:
    - Linhas 4,5,6: entre linha 3 e linha 7
    - Linhas 8,9,10,11,12,13,14,15,16: entre linha 7 e linha 17
    """
    coordenadas_completas = {}

    # Copia as conhecidas
    for linha, coord in COORDENADAS_CONHECIDAS.items():
        coordenadas_completas[linha] = coord

    # =========================================================================
    # Segmento 1: Linhas 4, 5, 6 (entre 3 e 7)
    # =========================================================================
    interpolar_segmento(coordenadas_completas, 3, 7)

    # =========================================================================
    # Segmento 2: Linhas 8 a 16 (entre 7 e 17)
    # =========================================================================
    interpolar_segmento(coordenadas_completas, 7, 17)

    return coordenadas_completas


def interpolar_segmento(coordenadas, l_inicio, l_fim):
    """
    Interpola linearmente entre duas linhas conhecidas.
    """
    coord_inicio = coordenadas[l_inicio]
    coord_fim = coordenadas[l_fim]

    num_intervalos = l_fim - l_inicio

    # Incrementos para RA
    ra_dx1 = (coord_fim['ra'][0] - coord_inicio['ra'][0]) / num_intervalos
    ra_dy1 = (coord_fim['ra'][1] - coord_inicio['ra'][1]) / num_intervalos
    ra_dx2 = (coord_fim['ra'][2] - coord_inicio['ra'][2]) / num_intervalos
    ra_dy2 = (coord_fim['ra'][3] - coord_inicio['ra'][3]) / num_intervalos

    # Incrementos para Nome
    nome_dx1 = (coord_fim['nome'][0] - coord_inicio['nome'][0]) / num_intervalos
    nome_dy1 = (coord_fim['nome'][1] - coord_inicio['nome'][1]) / num_intervalos
    nome_dx2 = (coord_fim['nome'][2] - coord_inicio['nome'][2]) / num_intervalos
    nome_dy2 = (coord_fim['nome'][3] - coord_inicio['nome'][3]) / num_intervalos

    for linha in range(l_inicio + 1, l_fim):
        offset = linha - l_inicio

        ra_x1 = int(coord_inicio['ra'][0] + ra_dx1 * offset)
        ra_y1 = int(coord_inicio['ra'][1] + ra_dy1 * offset)
        ra_x2 = int(coord_inicio['ra'][2] + ra_dx2 * offset)
        ra_y2 = int(coord_inicio['ra'][3] + ra_dy2 * offset)

        nome_x1 = int(coord_inicio['nome'][0] + nome_dx1 * offset)
        nome_y1 = int(coord_inicio['nome'][1] + nome_dy1 * offset)
        nome_x2 = int(coord_inicio['nome'][2] + nome_dx2 * offset)
        nome_y2 = int(coord_inicio['nome'][3] + nome_dy2 * offset)

        coordenadas[linha] = {
            'ra': (ra_x1, ra_y1, ra_x2, ra_y2),
            'nome': (nome_x1, nome_y1, nome_x2, nome_y2)
        }


# Gerar todas as coordenadas
COORDENADAS_COMPLETAS = interpolar_linhas_faltantes()

# =============================================================================
# EXTRAIR LISTAS PARA O FORMATO DO ARQUIVO
# =============================================================================

linhas_ordenadas = sorted(COORDENADAS_COMPLETAS.keys())

POSICOES_Y_RA = [COORDENADAS_COMPLETAS[l]['ra'][1] for l in linhas_ordenadas]
POSICOES_Y_NOME = [COORDENADAS_COMPLETAS[l]['nome'][1] for l in linhas_ordenadas]

# Calcular médias para X
todos_ra_x1 = [COORDENADAS_COMPLETAS[l]['ra'][0] for l in linhas_ordenadas]
todos_ra_x2 = [COORDENADAS_COMPLETAS[l]['ra'][2] for l in linhas_ordenadas]
todos_nome_x1 = [COORDENADAS_COMPLETAS[l]['nome'][0] for l in linhas_ordenadas]
todos_nome_x2 = [COORDENADAS_COMPLETAS[l]['nome'][2] for l in linhas_ordenadas]

X_INICIO_RA = int(np.mean(todos_ra_x1))
X_FIM_RA = int(np.mean(todos_ra_x2))
X_INICIO_NOME = int(np.mean(todos_nome_x1))
X_FIM_NOME = int(np.mean(todos_nome_x2))

# Calcular alturas médias
alturas_ra = [COORDENADAS_COMPLETAS[l]['ra'][3] - COORDENADAS_COMPLETAS[l]['ra'][1] for l in linhas_ordenadas]
alturas_nome = [COORDENADAS_COMPLETAS[l]['nome'][3] - COORDENADAS_COMPLETAS[l]['nome'][1] for l in linhas_ordenadas]

ALTURA_QUADRADO = int(np.mean(alturas_ra + alturas_nome))
LARGURA_QUADRADO_RA = X_FIM_RA - X_INICIO_RA
LARGURA_QUADRADO_NOME = X_FIM_NOME - X_INICIO_NOME

# =============================================================================
# CONFIGURAÇÕES UNIDADE
# =============================================================================
QUADRADO_UNIDADE = {
    'x1': 218, 'y1': 52, 'x2': 786, 'y2': 73,
    'largura': 568, 'altura': 21
}

# =============================================================================
# CONFIGURAÇÕES TURMA
# =============================================================================
QUADRADO_TURMA = {
    'x1': 198, 'y1': 96, 'x2': 600, 'y2': 122,
    'largura': 402, 'altura': 26
}

# =============================================================================
# TAMANHOS DAS FONTES
# =============================================================================
TAMANHO_FONTE_RA = 20
TAMANHO_FONTE_NOME = 20
TAMANHO_FONTE_UNIDADE = 32
TAMANHO_FONTE_TURMA = 29

# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================
COR_FONTE = (0, 0, 0)
PADDING = 5

# --- AJUSTES VERTICAIS ---
AJUSTE_VERTICAL_UNIDADE = -2
AJUSTE_VERTICAL_TURMA = -2

# =============================================================================
# CAMINHOS DOS ARQUIVOS
# =============================================================================
CAMINHO_TEMPLATE = r"C:\BI_Compartilhado\Repositorio\VsCode\04.CRIAR_CARTAO_AV\template.png"
PASTA_FONTES = "FONTES"
CAMINHO_FONTE = "arial.ttf"
CAMINHO_FONTE_NEGRITO = "arialbd.ttf"

# =============================================================================
# CONFIGURAÇÃO DOS CAMINHOS DAS UNIDADES
# =============================================================================
PASTA_BASE_CARTOES = r"G:\.shortcut-targets-by-id\ --- \Time BI\2. ALUNOS\CARTAO NOTA AV"
PASTA_CARTOES_GERADOS = os.path.join(PASTA_BASE_CARTOES, "0. CARTOES_GERADOS")

UNIDADES_CONFIG = {
    "MADUREIRA": {"sigla": "MD", "pasta": "MADUREIRA (MD)"},
    "CAMPO GRANDE": {"sigla": "CG", "pasta": "CAMPO GRANDE (CG)"},
    "BANGU": {"sigla": "BG", "pasta": "BANGU (BG)"},
    "DUQUE DE CAXIAS": {"sigla": "CX", "pasta": "DUQUE DE CAXIAS (CX)"},
    "NOVA IGUACU": {"sigla": "NI", "pasta": "NOVA IGUACU (NI)"},
    "RETIRO DOS ARTISTAS": {"sigla": "RA", "pasta": "RETIRO DOS ARTISTAS (RA)"},
    "ROCHA MIRANDA": {"sigla": "RM", "pasta": "ROCHA MIRANDA (RM)"},
    "SÃO JOÃO DE MERITI": {"sigla": "SJ", "pasta": "SÃO JOÃO DE MERITI (SJ)"},
    "TAQUARA": {"sigla": "TQ", "pasta": "TAQUARA (TQ)"},
    "TIJUCA": {"sigla": "TJ", "pasta": "TIJUCA (TJ)"}
}

# =============================================================================
# FUNÇÕES PARA GERAR QUADRADOS
# =============================================================================

def gerar_quadrados_ra():
    """Gera a lista de quadrados RA com coordenadas completas"""
    quadrados = []
    for linha in sorted(COORDENADAS_COMPLETAS.keys()):
        coord = COORDENADAS_COMPLETAS[linha]['ra']
        quadrados.append({
            'x1': coord[0], 'y1': coord[1], 'x2': coord[2], 'y2': coord[3],
            'numero': linha,
            'largura': coord[2] - coord[0],
            'altura': coord[3] - coord[1]
        })
    return quadrados


def gerar_quadrados_nome():
    """Gera a lista de quadrados Nome com coordenadas completas"""
    quadrados = []
    for linha in sorted(COORDENADAS_COMPLETAS.keys()):
        coord = COORDENADAS_COMPLETAS[linha]['nome']
        quadrados.append({
            'x1': coord[0], 'y1': coord[1], 'x2': coord[2], 'y2': coord[3],
            'numero': linha,
            'largura': coord[2] - coord[0],
            'altura': coord[3] - coord[1]
        })
    return quadrados


# =============================================================================
# DICIONÁRIO PRINCIPAL DE CONFIGURAÇÃO
# =============================================================================
CONFIG = {
    'coordenadas': COORDENADAS_COMPLETAS,
    'quadrados_ra': gerar_quadrados_ra(),
    'quadrados_nome': gerar_quadrados_nome(),
    'quadrado_unidade': QUADRADO_UNIDADE,
    'quadrado_turma': QUADRADO_TURMA,
    'posicoes_y_ra': POSICOES_Y_RA,
    'posicoes_y_nome': POSICOES_Y_NOME,
    'x_inicio_ra': X_INICIO_RA,
    'x_fim_ra': X_FIM_RA,
    'x_inicio_nome': X_INICIO_NOME,
    'x_fim_nome': X_FIM_NOME,
    'altura_quadrado': ALTURA_QUADRADO,
    'largura_quadrado_ra': LARGURA_QUADRADO_RA,
    'largura_quadrado_nome': LARGURA_QUADRADO_NOME,
    'tamanho_fonte_ra': TAMANHO_FONTE_RA,
    'tamanho_fonte_nome': TAMANHO_FONTE_NOME,
    'tamanho_fonte_unidade': TAMANHO_FONTE_UNIDADE,
    'tamanho_fonte_turma': TAMANHO_FONTE_TURMA,
    'cor_fonte': COR_FONTE,
    'padding': PADDING,
    'ajuste_vertical_unidade': AJUSTE_VERTICAL_UNIDADE,
    'ajuste_vertical_turma': AJUSTE_VERTICAL_TURMA,
    'caminho_template': CAMINHO_TEMPLATE,
    'pasta_fontes': PASTA_FONTES,
    'caminho_fonte': CAMINHO_FONTE,
    'caminho_fonte_negrito': CAMINHO_FONTE_NEGRITO,
    'pasta_base_cartoes': PASTA_BASE_CARTOES,
    'pasta_cartoes_gerados': PASTA_CARTOES_GERADOS,
    'unidades_config': UNIDADES_CONFIG
}

# =============================================================================
# EXIBIR RESUMO (apenas quando executado diretamente)
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("📋 COORDENADAS DO GERADOR DE CARTÕES (ATUALIZADAS)")
    print("=" * 70)
    print(f"Total de linhas: {len(COORDENADAS_COMPLETAS)}")
    print(f"\n🟢 Fornecidas (7): 1, 2, 3, 7, 17, 18, 19")
    print(f"🟠 Interpoladas (12): 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16")
    
    print(f"\n📐 Dimensões médias:")
    print(f"   RA:  {X_INICIO_RA}→{X_FIM_RA} ({LARGURA_QUADRADO_RA}px)")
    print(f"   Nome: {X_INICIO_NOME}→{X_FIM_NOME} ({LARGURA_QUADRADO_NOME}px)")
    print(f"   Altura média: {ALTURA_QUADRADO}px")
    
    print(f"\n📏 Coordenadas completas:")
    print("-" * 70)
    print(f"{'Linha':<6} {'RA (X1,Y1 - X2,Y2)':<30} {'Nome (X1,Y1 - X2,Y2)':<30}")
    print("-" * 70)
    
    for linha in sorted(COORDENADAS_COMPLETAS.keys()):
        coord = COORDENADAS_COMPLETAS[linha]
        ra = coord['ra']
        nome = coord['nome']
        marcador = "🟢" if linha in COORDENADAS_CONHECIDAS else "🟠"
        print(f"{marcador} {linha:<3} {ra[0]},{ra[1]} - {ra[2]},{ra[3]:<18} {nome[0]},{nome[1]} - {nome[2]},{nome[3]}")
    
    print("-" * 70)
    print(f"\n📏 Espaçamento Y1 entre linhas:")
    for i in range(len(POSICOES_Y_RA) - 1):
        esp = POSICOES_Y_RA[i+1] - POSICOES_Y_RA[i]
        print(f"   Linha {i+1}→{i+2}: {POSICOES_Y_RA[i]} → {POSICOES_Y_RA[i+1]} = {esp}px")
