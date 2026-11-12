"""Diagrama do projeto: botoeira → controlador → luzes, com a cor da permissão."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]

TINTA = "#1c1915"
MUDO = "#5c564e"
PAPEL = "#f7f4ee"
VERDE = "#1f8a56"
AMARELO = "#c4962a"
VERMELHO = "#c4473d"


def _caixa(ax, x, y, w, h, titulo, borda):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor="#fffdf8",
            edgecolor=borda,
            linewidth=1.3,
        )
    )
    ax.text(x + w / 2, y + h - 0.32, titulo, ha="center", va="center", fontsize=11, color=borda)


def gerar(caminho: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11.2, 5.15), dpi=160)
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 5.15)
    ax.axis("off")
    fig.patch.set_facecolor(PAPEL)
    ax.set_facecolor(PAPEL)

    _caixa(ax, 0.35, 0.85, 3.05, 3.55, "ENTRADA", TINTA)
    ax.add_patch(FancyBboxPatch((0.6, 2.55), 2.55, 1.15, boxstyle="round,pad=0.02", facecolor="#fff", edgecolor=VERMELHO, linewidth=1.2))
    ax.text(1.87, 3.28, "B_Pedestre", ha="center", fontsize=11, color=TINTA)
    ax.text(1.87, 2.95, "Botoeira  ·  só no verde", ha="center", fontsize=8, color=MUDO)
    ax.add_patch(
        FancyBboxPatch(
            (0.6, 1.2),
            2.55,
            1.05,
            boxstyle="round,pad=0.02",
            facecolor="#fff",
            edgecolor="#b7aea2",
            linewidth=1.0,
            linestyle=(0, (3, 2)),
        )
    )
    ax.text(1.87, 1.85, "S_Presenca", ha="center", fontsize=11, color=TINTA)
    ax.text(1.87, 1.52, "Sensor opcional  ·  mesma trava", ha="center", fontsize=8, color=MUDO)

    _caixa(ax, 4.05, 0.85, 3.15, 3.55, "CONTROLADOR", AMARELO)
    for i, linha in enumerate(
        (
            "Fase: verde · amarelo · vermelho",
            "Pedido aceito no clique",
            "≤ 3 s até o amarelo",
            "5 s de amarelo",
            "12 s de vermelho",
        )
    ):
        ax.text(5.62, 3.55 - i * 0.42, linha, ha="center", fontsize=9, color=TINTA)

    _caixa(ax, 7.85, 0.85, 2.95, 3.55, "SAÍDAS", VERDE)
    for y, cor, nome in (
        (3.35, VERMELHO, "L_Vermelha"),
        (2.55, AMARELO, "L_Amarela"),
        (1.75, VERDE, "L_Verde"),
    ):
        ax.add_patch(Circle((8.45, y), 0.18, facecolor=cor, edgecolor="none"))
        ax.text(8.8, y, nome, ha="left", va="center", fontsize=10, color=TINTA)

    for x0, x1 in ((3.4, 4.05), (7.2, 7.85)):
        ax.add_patch(FancyArrowPatch((x0, 2.6), (x1, 2.6), arrowstyle="-|>", mutation_scale=12, color=TINTA, lw=1.2))

    ax.text(
        5.6,
        0.38,
        "Permissão: verde veicular → botão vermelho    ·    amarelo → botão amarelo    ·    vermelho → botão verde",
        ha="center",
        fontsize=8.5,
        color=MUDO,
    )
    ax.set_title(
        "Semáforo inteligente  ·  solicitação de pedestres",
        loc="left",
        fontsize=13,
        color=TINTA,
        pad=8,
    )

    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(caminho, dpi=160, bbox_inches="tight", facecolor=PAPEL)
    plt.close(fig)
    return caminho


if __name__ == "__main__":
    destino = ROOT / "anexos" / "diagrama_projeto.png"
    print(f"Gerado: {gerar(destino)}")
