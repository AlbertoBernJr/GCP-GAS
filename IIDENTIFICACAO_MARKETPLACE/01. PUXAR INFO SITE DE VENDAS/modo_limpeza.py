"""
Módulo de Limpeza de Dados de Navegação do Chrome
Versão: 1.3 - Ordem de limpeza corrigida + tratamento de erros
Autor: Otimizado com sugestões do Gemini

Fornece funções para limpeza completa de dados de navegação,
simulando a opção "Sempre" do Chrome.
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def criar_chrome_com_limpeza(download_dir):
    """
    Cria e retorna um driver Chrome configurado com limpeza máxima
    e download automático para a pasta especificada.
    
    Configurações aplicadas:
    - Modo anônimo (--incognito)
    - Cache mínimo
    - Senhas e autofill desabilitados
    - Notificações bloqueadas
    - Download automático sem perguntar
    
    Args:
        download_dir: Caminho da pasta para downloads
    
    Returns:
        webdriver.Chrome: Driver configurado
    """
    
    # Garante que a pasta existe
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    prefs = {
        # Configurações de download AUTOMÁTICO
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        
        # 🔥 FORÇA download automático para todos os tipos de arquivo
        "download.extensions_to_open": "",
        "plugins.always_open_pdf_externally": True,
        
        # Bloqueia notificações
        "profile.default_content_setting_values.notifications": 2,
        
        # Desabilita salvamento de senhas
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        
        # Desabilita preenchimento automático
        "autofill.profile_enabled": False,
        "autofill.credit_card_enabled": False,
        "autofill.address_enabled": False,
    }
    
    options = Options()
    options.add_experimental_option("prefs", prefs)
    
    # Desabilita a pergunta "Onde salvar"
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Performance e estabilidade
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    
    # Cache mínimo
    options.add_argument("--disable-cache")
    options.add_argument("--disk-cache-size=1")
    options.add_argument("--media-cache-size=1")
    options.add_argument("--aggressive-cache-discard")
    
    # Sem extensões
    options.add_argument("--disable-extensions")
    
    # 🔥 MODO ANÔNIMO - Não herda sessões antigas
    options.add_argument("--incognito")
    
    # Desabilita a barra de "Este tipo de arquivo pode danificar..."
    options.add_argument("--safebrowsing-disable-download-protection")
    options.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")
    
    driver = webdriver.Chrome(options=options)
    
    # 🔥 Configuração adicional via CDP para forçar download automático
    try:
        driver.execute_cdp_cmd('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': download_dir
        })
        print("✅ Download automático configurado via CDP")
    except Exception as e:
        print(f"   ⚠️ CDP download: {e}")
    
    print("✅ Chrome iniciado em modo anônimo com limpeza máxima")
    print(f"📁 Downloads salvos em: {download_dir}")
    
    return driver


def limpar_dados_navegacao(driver):
    """
    Limpa TODOS os dados de navegação do Chrome de forma segura.
    Deve ser chamada APÓS navegar para uma página HTTP(S).
    
    Args:
        driver: Instância ativa do WebDriver do Chrome
    
    Exemplo:
        driver.get('https://google.com')  # Navega primeiro
        limpar_dados_navegacao(driver)     # Depois limpa
    """
    print("\n🧹 LIMPANDO DADOS DE NAVEGAÇÃO...")
    
    # 1. Cookies via Selenium (funciona em qualquer página)
    try:
        driver.delete_all_cookies()
        print("   ✅ Cookies (Selenium)")
    except Exception as e:
        print(f"   ⚠️ Cookies: {e}")
    
    # 2. localStorage e sessionStorage (SÓ funciona em HTTP(S))
    try:
        url_atual = driver.current_url
        if url_atual.startswith('http'):
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            print("   ✅ localStorage/sessionStorage")
        else:
            print("   ⚠️ Storage JS ignorado (URL não é HTTP)")
    except Exception as e:
        print(f"   ⚠️ JS Storage: {str(e)[:80]}...")
    
    # 3. Cache de rede global via CDP
    try:
        driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        print("   ✅ Cache de rede")
    except Exception as e:
        print(f"   ⚠️ Cache CDP: {e}")
    
    # 4. Cookies globais via CDP
    try:
        driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        print("   ✅ Cookies globais (CDP)")
    except Exception as e:
        print(f"   ⚠️ Cookies CDP: {e}")
    
    # 5. Storage da origem atual
    try:
        url_atual = driver.current_url
        if url_atual.startswith('http'):
            driver.execute_cdp_cmd('Storage.clearDataForOrigin', {
                'origin': url_atual,
                'storageTypes': 'all'
            })
            print("   ✅ Storage de origem (CDP)")
        else:
            print("   ⚠️ Storage CDP ignorado (URL não é HTTP)")
    except Exception as e:
        print(f"   ⚠️ Storage CDP: {e}")
    
    print("✅ Limpeza concluída!\n")


def limpar_dados_navegacao_simples(driver):
    """
    Versão simplificada da limpeza - apenas cookies e cache.
    Funciona em qualquer página, inclusive data: e about:blank.
    
    Args:
        driver: Instância ativa do WebDriver do Chrome
    """
    print("\n🧹 LIMPANDO DADOS DE NAVEGAÇÃO (modo simples)...")
    
    try:
        driver.delete_all_cookies()
        print("   ✅ Cookies")
    except:
        pass
    
    try:
        driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        print("   ✅ Cache")
    except:
        pass
    
    try:
        driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        print("   ✅ Cookies (CDP)")
    except:
        pass
    
    print("✅ Limpeza concluída!\n")
