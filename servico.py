"""
Camada de dados da rastreabilidade.

Fluxo (já desenhado para o futuro):
    hash (12 dígitos)  ->  ChaveRastreio (OP, Produto, Lote do fornecedor do tecido)
                      ->  demais dados (cliente, NF, pedido, ...)

Hoje: dicionários fictícios.
Futuro: trocar o corpo de `resolver_hash` e `buscar_detalhes` por chamadas à API.
O app.py não precisa mudar.

Credenciais da API: ler SEMPRE de st.secrets["api"] (base_url, token, timeout).
Nunca escrever URL interna ou token neste arquivo.
Exemplo para quando a API entrar:

    import requests, streamlit as st
    cfg = st.secrets["api"]
    r = requests.get(
        f"{cfg['base_url']}/rastreabilidade/{h}",
        headers={"Authorization": f"Bearer {cfg['token']}"},
        timeout=cfg.get("timeout", 10),
    )
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

HASH_RE = re.compile(r"^\d{12}$")


@dataclass(frozen=True)
class ChaveRastreio:
    op: str
    produto: str
    lote_fornecedor: str


@dataclass(frozen=True)
class Rastreabilidade:
    hash: str
    cliente: str
    nota_fiscal: str
    data_nota: date
    pedido: str
    pedido_cliente: str
    op: str
    data_op: date
    produto: str
    materia_prima: str
    lote_fornecedor: str


def hash_valido(h: str | None) -> bool:
    return bool(h) and bool(HASH_RE.fullmatch(h.strip()))


# ---------------------------------------------------------------------------
# MOCK — passo 1: hash -> chave (OP, Produto, Lote do fornecedor do tecido)
# Dados fictícios: fabricante Vectra Work, cliente Petrobras
# ---------------------------------------------------------------------------
_CHAVES: dict[str, ChaveRastreio] = {
    "999999999999": ChaveRastreio("31045", "MACACÃO ANTICHAMA NR-10 AZUL ROYAL M", "TF-AC-77120"),
    "100000310452": ChaveRastreio("31052", "CAMISA OPERACIONAL ANTICHAMA LARANJA G", "TF-AC-77188"),
    "100000310669": ChaveRastreio("31066", "CALÇA BRIM ANTICHAMA AZUL MARINHO 44", "TF-BR-55301"),
    "100000310783": ChaveRastreio("31078", "JAQUETA ANTICHAMA C/ FAIXA REFLETIVA GG", "TF-AC-77234"),
}

# ---------------------------------------------------------------------------
# MOCK — passo 2: chave -> demais informações
# ---------------------------------------------------------------------------
_PETROBRAS = "PETRÓLEO BRASILEIRO S.A. – PETROBRAS"

_DETALHES: dict[ChaveRastreio, dict] = {
    _CHAVES["999999999999"]: dict(
        cliente=_PETROBRAS,
        nota_fiscal="000.084.512",
        data_nota=date(2026, 11, 6),
        pedido="PV-VW-12045",
        pedido_cliente="4500987321",
        data_op=date(2026, 10, 20),
        materia_prima="Tecido antichama 100% algodão tratado 260 g/m² – Azul Royal",
    ),
    _CHAVES["100000310452"]: dict(
        cliente=_PETROBRAS,
        nota_fiscal="000.084.530",
        data_nota=date(2026, 11, 7),
        pedido="PV-VW-12052",
        pedido_cliente="4500987355",
        data_op=date(2026, 10, 22),
        materia_prima="Tecido antichama 88/12 algodão/poliamida 240 g/m² – Laranja",
    ),
    _CHAVES["100000310669"]: dict(
        cliente=_PETROBRAS,
        nota_fiscal="000.084.557",
        data_nota=date(2026, 11, 9),
        pedido="PV-VW-12066",
        pedido_cliente="4500987402",
        data_op=date(2026, 10, 27),
        materia_prima="Brim antichama 100% algodão 300 g/m² – Azul Marinho",
    ),
    _CHAVES["100000310783"]: dict(
        cliente=_PETROBRAS,
        nota_fiscal="000.084.589",
        data_nota=date(2026, 11, 10),
        pedido="PV-VW-12078",
        pedido_cliente="4500987460",
        data_op=date(2026, 10, 29),
        materia_prima="Tecido antichama 260 g/m² + faixa refletiva antichama – Azul Royal",
    ),
}


def resolver_hash(h: str) -> ChaveRastreio | None:
    """FUTURO: decodificar o hash ou consultar a API para obter OP/Produto/Lote."""
    return _CHAVES.get(h)


def buscar_detalhes(chave: ChaveRastreio) -> dict | None:
    """FUTURO: GET na API com chave.op, chave.produto, chave.lote_fornecedor."""
    return _DETALHES.get(chave)


def buscar_rastreabilidade(h: str) -> Rastreabilidade | None:
    h = h.strip()
    if not hash_valido(h):
        return None
    chave = resolver_hash(h)
    if chave is None:
        return None
    det = buscar_detalhes(chave)
    if det is None:
        return None
    return Rastreabilidade(
        hash=h,
        op=chave.op,
        produto=chave.produto,
        lote_fornecedor=chave.lote_fornecedor,
        **det,
    )


def hashes_demo() -> list[str]:
    return list(_CHAVES.keys())