import streamlit as st
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Reunião Local Ministerial - Jaciara MT", layout="wide")

# --- 2. INICIALIZAÇÃO DO "BANCO DE DADOS" (MEMÓRIA) ---
# Aqui definimos os dados iniciais, mas eles agora são editáveis na sessão

if 'db_locais' not in st.session_state:
    st.session_state['db_locais'] = {
        "Jaciara": [
            "Jaciara - Central", "Assentamento São Francisco", "Jaciara - Santa Rita", 
            "Reunião Renascer / Usina Pantanal"
        ],
        "Microrregião - MT": [
            "Irmão Duda - Barroso", "Irmã Marlene - Entre Rios", "Irenópolis", 
            "Assentamento Renascer", "Juscimeira", "Santa Elvira", 
            "Rondonópolis - Central", "Campo Verde - Central"
        ]
    }

if 'db_nomes' not in st.session_state:
    st.session_state['db_nomes'] = {
        "Jaciara": [
            "Irmão Marcos", "Irmão Israel", "Sebastião Leite", "Paulo Casarim", 
            "Robson", "Olegario Muniz", "Irmão Cristiano", "Irmão/Rodizio"
        ],
        "Microrregião - MT": [
            "Irmão Ercides", "Irmão Aguinaldo", "Marcos Gomes", "Valmir Silva", 
            "Elias Dourado", "Fabio André", "Dilmar Ferreira"
        ]
    }

if 'db_tipos' not in st.session_state:
    st.session_state['db_tipos'] = [
        "Ensaio para Cordas", "(Libras)", "Acerto Financeiro", 
        "Reunião para Porteiros/Som", "Admin./Colaboradores"
    ]

# Inicializa a escala vazia se não existir
if 'dados_escala' not in st.session_state:
    st.session_state['dados_escala'] = {
        "Evangelizacao": [], "Batismos": [], "Cordas": [], 
        "Mocidade": [], "Regionais": [], "Diversas": []
    }

# --- 3. BARRA LATERAL (GERENCIAMENTO DE CADASTROS) ---
with st.sidebar:
    st.header("⚙️ Gerenciar Cadastros")
    st.info("Adicione ou remova nomes e locais aqui.")
    
    tab_loc, tab_nom = st.tabs(["📍 Localidades", "👤 Irmãos/Anciães"])
    
    # Gestão de Localidades
    with tab_loc:
        regiao_add = st.selectbox("Selecione a Região para editar:", ["Jaciara", "Microrregião - MT"], key="reg_loc_sel")
        novo_local = st.text_input("Novo Local:")
        if st.button("Adicionar Local"):
            if novo_local and novo_local not in st.session_state['db_locais'][regiao_add]:
                st.session_state['db_locais'][regiao_add].append(novo_local)
                st.success(f"Adicionado em {regiao_add}!")
                st.rerun()
        
        st.markdown("---")
        st.markdown("**Excluir Local:**")
        local_del = st.selectbox("Selecione para excluir:", st.session_state['db_locais'][regiao_add], key="del_loc_sel")
        if st.button("Excluir Local"):
            st.session_state['db_locais'][regiao_add].remove(local_del)
            st.warning("Removido!")
            st.rerun()

    # Gestão de Nomes
    with tab_nom:
        regiao_nom = st.selectbox("Selecione a Região:", ["Jaciara", "Microrregião - MT"], key="reg_nom_sel")
        novo_nome = st.text_input("Novo Nome:")
        if st.button("Adicionar Irmão"):
            if novo_nome and novo_nome not in st.session_state['db_nomes'][regiao_nom]:
                st.session_state['db_nomes'][regiao_nom].append(novo_nome)
                st.success(f"Adicionado em {regiao_nom}!")
                st.rerun()
        
        st.markdown("---")
        st.markdown("**Excluir Nome:**")
        nome_del = st.selectbox("Selecione para excluir:", st.session_state['db_nomes'][regiao_nom], key="del_nom_sel")
        if st.button("Excluir Irmão"):
            st.session_state['db_nomes'][regiao_nom].remove(nome_del)
            st.warning("Removido!")
            st.rerun()

# --- 4. LÓGICA DE FILTRAGEM ---
st.title("⛪ RLM - Jaciara MT")

# Filtro Global para o preenchimento
col_filtro, col_vazio = st.columns([1, 2])
with col_filtro:
    st.markdown("### 🔍 Filtro de Preenchimento")
    filtro_regiao = st.radio("Mostrar opções de:", ["Jaciara", "Microrregião - MT", "Todos"], horizontal=True)

# Define as listas baseadas no filtro
listas_locais = []
listas_nomes = []

if filtro_regiao == "Todos":
    listas_locais = st.session_state['db_locais']["Jaciara"] + st.session_state['db_locais']["Microrregião - MT"]
    listas_nomes = st.session_state['db_nomes']["Jaciara"] + st.session_state['db_nomes']["Microrregião - MT"]
else:
    listas_locais = st.session_state['db_locais'][filtro_regiao]
    listas_nomes = st.session_state['db_nomes'][filtro_regiao]

# Ordenar alfabeticamente para facilitar
listas_locais.sort()
listas_nomes.sort()

# --- 5. FUNÇÕES DE EXPORTAÇÃO (PDF/EXCEL) ---
def gerar_pdf_bytes():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.5*cm, leftMargin=0.5*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    elements = []
    styles = getSampleStyleSheet()
    
    # Cabeçalho Personalizado
    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=2)
    estilo_subtitulo = ParagraphStyle('Sub', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=10)

    elements.append(Paragraph("CONGREGAÇÃO CRISTÃ NO BRASIL", estilo_titulo))
    elements.append(Paragraph("REUNIÃO LOCAL MINISTERIAL - RLM - JACIARA/MT", estilo_subtitulo))
    elements.append(Paragraph(f"DATA DE EMISSÃO: {datetime.now().strftime('%d/%m/%Y')}", estilo_subtitulo))
    elements.append(Spacer(1, 0.5*cm))

    def criar_tabela(titulo, headers, chave):
        dados = st.session_state['dados_escala'][chave]
        if not dados: return
        
        # Transforma lista de dicts em lista de listas
        lista_dados = [headers] + [list(d.values()) for d in dados]

        # Título da Seção (Cinza)
        t_titulo = Table([[titulo]], colWidths=[19*cm])
        t_titulo.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.gray),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
        ]))
        elements.append(t_titulo)

        # Tabela de Dados
        col_w = 19*cm / len(headers)
        t_dados = Table(lista_dados, colWidths=[col_w]*len(headers))
        t_dados.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t_dados)
        elements.append(Spacer(1, 0.3*cm))

    # Gera as seções
    criar_tabela("REUNIÕES DE EVANGELIZAÇÃO", ["DT/HORA", "LOCALIDADE", "ATENDENTE"], "Evangelizacao")
    criar_tabela("BATISMOS", ["DT/HORA", "LOCALIDADE", "LOCALIDADE 2", "ANCIÃO"], "Batismos")
    criar_tabela("ENSAIO PARA CATEGORIA DAS CORDAS", ["DT/HORA", "LOCALIDADE", "TIPO", "ATENDENTE"], "Cordas")
    criar_tabela("REUNIÃO PARA MOCIDADE", ["DT/HORA", "LOCALIDADE", "OBS", "ANCIÃO"], "Mocidade")
    criar_tabela("ENSAIOS REGIONAIS", ["DT/HORA", "LOCALIDADE", "ANCIÃO", "ENC. REGIONAL"], "Regionais")
    criar_tabela("REUNIÕES DIVERSAS", ["DT/HORA", "LOCALIDADE", "TIPO", "ATENDENTE"], "Diversas")

    # Rodapé fixo
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("ASSUNTOS DIVERSOS", estilo_titulo))
    elements.append(Paragraph("*COLETA DO COFRINHO TODO PRIMEIRO FINAL DE SEMANA DE CADA MÊS", styles['Normal']))
    elements.append(Paragraph("*COLETA DE INTENÇÃO ATÉ TODO DIA 10 DE CADA MÊS", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def gerar_excel_bytes():
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for chave, dados in st.session_state['dados_escala'].items():
        if dados:
            df = pd.DataFrame(dados)
            df.to_excel(writer, sheet_name=chave, index=False)
    writer.close()
    output.seek(0)
    return output

# --- 6. INTERFACE DE PREENCHIMENTO ---
abas = st.tabs(["Evangelização", "Batismos", "Cordas", "Mocidade", "Regionais", "Diversas"])

def criar_formulario(tab, titulo, chave, colunas):
    with tab:
        st.subheader(titulo)
        
        # Formulário de Adição
        with st.form(key=f"form_{chave}"):
            cols = st.columns(len(colunas))
            inputs = {}
            
            for i, col_name in enumerate(colunas):
                with cols[i]:
                    # Lógica para decidir qual lista mostrar baseado no filtro
                    if "LOCAL" in col_name:
                        inputs[col_name] = st.selectbox(f"{col_name}", listas_locais, key=f"{chave}_{col_name}")
                    elif "ATENDENTE" in col_name or "ANCIÃO" in col_name or "REGIONAL" in col_name:
                        inputs[col_name] = st.selectbox(f"{col_name}", listas_nomes, key=f"{chave}_{col_name}")
                    elif "TIPO" in col_name or "OBS" in col_name:
                         inputs[col_name] = st.selectbox(f"{col_name}", st.session_state['db_tipos'], key=f"{chave}_{col_name}")
                    else:
                        inputs[col_name] = st.text_input(f"{col_name}", key=f"{chave}_{col_name}")
            
            if st.form_submit_button("➕ Adicionar na Escala"):
                st.session_state['dados_escala'][chave].append(inputs)
                st.success("Adicionado!")
                st.rerun()
        
        # Visualização e Exclusão da Tabela
        if st.session_state['dados_escala'][chave]:
            df = pd.DataFrame(st.session_state['dados_escala'][chave])
            st.markdown("#### Visualização Atual")
            st.table(df)
            
            # Botão para remover último item (simples) ou limpar tudo
            c1, c2 = st.columns(2)
            if c1.button("❌ Remover Último", key=f"del_last_{chave}"):
                st.session_state['dados_escala'][chave].pop()
                st.rerun()
            if c2.button("🗑️ Limpar Tudo", key=f"clean_{chave}"):
                st.session_state['dados_escala'][chave] = []
                st.rerun()
        else:
            st.info("Nenhum item adicionado nesta seção.")

# Criar as abas
criar_formulario(abas[0], "Reuniões de Evangelização", "Evangelizacao", ["DT/HORA", "LOCALIDADE", "ATENDENTE"])
criar_formulario(abas[1], "Batismos", "Batismos", ["DT/HORA", "LOCALIDADE", "LOCALIDADE 2", "ANCIÃO"])
criar_formulario(abas[2], "Ensaios de Cordas", "Cordas", ["DT/HORA", "LOCALIDADE", "TIPO", "ATENDENTE"])
criar_formulario(abas[3], "Reunião da Mocidade", "Mocidade", ["DT/HORA", "LOCALIDADE", "OBS", "ANCIÃO"])
criar_formulario(abas[4], "Ensaios Regionais", "Regionais", ["DT/HORA", "LOCALIDADE", "ANCIÃO", "ENC. REGIONAL"])
criar_formulario(abas[5], "Reuniões Diversas", "Diversas", ["DT/HORA", "LOCALIDADE", "TIPO", "ATENDENTE"])

st.divider()

# --- 7. DOWNLOADS ---
col1, col2 = st.columns(2)
with col1:
    if st.button("📄 Gerar PDF Final"):
        pdf = gerar_pdf_bytes()
        st.download_button("⬇️ Baixar PDF", pdf, "Escala_RLM_Jaciara.pdf", "application/pdf")

with col2:
    if st.button("📊 Gerar Excel"):
        excel = gerar_excel_bytes()
        st.download_button("⬇️ Baixar Excel", excel, "Escala_RLM_Jaciara.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
