import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import tempfile
from fpdf import FPDF

st.set_page_config(page_title="Perito Contábil - Completo", layout="wide")
st.title("📊 Robô Perito Contábil - Índices, Pareceres e PDF")

uploaded_file = st.file_uploader("📁 Envie o balancete ou DRE (PDF ou Excel)", type=["xlsx", "pdf"])

# Checkboxes
st.markdown("### ✅ Selecione as análises desejadas:")
check_indices = st.checkbox("📈 Índices Financeiros")
check_parecer = st.checkbox("📄 Parecer Técnico")
check_opiniao = st.checkbox("⚖️ Opinião Pericial")
check_sugestao = st.checkbox("💡 Sugestões Gerenciais")
check_consolidado = st.checkbox("📚 Relatório Consolidado (PDF)")

def buscar_valor(df, nomes_possiveis):
    for nome in nomes_possiveis:
        for col in df.columns:
            if nome.lower() in str(col).lower():
                return df[col].sum()
    return None

def extrair_texto_pdf(file):
    texto = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def gerar_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for linha in texto.split("\n"):
        pdf.multi_cell(0, 10, linha)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp.name)
    return temp.name

texto_pdf = ""
resultados = {}

if uploaded_file:
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        st.write("📑 Planilha carregada:")
        st.dataframe(df)

        ac = buscar_valor(df, ["Ativo Circulante"])
        pc = buscar_valor(df, ["Passivo Circulante"])
        est = buscar_valor(df, ["Estoques"])
        at = buscar_valor(df, ["Ativo Total"])
        pt = buscar_valor(df, ["Passivo Total"])
        pl = buscar_valor(df, ["Patrimônio Líquido"])

        if ac and pc:
            resultados["Liquidez Corrente"] = ac / pc
        if ac and est and pc:
            resultados["Liquidez Seca"] = (ac - est) / pc
        if at and pt:
            resultados["Liquidez Geral"] = at / pt
        if pt and pl:
            resultados["Grau de Endividamento"] = pt / pl
        if pt and at:
            resultados["Participação de Capital de Terceiros"] = pt / at

    elif uploaded_file.name.endswith(".pdf"):
        texto_pdf = extrair_texto_pdf(uploaded_file)
        st.subheader("📝 Texto extraído do PDF:")
        st.text_area("Conteúdo detectado:", value=texto_pdf, height=300)

# Apresentação interativa dos resultados
conteudo_final = ""

if check_indices and resultados:
    st.subheader("📈 Índices Financeiros Calculados")
    for k, v in resultados.items():
        st.write(f"**{k}:** {v:.2f}")
        conteudo_final += f"{k}: {v:.2f}\n"

if check_parecer:
    st.subheader("📄 Parecer Técnico")
    parecer = """
Com base nos cálculos dos principais índices financeiros:

- Liquidez Corrente e Seca indicam a capacidade de pagamento.
- Grau de Endividamento e Participação de Capital de Terceiros mostram dependência de capital externo.
- Interpretado conforme Lei 6.404/76, CPC 26 e NBCTG 12.
"""
    st.markdown(parecer)
    conteudo_final += parecer + "\n"

if check_opiniao:
    st.subheader("⚖️ Opinião Pericial")
    opiniao = """
As demonstrações analisadas demonstram consistência. A estrutura patrimonial indica boa gestão dos recursos.

Riscos observados devem ser monitorados com atenção às práticas contábeis e à evolução dos passivos.
"""
    st.markdown(opiniao)
    conteudo_final += opiniao + "\n"

if check_sugestao:
    st.subheader("💡 Sugestões Gerenciais")
    sugestao = """
- Reduzir estoques para melhorar a liquidez seca.
- Reforçar capital próprio para reduzir grau de endividamento.
- Rever custos operacionais para elevar rentabilidade.
"""
    st.markdown(sugestao)
    conteudo_final += sugestao + "\n"

# Baixar relatório completo
if check_consolidado and conteudo_final:
    pdf_path = gerar_pdf(conteudo_final)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Baixar Relatório Consolidado em PDF", f.read(), file_name="relatorio_consolidado.pdf")
