# interface_grafica_local.py
# Interface gráfica do Gerador de Cartões - Versão LOCAL
# Tkinter tradicional - Tema limpo e moderno

import os
import sys
import threading
import pandas as pd
from PIL import Image
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Configurações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tamanho_altura import CONFIG
from redistribuicao import (
    UNIDADES_CONFIG,
    PASTA_CARTOES_GERADOS,
    obter_sigla,
    obter_caminho_unidade,
    garantir_pastas_existem
)
from gerador_cartoes import gerar_pagina_cartao

ALUNOS_POR_PAGINA = 19

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================
CAMINHO_PADRAO_PLANILHA = r"C:\BI_Compartilhado\Repositorio\VsCode\04.CRIAR_CARTAO_AV\[BD]_ALUNOS_AV.xlsx"
ABA_PADRAO = "FINAL"

COLUNAS_ESPERADAS = {
    'RA': 'Registro Acadêmico',
    'NOME': 'Nome completo',
    'GRADE': 'Grade/Horário',
    'TURMA': 'Turma',
    'UNIDADE': 'Unidade escolar',
    'CURSO': 'Nome do curso'
}

# Cores do tema
COR_FUNDO = "#f0f4f8"
COR_CARTAO = "#ffffff"
COR_PRIMARIA = "#2563eb"
COR_SUCESSO = "#059669"
COR_TEXTO = "#1e293b"
COR_TEXTO_CLARO = "#64748b"
COR_BORDA = "#e2e8f0"
COR_VISOR_BG = "#1e293b"
COR_VISOR_TXT = "#4ade80"


class AplicacaoLocal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gerador de Cartões")
        self.root.geometry("1050x640")
        self.root.resizable(True, True)
        self.root.minsize(950, 580)
        self.root.configure(bg=COR_FUNDO)
        
        # Garantir pastas
        garantir_pastas_existem()
        
        # Variáveis de dados
        self.arquivo_selecionado = None
        self.pagina_selecionada = None
        self.paginas_disponiveis = []
        self.df = None
        self.turmas_completas = []
        self.turmas_filtradas = []
        self.alunos_por_turma = {}
        self.checkboxes_vars = []
        
        # Filtros - StringVar
        self.filtro_sigla = tk.StringVar()
        self.filtro_unidade = tk.StringVar()
        self.filtro_curso = tk.StringVar()
        self.filtro_turma = tk.StringVar()
        self.filtro_grade = tk.StringVar()
        
        self.caminho_arquivo_texto = tk.StringVar(value="Planilha padrão carregada")
        
        self.criar_interface()
        self.root.after(500, self.carregar_planilha_padrao)
    
    # =========================================================================
    # INTERFACE
    # =========================================================================
    def criar_interface(self):
        main_frame = tk.Frame(self.root, bg=COR_FUNDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        
        # =====================================================================
        # CABEÇALHO
        # =====================================================================
        header = tk.Frame(main_frame, bg=COR_FUNDO)
        header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header, text="Gerador de Cartões", font=('Segoe UI', 16, 'bold'),
                bg=COR_FUNDO, fg=COR_TEXTO).pack(side=tk.LEFT)
        tk.Label(header, text="v2.0", font=('Segoe UI', 9),
                bg=COR_FUNDO, fg=COR_TEXTO_CLARO).pack(side=tk.LEFT, padx=8)
        
        # =====================================================================
        # LINHA SUPERIOR: ARQUIVO + GERAÇÃO
        # =====================================================================
        linha_superior = tk.Frame(main_frame, bg=COR_FUNDO)
        linha_superior.pack(fill=tk.X, pady=(0, 8))
        
        # ----- ARQUIVO (esquerda) -----
        arquivo_frame = tk.Frame(linha_superior, bg=COR_CARTAO, highlightbackground=COR_BORDA,
                                 highlightthickness=1, padx=12, pady=10)
        arquivo_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(arquivo_frame, text="📂 Arquivo de Dados", font=('Segoe UI', 11, 'bold'),
                bg=COR_CARTAO, fg=COR_TEXTO).pack(anchor='w', pady=(0, 8))
        
        # Linha planilha
        row_arq = tk.Frame(arquivo_frame, bg=COR_CARTAO)
        row_arq.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(row_arq, text="Planilha:", font=('Segoe UI', 9, 'bold'),
                bg=COR_CARTAO, fg=COR_TEXTO, width=9, anchor='w').pack(side=tk.LEFT)
        
        self.label_arquivo = tk.Label(row_arq, textvariable=self.caminho_arquivo_texto,
                                      font=('Segoe UI', 8), bg=COR_CARTAO,
                                      fg=COR_TEXTO_CLARO, anchor='w', wraplength=350)
        self.label_arquivo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        
        tk.Button(row_arq, text="Selecionar", font=('Segoe UI', 8),
                 bg=COR_CARTAO, fg=COR_PRIMARIA, borderwidth=1, relief='solid',
                 cursor='hand2', command=self.selecionar_arquivo).pack(side=tk.RIGHT)
        
        # Linha página + carregar
        row_pag = tk.Frame(arquivo_frame, bg=COR_CARTAO)
        row_pag.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(row_pag, text="Página:", font=('Segoe UI', 9, 'bold'),
                bg=COR_CARTAO, fg=COR_TEXTO, width=9, anchor='w').pack(side=tk.LEFT)
        
        self.pagina_combo = ttk.Combobox(row_pag, width=22, state="disabled", font=('Segoe UI', 9))
        self.pagina_combo.pack(side=tk.LEFT, padx=6)
        self.pagina_combo.bind('<<ComboboxSelected>>', self.selecionar_pagina)
        
        self.btn_carregar = tk.Button(row_pag, text="📊  CARREGAR DADOS",
                                      font=('Segoe UI', 9, 'bold'),
                                      bg=COR_PRIMARIA, fg='white', borderwidth=0,
                                      padx=16, pady=5, cursor='hand2', state='disabled',
                                      command=self.carregar_dados)
        self.btn_carregar.pack(side=tk.RIGHT)
        
        # Colunas
        colunas_texto = "Colunas: " + "  •  ".join(COLUNAS_ESPERADAS.keys())
        tk.Label(arquivo_frame, text=colunas_texto, font=('Segoe UI', 7),
                bg=COR_CARTAO, fg=COR_PRIMARIA).pack(anchor='w', pady=(2, 0))
        
        # ----- GERAÇÃO (direita) -----
        geracao_frame = tk.Frame(linha_superior, bg=COR_CARTAO, highlightbackground=COR_BORDA,
                                 highlightthickness=1, padx=16, pady=12)
        geracao_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        tk.Label(geracao_frame, text="⚡ Geração", font=('Segoe UI', 11, 'bold'),
                bg=COR_CARTAO, fg=COR_TEXTO).pack(pady=(0, 8))
        
        tk.Label(geracao_frame, text="Gerar todos os PDFs simultaneamente:",
                font=('Segoe UI', 9), bg=COR_CARTAO, fg=COR_TEXTO).pack()
        
        self.btn_gerar = tk.Button(geracao_frame, text="📄  GERAR PDFs",
                                   font=('Segoe UI', 11, 'bold'),
                                   bg=COR_SUCESSO, fg='white', borderwidth=0,
                                   padx=24, pady=10, cursor='hand2', state='disabled',
                                   command=self.gerar_pdfs)
        self.btn_gerar.pack(pady=(10, 5))
        
        tk.Label(geracao_frame, text="PDFs por TURMA + GRADE + CURSO\nSalvos direto nas pastas",
                font=('Segoe UI', 7), bg=COR_CARTAO, fg=COR_TEXTO_CLARO, justify='center').pack()
        
        # =====================================================================
        # FILTROS
        # =====================================================================
        filtro_frame = tk.Frame(main_frame, bg=COR_CARTAO, highlightbackground=COR_BORDA,
                                highlightthickness=1, padx=10, pady=8)
        filtro_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(filtro_frame, text="🔍 Filtros", font=('Segoe UI', 11, 'bold'),
                bg=COR_CARTAO, fg=COR_TEXTO).pack(anchor='w', pady=(0, 5))
        
        row_f = tk.Frame(filtro_frame, bg=COR_CARTAO)
        row_f.pack(fill=tk.X)
        
        # Criar filtros como ATRIBUTOS DIRETOS
        self.sigla_combo = self._criar_filtro(row_f, "Sigla", self.filtro_sigla, 8)
        self.unidade_combo = self._criar_filtro(row_f, "Unidade", self.filtro_unidade, 18)
        self.curso_combo = self._criar_filtro(row_f, "Curso", self.filtro_curso, 18)
        self.turma_combo = self._criar_filtro(row_f, "Turma", self.filtro_turma, 14)
        self.grade_combo = self._criar_filtro(row_f, "Grade", self.filtro_grade, 14)
        
        # Bind
        for combo in [self.sigla_combo, self.unidade_combo, self.curso_combo,
                      self.turma_combo, self.grade_combo]:
            combo.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        tk.Button(row_f, text="Limpar", font=('Segoe UI', 8),
                 bg=COR_CARTAO, fg=COR_TEXTO_CLARO, borderwidth=1, relief='solid',
                 cursor='hand2', command=self.limpar_filtros).pack(side=tk.RIGHT, padx=(8, 0))
        
        # =====================================================================
        # LISTA DE TURMAS
        # =====================================================================
        lista_frame = tk.Frame(main_frame, bg=COR_CARTAO, highlightbackground=COR_BORDA,
                               highlightthickness=1, padx=10, pady=8)
        lista_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        tk.Label(lista_frame, text="📋 Turmas Encontradas", font=('Segoe UI', 11, 'bold'),
                bg=COR_CARTAO, fg=COR_TEXTO).pack(anchor='w', pady=(0, 5))
        
        # Botões seleção
        sel_frame = tk.Frame(lista_frame, bg=COR_CARTAO)
        sel_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_sel_todas = tk.Button(sel_frame, text="✓ Selecionar Todas", font=('Segoe UI', 8),
                                       bg=COR_CARTAO, fg=COR_PRIMARIA, borderwidth=1, relief='solid',
                                       cursor='hand2', state='disabled', command=self.selecionar_todas)
        self.btn_sel_todas.pack(side=tk.LEFT, padx=(0, 4))
        
        self.btn_desm_todas = tk.Button(sel_frame, text="✗ Limpar Seleção", font=('Segoe UI', 8),
                                        bg=COR_CARTAO, fg=COR_TEXTO_CLARO, borderwidth=1, relief='solid',
                                        cursor='hand2', state='disabled', command=self.desmarcar_todas)
        self.btn_desm_todas.pack(side=tk.LEFT)
        
        tk.Label(sel_frame, text="19 alunos/página  •  Ordem alfabética",
                font=('Segoe UI', 7), bg=COR_CARTAO, fg=COR_TEXTO_CLARO).pack(side=tk.RIGHT)
        
        # Lista com scroll
        lista_cont = tk.Frame(lista_frame, bg=COR_CARTAO)
        lista_cont.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(lista_cont, bg=COR_CARTAO, highlightthickness=0, height=150)
        scrollbar = ttk.Scrollbar(lista_cont, orient="vertical", command=canvas.yview)
        self.turmas_frame = tk.Frame(canvas, bg=COR_CARTAO)
        
        self.turmas_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.turmas_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # =====================================================================
        # VISOR DE PROCESSAMENTO
        # =====================================================================
        process_frame = tk.Frame(main_frame, bg=COR_CARTAO, highlightbackground=COR_BORDA,
                                 highlightthickness=1, padx=10, pady=8)
        process_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(process_frame, text="💻 Processamento", font=('Segoe UI', 11, 'bold'),
                bg=COR_CARTAO, fg=COR_TEXTO).pack(anchor='w', pady=(0, 5))
        
        visor_container = tk.Frame(process_frame, bg=COR_CARTAO, height=70)
        visor_container.pack(fill=tk.BOTH, expand=True)
        visor_container.pack_propagate(False)
        
        self.visor_texto = tk.Text(visor_container, height=4, width=80,
                                   font=('Consolas', 8), bg=COR_VISOR_BG, fg=COR_VISOR_TXT,
                                   state='disabled', wrap=tk.WORD, relief='flat', borderwidth=0)
        visor_scroll = ttk.Scrollbar(visor_container, orient="vertical", command=self.visor_texto.yview)
        self.visor_texto.configure(yscrollcommand=visor_scroll.set)
        
        self.visor_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        visor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # =====================================================================
        # PROGRESSO + STATUS
        # =====================================================================
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 4))
        self.progress.pack_forget()
        
        self.status_label = tk.Label(main_frame, text="Aguardando carregamento...",
                                     font=('Segoe UI', 8), bg=COR_FUNDO, fg=COR_TEXTO_CLARO)
        self.status_label.pack()
        
        # Centralizar
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 1050) // 2
        y = (self.root.winfo_screenheight() - 640) // 2
        self.root.geometry(f'1050x640+{x}+{y}')
    
    def _criar_filtro(self, parent, label, variable, width):
        """Cria um combo de filtro e retorna o widget"""
        f = tk.Frame(parent, bg=COR_CARTAO)
        f.pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(f, text=label, font=('Segoe UI', 8), bg=COR_CARTAO, fg=COR_TEXTO_CLARO).pack(anchor='w')
        combo = ttk.Combobox(f, textvariable=variable, width=width, state='readonly', font=('Segoe UI', 9))
        combo.pack()
        return combo
    
    # =========================================================================
    # VISOR
    # =========================================================================
    def log_visor(self, mensagem):
        self.root.after(0, self._log, mensagem)
    
    def _log(self, msg):
        self.visor_texto.configure(state='normal')
        self.visor_texto.insert(tk.END, msg + "\n")
        self.visor_texto.see(tk.END)
        self.visor_texto.configure(state='disabled')
    
    def limpar_visor(self):
        self.visor_texto.configure(state='normal')
        self.visor_texto.delete("1.0", tk.END)
        self.visor_texto.configure(state='disabled')
    
    # =========================================================================
    # SELEÇÃO DE ARQUIVO
    # =========================================================================
    def carregar_planilha_padrao(self):
        if os.path.exists(CAMINHO_PADRAO_PLANILHA):
            self.arquivo_selecionado = CAMINHO_PADRAO_PLANILHA
            self.caminho_arquivo_texto.set(CAMINHO_PADRAO_PLANILHA)
            self.label_arquivo.configure(fg=COR_PRIMARIA)
            self.carregar_paginas(aba_padrao=ABA_PADRAO)
            self.status_label.configure(text="📂 Planilha padrão carregada. Carregue os dados.")
        else:
            self.caminho_arquivo_texto.set("Planilha padrão não encontrada")
            self.status_label.configure(text="⚠️ Selecione uma planilha manualmente.")
    
    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione a planilha de dados",
            initialdir=os.path.dirname(CAMINHO_PADRAO_PLANILHA),
            filetypes=[("Excel", "*.xlsx *.xls"), ("CSV", "*.csv"), ("Todos", "*.*")]
        )
        if caminho:
            self.arquivo_selecionado = caminho
            self.caminho_arquivo_texto.set(caminho)
            self.label_arquivo.configure(fg=COR_PRIMARIA)
            self.carregar_paginas()
    
    def carregar_paginas(self, aba_padrao=None):
        try:
            if self.arquivo_selecionado.endswith('.csv'):
                self.pagina_combo['values'] = ['CSV (única)']
                self.pagina_combo.set('CSV (única)')
                self.pagina_combo.config(state="readonly")
                self.pagina_selecionada = 'CSV (única)'
                self.btn_carregar.config(state='normal')
            else:
                xls = pd.ExcelFile(self.arquivo_selecionado)
                self.pagina_combo['values'] = xls.sheet_names
                self.pagina_combo.config(state="readonly")
                
                if aba_padrao and aba_padrao in xls.sheet_names:
                    self.pagina_combo.set(aba_padrao)
                    self.pagina_selecionada = aba_padrao
                    self.btn_carregar.config(state='normal')
                elif ABA_PADRAO in xls.sheet_names:
                    self.pagina_combo.set(ABA_PADRAO)
                    self.pagina_selecionada = ABA_PADRAO
                    self.btn_carregar.config(state='normal')
                else:
                    self.pagina_combo.set('')
                    self.btn_carregar.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def selecionar_pagina(self, event=None):
        p = self.pagina_combo.get()
        if p:
            self.pagina_selecionada = p
            self.btn_carregar.config(state='normal')
    
    # =========================================================================
    # CARREGAR DADOS
    # =========================================================================
    def carregar_dados(self):
        if not self.arquivo_selecionado:
            return
        
        self.limpar_lista_turmas()
        self.limpar_visor()
        self.log_visor("═" * 45)
        self.log_visor("📥 CARREGANDO DADOS...")
        self.log_visor(f"   {os.path.basename(self.arquivo_selecionado)} › {self.pagina_selecionada}")
        
        self.status_label.configure(text="Carregando dados...")
        self.progress.pack(fill=tk.X, pady=(0, 4))
        self.progress.config(mode='indeterminate')
        self.progress.start()
        
        threading.Thread(target=self.processar_carregamento, daemon=True).start()
    
    def processar_carregamento(self):
        try:
            if self.arquivo_selecionado.endswith('.csv'):
                self.df = pd.read_csv(self.arquivo_selecionado)
            else:
                self.df = pd.read_excel(self.arquivo_selecionado, sheet_name=self.pagina_selecionada)
            
            self.log_visor(f"   {len(self.df)} linhas • {len(self.df.columns)} colunas")
            
            faltantes = [c for c in COLUNAS_ESPERADAS if c not in self.df.columns]
            if faltantes:
                self.log_visor(f"❌ Colunas faltantes: {faltantes}")
                msg = "Colunas obrigatórias:\n\n" + "\n".join(f"  ❌ {c}" for c in faltantes)
                msg += f"\n\nEncontradas: {list(self.df.columns)}"
                self.root.after(0, lambda: messagebox.showerror("Erro", msg))
                self.root.after(0, self.finalizar_carregamento)
                return
            
            self.log_visor("✅ Colunas validadas")
            
            self.df = self.df.dropna(subset=list(COLUNAS_ESPERADAS))
            self.df['NOME'] = self.df['NOME'].astype(str).str.strip()
            self.df['RA'] = self.df['RA'].astype(str).str.strip()
            self.df['CURSO'] = self.df['CURSO'].astype(str).str.strip()
            
            self.alunos_por_turma = {}
            self.turmas_completas = []
            
            for (u, c, g, t), grupo in self.df.groupby(['UNIDADE', 'CURSO', 'GRADE', 'TURMA']):
                alunos = grupo[['RA', 'NOME']].sort_values('NOME').to_dict('records')
                self.alunos_por_turma[(u, c, g, t)] = alunos
                self.turmas_completas.append((u, c, g, t))
            
            self.turmas_filtradas = self.turmas_completas.copy()
            
            self.log_visor(f"✅ {len(self.turmas_completas)} turmas • {len(self.df)} alunos")
            self.log_visor("═" * 45)
            
            self.root.after(0, self.atualizar_opcoes_filtros)
            self.root.after(0, self.exibir_lista_turmas)
            self.root.after(0, lambda: self.status_label.configure(
                text=f"✅ {len(self.turmas_completas)} turmas • Selecione e gere os PDFs"))
            self.root.after(0, self.finalizar_carregamento)
            
        except Exception as e:
            self.log_visor(f"❌ ERRO: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro", str(e)))
            self.root.after(0, self.finalizar_carregamento)
    
    # =========================================================================
    # LISTA E FILTROS
    # =========================================================================
    def limpar_lista_turmas(self):
        for w in self.turmas_frame.winfo_children():
            w.destroy()
        self.checkboxes_vars.clear()
    
    def aplicar_filtros(self, event=None):
        if not self.turmas_completas:
            return
        sf, uf, cf, tf, gf = (self.filtro_sigla.get(), self.filtro_unidade.get(),
                               self.filtro_curso.get(), self.filtro_turma.get(),
                               self.filtro_grade.get())
        self.turmas_filtradas = []
        for u, c, g, t in self.turmas_completas:
            sigla = UNIDADES_CONFIG.get(u, {}).get('sigla', '')
            if sf and sigla != sf: continue
            if uf and u != uf: continue
            if cf and c != cf: continue
            if tf and t != tf: continue
            if gf and g != gf: continue
            self.turmas_filtradas.append((u, c, g, t))
        self.exibir_lista_turmas()
    
    def limpar_filtros(self):
        for v in [self.filtro_sigla, self.filtro_unidade, self.filtro_curso,
                  self.filtro_turma, self.filtro_grade]:
            v.set("")
        self.turmas_filtradas = self.turmas_completas.copy()
        self.exibir_lista_turmas()
    
    def atualizar_opcoes_filtros(self):
        if not self.turmas_completas:
            return
        siglas, unidades, cursos, turmas, grades = set(), set(), set(), set(), set()
        for u, c, g, t in self.turmas_completas:
            siglas.add(UNIDADES_CONFIG.get(u, {}).get('sigla', ''))
            unidades.add(u); cursos.add(c); turmas.add(t); grades.add(g)
        
        self.sigla_combo['values'] = [''] + sorted(siglas)
        self.unidade_combo['values'] = [''] + sorted(unidades)
        self.curso_combo['values'] = [''] + sorted(cursos)
        self.turma_combo['values'] = [''] + sorted(turmas)
        self.grade_combo['values'] = [''] + sorted(grades)
    
    def exibir_lista_turmas(self):
        self.limpar_lista_turmas()
        
        if not self.turmas_filtradas:
            tk.Label(self.turmas_frame, text="Nenhuma turma com os filtros selecionados.",
                    font=('Segoe UI', 10), bg=COR_CARTAO, fg=COR_TEXTO_CLARO).pack(pady=25)
            self.btn_sel_todas.config(state='disabled')
            self.btn_desm_todas.config(state='disabled')
            self.btn_gerar.config(state='disabled')
            return
        
        # Cabeçalho
        h = tk.Frame(self.turmas_frame, bg='#f1f5f9')
        h.pack(fill=tk.X, pady=(0, 2))
        
        for txt, w in [("", 3), ("Sigla", 7), ("Unidade", 22), ("Curso", 22),
                       ("Turma", 16), ("Grade", 14), ("Alunos", 8), ("Págs", 6)]:
            tk.Label(h, text=txt, font=('Segoe UI', 8, 'bold'), bg='#f1f5f9',
                    fg=COR_TEXTO, width=w, anchor='w').pack(side=tk.LEFT, padx=1)
        
        # Linhas
        for u, c, g, t in self.turmas_filtradas:
            var = tk.BooleanVar(value=False)
            self.checkboxes_vars.append(var)
            
            f = tk.Frame(self.turmas_frame, bg=COR_CARTAO)
            f.pack(fill=tk.X, pady=1)
            
            tk.Checkbutton(f, variable=var, bg=COR_CARTAO, activebackground=COR_CARTAO,
                          highlightthickness=0).pack(side=tk.LEFT, padx=2)
            
            sigla = UNIDADES_CONFIG.get(u, {}).get('sigla', '--')
            for txt, w in [(sigla, 7), (u, 22), (c, 22), (t, 16), (g, 14)]:
                tk.Label(f, text=txt, font=('Segoe UI', 8), bg=COR_CARTAO,
                        fg=COR_TEXTO, width=w, anchor='w', wraplength=w*7).pack(side=tk.LEFT, padx=1)
            
            qtd = len(self.alunos_por_turma.get((u, c, g, t), []))
            pag = (qtd + 18) // 19
            tk.Label(f, text=str(qtd), font=('Segoe UI', 8), bg=COR_CARTAO,
                    fg=COR_TEXTO, width=8, anchor='center').pack(side=tk.LEFT)
            tk.Label(f, text=str(pag), font=('Segoe UI', 8), bg=COR_CARTAO,
                    fg=COR_TEXTO_CLARO, width=6, anchor='center').pack(side=tk.LEFT)
        
        self.btn_sel_todas.config(state='normal')
        self.btn_desm_todas.config(state='normal')
        self.btn_gerar.config(state='normal')
        self.status_label.configure(text=f"{len(self.turmas_filtradas)} turmas • Selecione e clique em GERAR PDFs")
    
    def finalizar_carregamento(self):
        self.progress.stop()
        self.progress.pack_forget()
    
    def selecionar_todas(self):
        for v in self.checkboxes_vars: v.set(True)
    def desmarcar_todas(self):
        for v in self.checkboxes_vars: v.set(False)
    
    # =========================================================================
    # GERAÇÃO DE PDFs
    # =========================================================================
    def gerar_pdfs(self):
        turmas_sel = [self.turmas_filtradas[i] for i, v in enumerate(self.checkboxes_vars) if v.get()]
        if not turmas_sel:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma turma.")
            return
        
        if not messagebox.askyesno("Confirmar",
            f"Gerar PDFs para {len(turmas_sel)} turma(s)?\n\n"
            "✅ PDFs por TURMA\n✅ COMPACTADOS por GRADE\n✅ COMPACTADOS por CURSO\n\n"
            "📁 Salvos direto nas pastas das unidades"):
            return
        
        self.limpar_visor()
        self.log_visor("═" * 45)
        self.log_visor("🚀 INICIANDO GERAÇÃO")
        self.log_visor(f"   Turmas: {len(turmas_sel)}")
        self.log_visor("═" * 45)
        
        self.status_label.configure(text="Gerando PDFs...")
        self.progress.pack(fill=tk.X, pady=(0, 4))
        self.progress.config(mode='determinate', maximum=100, value=0)
        self.btn_gerar.config(state='disabled')
        self.btn_sel_todas.config(state='disabled')
        self.btn_desm_todas.config(state='disabled')
        
        threading.Thread(target=self.processar_geracao, args=(turmas_sel,), daemon=True).start()
    
    def processar_geracao(self, turmas_sel):
        try:
            pdfs = self.gerar_todos_pdfs(turmas_sel)
            tn = len([p for p in pdfs if p['tipo'] == 'TURMA'])
            gn = len([p for p in pdfs if p['tipo'] == 'GRADE_COMPACTADO'])
            cn = len([p for p in pdfs if p['tipo'] == 'CURSO_COMPACTADO'])
            
            self.log_visor("═" * 45)
            self.log_visor(f"✅ {len(pdfs)} PDFS GERADOS!")
            self.log_visor(f"   📄 Turmas: {tn}  •  📦 Grades: {gn}  •  📦 Cursos: {cn}")
            self.log_visor("═" * 45)
            
            self.root.after(0, lambda: self.progress.configure(value=100))
            self.root.after(0, lambda: messagebox.showinfo("Sucesso!",
                f"{len(pdfs)} PDFs gerados!\n\n📄 Turmas: {tn}\n📦 Grades: {gn}\n📦 Cursos: {cn}"))
            
        except Exception as e:
            self.log_visor(f"❌ ERRO: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro", str(e)))
        finally:
            self.root.after(0, self.finalizar_geracao)
    
    # =========================================================================
    # GERAÇÃO DOS 3 TIPOS
    # =========================================================================
    def gerar_todos_pdfs(self, turmas_sel):
        import shutil
        pdfs = []
        garantir_pastas_existem()
        
        # ETAPA 1: TURMA
        self.log_visor("\n📄 ETAPA 1/3: PDFs por TURMA...")
        self.root.after(0, lambda: self.progress.configure(value=10))
        
        for idx, (u, c, g, t) in enumerate(turmas_sel):
            alunos = self.alunos_por_turma.get((u, c, g, t), [])
            if not alunos: continue
            alunos_n = [{'RA': a['RA'], 'NOME': a['NOME']} for a in alunos]
            paginas = [gerar_pagina_cartao(alunos_n[i:i+19], u, t) for i in range(0, len(alunos_n), 19)]
            if not paginas: continue
            
            nome = f"{t}_{c}_{g}.pdf"
            nome = "".join(x for x in nome if x.isalnum() or x in '._- ')
            pasta = os.path.join(obter_caminho_unidade(u), c, g)
            os.makedirs(pasta, exist_ok=True)
            self._salvar_pdf(paginas, os.path.join(pasta, nome))
            
            pdfs.append({'arquivo': os.path.join(pasta, nome), 'tipo': 'TURMA'})
            self.log_visor(f"   ✅ {nome} ({len(alunos)} alunos)")
            self.root.after(0, lambda p=10+int((idx+1)/len(turmas_sel)*25): self.progress.configure(value=p))
        
        # ETAPA 2: GRADE
        self.log_visor("\n📦 ETAPA 2/3: COMPACTADOS por GRADE...")
        self.root.after(0, lambda: self.progress.configure(value=40))
        
        grupos_g = {}
        for (u, c, g, t) in turmas_sel: grupos_g.setdefault((u, c, g), []).append(t)
        
        for idx_g, ((u, c, g), turmas_g) in enumerate(grupos_g.items()):
            turmas_g.sort()
            todas, total_a = [], 0
            for t in turmas_g:
                alunos = self.alunos_por_turma.get((u, c, g, t), [])
                if not alunos: continue
                total_a += len(alunos)
                for i in range(0, len(alunos), 19):
                    todas.append(gerar_pagina_cartao([{'RA': a['RA'], 'NOME': a['NOME']} for a in alunos[i:i+19]], u, t))
            if not todas: continue
            
            sigla = obter_sigla(u)
            nome = f"{sigla}_{g}_COMPACTADO.pdf"
            nome = "".join(x for x in nome if x.isalnum() or x in '._- ')
            pasta = os.path.join(obter_caminho_unidade(u), c, g)
            os.makedirs(pasta, exist_ok=True)
            self._salvar_pdf(todas, os.path.join(pasta, nome))
            
            pdfs.append({'arquivo': os.path.join(pasta, nome), 'tipo': 'GRADE_COMPACTADO'})
            self.log_visor(f"   ✅ {nome} ({total_a} alunos, {len(turmas_g)} turmas)")
            self.root.after(0, lambda p=40+int((idx_g+1)/len(grupos_g)*25): self.progress.configure(value=p))
        
        # ETAPA 3: CURSO
        self.log_visor("\n📦 ETAPA 3/3: COMPACTADOS por CURSO...")
        self.root.after(0, lambda: self.progress.configure(value=70))
        
        grupos_c = {}
        for (u, c, g, t) in turmas_sel: grupos_c.setdefault((u, c), []).append((g, t))
        
        for idx_c, ((u, c), turmas_c) in enumerate(grupos_c.items()):
            turmas_c.sort(key=lambda x: x[1])
            todas, total_a = [], 0
            for (g, t) in turmas_c:
                alunos = self.alunos_por_turma.get((u, c, g, t), [])
                if not alunos: continue
                total_a += len(alunos)
                for i in range(0, len(alunos), 19):
                    todas.append(gerar_pagina_cartao([{'RA': a['RA'], 'NOME': a['NOME']} for a in alunos[i:i+19]], u, t))
            if not todas: continue
            
            sigla = obter_sigla(u)
            nome = f"{sigla}_{c}_COMPACTADO.pdf"
            nome = "".join(x for x in nome if x.isalnum() or x in '._- ')
            pasta = os.path.join(obter_caminho_unidade(u), c)
            os.makedirs(pasta, exist_ok=True)
            self._salvar_pdf(todas, os.path.join(pasta, nome))
            
            pdfs.append({'arquivo': os.path.join(pasta, nome), 'tipo': 'CURSO_COMPACTADO'})
            self.log_visor(f"   ✅ {nome} ({total_a} alunos, {len(turmas_c)} turmas)")
            self.root.after(0, lambda p=70+int((idx_c+1)/len(grupos_c)*25): self.progress.configure(value=p))
        
        self.root.after(0, lambda: self.progress.configure(value=100))
        return pdfs
    
    def _salvar_pdf(self, paginas, caminho):
        primeira = paginas[0]
        demais = paginas[1:] if len(paginas) > 1 else []
        try:
            if demais:
                primeira.save(caminho, "PDF", save_all=True, append_images=demais, resolution=100.0)
            else:
                primeira.save(caminho, "PDF", resolution=100.0)
        except:
            import tempfile
            pngs = []
            for idx, p in enumerate(paginas):
                png = os.path.join(tempfile.gettempdir(), f"_ct_{idx}.png")
                p.save(png, "PNG"); pngs.append(png)
            imgs = [Image.open(p).convert('RGB') for p in pngs]
            imgs[0].save(caminho, "PDF", save_all=True, append_images=imgs[1:], resolution=100.0)
            for p in pngs:
                try: os.remove(p)
                except: pass
    
    def finalizar_geracao(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_gerar.config(state='normal')
        self.btn_sel_todas.config(state='normal')
        self.btn_desm_todas.config(state='normal')
    
    def executar(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AplicacaoLocal()
    app.executar()
