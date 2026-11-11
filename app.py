from datetime import date
from html import escape

import streamlit as st

from servico import buscar_rastreabilidade, hash_valido

# ------------------------------------------------ configuração (st.secrets)
try:
    SITE = st.secrets["app"]["site_imagens"].rstrip("/")
except Exception:
    SITE = None

if not SITE:
    st.set_page_config(page_title="Rastreabilidade", layout="centered")
    st.error("Configuração ausente. Defina [app] site_imagens no secrets.toml.")
    st.stop()

LOGO_URL = f"{SITE}/logo_v.png"
FAVICON_URL = f"{SITE}/favicon.png"

st.set_page_config(page_title="Vectra Work | Rastreabilidade", page_icon=FAVICON_URL, layout="centered")

st.markdown(
    """
    <style>
      /* limpa o "chrome" do Streamlit */
      header[data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stDecoration"], #MainMenu, footer {display: none !important;}

      .block-container {padding: 1.2rem 1rem 1.5rem !important; max-width: 760px;}
      [data-testid="stVerticalBlock"] {gap: .4rem;}

      .logo {display: block; width: 150px; max-width: 45vw; height: auto; margin: 0 auto .8rem;}

      .titulo {font-size: 1.25rem; font-weight: 700; line-height: 1.3; margin: 0;}
      .codigo {font-size: .85rem; color: #6B7280; margin: .15rem 0 0;}
      .codigo span {font-family: ui-monospace, Consolas, monospace; letter-spacing: .08em;}

      .secao {margin-top: 1.1rem;}
      .secao h4 {font-size: .95rem; color: #1F4E79; margin: 0 0 .45rem;
                 padding-bottom: .3rem; border-bottom: 1px solid rgba(128,128,128,.25);}

      .grade {display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
              column-gap: 1.2rem; row-gap: .55rem;}
      .full {grid-column: 1 / -1;}
      .rotulo {font-size: .75rem; color: #6B7280;}
      .valor  {font-size: 1rem; font-weight: 600; word-break: break-word;}

      @media (max-width: 480px) {
        .block-container {padding: .8rem .8rem 1.2rem !important;}
        .titulo {font-size: 1.08rem;}
        .grade {grid-template-columns: 1fr 1fr;}
        .valor {font-size: .95rem;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_data(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def campo(rotulo: str, valor: str, full: bool = False) -> str:
    cls = ' class="full"' if full else ""
    return f'<div{cls}><div class="rotulo">{escape(rotulo)}</div><div class="valor">{escape(valor)}</div></div>'


def secao(titulo: str, campos: list[str]) -> str:
    return f'<div class="secao"><h4>{escape(titulo)}</h4><div class="grade">{"".join(campos)}</div></div>'


@st.cache_data(ttl=300, max_entries=500, show_spinner=False)
def carregar(h: str):
    return buscar_rastreabilidade(h)


def logo() -> None:
    st.markdown(f'<img class="logo" src="{LOGO_URL}" alt="Vectra Work">', unsafe_allow_html=True)


def tela_detalhe(h: str) -> None:
    logo()
    # valida ANTES de consultar/cachear e nunca devolve o texto da URL na tela
    if not hash_valido(h):
        st.error("Código inválido. Confira o QR code da etiqueta.")
        return
    reg = carregar(h)
    if reg is None:
        st.error("Nenhum registro encontrado para este código.")
        return

    html = (
        f'<p class="titulo">{escape(reg.produto)}</p>'
        f'<p class="codigo">Código <span>{escape(reg.hash)}</span></p>'
        + secao("Cliente e faturamento", [
            campo("Cliente", reg.cliente, full=True),
            campo("Nota fiscal", reg.nota_fiscal),
            campo("Data da nota", fmt_data(reg.data_nota)),
            campo("Pedido", reg.pedido),
            campo("Pedido do cliente", reg.pedido_cliente),
        ])
        + secao("Produção", [
            campo("OP", reg.op),
            campo("Data da OP", fmt_data(reg.data_op)),
            campo("Produto", reg.produto, full=True),
        ])
        + secao("Matéria-prima", [
            campo("Tecido", reg.materia_prima, full=True),
            campo("Lote do fornecedor", reg.lote_fornecedor),
        ])
    )
    st.markdown(html, unsafe_allow_html=True)


def tela_inicial() -> None:
    logo()
    st.markdown('<p class="titulo" style="text-align:center">Rastreabilidade do produto</p>', unsafe_allow_html=True)
    with st.form("busca", border=False):
        h = st.text_input("Código da etiqueta", max_chars=12, placeholder="000000000000")
        enviar = st.form_submit_button("Consultar", use_container_width=True)
    if enviar:
        if hash_valido(h):
            st.query_params["hash"] = h.strip()
            st.rerun()
        else:
            st.warning("O código precisa ter 12 números.")


hash_url = st.query_params.get("hash")
if hash_url:
    tela_detalhe(hash_url.strip()[:20])
else:
    tela_inicial()