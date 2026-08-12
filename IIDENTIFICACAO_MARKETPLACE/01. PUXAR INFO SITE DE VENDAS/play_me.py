import os
import sys
import time
import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from google.oauth2.service_account import Credentials
from limpeza_logs import limpar_logs_excedentes

# --- CONFIGURAÇÕES ---
BASE_DIR = r'C:\BI_Compartilhado\Repositorio\VsCode\1.PUXAR_INFO_LAYERS'
sys.path.append(BASE_DIR)
from config_login import EMAIL, SENHA, URL

# 🔥 IMPORTA OS MÓDULOS
from metodo_limpeza import criar_chrome_com_limpeza, limpar_dados_navegacao
from filtros_planilha import filtrar_dados

# --- CAMINHOS ---
DOWNLOAD_DIR = r'C:\Users\alberto.bernardo\Downloads\Temp_Layers'
GOOGLE_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credenciais_google.json')
PLANILHA_URL = ' '

# ============================================================
# FUNÇÕES DE PREPARAÇÃO
# ============================================================

def criar_pasta_download():
    """Cria a pasta Temp_Layers"""
    print("\n📁 Verificando pasta de download...")
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"✅ Pasta criada: {DOWNLOAD_DIR}")
    else:
        print(f"✅ Pasta existe: {DOWNLOAD_DIR}")
    
    arquivos = glob.glob(os.path.join(DOWNLOAD_DIR, "*"))
    for arq in arquivos:
        try:
            os.remove(arq)
        except:
            pass
    if arquivos:
        print(f"✅ {len(arquivos)} arquivos antigos removidos")
    
    return DOWNLOAD_DIR

# ============================================================
# FUNÇÕES DE AUTOMAÇÃO (LAYERS)
# ============================================================

def fazer_login(driver, wait):
    """Realiza o login no Layers"""
    print("\n🔐 Fazendo login...")
    
    driver.get(URL)
    time.sleep(3)
    
    email_input = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//input[@name='email' or @id='email' or @type='email']")))
    email_input.click()
    email_input.clear()
    email_input.send_keys(EMAIL)
    print("✅ Email preenchido")
    time.sleep(2)
    
    try:
        btn_continuar = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Continuar')]")))
        driver.execute_script("arguments[0].click();", btn_continuar)
        print("✅ Continuar clicado")
        time.sleep(3)
    except:
        print("ℹ️ Login em etapa única")
    
    senha_input = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//input[@name='password' or @type='password']")))
    senha_input.click()
    senha_input.clear()
    senha_input.send_keys(SENHA)
    print("✅ Senha preenchida")
    time.sleep(1)
    
    btn_entrar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[contains(text(), 'Entrar')]")))
    driver.execute_script("arguments[0].click();", btn_entrar)
    print("✅ Login realizado!")
    time.sleep(5)


def navegar_dashboard(driver, wait):
    """Navega até o dashboard de pagamentos"""
    print("\n🧭 Navegando para o dashboard...")
    
    try:
        btn_dashboard = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, 'payments-dashboard')]")))
        driver.execute_script("arguments[0].click();", btn_dashboard)
        print("✅ Dashboard clicado")
        time.sleep(5)
    except Exception as e:
        print(f"⚠️ Erro: {e}")
    
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"   Iframes: {len(iframes)}")
        
        if iframes:
            driver.switch_to.frame(iframes[0])
            print("✅ Iframe principal")
            time.sleep(3)
            
            iframes_internos = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"   Iframes internos: {len(iframes_internos)}")
            
            if iframes_internos:
                driver.switch_to.frame(iframes_internos[0])
                print("✅ Iframe Metabase")
                time.sleep(3)
    except Exception as e:
        print(f"❌ Erro iframes: {e}")
        raise


def selecionar_aba_itens(driver, wait):
    """Seleciona a aba Itens"""
    print("\n📑 Selecionando aba 'Itens'...")
    
    xpath_itens = "//div[@role='tab' and @aria-label='Itens']"
    btn_itens = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_itens)))
    driver.execute_script("arguments[0].click();", btn_itens)
    print("✅ Aba 'Itens' selecionada")
    time.sleep(3)


def configurar_filtro_data(driver, wait):
    """Configura o filtro de data"""
    print("\n📅 Configurando filtro de data...")
    
    # 1. Abre filtro
    xpath_filtro = "//button[@aria-label='Filtro de data']"
    btn_filtro = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_filtro)))
    driver.execute_script("arguments[0].click();", btn_filtro)
    print("✅ Filtro aberto")
    time.sleep(2)
    
    # 2. Anterior (se existir)
    try:
        opcao_anterior = driver.find_element(By.XPATH, "//*[contains(text(), 'Anterior')]")
        if opcao_anterior.is_displayed():
            driver.execute_script("arguments[0].click();", opcao_anterior)
            print("✅ 'Anterior' selecionado")
            time.sleep(1)
    except:
        print("ℹ️ 'Anterior' não encontrado")
    
    # 3. Unidade para meses
    input_unidade = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//input[@aria-label='Unidade']")))
    driver.execute_script("arguments[0].click();", input_unidade)
    time.sleep(1)
    
    opcao_meses = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[text()='meses']")))
    driver.execute_script("arguments[0].click();", opcao_meses)
    print("✅ Unidade: meses")
    time.sleep(1)
    
    # 4. Atualizar filtro
    btn_atualizar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[contains(@class, 'm_811560b9') and contains(text(), 'Atualizar filtro')]")))
    driver.execute_script("arguments[0].click();", btn_atualizar)
    print("✅ Filtro atualizado")
    time.sleep(5)


def baixar_arquivo(driver, wait):
    """Faz o download do arquivo .xlsx"""
    print("\n📥 Baixando arquivo .xlsx...")
    
    try:
        # 1. Menu (...)
        print("1️⃣ Abrindo menu...")
        btn_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-testid='public-or-embedded-dashcard-menu']")))
        driver.execute_script("arguments[0].click();", btn_menu)
        print("✅ Menu aberto")
        time.sleep(3)
        
        # 2. Download de resultados
        print("2️⃣ Download de resultados...")
        btn_download = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(text(), 'Fazer download de resultados')]")))
        driver.execute_script("arguments[0].click();", btn_download)
        print("✅ Opção selecionada")
        time.sleep(3)
        
        # 3. Seleciona .xlsx
        print("3️⃣ Selecionando .xlsx...")
        try:
            opcao_xlsx = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(@class, 'm_78882f40') and text()='.xlsx']")))
            driver.execute_script("arguments[0].click();", opcao_xlsx)
        except:
            label_xlsx = driver.find_element(By.XPATH,
                "//label[contains(@class, 'mb-mantine-SegmentedControl-label') and contains(@for, 'xlsx')]")
            driver.execute_script("arguments[0].click();", label_xlsx)
        print("✅ .xlsx selecionado")
        time.sleep(2)
        
        # 4. Clica em Baixar
        print("4️⃣ Clicando em Baixar...")
        btn_baixar = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'm_811560b9') and text()='Baixar']")))
        driver.execute_script("arguments[0].click();", btn_baixar)
        print("✅ Download iniciado!")
        
        # 5. Aguarda conclusão
        print("5️⃣ Aguardando download...")
        return aguardar_download(DOWNLOAD_DIR, timeout=60)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        driver.save_screenshot(os.path.join(DOWNLOAD_DIR, "erro_download.png"))
        return False


def aguardar_download(pasta, timeout=60):
    """Aguarda o download concluir"""
    tempo_inicio = time.time()
    tamanho_anterior = 0
    arquivo_anterior = None
    contador = 0
    
    while time.time() < tempo_inicio + timeout:
        arquivos = glob.glob(os.path.join(pasta, "*.xlsx"))
        crdownload = glob.glob(os.path.join(pasta, "*.crdownload"))
        
        if arquivos and not crdownload:
            arquivo_atual = max(arquivos, key=os.path.getctime)
            tamanho_atual = os.path.getsize(arquivo_atual)
            
            if arquivo_atual == arquivo_anterior and tamanho_atual == tamanho_anterior:
                contador += 1
                if contador >= 3:
                    print(f"\n✅ Download concluído!")
                    print(f"   Arquivo: {os.path.basename(arquivo_atual)}")
                    print(f"   Tamanho: {tamanho_atual:,} bytes")
                    return True
            else:
                contador = 0
            
            arquivo_anterior = arquivo_atual
            tamanho_anterior = tamanho_atual
            
        elif crdownload:
            print(f"   ⏳ Baixando...", end='\r')
        else:
            print(f"   🔍 Aguardando...", end='\r')
        
        time.sleep(1)
    
    # Timeout
    arquivos = glob.glob(os.path.join(pasta, "*.xlsx"))
    if arquivos:
        print(f"\n✅ Arquivo encontrado: {os.path.basename(arquivos[0])}")
        return True
    
    print("\n❌ Timeout!")
    return False


# ============================================================
# FUNÇÕES DE LEITURA E UPLOAD
# ============================================================

def encontrar_arquivo_xlsx():
    """Encontra o arquivo XLSX mais recente (ignora temporários)"""
    print("\n🔍 Procurando arquivo XLSX...")
    print(f"   Pasta: {DOWNLOAD_DIR}")
    
    todos_arquivos = glob.glob(os.path.join(DOWNLOAD_DIR, "*.xlsx"))
    
    # Filtra apenas arquivos válidos (ignora ~$)
    arquivos_validos = []
    for arq in todos_arquivos:
        nome_arquivo = os.path.basename(arq)
        if not nome_arquivo.startswith('~$') and os.path.getsize(arq) > 0:
            arquivos_validos.append(arq)
    
    if not arquivos_validos:
        # Tenta na pasta Downloads
        pasta_downloads = r'C:\Users\alberto.bernardo\Downloads'
        todos_arquivos = glob.glob(os.path.join(pasta_downloads, "*.xlsx"))
        arquivos_validos = []
        for arq in todos_arquivos:
            nome_arquivo = os.path.basename(arq)
            if not nome_arquivo.startswith('~$') and os.path.getsize(arq) > 0:
                arquivos_validos.append(arq)
        
        if arquivos_validos:
            import shutil
            arquivo = max(arquivos_validos, key=os.path.getctime)
            destino = os.path.join(DOWNLOAD_DIR, os.path.basename(arquivo))
            shutil.copy2(arquivo, destino)
            print(f"✅ Copiado para Temp_Layers")
            return destino
    
    if arquivos_validos:
        arquivo = max(arquivos_validos, key=os.path.getctime)
        print(f"✅ Encontrado: {os.path.basename(arquivo)}")
        print(f"   Tamanho: {os.path.getsize(arquivo):,} bytes")
        return arquivo
    
    print("❌ Nenhum arquivo encontrado!")
    return None


def ler_xlsx(arquivo):
    """Lê o arquivo XLSX e retorna lista de listas"""
    print("\n📖 LENDO ARQUIVO XLSX...")
    print("-" * 60)
    
    try:
        import openpyxl
    except ImportError:
        print("❌ Execute: pip install openpyxl")
        return None
    
    try:
        workbook = openpyxl.load_workbook(arquivo, read_only=True)
        sheet = workbook['Resultado da consulta']  # Aba correta
        
        print(f"   Planilha: {sheet.title}")
        
        dados = []
        contador = 0
        
        for row in sheet.iter_rows(values_only=True):
            linha = [str(celula) if celula is not None else '' for celula in row]
            dados.append(linha)
            contador += 1
            if contador % 2000 == 0:
                print(f"   Lidas {contador} linhas...")
        
        workbook.close()
        
        print(f"✅ {len(dados)} linhas lidas")
        
        if not dados:
            print("❌ Arquivo vazio!")
            return None
        
        # Preview
        print(f"\n📊 Preview:")
        print(f"   Colunas: {len(dados[0])}")
        print(f"   Cabeçalho: {dados[0][:5]}...")
        if len(dados) > 1:
            print(f"   Linha 2: {dados[1][:5]}...")
        print(f"   Última: {dados[-1][:5]}...")
        print("-" * 60)
        
        return dados
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


# ============================================================
# FUNÇÃO DO GOOGLE SHEETS
# ============================================================

def conectar_google_sheets():
    """Conecta ao Google Sheets e seleciona a aba Layers"""
    print("\n📊 Conectando ao Google Sheets...")
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    credentials = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=scopes)
    gc = gspread.authorize(credentials)
    planilha = gc.open_by_url(PLANILHA_URL)
    
    # Lista todas as abas
    worksheets = planilha.worksheets()
    print(f"   Abas encontradas: {[w.title for w in worksheets]}")
    
    # Procura a aba "Layers"
    worksheet = None
    for ws in worksheets:
        if ws.title == 'Layers':
            worksheet = ws
            break
    
    # Se não encontrar, usa a primeira aba
    if not worksheet:
        print("   ⚠️ Aba 'Layers' não encontrada! Usando primeira aba...")
        worksheet = planilha.sheet1
    
    print(f"✅ Conectado à aba: {worksheet.title}")
    return worksheet


def atualizar_google_sheets(dados, worksheet):
    """Limpa a planilha e insere os dados filtrados"""
    print("\n📤 ATUALIZANDO GOOGLE SHEETS...")
    print("-" * 60)
    
    if not dados:
        print("❌ Sem dados!")
        return False
    
    try:
        print(f"🧹 Limpando planilha...")
        worksheet.clear()
        time.sleep(2)
        
        print(f"📝 Inserindo {len(dados)} linhas filtradas...")
        
        for i in range(0, len(dados), 100):
            lote = dados[i:i+100]
            worksheet.append_rows(lote, value_input_option='USER_ENTERED')
            print(f"   ✅ {i+1} a {min(i+100, len(dados))} de {len(dados)}")
            time.sleep(1)
        
        time.sleep(2)
        total = len(worksheet.col_values(1))
        print(f"\n✅ PLANILHA ATUALIZADA!")
        print(f"   Total: {total} linhas")
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def run():
    """Executa todo o processo"""
    print("\n" + "="*60)
    print("🚀 LAYERS SCRAPER - FILTRO: COLÉGIO MATRIZ")
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*60)

    # 🔥 VERIFICA E LIMPA LOGS EXCEDENTES
    limpar_logs_excedentes(max_arquivos=30)
    
    driver = None
    
    try:
        # PASSO 1: Preparação
        criar_pasta_download()
        
        # PASSO 2: Configurar navegador com limpeza máxima
        print("\n⚙️ Configurando Chrome com limpeza máxima...")
        driver = criar_chrome_com_limpeza(DOWNLOAD_DIR)
        wait = WebDriverWait(driver, 30)
        
        # PASSO 3: Login e navegação
        fazer_login(driver, wait)
        navegar_dashboard(driver, wait)
        selecionar_aba_itens(driver, wait)
        configurar_filtro_data(driver, wait)
        
        # 🔥 LIMPEZA COMPLETA antes do download
        limpar_dados_navegacao(driver)
        time.sleep(1)
        
        # PASSO 4: Download
        if not baixar_arquivo(driver, wait):
            print("\n❌ Falha no download")
            return
        
        # PASSO 5: Encontrar e ler XLSX
        arquivo = encontrar_arquivo_xlsx()
        if not arquivo:
            print("\n❌ Arquivo não encontrado")
            return
        
        dados = ler_xlsx(arquivo)
        if not dados:
            print("\n❌ Falha na leitura")
            return
        
        # PASSO 6: FILTRAR DADOS
        dados_filtrados = filtrar_dados(dados)
        
        if len(dados_filtrados) <= 1:
            print("\n⚠️ NENHUMA LINHA ATENDE AOS CRITÉRIOS DE FILTRO!")
            return
        
        # PASSO 7: Conectar e atualizar Google Sheets
        worksheet = conectar_google_sheets()
        
        if atualizar_google_sheets(dados_filtrados, worksheet):
            print("\n" + "="*60)
            print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
            print("="*60)
            print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"📁 Arquivo: {os.path.basename(arquivo)}")
            print(f"📊 Total de linhas lidas: {len(dados)}")
            print(f"🔍 Linhas filtradas: {len(dados_filtrados)}")
            print(f"📊 Planilha: {PLANILHA_URL}")
        else:
            print("\n❌ Falha na atualização")
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            try:
                driver.save_screenshot(os.path.join(DOWNLOAD_DIR, "erro_geral.png"))
            except:
                pass
    
    finally:
        if driver:
            print("\n⚠️ Navegador mantido aberto")
            print("   Feche manualmente")


if __name__ == "__main__":
    run()
