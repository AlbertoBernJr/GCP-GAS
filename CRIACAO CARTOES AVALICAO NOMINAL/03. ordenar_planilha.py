# ordenar_planilha.py
# Ordena a planilha de alunos usando a MESMA lógica do gerador de cartões
# Assim o Google Sheets e o sistema ficam com a mesma ordem

import pandas as pd
import os
from datetime import datetime

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

CAMINHO_PLANILHA = r"C:\BI_Compartilhado\Repositorio\VsCode\04.CRIAR_CARTAO_AV\[BD]_ALUNOS_AV.xlsx"
ABA = "FINAL"  # Aba a ser ordenada
COLUNA_NOME = "NOME"  # Coluna B = NOME

# =============================================================================
# FUNÇÃO DE ORDENAÇÃO (MESMA LÓGICA DO SISTEMA)
# =============================================================================

def ordenar_planilha():
    """Ordena a planilha usando a mesma lógica do gerador de cartões"""
    
    print("=" * 60)
    print("🔤 ORDENADOR DE PLANILHA - MESMA LÓGICA DO SISTEMA")
    print("=" * 60)
    
    # 1. Verificar se arquivo existe
    if not os.path.exists(CAMINHO_PLANILHA):
        print(f"\n❌ ERRO: Planilha não encontrada!")
        print(f"   Caminho: {CAMINHO_PLANILHA}")
        input("\nPressione Enter para sair...")
        return
    
    print(f"\n📥 Lendo planilha: {CAMINHO_PLANILHA}")
    
    try:
        # 2. Fazer backup antes de modificar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_backup = CAMINHO_PLANILHA.replace('.xlsx', f'_BACKUP_{timestamp}.xlsx')
        
        import shutil
        shutil.copy2(CAMINHO_PLANILHA, caminho_backup)
        print(f"💾 Backup criado: {os.path.basename(caminho_backup)}")
        
        # 3. Ler a planilha
        df = pd.read_excel(CAMINHO_PLANILHA, sheet_name=ABA)
        
        print(f"\n📊 DADOS ORIGINAIS:")
        print(f"   Linhas: {len(df)}")
        print(f"   Colunas: {list(df.columns)}")
        
        # Mostrar primeiros 5 nomes (ANTES)
        if COLUNA_NOME in df.columns:
            print(f"\n   Primeiros 5 nomes (ANTES):")
            for i, nome in enumerate(df[COLUNA_NOME].dropna().head(5), 1):
                print(f"   {i}. {nome}")
        
        # 4. APLICAR A MESMA ORDENAÇÃO DO SISTEMA
        # O sistema faz: .sort_values('NOME') 
        # que é ordenação alfabética padrão do pandas (Unicode)
        
        if COLUNA_NOME not in df.columns:
            print(f"\n❌ ERRO: Coluna '{COLUNA_NOME}' não encontrada!")
            print(f"   Colunas disponíveis: {list(df.columns)}")
            input("\nPressione Enter para sair...")
            return
        
        # Limpar e padronizar nomes (igual o sistema faz)
        df[COLUNA_NOME] = df[COLUNA_NOME].astype(str).str.strip()
        
        # ORDENAR (MESMA LÓGICA)
        df_ordenado = df.sort_values(COLUNA_NOME, ascending=True)
        df_ordenado = df_ordenado.reset_index(drop=True)
        
        print(f"\n📊 DADOS ORDENADOS:")
        print(f"   Linhas: {len(df_ordenado)}")
        
        # Mostrar primeiros 5 nomes (DEPOIS)
        print(f"\n   Primeiros 5 nomes (DEPOIS):")
        for i, nome in enumerate(df_ordenado[COLUNA_NOME].dropna().head(5), 1):
            print(f"   {i}. {nome}")
        
        # Mostrar últimos 5 nomes
        print(f"\n   Últimos 5 nomes (DEPOIS):")
        for i, nome in enumerate(df_ordenado[COLUNA_NOME].dropna().tail(5), 1):
            print(f"   {i}. {nome}")
        
        # 5. Verificar se mudou algo
        if df.equals(df_ordenado):
            print(f"\n⚠️ A planilha JÁ ESTÁ na ordem correta!")
            print(f"   Nenhuma alteração necessária.")
            # Remover backup se não houve mudança
            os.remove(caminho_backup)
            print(f"   Backup removido (desnecessário).")
        else:
            # 6. Salvar planilha ordenada
            print(f"\n💾 Salvando planilha ordenada...")
            
            with pd.ExcelWriter(CAMINHO_PLANILHA, engine='openpyxl') as writer:
                df_ordenado.to_excel(writer, sheet_name=ABA, index=False)
            
            print(f"✅ Planilha salva com sucesso!")
            print(f"📁 Backup mantido em: {os.path.basename(caminho_backup)}")
            
            # Mostrar diferenças
            mudancas = 0
            for i in range(len(df)):
                if df.iloc[i][COLUNA_NOME] != df_ordenado.iloc[i][COLUNA_NOME]:
                    mudancas += 1
            
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"   Total de linhas: {len(df)}")
            print(f"   Linhas que mudaram de posição: {mudancas}")
            print(f"   Método: sort_values('{COLUNA_NOME}') - padrão Unicode")
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 ORDENAÇÃO CONCLUÍDA")
    print("=" * 60)
    input("\nPressione Enter para sair...")


# =============================================================================
# EXECUTAR
# =============================================================================
if __name__ == "__main__":
    ordenar_planilha()
