import tkinter as tk
from tkinter import ttk
import webbrowser
import pandas as pd
import tkinter.messagebox as tkm
import threading
import time

bases_sisu = {
    "2016-1": {"ano": 2016, "semestre": 1, "encoding": "utf-8", "delimiter": "|"},
    "2016-2": {"ano": 2016, "semestre": 2, "encoding": "utf-8", "delimiter": "|"},
    "2017-1": {"ano": 2017, "semestre": 1, "encoding": "cp1252", "delimiter": "|"},
    "2017-2": {"ano": 2017, "semestre": 2, "encoding": "utf-8", "delimiter": ";"},
    "2018-1": {"ano": 2018, "semestre": 1, "encoding": "cp1252", "delimiter": "|"},
    "2018-2": {"ano": 2018, "semestre": 2, "encoding": "utf-8", "delimiter": ";"},
    "2019-1": {"ano": 2019, "semestre": 1, "encoding": "utf-8", "delimiter": ";"},
    "2019-2": {"ano": 2019, "semestre": 2, "encoding": "utf-8", "delimiter": ";"},
    "2020-1": {"ano": 2020, "semestre": 1, "encoding": "utf-8", "delimiter": ";"},
    "2020-2": {"ano": 2020, "semestre": 2, "encoding": "utf-8", "delimiter": ";"},
    "2021-1": {"ano": 2021, "semestre": 1, "encoding": "utf-8", "delimiter": ";"},
    "2021-2": {"ano": 2021, "semestre": 2, "encoding": "cp1252", "delimiter": "|"},
    "2022-1": {"ano": 2022, "semestre": 1, "encoding": "cp1252", "delimiter": "|"},
    "2022-2": {"ano": 2022, "semestre": 2, "encoding": "cp1252", "delimiter": "|"},
}

def selecionar_colunas(chave, dados_sisu, dados_enem):

    enem = dados_enem[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO', 'TP_SEXO', 'Q001', 'Q002', 'Q003', 'Q004', 'Q005', 'Q006', 'Q022', 'Q024', 'Q025']].copy()

    enem = enem.rename(columns={'NU_NOTA_CN': 'CN', 'NU_NOTA_CH': 'CH', 'NU_NOTA_LC': 'LC', 'NU_NOTA_MT': 'MT', 'NU_NOTA_REDACAO': 'REDACAO', 'TP_SEXO': 'SEXO'})

    if chave in ["2016-1", "2016-2"]:
        sisu = dados_sisu[['nu_nota_cn', 'nu_nota_ch', 'nu_nota_l', 'nu_nota_m', 'nu_nota_r', 'nota_concorrencia', 'nu_notacorte', 'tp_sexo', 'nome_curso', 'dt_nascimento', 'uf_origem', 'municipio_candidato', 'st_aprovado', 'nu_ano', 'nu_edicao', 'sigla_ies', 'campus']].copy()
        sisu = sisu.rename(columns={'nu_nota_l': 'LC', 'nu_nota_ch': 'CH', 'nu_nota_cn': 'CN', 'nu_nota_m': 'MT', 'nu_nota_r': 'REDACAO'})
        
    elif chave in ["2018-1", "2021-2", "2022-1", "2022-2"]:
        sisu = dados_sisu[['NOTA_CN', 'NOTA_CH', 'NOTA_L', 'NOTA_M', 'NOTA_R', 'NOTA_CANDIDATO', 'NOTA_CORTE', 'SEXO', 'NOME_CURSO', 'DATA_NASCIMENTO', 'UF_CANDIDATO', 'MUNICIPIO_CANDIDATO', 'APROVADO','ANO', 'EDICAO', 'SIGLA_IES', 'NOME_CAMPUS']].copy()
        sisu = sisu.rename(columns={'NOTA_L': 'LC', 'NOTA_CH': 'CH', 'NOTA_CN': 'CN', 'NOTA_M': 'MT', 'NOTA_R': 'REDACAO'})

    else:
        sisu = dados_sisu[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_L', 'NU_NOTA_M', 'NU_NOTA_R', 'NU_NOTA_CANDIDATO', 'NU_NOTACORTE', 'TP_SEXO', 'NO_CURSO', 'DT_NASCIMENTO', 'SG_UF_CANDIDATO', 'MUNICIPIO_CANDIDATO', 'ST_APROVADO', 'NU_ANO', 'NU_EDICAO', 'SIGLA_IES', 'NO_CAMPUS']].copy()
        sisu = sisu.rename(columns={'NU_NOTA_L': 'LC', 'NU_NOTA_CH': 'CH', 'NU_NOTA_CN': 'CN', 'NU_NOTA_M': 'MT', 'NU_NOTA_R': 'REDACAO'})

    return sisu, enem

def filtrar_instituicao(chave, sisu, cod_instituicao):
    if chave in ["2016-1", "2016-2"]:
        sisu = sisu[sisu["cod_ies"] == cod_instituicao]
    elif chave in ["2018-1", "2021-2", "2022-1", "2022-2"]:
        sisu = sisu[sisu['CODIGO_IES'] == cod_instituicao]
    else:
        sisu = sisu[sisu['CO_IES'] == cod_instituicao]
    
    return sisu

def filtrar_campus(chave, sisu, cod_campus):
    if chave in ["2016-1", "2016-2"]:
        sisu = sisu[sisu["cod_campus"] == cod_campus]
    elif chave in ["2018-1", "2021-2", "2022-1", "2022-2"]:
        sisu = sisu[sisu['CODIGO_CAMPUS'] == cod_campus]
    else:
        sisu = sisu[sisu['CO_CAMPUS'] == cod_campus]
    
    return sisu

def processar_base(chave, sisu, enem):
    
    colunas = ['CH', 'CN', 'MT', 'LC', 'REDACAO']
    
    for col in colunas:
        if col in sisu.columns:
            sisu.loc[:, col] = sisu[col].astype(str).str.replace(',', '.').astype(float)
    
    colunas_com_nan = sisu.columns[sisu.isnull().any()].tolist()

    if len(colunas_com_nan) > 0:
        if chave in ["2016-1", "2016-2"]:
            sisu['nu_notacorte'] = pd.to_numeric(sisu['nu_notacorte'], errors='coerce')
            sisu['nu_notacorte'] = sisu.groupby('nome_curso')['nu_notacorte'].transform(lambda x: x.fillna(x.mean()))

        elif chave in ["2018-1", "2021-2", "2022-1", "2022-2"]:
            sisu['NOTA_CORTE'] = pd.to_numeric(sisu['NOTA_CORTE'], errors='coerce')
            sisu['NOTA_CORTE'] = sisu.groupby('NOME_CURSO')['NOTA_CORTE'].transform(lambda x: x.fillna(x.mean()))

        else:
            sisu['NU_NOTACORTE'] = pd.to_numeric(sisu['NU_NOTACORTE'], errors='coerce')
            sisu['NU_NOTACORTE'] = sisu.groupby('NO_CURSO')['NU_NOTACORTE'].transform(lambda x: x.fillna(x.mean()))



    for col in colunas:
        if col in enem.columns:
            enem.loc[:, col] = enem[col].round(2).astype(float)
        if col in sisu.columns:
            sisu.loc[:, col] = sisu[col].round(2).astype(float)

    return sisu, enem

def mesclar_base(sisu, enem):
    return pd.merge(sisu, enem, on=['CH', 'CN', 'MT', 'LC', 'REDACAO'], how='inner')


def abrir_link():
    webbrowser.open("https://emec.mec.gov.br/emec/nova")

def gerar_edicoes(ano_inicial, semestre_inicial, ano_final, semestre_final):
    edicoes = []
    for ano in range(ano_inicial, ano_final + 1):
        for semestre in range(1, 3):
            if ano == ano_inicial and semestre < semestre_inicial:
                continue
            if ano == ano_final and semestre > semestre_final:
                continue
            edicoes.append((ano, semestre))
    return edicoes

def parametros(ano_inicial, ano_final, semestre_inicial, semestre_final, cod_campus, cod_instituicao):

    ano_inicial = int(ano_inicial)
    semestre_inicial = int(semestre_inicial)
    ano_final = int(ano_final)
    semestre_final = int(semestre_final)

    if cod_instituicao != "":
        cod_instituicao = int(cod_instituicao)
    else:
        cod_instituicao = None

    if cod_campus != "":
        cod_campus = int(cod_campus)
    else:
        cod_campus = None

    return ano_inicial, ano_final, semestre_inicial, semestre_final, cod_campus, cod_instituicao

cronometro_ativo = False
tempo_inicial = 0

def atualizar_cronometro():
    global tempo_inicial, cronometro_ativo
    while cronometro_ativo:
        tempo_decorrido = time.time() - tempo_inicial
        minutos = int(tempo_decorrido // 60)
        segundos = int(tempo_decorrido % 60)
        cronometro_label.config(text=f"Tempo decorrido: {minutos} minutos e {segundos} segundos")
        time.sleep(1)

def fechar_programa():
    root.destroy()

def gerar_base():
    global tempo_inicial, cronometro_ativo
    cronometro_ativo = True
    tempo_inicial = time.time()

    todas_bases = []

    threading.Thread(target=atualizar_cronometro, daemon=True).start()
    
    ano_inicial = var_ano_inicial.get()
    ano_final = var_ano_final.get()
    semestre_inicial = var_semestre_inicial.get()
    semestre_final = var_semestre_final.get()
    cod_instituicao = entry_cod_instituicao.get()
    cod_campus = entry_cod_campus.get()
    
    ano_inicial, ano_final, semestre_inicial, semestre_final, cod_campus, cod_instituicao = parametros(ano_inicial, ano_final, semestre_inicial, semestre_final, cod_campus, cod_instituicao)

    edicoes = gerar_edicoes(ano_inicial, semestre_inicial, ano_final, semestre_final)

    for ano, semestre in edicoes:
        chave = f"{ano}-{semestre}"

        endereco_ENEM = f'./DADOS/ENEM/microdados_enem_{ano-1}/DADOS/microdados_enem_{ano-1}.csv'
        endereco_SISU = f'./DADOS/SISU/ListagemChamadaRegular_{ano}-{semestre}/ListagemChamadaRegular_{ano}-{semestre}.csv'
        delimiter_SISU = bases_sisu[chave]["delimiter"]
        encoding_SISU = bases_sisu[chave]["encoding"]

        dados_enem = pd.read_csv(endereco_ENEM, delimiter=";", encoding="cp1252")
        dados_sisu = pd.read_csv(endereco_SISU, delimiter=delimiter_SISU, encoding=encoding_SISU, low_memory=False)


        if cod_instituicao != None:
            dados_sisu = filtrar_instituicao(chave, dados_sisu, cod_instituicao)

        if cod_campus !=  None:
            dados_sisu = filtrar_campus(chave, dados_sisu, cod_campus)

        sisu, enem = selecionar_colunas(chave, dados_sisu, dados_enem)


        sisu, enem = processar_base(chave, sisu, enem)


        base_mesclada = mesclar_base(sisu, enem)

        print(f'Base {ano}-{semestre} concluída!')
        print(f' - Nesta edição a instituição ou campus obteve {len(sisu)} inscrições e a base mesclada tem {len(base_mesclada)} linhas')


        colunas_padronizadas = ['CN', 'CH', 'LC', 'MT', 'REDACAO', 'NOTA_GERAL', 'NOTA_CORTE', 'SEXO_S', 'CURSO', 'DATA DE NASCIMENTO', 'UF', 'MUNICIPIO', 'APROVADO','ANO', 'EDICAO', 'SIGLA_IES', 'CAMPUS','SEXO_E', 'Q001', 'Q002', 'Q003', 'Q004', 'Q005', 'Q006', 'Q022', 'Q024', 'Q025']
        base_mesclada.columns = colunas_padronizadas
        todas_bases.append(base_mesclada)


        progress['value'] += 100 / len(edicoes)
        root.update_idletasks()

    Base_Final = pd.concat(todas_bases, ignore_index=True)
    Base_Final.insert(0, 'ID', range(1, len(Base_Final) + 1))

    Base_Final.to_excel('./BaseFinal.xlsx', index=False)

    tkm.showinfo("Concluído", "A base de dados foi gerada com sucesso!")

    cronometro_ativo = False
    cronometro_label.config(text="Processo concluído!")

root = tk.Tk()
root.title("Gerador de Base de Dados Filtrada")
root.geometry("500x500")
root.resizable(False, False)

anos = ["2016", "2017", "2018", "2019", "2020", "2021", "2022"]
semestres = ["1", "2"]

frame = tk.Frame(root)
frame.pack(expand=True)

tk.Label(frame, text="Ano Inicial:").grid(row=0, column=0, padx=10, pady=5)
var_ano_inicial = tk.StringVar(value=anos[0])
lista_ano_inicial = tk.OptionMenu(frame, var_ano_inicial, *anos)
lista_ano_inicial.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Ano Final:").grid(row=1, column=0, padx=10, pady=5)
var_ano_final = tk.StringVar(value=anos[0])
lista_ano_final = tk.OptionMenu(frame, var_ano_final, *anos)
lista_ano_final.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="Semestre Inicial:").grid(row=2, column=0, padx=10, pady=5)
var_semestre_inicial = tk.StringVar(value=semestres[0])
lista_semestre_inicial = tk.OptionMenu(frame, var_semestre_inicial, *semestres)
lista_semestre_inicial.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame, text="Semestre Final:").grid(row=3, column=0, padx=10, pady=5)
var_semestre_final = tk.StringVar(value=semestres[0])
lista_semestre_final = tk.OptionMenu(frame, var_semestre_final, *semestres)
lista_semestre_final.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame, text="Código da Instituição:").grid(row=4, column=0, padx=10, pady=5)
entry_cod_instituicao = tk.Entry(frame)
entry_cod_instituicao.grid(row=4, column=1, padx=10, pady=5)

tk.Label(frame, text="Código do Campus:").grid(row=5, column=0, padx=10, pady=5)
entry_cod_campus = tk.Entry(frame)
entry_cod_campus.grid(row=5, column=1, padx=10, pady=5)

btn_gerar = tk.Button(frame, text="Gerar Base", command=lambda: threading.Thread(target=gerar_base).start())
btn_gerar.grid(row=6, column=0, columnspan=2, pady=10)

label_link = tk.Label(frame, text="Não sabe o código do campus ou da instituição? Acesse AQUI", fg="blue", cursor="hand2")
label_link.grid(row=7, column=0, columnspan=2, pady=10)
label_link.bind("<Button-1>", lambda e: abrir_link())

aviso = tk.Label(frame, text="Tempo médio de espera: 3 minutos para cada semestre selecionado.")
aviso.grid(row=8, column=0, columnspan=2, pady=10)

cronometro_label = tk.Label(frame, text="Tempo decorrido: 0.0 segundos")
cronometro_label.grid(row=9, column=0, columnspan=2, pady=10)

progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode='determinate')
progress.grid(row=10, column=0, columnspan=2, pady=20)

btn_fechar = tk.Button(frame, text="Fechar", command=fechar_programa)
btn_fechar.grid(row=11, column=0, columnspan=2, pady=10)

frame.pack(expand=True)

root.mainloop()
