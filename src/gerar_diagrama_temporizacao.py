"""Diagrama de temporização: botoeira, permissão e fases do semáforo."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from semaforo import SemaforoInteligente, Tempos  # noqa: E402

PALETA = {
    "fundo": "#f7f4ee",
    "tinta": "#1c1915",
    "eixo": "#8a8378",
    "pedido": "#9a3b32",
    "verde": "#1f8a56",
    "amarelo": "#c4962a",
    "vermelho": "#c4473d",
    "ack": "#2f6f56",
}


def _degrau(ax, tempos, base, sinal, cor):
    niveis = [base + (0.72 if valor else 0.08) for valor in sinal]
    ax.step(tempos, niveis, where="post", color=cor, linewidth=1.8)
    ax.fill_between(tempos, base, niveis, step="post", color=cor, alpha=0.14, linewidth=0)


def gerar(caminho: Path) -> Path:
    controlador = SemaforoInteligente(tempos=Tempos())
    # Pedido aos 4 s → amarelo aos 7 s → vermelho aos 12 s → verde aos 24 s.
    historico = controlador.simular(duracao=28.0, dt=0.05, eventos_botao=[4.0])

    t = [a.t for a in historico]
    pedido = [a.pedido_aceito and a.fase == "VERDE" for a in historico]
    verde = [a.verde for a in historico]
    amarelo = [a.amarelo for a in historico]
    vermelho = [a.vermelho for a in historico]

    fig, ax = plt.subplots(figsize=(11.2, 5.4), dpi=160)
    fig.patch.set_facecolor(PALETA["fundo"])
    ax.set_facecolor(PALETA["fundo"])

    _degrau(ax, t, 3.0, pedido, PALETA["ack"])
    _degrau(ax, t, 2.0, verde, PALETA["verde"])
    _degrau(ax, t, 1.0, amarelo, PALETA["amarelo"])
    _degrau(ax, t, 0.0, vermelho, PALETA["vermelho"])

    for instante, rotulo, cor in (
        (4.0, "clique", PALETA["pedido"]),
        (7.0, "amarelo", PALETA["amarelo"]),
        (12.0, "vermelho", PALETA["vermelho"]),
        (24.0, "verde", PALETA["verde"]),
    ):
        ax.axvline(instante, color=cor, linestyle=(0, (2, 2)), linewidth=0.8, alpha=0.85)
        ax.text(instante + 0.15, 4.15, rotulo, fontsize=8, color=cor, fontname="DejaVu Sans")

    ax.set_xlim(0, 28)
    ax.set_ylim(-0.15, 4.45)
    ax.set_yticks([0.4, 1.4, 2.4, 3.4])
    ax.set_yticklabels(["Vermelho  12 s", "Amarelo  5 s", "Verde", "Pedido aceito  ≤ 3 s"])
    ax.set_xlabel("Tempo (s)", color=PALETA["tinta"], fontsize=10)
    ax.set_title(
        "Temporização — clique no verde, amarelo em 3 s, amarelo por 5 s, vermelho por 12 s",
        loc="left",
        color=PALETA["tinta"],
        fontsize=12,
        pad=12,
        fontname="DejaVu Sans",
    )
    ax.tick_params(colors=PALETA["eixo"], length=0)
    for spine in ax.spines.values():
        spine.set_color("#e4ddd2")
    ax.grid(axis="x", color="#e4ddd2", linewidth=0.6)
    ax.legend(
        handles=[
            Line2D([0], [0], color=PALETA["ack"], lw=2, label="Pedido aceito (botão verde)"),
            Line2D([0], [0], color=PALETA["verde"], lw=2, label="Saída verde"),
            Line2D([0], [0], color=PALETA["amarelo"], lw=2, label="Saída amarela"),
            Line2D([0], [0], color=PALETA["vermelho"], lw=2, label="Saída vermelha"),
        ],
        frameon=False,
        fontsize=8,
        loc="upper right",
    )

    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(caminho, dpi=160)
    plt.close(fig)
    return caminho


if __name__ == "__main__":
    destino = ROOT / "anexos" / "diagrama_temporizacao.png"
    print(f"Gerado: {gerar(destino)}")
