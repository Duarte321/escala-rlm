import streamlit as st
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Escala RLM", layout="wide")

# --- DADOS PRÉ-SELECIONADOS ---
OPCOES_LOCALIDADES = [
    "Assentamento São Francisco", "Irmão Duda - Barroso", "Irmã Marlene - Entre Rios",
    "Irenópolis", "Assentamento Renascer", "Juscimeira", "Jaciara - Central",
    "Santa Elvira", "Rondonópolis - Central", "Campo Verde - Central", 
    "Reunião Renascer / Usina Pantanal"
]
OPCOES_NOMES = [
    "Irmão Marcos", "Irmão Israel", "Irmão Ercides", "Irmão Aguinaldo",
    "Irmão/Rodizio", "Marcos Gomes", "Sebastião Leite", "Paulo Casarim",
    "Valmir Silva", "Elias Dourado", "Robson", "Fabio André", 
    "Dilmar Ferreira", "Olegario Muniz", "Irmão Cristiano"
]
OPCOES_TIPOS = [
    "Ensaio para Cordas", "(Libras)", "Acerto Financeiro", 
    "Reunião para Porteiros/Som", "Admin./Colaboradores"
]

# --- INICIALIZAÇÃO DO ESTADO (Memória) ---
if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        "Evangelizacao": [],
        "Batismos": [],
        "Cordas": [],
        "Mocidade": [],
        "Regionais": [],
        "Diversas": []
    }

st.title("⛪ Painel de Escala - RLM Jaciara/MT")

# --- FUNÇÃO PARA GERAR PDF NA MEMÓRIA ---
def gerar_pdf_bytes():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    elements = []
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=2)
    estilo_subtitulo = ParagraphStyle('Sub', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=10)

    elements.append(Paragraph("CONGREGAÇÃO CRISTÃ NO BRASIL", estilo_titulo))
    elements.append(Paragraph("REUNIÃO LOCAL MINISTERIAL - RLM - JACIARA/MT", estilo_subtitulo))
    elements.append(Paragraph(f"DATA DE EMISSÃO: {datetime.now().strftime('%d/%m/%Y')}", estilo_subtitulo))
    elements.append(Spacer(1, 0.5*cm))

    def criar_tabela(titulo, headers, chave):
        dados = st.session_state['dados'][chave]
        if not dados: return
        
        # Prepara dados para o ReportLab (DataFrame para lista de listas)
        # Adiciona o header manualmente
        lista_dados = [headers] + [list(d.values()) for d in dados]

        t_titulo = Table([[titulo]], colWidths=[19*cm])
        t_titulo.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.gray),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
        ]))
        elements.append(t_titulo)

        col_w = 19*cm / len(headers)
        t_dados = Table(lista_dados, colWidths=[col_w]*len(headers))
        t_dados.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        elements.append(t_dados)
        elements.append(Spacer(1, 0.3*cm))

    criar_tabela("REUNIÕES DE EVANGELIZAÇÃO", ["DT/HORA", "LOCALIDADE", "ATENDENTE"], "Evangelizacao")
    criar_tabela("BATISMOS", ["DT/HORA", "LOCALIDADE", "LOCALIDADE 2", "ANCIÃO"], "Batismos")
    criar_tabela("ENSAIO PARA CATEGORIA DAS CORDAS", ["DT/HORA", "LOCALIDADE", "TIPO", "ATENDENTE"], "Cordas")
    criar_tabela("REUNIÃO PARA MOCIDADE", ["DT/HORA", "LOCALIDADE", "OBS", "ANCIÃO"], "Mocidade")
    criar_tabela("ENSAIOS REGIONAIS", ["DT/HORA", "LOCALIDADE", "ANCIÃO", "ENC. REGIONAL"], "Regionais")
    criar_tabela("REUNIÕES DIVERSAS", ["DT/HORA", "LOCALIDADE", "TIPO", "ATENDENTE"], "Diversas")

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- FUNÇÃO PARA GERAR EXCEL ---
def gerar_excel_bytes():
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for chave, dados in st.session_state['dados'].items():
        if dados:
            df = pd.DataFrame(dados)
            df.to_excel(writer, sheet_name=chave, index=False)
    writer.close()
    output.seek(0)
    return output

# --- INTERFACE DAS ABAS ---
abas = st.tabs(["Evangelização", "Batismos", "Cordas", "Mocidade", "Regionais", "Diversas"])

def criar_formulario(tab, titulo, chave, colunas):
    with tab:
        st.subheader(titulo)
        
        # Formulário para adicionar
        with st.form(key=f"form_{chave}"):
            cols = st.columns(len(colunas))
            inputs = {}
            
            for i, col_name in enumerate(colunas):
                with cols[i]:
                    if "LOCAL" in col_name:
                        inputs[col_name] = st.selectbox(f"{col_name}", OPCOES_LOCALIDADES, key=f"{chave}_{col_name}")
                    elif "ATENDENTE" in col_name or "ANCIÃO" in col_name or "REGIONAL" in col_name:
                        inputs[col_name] = st.selectbox(f"{col_name}", OPCOES_NOMES, key=f"{chave}_{col_name}")
                    elif "TIPO" in col_name or "OBS" in col_name:
                         inputs[col_name] = st.selectbox(f"{col_name}", OPCOES_TIPOS, key=f"{chave}_{col_name}")
                    else:
                        inputs[col_name] = st.text_input(f"{col_name}", key=f"{chave}_{col_name}")
            
            submit = st.form_submit_button("Adicionar na Lista")
            
            if submit:
                st.session_state['dados'][chave].append(inputs)
                st.success("Adicionado!")
        
        # Mostrar tabela atual
        if st.session_state['dados'][chave]:
            df = pd.DataFrame(st.session_state['dados'][chave])
            st.table(df)
            if st.button("Limpar Lista", key=f"clean_{chave}"):
                st.session_state['dados'][chave] = []
                st.rerun()

# Criando as interfaces
criar_formulario(abas[0], "Reuniões de Evangelização", "Evangelizacao", ["DT/HORA", "LOCALIDADE", "ATENDENTE"])
criar_formulario(abas[1], "Batismos", "Batismos", ["DT/HORA", "LOCALIDADE", "LOCALIDADE 2", "ANCIÃO"])
criar_formulario(abas[2], "Ensaios de Cordas", "Cordas", ["DT/HORA", "LOCALIDADE", "TIPO", "ATENDENTE"])
criar_formulario(abas[3], "Reunião da Mocidade", "Mocidade", ["DT/HORA", "LOCALIDADE", "OBS", "ANCIÃO"])
criar_formulario(abas[4], "Ensaios Regionais", "Regionais", ["DT/HORA", "LOCALIDADE", "ANCIÃO", "ENC. REGIONAL"])
criar_formulario(abas[5], "Reuniões Diversas", "Diversas", ["DT/HORA", "LOCALIDADE", "TIPO", "ATENDENTE"])

st.divider()

# --- ÁREA DE DOWNLOAD ---
col1, col2 = st.columns(2)

with col1:
    if st.button("Gerar PDF"):
        pdf_bytes = gerar_pdf_bytes()
        st.download_button(
            label="⬇️ Baixar PDF Pronto",
            data=pdf_bytes,
            file_name="Escala_RLM.pdf",
            mime="application/pdf"
        )

with col2:
    if st.button("Gerar Excel"):
        excel_bytes = gerar_excel_bytes()
        st.download_button(
            label="⬇️ Baixar Planilha Excel",
            data=excel_bytes,
            file_name="Escala_RLM.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
