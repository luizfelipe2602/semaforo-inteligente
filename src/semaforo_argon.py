"""
Semáforo inteligente com solicitação de pedestres.
Sistemas Digitais / Sinais e Sistemas (Turma ENGCO241N01 — 6º Semestre).
Equipe: Luiz Felipe, Luigi Espagnoli, Jeremias, Dioermeson Junior,
        José Ricardo, Rhyatt Kayck e Guilherme Cavalcante.
Regras CONTRAN / MBST Vol. V.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Estado(str, Enum):
    VERDE = "VERDE"
    AMARELO = "AMARELO"
    VERMELHO = "VERMELHO"


@dataclass
class Tempos:
    verde_max: float = 45.0
    delay_apos_pedido: float = 3.0
    amarelo: float = 5.0
    travessia: float = 12.0


@dataclass
class Amostra:
    """Amostra detalhada para log de simulação e diagrama de temporização."""

    t: float
    botao: bool
    sensor: bool
    solicitacao_pendente: bool
    estado: str
    tempo_no_estado: float
    countdown_amarelo: Optional[float]
    verde: bool
    amarelo: bool
    vermelho: bool
    cor_botao: str
    botao_habilitado: bool


@dataclass
class SemaforoInteligente:
    tempos: Tempos = field(default_factory=Tempos)
    sensor_instalado: bool = True
    estado: Estado = Estado.VERDE
    solicitacao_pendente: bool = False
    botao_anterior: bool = False
    sensor_anterior: bool = False
    tempo_no_estado: float = 0.0
    countdown_amarelo: Optional[float] = None
    historico: List[Amostra] = field(default_factory=list)

    # Saídas do semáforo e da botoeira
    l_verde: bool = True
    l_amarelo: bool = False
    l_vermelho: bool = False
    cor_botao: str = "VERMELHO"
    botao_habilitado: bool = True

    def _atualizar_saidas(self) -> None:
        self.l_verde = self.estado == Estado.VERDE
        self.l_amarelo = self.estado == Estado.AMARELO
        self.l_vermelho = self.estado == Estado.VERMELHO

        if self.estado == Estado.VERDE:
            if self.solicitacao_pendente:
                self.cor_botao = "VERDE"
                self.botao_habilitado = False
            else:
                self.cor_botao = "VERMELHO"
                self.botao_habilitado = True
        elif self.estado == Estado.AMARELO:
            self.cor_botao = "AMARELO"
            self.botao_habilitado = False
        elif self.estado == Estado.VERMELHO:
            self.cor_botao = "VERDE"
            self.botao_habilitado = False

    def _registrar_pedido(self, botao: bool, sensor: bool) -> None:
        borda_botao = botao and not self.botao_anterior
        borda_sensor = self.sensor_instalado and (sensor and not self.sensor_anterior)
        pedido_novo = borda_botao or borda_sensor

        # Aceita pedido somente durante o VERDE quando o botão está habilitado
        if (
            pedido_novo
            and self.estado == Estado.VERDE
            and self.botao_habilitado
            and not self.solicitacao_pendente
        ):
            self.solicitacao_pendente = True
            self.countdown_amarelo = self.tempos.delay_apos_pedido

        self.botao_anterior = botao
        if self.sensor_instalado:
            self.sensor_anterior = sensor

    def _transicionar(self, dt: float) -> None:
        if self.estado == Estado.VERDE:
            if self.solicitacao_pendente:
                if self.countdown_amarelo is None:
                    self.countdown_amarelo = self.tempos.delay_apos_pedido
                self.countdown_amarelo = round(self.countdown_amarelo - dt, 6)
                if (
                    self.countdown_amarelo <= 1e-9
                    or self.tempo_no_estado >= self.tempos.verde_max - 1e-9
                ):
                    self.estado = Estado.AMARELO
                    self.tempo_no_estado = 0.0
                    self.countdown_amarelo = None
            elif self.tempo_no_estado >= self.tempos.verde_max - 1e-9:
                self.estado = Estado.AMARELO
                self.tempo_no_estado = 0.0

        elif self.estado == Estado.AMARELO:
            if self.tempo_no_estado >= self.tempos.amarelo - 1e-9:
                self.estado = Estado.VERMELHO
                self.tempo_no_estado = 0.0
                self.solicitacao_pendente = False
                self.countdown_amarelo = None

        elif self.estado == Estado.VERMELHO:
            if self.tempo_no_estado >= self.tempos.travessia - 1e-9:
                self.estado = Estado.VERDE
                self.tempo_no_estado = 0.0
                self.solicitacao_pendente = False
                self.countdown_amarelo = None

    def passo(
        self,
        dt: float,
        botao: bool = False,
        sensor: bool = False,
        t_abs: Optional[float] = None,
    ) -> Amostra:
        """Um ciclo de varredura: lê entradas, atualiza estado e saídas."""
        self._registrar_pedido(botao, sensor)
        self.tempo_no_estado = round(self.tempo_no_estado + dt, 6)
        self._transicionar(dt)
        self._atualizar_saidas()

        amostra = Amostra(
            t=0.0 if t_abs is None else round(t_abs, 6),
            botao=botao,
            sensor=sensor,
            solicitacao_pendente=self.solicitacao_pendente,
            estado=self.estado.value,
            tempo_no_estado=round(self.tempo_no_estado, 6),
            countdown_amarelo=(
                None
                if self.countdown_amarelo is None
                else round(max(0.0, self.countdown_amarelo), 6)
            ),
            verde=self.l_verde,
            amarelo=self.l_amarelo,
            vermelho=self.l_vermelho,
            cor_botao=self.cor_botao,
            botao_habilitado=self.botao_habilitado,
        )
        self.historico.append(amostra)
        return amostra

    def simular(
        self,
        duracao: float,
        dt: float = 0.1,
        eventos_botao: Optional[List[float]] = None,
        eventos_sensor: Optional[List[float]] = None,
        duracao_pulso: float = 0.5,
    ) -> List[Amostra]:
        """
        Simula o sistema por `duracao` segundos.
        `eventos_botao` / `eventos_sensor`: instantes (s) em que o pulso sobe.
        """
        self.historico.clear()
        eventos_botao = eventos_botao or []
        eventos_sensor = eventos_sensor or []
        t = 0.0
        self.estado = Estado.VERDE
        self.solicitacao_pendente = False
        self.botao_anterior = False
        self.sensor_anterior = False
        self.tempo_no_estado = 0.0
        self.countdown_amarelo = None
        self._atualizar_saidas()

        while t <= duracao + 1e-9:
            botao = any(ini <= t < ini + duracao_pulso for ini in eventos_botao)
            sensor = any(ini <= t < ini + duracao_pulso for ini in eventos_sensor)
            self.passo(dt, botao=botao, sensor=sensor, t_abs=round(t, 6))
            t = round(t + dt, 6)
        return self.historico


def main() -> None:
    """Demonstração rápida: pedido aos 4 s no sinal verde."""
    s = SemaforoInteligente()
    hist = s.simular(duracao=30.0, dt=0.2, eventos_botao=[4.0])
    print("t(s)  | BOTÃO | PEND | ESTADO   | COR BOTÃO | HAB | CONTAGEM | V A R")
    print("-" * 72)
    ultimo = None
    for a in hist:
        chave = (
            a.botao,
            a.solicitacao_pendente,
            a.estado,
            a.cor_botao,
            a.botao_habilitado,
            a.verde,
            a.amarelo,
            a.vermelho,
        )
        if chave != ultimo:
            cont = "-" if a.countdown_amarelo is None else f"{a.countdown_amarelo:4.1f}s"
            print(
                f"{a.t:5.1f} | {int(a.botao):5d} | {int(a.solicitacao_pendente):4d} | "
                f"{a.estado:8s} | {a.cor_botao:9s} | {int(a.botao_habilitado):3d} | "
                f"{cont:8s} | {int(a.verde)} {int(a.amarelo)} {int(a.vermelho)}"
            )
            ultimo = chave


if __name__ == "__main__":
    main()
