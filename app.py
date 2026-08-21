import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Gerador Veo 3", layout="centered")
st.title("🚀 Gerador de Prompts para Vendas (Google Veo 3)")

api_key_usuario = st.text_input("Sua API Key do Gemini", type="password")
nicho = st.text_input("Nicho do Produto", value="Cosméticos / Skincare")

col1, col2 = st.columns(2)
with col1:
    img_prod_file = st.file_uploader("Foto do Produto", type=["png", "jpg", "jpeg"])
with col2:
    img_inf_file = st.file_uploader("Foto da Influencer", type=["png", "jpg", "jpeg"])

if st.button("🔥 Gerar Sequência de Prompts", type="primary"):
    if not api_key_usuario:
        st.error("⚠️ Erro: Insira a API Key do Gemini.")
    elif not img_prod_file or not img_inf_file:
        st.error("⚠️ Erro: Envie a foto do produto e a foto da influencer.")
    else:
        try:
            genai.configure(api_key=api_key_usuario)
            model = genai.GenerativeModel('gemini-1.5-flash')

            prod_pil = Image.open(img_prod_file)
            inf_pil = Image.open(img_inf_file)

            system_prompt = f"""
            Você é um diretor de comerciais para e-commerce especialista no Google Veo 3.
            Analise a Imagem 1 (Produto de {nicho}) e a Imagem 2 (Influencer).
            
            Gere 4 PROMPTS INDIVIDUAIS EM INGLÊS otimizados para o Google Veo 3:
            1. SCENE 1 - HOOK (Push-in Camera Movement)
            2. SCENE 2 - SHOWCASE (Macro / 360 Orbit)
            3. SCENE 3 - UGC DEMO (Handheld Motion)
            4. SCENE 4 - CALL TO ACTION (Pull-back Shot)
            
            Mantenha a fidelidade física da influencer e do produto em todos os prompts.
            """

            with st.spinner("Gerando prompts..."):
                response = model.generate_content([system_prompt, prod_pil, inf_pil])
                st.success("Prompts gerados com sucesso!")
                st.text_area("Prompts Gerados para o Veo 3", value=response.text, height=350)
        except Exception as e:
            st.error(f"Erro ao processar: {str(e)}")
