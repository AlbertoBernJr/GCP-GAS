# gerador_cartoes.py
# Responsável pela geração dos cartões (desenho, PDF)
# ATUALIZADO com espaçamento entre dígitos do RA

import os
import sys
import textwrap
import shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from tamanho_altura import CONFIG
from redistribuicao import (
    PASTA_BASE_CARTOES,
    PASTA_CARTOES_GERADOS,
    UNIDADES_CONFIG,
    obter_sigla,
    obter_pasta,
    obter_caminho_unidade,
    gerar_nome_arquivo,
    garantir_pastas_existem
)

ALUNOS_POR_PAGINA = 19
ESPACAMENTO_RA = 3  # ← NOVO: pixels extras entre dígitos do RA

# =============================================================================
# FUNÇÕES AUXILIARES DE FONTE E DESENHO
# =============================================================================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def calcular_tamanho_fonte_para_uma_linha(draw, texto, largura_maxima, fonte_path, 
                                           tamanho_maximo, espessura='negrito', espacamento_extra=0):
    def criar_fonte(tam):
        try:
            return ImageFont.truetype(fonte_path, tam)
        except:
            return ImageFont.load_default()
    
    for tamanho in range(tamanho_maximo, 7, -1):
        fonte = criar_fonte(tamanho)
        
        # Calcular largura com espaçamento
        largura_total = 0
        for idx, char in enumerate(texto):
            try:
                bbox = draw.textbbox((0, 0), char, font=fonte)
                largura_total += (bbox[2] - bbox[0])
            except:
                largura_total += tamanho // 2
            if idx < len(texto) - 1:
                largura_total += espacamento_extra
        
        if largura_total <= largura_maxima:
            return fonte, tamanho, [texto]
    
    fonte_min = criar_fonte(8)
    texto_truncado = texto[:25] + "..." if len(texto) > 25 else texto
    return fonte_min, 8, [texto_truncado]


def calcular_linhas_e_tamanho_fonte(draw, texto, largura_maxima, altura_maxima, 
                                     fonte_path, tamanho_maximo, espessura='negrito'):
    def criar_fonte(tam):
        try:
            return ImageFont.truetype(fonte_path, tam)
        except:
            return ImageFont.load_default()
    
    fonte_max = criar_fonte(tamanho_maximo)
    
    try:
        bbox = draw.textbbox((0, 0), 'A', font=fonte_max)
        largura_char = bbox[2] - bbox[0]
    except:
        largura_char = tamanho_maximo // 2
    
    caracteres_por_linha = max(3, int(largura_maxima / largura_char))
    linhas = textwrap.wrap(texto, width=caracteres_por_linha)
    altura_linha = tamanho_maximo + 4
    altura_total_linhas = len(linhas) * altura_linha
    
    if altura_total_linhas <= altura_maxima:
        todas_cabem = True
        for linha in linhas:
            try:
                bbox = draw.textbbox((0, 0), linha, font=fonte_max)
                largura_linha = bbox[2] - bbox[0]
            except:
                largura_linha = len(linha) * tamanho_maximo // 2
            
            if largura_linha > largura_maxima:
                todas_cabem = False
                break
        
        if todas_cabem:
            return fonte_max, tamanho_maximo, linhas
    
    for tamanho in range(tamanho_maximo - 1, 7, -1):
        fonte = criar_fonte(tamanho)
        
        try:
            bbox = draw.textbbox((0, 0), 'A', font=fonte)
            largura_char = bbox[2] - bbox[0]
        except:
            largura_char = tamanho // 2
        
        caracteres_por_linha = max(3, int(largura_maxima / largura_char))
        linhas = textwrap.wrap(texto, width=caracteres_por_linha)
        altura_linha = tamanho + 4
        altura_total_linhas = len(linhas) * altura_linha
        
        if altura_total_linhas <= altura_maxima:
            todas_cabem = True
            for linha in linhas:
                try:
                    bbox = draw.textbbox((0, 0), linha, font=fonte)
                    largura_linha = bbox[2] - bbox[0]
                except:
                    largura_linha = len(linha) * tamanho // 2
                
                if largura_linha > largura_maxima:
                    todas_cabem = False
                    break
            
            if todas_cabem:
                return fonte, tamanho, linhas
    
    fonte_min = criar_fonte(8)
    linhas = textwrap.wrap(texto, width=10)
    return fonte_min, 8, linhas


def desenhar_texto_centralizado_no_quadrado(draw, texto, quadrado, fonte_path, 
                                             tamanho_maximo, permite_quebra=True, 
                                             cor=None, espacamento_extra=0):
    """
    Desenha texto centralizado no quadrado.
    espacamento_extra: pixels extras entre caracteres (para RA)
    """
    if cor is None:
        cor = CONFIG['cor_fonte']
    
    padding = CONFIG['padding']
    largura_max = quadrado['largura'] - (padding * 2)
    altura_max = quadrado['altura'] - (padding * 2)
    
    if permite_quebra:
        fonte, tamanho_usado, linhas = calcular_linhas_e_tamanho_fonte(
            draw, texto, largura_max, altura_max, fonte_path, tamanho_maximo, 'negrito'
        )
    else:
        fonte, tamanho_usado, linhas = calcular_tamanho_fonte_para_uma_linha(
            draw, texto, largura_max, fonte_path, tamanho_maximo, 'negrito', espacamento_extra
        )
    
    centro_y = (quadrado['y1'] + quadrado['y2']) // 2
    altura_total_linhas = len(linhas) * (tamanho_usado + 4)
    inicio_y = centro_y - (altura_total_linhas // 2)
    
    for i, linha in enumerate(linhas):
        if espacamento_extra > 0:
            # Desenhar caractere por caractere com espaçamento
            largura_total_com_espacamento = 0
            for idx, char in enumerate(linha):
                try:
                    bbox_char = draw.textbbox((0, 0), char, font=fonte)
                    largura_total_com_espacamento += (bbox_char[2] - bbox_char[0])
                except:
                    largura_total_com_espacamento += tamanho_usado // 2
                if idx < len(linha) - 1:
                    largura_total_com_espacamento += espacamento_extra
            
            pos_x = (quadrado['x1'] + quadrado['x2']) // 2 - (largura_total_com_espacamento // 2)
            pos_y = inicio_y + (i * (tamanho_usado + 4))
            
            x_atual = pos_x
            for char in linha:
                draw.text((x_atual, pos_y), char, font=fonte, fill=cor)
                try:
                    bbox_char = draw.textbbox((0, 0), char, font=fonte)
                    largura_char = bbox_char[2] - bbox_char[0]
                except:
                    largura_char = tamanho_usado // 2
                x_atual += largura_char + espacamento_extra
        else:
            # Sem espaçamento extra (original)
            try:
                bbox = draw.textbbox((0, 0), linha, font=fonte)
                largura_linha = bbox[2] - bbox[0]
            except:
                largura_linha = len(linha) * tamanho_usado // 2
            
            pos_x = (quadrado['x1'] + quadrado['x2']) // 2 - (largura_linha // 2)
            pos_y = inicio_y + (i * (tamanho_usado + 4))
            draw.text((pos_x, pos_y), linha, font=fonte, fill=cor)
    
    return linhas, tamanho_usado


def desenhar_texto_alinhado_esquerda_centralizado(draw, texto, quadrado, fonte_path, 
                                                   tamanho_maximo, ajuste_vertical, cor=None):
    if cor is None:
        cor = CONFIG['cor_fonte']
    
    padding = CONFIG['padding']
    largura_max = quadrado['largura'] - (padding * 2)
    
    fonte, tamanho_usado, linhas = calcular_tamanho_fonte_para_uma_linha(
        draw, texto, largura_max, fonte_path, tamanho_maximo, 'negrito'
    )
    
    centro_y = (quadrado['y1'] + quadrado['y2']) // 2
    
    try:
        bbox = draw.textbbox((0, 0), linhas[0], font=fonte)
        altura_texto = bbox[3] - bbox[1]
    except:
        altura_texto = tamanho_usado
    
    pos_y = centro_y - (altura_texto // 2) + ajuste_vertical
    pos_x = quadrado['x1'] + padding
    
    draw.text((pos_x, pos_y), linhas[0], font=fonte, fill=cor)
    
    return linhas, tamanho_usado


# =============================================================================
# GERAÇÃO DE PÁGINA DO CARTÃO
# =============================================================================

def gerar_pagina_cartao(alunos_pagina, unidade, turma):
    template_path = CONFIG['caminho_template']
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template não encontrado: {template_path}")
    
    template_img = Image.open(template_path)
    img = template_img.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    
    pasta_fontes = CONFIG['pasta_fontes']
    fonte_negrito_path = resource_path(os.path.join(pasta_fontes, CONFIG['caminho_fonte_negrito']))
    
    desenhar_texto_alinhado_esquerda_centralizado(
        draw, unidade, CONFIG['quadrado_unidade'], fonte_negrito_path, 
        CONFIG['tamanho_fonte_unidade'], CONFIG['ajuste_vertical_unidade']
    )
    
    desenhar_texto_alinhado_esquerda_centralizado(
        draw, turma, CONFIG['quadrado_turma'], fonte_negrito_path, 
        CONFIG['tamanho_fonte_turma'], CONFIG['ajuste_vertical_turma']
    )
    
    for i, aluno in enumerate(alunos_pagina):
        if i >= ALUNOS_POR_PAGINA:
            break
            
        quadrado_ra = CONFIG['quadrados_ra'][i]
        quadrado_nome = CONFIG['quadrados_nome'][i]
        
        # RA com ESPAÇAMENTO extra entre dígitos
        desenhar_texto_centralizado_no_quadrado(
            draw, aluno['RA'], quadrado_ra, fonte_negrito_path, 
            CONFIG['tamanho_fonte_ra'], permite_quebra=True,
            espacamento_extra=ESPACAMENTO_RA  # ← 3px entre dígitos
        )
        
        # Nome sem espaçamento extra
        desenhar_texto_centralizado_no_quadrado(
            draw, aluno['NOME'], quadrado_nome, fonte_negrito_path, 
            CONFIG['tamanho_fonte_nome'], permite_quebra=True
        )
    
    return img


# =============================================================================
# GERAÇÃO DE PDF COMPLETO
# =============================================================================

def gerar_pdf_completo(turmas_selecionadas, alunos_por_turma, redistribuir=True):
    """Gera um arquivo PDF para cada turma selecionada."""
    pdfs_gerados = []
    garantir_pastas_existem()
    
    for (unidade, turma, grade) in turmas_selecionadas:
        chave = (unidade, turma, grade)
        alunos = alunos_por_turma.get(chave, [])
        
        if not alunos:
            continue
        
        # Normalizar alunos (aceitar RA/NOME maiúsculo ou minúsculo)
        alunos_normalizados = []
        for a in alunos:
            alunos_normalizados.append({
                'RA': str(a.get('RA', a.get('RA', ''))),
                'NOME': str(a.get('NOME', a.get('NOME', a.get('NOME', ''))))
            })
        
        paginas = []
        for i in range(0, len(alunos_normalizados), ALUNOS_POR_PAGINA):
            pagina_alunos = alunos_normalizados[i:i + ALUNOS_POR_PAGINA]
            img = gerar_pagina_cartao(pagina_alunos, unidade, turma)
            paginas.append(img)
        
        if not paginas:
            continue
        
        nome_arquivo = gerar_nome_arquivo(unidade, turma, grade)
        nome_base = nome_arquivo.replace('.pdf', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{nome_base}_{timestamp}.pdf"
        nome_arquivo = "".join(c for c in nome_arquivo if c.isalnum() or c in '._-')
        
        caminho_backup = os.path.join(PASTA_CARTOES_GERADOS, nome_arquivo)
        
        primeira_pagina = paginas[0]
        demais_paginas = paginas[1:] if len(paginas) > 1 else []
        
        try:
            if demais_paginas:
                primeira_pagina.save(caminho_backup, "PDF", save_all=True,
                                     append_images=demais_paginas, resolution=100.0)
            else:
                primeira_pagina.save(caminho_backup, "PDF", resolution=100.0)
        except:
            pngs = []
            for idx, pagina in enumerate(paginas):
                png_path = os.path.join(PASTA_CARTOES_GERADOS, f"_temp_{idx}.png")
                pagina.save(png_path, "PNG")
                pngs.append(png_path)
            
            imagens = [Image.open(p).convert('RGB') for p in pngs]
            imagens[0].save(caminho_backup, "PDF", save_all=True,
                           append_images=imagens[1:], resolution=100.0)
            
            for p in pngs:
                try: os.remove(p)
                except: pass
        
        resultado = {
            'backup': caminho_backup,
            'turma': turma,
            'unidade': unidade,
            'grade': grade,
            'sigla': obter_sigla(unidade),
            'total_alunos': len(alunos),
            'total_paginas': len(paginas)
        }
        
        if redistribuir:
            pasta_destino = obter_caminho_unidade(unidade)
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)
            
            caminho_pdf = os.path.join(pasta_destino, nome_arquivo)
            shutil.copy2(caminho_backup, caminho_pdf)
            resultado['arquivo'] = caminho_pdf
            resultado['pasta_destino'] = pasta_destino
        
        pdfs_gerados.append(resultado)
    
    return pdfs_gerados


# =============================================================================
# REDISTRIBUIÇÃO E JUNÇÃO (mantidas iguais)
# =============================================================================

def redistribuir_pdfs_existentes():
    resultado = {'total': 0, 'redistribuidos': 0, 'erros': 0}
    
    if not os.path.exists(PASTA_CARTOES_GERADOS):
        os.makedirs(PASTA_CARTOES_GERADOS)
        return resultado
    
    pdfs = [f for f in os.listdir(PASTA_CARTOES_GERADOS) if f.lower().endswith('.pdf')]
    resultado['total'] = len(pdfs)
    
    for pdf in pdfs:
        try:
            unidade_encontrada = None
            for unidade, config in UNIDADES_CONFIG.items():
                if unidade in pdf or config['sigla'] in pdf.split('-')[0]:
                    unidade_encontrada = unidade
                    break
            
            if unidade_encontrada:
                pasta_destino = obter_caminho_unidade(unidade_encontrada)
                if not os.path.exists(pasta_destino):
                    os.makedirs(pasta_destino)
                
                origem = os.path.join(PASTA_CARTOES_GERADOS, pdf)
                destino = os.path.join(pasta_destino, pdf)
                shutil.copy2(origem, destino)
                resultado['redistribuidos'] += 1
            else:
                resultado['erros'] += 1
        except:
            resultado['erros'] += 1
    
    return resultado


def juntar_pdfs_por_unidade(pasta_origem):
    from PyPDF2 import PdfMerger
    
    resultado = {'total': 0, 'unidades_processadas': set(), 'arquivos_gerados': {}}
    
    if not os.path.exists(pasta_origem):
        return resultado
    
    pdfs = [f for f in os.listdir(pasta_origem) if f.lower().endswith('.pdf')]
    resultado['total'] = len(pdfs)
    
    if resultado['total'] == 0:
        return resultado
    
    pdfs_por_unidade = {}
    for pdf in pdfs:
        unidade_encontrada = None
        for unidade, config in UNIDADES_CONFIG.items():
            if unidade in pdf or config['sigla'] in pdf.split('-')[0]:
                unidade_encontrada = unidade
                break
        
        if unidade_encontrada:
            if unidade_encontrada not in pdfs_por_unidade:
                pdfs_por_unidade[unidade_encontrada] = []
            pdfs_por_unidade[unidade_encontrada].append(os.path.join(pasta_origem, pdf))
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for unidade, lista_pdfs in pdfs_por_unidade.items():
        resultado['unidades_processadas'].add(unidade)
        
        if len(lista_pdfs) == 1:
            nome_destino = os.path.join(pasta_origem, f"{unidade}_UNICO_{timestamp}.pdf")
            shutil.copy2(lista_pdfs[0], nome_destino)
            resultado['arquivos_gerados'][unidade] = nome_destino
        else:
            merger = PdfMerger()
            for pdf in sorted(lista_pdfs):
                merger.append(pdf)
            
            nome_destino = os.path.join(pasta_origem, f"{unidade}_JUNTADO_{timestamp}.pdf")
            merger.write(nome_destino)
            merger.close()
            resultado['arquivos_gerados'][unidade] = nome_destino
    
    return resultado
