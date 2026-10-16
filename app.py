import os
import io
import streamlit as st
from PIL import Image, ImageOps
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Gerador Veo 3 - Anúncios",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Gerador de Prompts Veo 3")
st.caption("Crie anúncios comerciais com quatro cenas para vender produtos.")

# ============================================================
# CONFIGURAÇÃO DA CHAVE
# ============================================================

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
        ["gemini-3.8-flash"]
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

# ============================================================
# INFORMAÇÕES DO PRODUTO
# ============================================================

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

# ============================================================
# IMAGENS
# ============================================================

st.subheader("2. Imagens de referência")

col3, col4 = st.columns(2)

with col3:
    foto_produto = st.file_uploader(
        "Envie a foto do produto",
        type=["png", "jpg", "jpeg"]
    )

    if foto_produto:
        st.image(
            foto_produto,
            caption="Produto",
            use_container_width=True
        )

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

# ============================================================
# PREPARAR IMAGEM
# ============================================================

def preparar_imagem(arquivo):
    imagem = Image.open(arquivo)
    imagem = ImageOps.exif_transpose(imagem)

    if imagem.mode not in ("RGB", "RGBA"):
        imagem = imagem.convert("RGB")

    return imagem


def imagem_para_part(arquivo):
    imagem = preparar_imagem(arquivo)

    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")

    return types.Part.from_bytes(
        data=buffer.getvalue(),
        mime_type="image/png"
    )


# ============================================================
# PROMPT PRINCIPAL
# ============================================================

def criar_prompt():
    return f"""
You are an expert e-commerce advertising creative director
specialized in writing high-quality video prompts for Google Veo.

PRODUCT INFORMATION

Category: {nicho or "Identify only what is visible in the reference."}

Product name:
{produto or "Do not invent a brand name."}

Verified features:
{beneficios or "Do not invent product claims."}

Target audience:
{publico or "People interested in this product category."}

Offer:
{oferta or "No specific offer. Do not invent prices, discounts or deadlines."}

Call to action:
{cta}

Advertising style:
{estilo}

Video format:
{formato}

Duration per scene:
{duracao}

Spoken language:
{idioma}


REFERENCE IMAGES

Image 1 is the product reference.

Image 2 is the influencer or presenter reference.

Use both images as visual references.

Maintain visual continuity across all four scenes whenever possible.

Keep the same presenter, facial appearance, hairstyle, clothing,
product design, packaging, colors and visible details.

Do not invent logos, labels, certifications, prices,
medical claims or product properties.


CREATE FOUR SEPARATE VIDEO PROMPTS

SCENE 1 — HOOK

Create a powerful attention-grabbing opening during the first seconds.

Use a strong visual composition, realistic environment,
appropriate camera framing and cinematic camera movement.

Introduce the product naturally.


SCENE 2 — PRODUCT SHOWCASE

Show the product clearly.

Use detailed close-ups, realistic lighting, texture,
material details and professional camera movement.

Keep the packaging visually consistent with the reference image.


SCENE 3 — DEMONSTRATION

Show a plausible and visually clear way to use,
hold or present the product.

Do not invent results, medical claims or unverified benefits.

Keep the same presenter and product appearance.


SCENE 4 — CALL TO ACTION

Finish with a strong product hero shot.

Create a natural invitation to purchase using the specified
call to action.

Never invent a price, discount, deadline or promotion.


IMPORTANT RULES

- Write the four video prompts in English.
- Spoken dialogue, if any, must be in the selected language.
- Each scene must have its own independent prompt.
- Make every prompt ready to copy directly into a video generator.
- Specify camera framing.
- Specify camera movement.
- Specify subject action.
- Specify lighting.
- Specify environment.
- Specify sound effects.
- Specify dialogue when appropriate.
- Maintain visual continuity between all four scenes.
- Avoid distorted hands.
- Avoid extra fingers.
- Avoid duplicated products.
- Avoid changing faces.
- Avoid changing the packaging.
- Avoid random text appearing on screen.
- Leave clear space for captions to be added during editing.
- Do not claim that a video has already been generated.
- Do not invent facts about the product.

After the four prompts, provide brief editing suggestions in Portuguese.
"""


# ============================================================
# GERAÇÃO
# ============================================================

if st.button(
    "✨ GERAR OS 4 PROMPTS",
    type="primary",
    use_container_width=True
):

    if not api_key:
        st.error(
            "Informe a chave da API Gemini na barra lateral."
        )

    elif not foto_produto or not foto_influencer:
        st.error(
            "Envie a foto do produto e a foto da influenciadora."
        )

    else:

        try:
            cliente = genai.Client(
                api_key=api_key
            )

            imagem_produto = imagem_para_part(
                foto_produto
            )

            imagem_influencer = imagem_para_part(
                foto_influencer
            )

            prompt = criar_prompt()

            conteudo = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=prompt
                        ),
                        types.Part.from_text(
                            text="IMAGE 1 — PRODUCT REFERENCE:"
                        ),
                        imagem_produto,
                        types.Part.from_text(
                            text="IMAGE 2 — INFLUENCER REFERENCE:"
                        ),
                        imagem_influencer
                    ]
                )
            ]

            with st.spinner(
                "Criando seus prompts comerciais..."
            ):

                resposta = cliente.models.generate_content(
                    model=model_name,
                    contents=conteudo
                )

            texto = getattr(
                resposta,
                "text",
                None
            )

            if texto:

                st.success(
                    "Prompts gerados com sucesso!"
                )

                st.markdown(texto)

                st.text_area(
                    "Todos os prompts para copiar",
                    value=texto,
                    height=500
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
                    "A resposta do Gemini veio vazia. "
                    "Tente novamente."
                )

        except Exception as erro:

            st.error(
                "Não foi possível gerar os prompts."
            )

            st.caption(
                "O aplicativo recebeu um erro da API Gemini."
            )

            st.code(
                str(erro)
            )


# ============================================================
# SEGURANÇA
# ============================================================

with st.expander("🔐 Segurança da chave da API"):

    st.write(
        "Não publique sua chave no código. "
        "Em uma hospedagem, configure GEMINI_API_KEY "
        "nos Secrets. "
        "A utilização da API pode estar sujeita a limites "
        "ou custos."
    )

st.caption(
    "Esta ferramenta gera prompts comerciais. "
    "A geração dos vídeos acontece em uma ferramenta "
    "de vídeo compatível."
)
