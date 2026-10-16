import os
import streamlit as st
from PIL import Image, ImageOps
import google.generativeai as genai

st.set_page_config(
    page_title="Gerador Veo 3 - Anúncios",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Gerador de Prompts Veo 3")
st.caption("Crie anúncios comerciais com quatro cenas para vender produtos.")

# Configuração da chave
try:
    saved_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    saved_key = ""

default_key = saved_key or os.environ.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("Configurações do anúncio")
    api_key = st.text_input(
        "Chave da API Gemini",
        value=default_key,
        type="password"
    )

    model_name = st.selectbox(
        "Modelo Gemini",
        ["gemini-2.5-flash", "gemini-2.0-flash"]
    )

    formato = st.selectbox(
        "Formato do vídeo",
        [
            "9:16 vertical - Reels, TikTok e Shorts",
            "16:9 horizontal - YouTube",
            "1:1 quadrado"
        ]
    )

    idioma = st.selectbox(
        "Idioma das falas",
        [
            "Português brasileiro",
            "English",
            "Sem falas, apenas sons"
        ]
    )

    duracao = st.selectbox(
        "Duração de cada cena",
        ["4 segundos", "6 segundos", "8 segundos"]
    )

st.subheader("1. Informações do produto")

col1, col2 = st.columns(2)

with col1:
    nicho = st.text_input(
        "Categoria do produto",
        placeholder="Ex.: cosméticos, roupas, eletrônicos"
    )

    produto = st.text_input(
        "Nome do produto",
        placeholder="Ex.: sérum facial de vitamina C"
    )

    beneficios = st.text_area(
        "Características e benefícios verdadeiros",
        placeholder="Descreva o produto e seus diferenciais."
    )

with col2:
    publico = st.text_input(
        "Público-alvo",
        placeholder="Ex.: pessoas interessadas em cuidados com a pele"
    )

    oferta = st.text_input(
        "Oferta, preço ou desconto (opcional)",
        placeholder="Informe somente uma oferta real."
    )

    cta = st.text_input(
        "Chamada para compra",
        value="Compre agora"
    )

estilo = st.selectbox(
    "Estilo do anúncio",
    [
        "UGC natural, estilo criadora de conteúdo",
        "Comercial premium cinematográfico",
        "Demonstração prática do produto",
        "Unboxing e primeira impressão",
        "Anúncio dinâmico para redes sociais"
    ]
)

st.subheader("2. Imagens de referência")

col3, col4 = st.columns(2)

with col3:
    foto_produto = st.file_uploader(
        "Envie a foto do produto",
        type=["png", "jpg", "jpeg"]
    )

    if foto_produto:
        st.image(foto_produto, caption="Produto", use_container_width=True)

with col4:
    foto_influencer = st.file_uploader(
        "Envie a foto da influenciadora",
        type=["png", "jpg", "jpeg"]
    )

    if foto_influencer:
        st.image(
            foto_influencer,
            caption="Influenciadora",
            use_container_width=True
        )

st.info(
    "Use imagens nítidas. As referências orientam o vídeo, "
    "mas não garantem a preservação perfeita do rosto ou da embalagem."
)

def preparar_imagem(arquivo):
    imagem = Image.open(arquivo)
    imagem = ImageOps.exif_transpose(imagem)

    if imagem.mode not in ("RGB", "RGBA"):
        imagem = imagem.convert("RGB")

    return imagem


def criar_prompt():
    return f"""
You are an expert e-commerce advertising creative director
specialized in writing video prompts for Google Veo.

PRODUCT INFORMATION
Category: {nicho or "Identify only what is visible in the reference"}
Product name: {produto or "Do not invent a brand name"}
Verified features: {beneficios or "Do not invent product claims"}
Target audience: {publico or "People interested in this product category"}
Offer: {oferta or "No specific offer; do not invent prices or discounts"}
Call to action: {cta}
Advertising style: {estilo}
Video format: {formato}
Duration per scene: {duracao}
Spoken language: {idioma}

REFERENCE IMAGES
Image 1 is the product.
Image 2 is the influencer or presenter.

Use both images as visual references.
Maintain the same presenter, hairstyle, clothing, product design,
packaging, colors and visible details across all four scenes,
as far as the video model allows.
Do not invent logos, labels, certifications or product properties.

CREATE FOUR SEPARATE VIDEO PROMPTS:

SCENE 1 — HOOK
Create an attention-grabbing opening in the first seconds.
Use a strong visual composition and a suitable camera movement.
Introduce the product naturally.

SCENE 2 — PRODUCT SHOWCASE
Show the product clearly with detailed close-ups,
appropriate lighting, texture and camera movement.
Keep the packaging consistent with the reference.

SCENE 3 — DEMONSTRATION
Show a plausible and visually clear way to use or present the product.
Do not invent results, medical claims or unverified benefits.
Keep the same presenter and product.

SCENE 4 — CALL TO ACTION
Finish with a clear product hero shot and a natural invitation to buy.
Use the specified call to action.
Never invent a price, discount or deadline.

IMPORTANT RULES
- Write the four video prompts in English.
- Spoken dialogue, if any, must use the selected language.
- Give each scene its own prompt, ready to copy separately.
- Specify camera framing, camera movement, action, lighting,
  setting, sound effects and dialogue where appropriate.
- Keep visual continuity between all four scenes.
- Avoid distorted hands, extra fingers, duplicated products,
  changing faces, altered packaging and random on-screen text.
- Leave clear space for captions to be added during editing.
- Do not claim that a video has already been generated.
- Do not invent facts about the product.

After the four prompts, provide brief editing suggestions in Portuguese.
"""


if st.button(
    "✨ GERAR OS 4 PROMPTS",
    type="primary",
    use_container_width=True
):
    if not api_key:
        st.error("Informe a chave da API Gemini na barra lateral.")

    elif not foto_produto or not foto_influencer:
        st.error("Envie a foto do produto e a foto da influenciadora.")

    else:
        try:
            genai.configure(api_key=api_key)
            modelo = genai.GenerativeModel(model_name)

            imagem_produto = preparar_imagem(foto_produto)
            imagem_influencer = preparar_imagem(foto_influencer)

            with st.spinner("Criando seus prompts comerciais..."):
                resposta = modelo.generate_content([
                    criar_prompt(),
                    "IMAGE 1 — PRODUCT REFERENCE:",
                    imagem_produto,
                    "IMAGE 2 — INFLUENCER REFERENCE:",
                    imagem_influencer
                ])

            texto = getattr(resposta, "text", None)

            if texto:
                st.success("Prompts gerados com sucesso!")

                st.markdown(texto)

                st.text_area(
                    "Todos os prompts para copiar",
                    value=texto,
                    height=400
                )

                st.download_button(
                    "⬇️ BAIXAR PROMPTS EM TXT",
                    data=texto,
                    file_name="prompts_comerciais_veo.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.error(
                    "A resposta veio vazia. "
                    "Tente novamente ou escolha outro modelo."
                )

        except Exception as erro:
            st.error("Não foi possível gerar os prompts.")
            st.caption(
                "Verifique a chave da API, a conexão e a disponibilidade "
                "do modelo selecionado."
            )
            st.code(str(erro))

with st.expander("🔐 Segurança da chave da API"):
    st.write(
        "Não publique sua chave no código. "
        "Em uma hospedagem, configure GEMINI_API_KEY nos Secrets. "
        "A utilização da API pode estar sujeita a limites ou custos."
    )

st.caption(
    "Esta ferramenta gera prompts comerciais. "
    "A geração dos vídeos acontece em uma ferramenta de vídeo compatível."
)
