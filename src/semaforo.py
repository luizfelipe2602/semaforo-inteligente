"""
Semáforo inteligente com solicitação de pedestres.

A botoeira mostra a permissão e só aceita pedido no verde veicular.
Depois do clique o semáforo vai ao amarelo em até 3 s, permanece 5 s
no amarelo e 12 s no vermelho de travessia.

Tempos didáticos — não dimensionam via pública.
Amarelo de referência CONTRAN/MBST: 3 s a 5 s.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Fase(str, Enum):
    VERDE = "VERDE"
    AMARELO = "AMARELO"
    VERMELHO = "VERMELHO"


class CorBotao(str, Enum):
    """Cor da botoeira, oposta à permissão veicular (exceto o ack do pedido)."""

    VERMELHO = "VERMELHO"
    AMARELO = "AMARELO"
    VERDE = "VERDE"


@dataclass(frozen=True)
class Tempos:
    """Parâmetros do ciclo. Unidades em segundos."""

    atraso_amarelo: float = 3.0
    amarelo: float = 5.0
    vermelho: float = 12.0
    verde_max: float = 45.0

    def __post_init__(self) -> None:
        for nome, valor in (
            ("atraso_amarelo", self.atraso_amarelo),
            ("amarelo", self.amarelo),
            ("vermelho", self.vermelho),
            ("verde_max", self.verde_max),
        ):
            if valor <= 0:
                raise ValueError(f"{nome} deve ser positivo, recebido {valor}")


@dataclass(frozen=True)
class Permissao:
    cor: CorBotao
    habilitado: bool
    rotulo: str


@dataclass(frozen=True)
class Amostra:
    t: float
    fase: str
    verde: bool
    amarelo: bool
    vermelho: bool
    pedido_aceito: bool
    cor_botao: str
    botao_habilitado: bool
    atraso_restante: Optional[float]


def _ms(segundos: float) -> int:
    return int(round(segundos * 1000))


def permissao_da(fase: Fase, pedido_aceito: bool) -> Permissao:
    """Verde → botão vermelho; amarelo → amarelo; vermelho → verde.

    Com pedido aceito, ainda no verde, o botão já fica verde e bloqueado.
    Amarelo e vermelho permanecem desabilitados.
    """
    if fase is Fase.VERDE and pedido_aceito:
        return Permissao(CorBotao.VERDE, False, "Pedido aceito")
    if fase is Fase.VERDE:
        return Permissao(CorBotao.VERMELHO, True, "Solicitar travessia")
    if fase is Fase.AMARELO:
        return Permissao(CorBotao.AMARELO, False, "Aguarde")
    return Permissao(CorBotao.VERDE, False, "Atravessar")


@dataclass
class SemaforoInteligente:
    tempos: Tempos = field(default_factory=Tempos)
    sensor_instalado: bool = True
    fase: Fase = Fase.VERDE
    pedido_aceito: bool = False
    atraso_restante: Optional[float] = None
    tempo_na_fase: float = 0.0
    t: float = 0.0
    historico: List[Amostra] = field(default_factory=list)
    _t_ms: int = field(default=0, repr=False)
    _fase_ms: int = field(default=0, repr=False)
    _atraso_ms: Optional[int] = field(default=None, repr=False)

    @property
    def permissao(self) -> Permissao:
        return permissao_da(self.fase, self.pedido_aceito)

    @property
    def l_verde(self) -> bool:
        return self.fase is Fase.VERDE

    @property
    def l_amarelo(self) -> bool:
        return self.fase is Fase.AMARELO

    @property
    def l_vermelho(self) -> bool:
        return self.fase is Fase.VERMELHO

    def reiniciar(self) -> None:
        self.fase = Fase.VERDE
        self.pedido_aceito = False
        self._t_ms = 0
        self._fase_ms = 0
        self._atraso_ms = None
        self._publicar_relogio()
        self.historico.clear()

    def solicitar(self) -> bool:
        """Aceita um pedido só com a botoeira habilitada (verde, sem pedido)."""
        if not self.permissao.habilitado:
            return False
        self.pedido_aceito = True
        self._atraso_ms = _ms(self.tempos.atraso_amarelo)
        self._publicar_relogio()
        return True

    def _publicar_relogio(self) -> None:
        self.t = self._t_ms / 1000
        self.tempo_na_fase = self._fase_ms / 1000
        self.atraso_restante = None if self._atraso_ms is None else self._atraso_ms / 1000

    def _ir_para(self, fase: Fase) -> None:
        self.fase = fase
        self._fase_ms = 0
        if fase is not Fase.VERDE:
            self._atraso_ms = None
        if fase is Fase.VERMELHO:
            self.pedido_aceito = False

    def avancar(self, dt: float) -> Amostra:
        if dt < 0:
            raise ValueError("dt não pode ser negativo")
        passo = _ms(dt)
        self._t_ms += passo
        self._fase_ms += passo
        self._transicionar(passo)
        self._publicar_relogio()
        amostra = self._amostra()
        self.historico.append(amostra)
        return amostra

    def _transicionar(self, passo_ms: int) -> None:
        if self.fase is Fase.VERDE and self.pedido_aceito:
            restante = _ms(self.tempos.atraso_amarelo) if self._atraso_ms is None else self._atraso_ms
            restante -= passo_ms
            if restante <= 0:
                self._ir_para(Fase.AMARELO)
            else:
                self._atraso_ms = restante
            return

        if self.fase is Fase.VERDE and self._fase_ms >= _ms(self.tempos.verde_max):
            self._ir_para(Fase.AMARELO)
            return

        if self.fase is Fase.AMARELO and self._fase_ms >= _ms(self.tempos.amarelo):
            self._ir_para(Fase.VERMELHO)
            return

        if self.fase is Fase.VERMELHO and self._fase_ms >= _ms(self.tempos.vermelho):
            self.pedido_aceito = False
            self._atraso_ms = None
            self._ir_para(Fase.VERDE)

    def _amostra(self) -> Amostra:
        perm = self.permissao
        return Amostra(
            t=round(self.t, 6),
            fase=self.fase.value,
            verde=self.l_verde,
            amarelo=self.l_amarelo,
            vermelho=self.l_vermelho,
            pedido_aceito=self.pedido_aceito,
            cor_botao=perm.cor.value,
            botao_habilitado=perm.habilitado,
            atraso_restante=None if self.atraso_restante is None else round(self.atraso_restante, 6),
        )

    def simular(
        self,
        duracao: float,
        dt: float = 0.05,
        eventos_botao: Optional[List[float]] = None,
        eventos_sensor: Optional[List[float]] = None,
        duracao_pulso: float = 0.4,
    ) -> List[Amostra]:
        """Avança o relógio e trata pulsos da botoeira e do sensor opcional.

        O sensor, quando instalado, equivale a um toque: só vale no verde,
        com a mesma trava da botoeira.
        """
        if dt <= 0:
            raise ValueError("dt deve ser positivo")
        self.reiniciar()
        pulsos_botao = eventos_botao or []
        pulsos_sensor = eventos_sensor or []
        botao_antes = False
        sensor_antes = False
        limite_ms = _ms(duracao)

        while self._t_ms <= limite_ms:
            instante = self._t_ms / 1000
            botao = any(ini <= instante < ini + duracao_pulso for ini in pulsos_botao)
            sensor = any(ini <= instante < ini + duracao_pulso for ini in pulsos_sensor)
            subida = (botao and not botao_antes) or (
                self.sensor_instalado and sensor and not sensor_antes
            )
            if subida:
                self.solicitar()
            botao_antes, sensor_antes = botao, sensor
            self.avancar(dt)
        return self.historico


def main() -> None:
    semaforo = SemaforoInteligente()
    historico = semaforo.simular(duracao=28.0, dt=0.1, eventos_botao=[4.0])
    print(f"{'t':>6}  {'fase':<10}  {'botão':<10}  {'hab':<3}  {'atraso'}")
    print("-" * 48)
    ultima = None
    for amostra in historico:
        chave = (amostra.fase, amostra.cor_botao, amostra.botao_habilitado, amostra.pedido_aceito)
        if chave == ultima:
            continue
        atraso = "—" if amostra.atraso_restante is None else f"{amostra.atraso_restante:4.1f}s"
        print(
            f"{amostra.t:6.1f}  {amostra.fase:<10}  {amostra.cor_botao:<10}  "
            f"{'sim' if amostra.botao_habilitado else 'não':<3}  {atraso}"
        )
        ultima = chave


if __name__ == "__main__":
    main()
