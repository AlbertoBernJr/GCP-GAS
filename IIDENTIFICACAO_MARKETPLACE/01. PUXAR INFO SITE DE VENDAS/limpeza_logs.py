"""
Módulo de Limpeza de Logs
Versão: 1.0

Gerencia a pasta de logs, mantendo no máximo 30 arquivos.
Remove os mais antigos quando o limite é excedido.
"""

import os
import glob


def limpar_logs_excedentes(pasta_logs=None, max_arquivos=30):
    """
    Verifica a quantidade de arquivos na pasta de logs.
    Se houver mais que max_arquivos, remove os mais antigos.
    
    Args:
        pasta_logs: Caminho da pasta de logs. Se None, usa a pasta padrão.
        max_arquivos: Número máximo de arquivos a manter (padrão: 30)
    
    Returns:
        tuple: (total_antes, removidos, total_depois)
    """
    # Se não especificar pasta, usa a pasta logs do projeto
    if pasta_logs is None:
        pasta_logs = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'logs'
        )
    
    # Cria a pasta se não existir
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)
        print(f"📁 Pasta de logs criada: {pasta_logs}")
        return (0, 0, 0)
    
    # Lista todos os arquivos .log
    arquivos_log = glob.glob(os.path.join(pasta_logs, '*.log'))
    total_antes = len(arquivos_log)
    
    # Se estiver dentro do limite, não faz nada
    if total_antes <= max_arquivos:
        return (total_antes, 0, total_antes)
    
    # Ordena por data de modificação (mais recente primeiro)
    arquivos_log.sort(key=os.path.getmtime, reverse=True)
    
    # Remove os excedentes (mais antigos)
    arquivos_para_remover = arquivos_log[max_arquivos:]
    removidos = 0
    
    for arquivo in arquivos_para_remover:
        try:
            os.remove(arquivo)
            removidos += 1
        except Exception as e:
            print(f"   ⚠️ Erro ao remover {os.path.basename(arquivo)}: {e}")
    
    total_depois = total_antes - removidos
    
    if removidos > 0:
        print(f"🧹 Logs: {removidos} antigo(s) removido(s) ({total_antes} → {total_depois})")
    
    return (total_antes, removidos, total_depois)


def verificar_quantidade_logs(pasta_logs=None):
    """
    Retorna a quantidade de arquivos de log na pasta.
    
    Args:
        pasta_logs: Caminho da pasta de logs
    
    Returns:
        int: Quantidade de arquivos .log
    """
    if pasta_logs is None:
        pasta_logs = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'logs'
        )
    
    if not os.path.exists(pasta_logs):
        return 0
    
    return len(glob.glob(os.path.join(pasta_logs, '*.log')))


def obter_mais_antigo(pasta_logs=None):
    """
    Retorna o nome do arquivo de log mais antigo.
    
    Args:
        pasta_logs: Caminho da pasta de logs
    
    Returns:
        str or None: Nome do arquivo mais antigo
    """
    if pasta_logs is None:
        pasta_logs = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'logs'
        )
    
    if not os.path.exists(pasta_logs):
        return None
    
    arquivos = glob.glob(os.path.join(pasta_logs, '*.log'))
    if not arquivos:
        return None
    
    arquivos.sort(key=os.path.getmtime)
    return os.path.basename(arquivos[0])


def obter_mais_recente(pasta_logs=None):
    """
    Retorna o nome do arquivo de log mais recente.
    
    Args:
        pasta_logs: Caminho da pasta de logs
    
    Returns:
        str or None: Nome do arquivo mais recente
    """
    if pasta_logs is None:
        pasta_logs = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'logs'
        )
    
    if not os.path.exists(pasta_logs):
        return None
    
    arquivos = glob.glob(os.path.join(pasta_logs, '*.log'))
    if not arquivos:
        return None
    
    arquivos.sort(key=os.path.getmtime, reverse=True)
    return os.path.basename(arquivos[0])
