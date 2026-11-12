"""Regras da botoeira e da temporização do semáforo inteligente."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from semaforo import CorBotao, Fase, SemaforoInteligente, Tempos, permissao_da  # noqa: E402


def _primeiro(historico, predicado):
    return next((amostra for amostra in historico if predicado(amostra)), None)


def _em(historico, instante, tolerancia=0.06):
    return next(amostra for amostra in historico if abs(amostra.t - instante) <= tolerancia)


class TestPermissao(unittest.TestCase):
    def test_cores_acompanham_a_fase(self) -> None:
        self.assertEqual(permissao_da(Fase.VERDE, False).cor, CorBotao.VERMELHO)
        self.assertTrue(permissao_da(Fase.VERDE, False).habilitado)
        self.assertEqual(permissao_da(Fase.VERDE, True).cor, CorBotao.VERDE)
        self.assertFalse(permissao_da(Fase.VERDE, True).habilitado)
        self.assertEqual(permissao_da(Fase.AMARELO, False).cor, CorBotao.AMARELO)
        self.assertFalse(permissao_da(Fase.AMARELO, False).habilitado)
        self.assertEqual(permissao_da(Fase.VERMELHO, False).cor, CorBotao.VERDE)
        self.assertFalse(permissao_da(Fase.VERMELHO, False).habilitado)


class TestTemporizacao(unittest.TestCase):
    def setUp(self) -> None:
        self.tempos = Tempos(atraso_amarelo=3, amarelo=5, vermelho=12, verde_max=45)

    def test_pedido_no_verde_amarelo_em_3s_e_vermelho_apos_5s(self) -> None:
        semaforo = SemaforoInteligente(tempos=self.tempos)
        historico = semaforo.simular(duracao=30, dt=0.05, eventos_botao=[4.0])

        durante = _em(historico, 6.0)
        self.assertEqual(durante.fase, Fase.VERDE.value)
        self.assertTrue(durante.pedido_aceito)
        self.assertEqual(durante.cor_botao, CorBotao.VERDE.value)
        self.assertFalse(durante.botao_habilitado)
        self.assertAlmostEqual(durante.atraso_restante, 1.0, delta=0.1)

        amarelo = _primeiro(historico, lambda a: a.fase == Fase.AMARELO.value)
        vermelho = _primeiro(historico, lambda a: a.fase == Fase.VERMELHO.value)
        self.assertIsNotNone(amarelo)
        self.assertIsNotNone(vermelho)
        self.assertAlmostEqual(amarelo.t, 7.0, delta=0.1)
        self.assertAlmostEqual(vermelho.t, 12.0, delta=0.1)
        self.assertEqual(amarelo.cor_botao, CorBotao.AMARELO.value)
        self.assertFalse(amarelo.botao_habilitado)
        self.assertEqual(vermelho.cor_botao, CorBotao.VERDE.value)
        self.assertFalse(vermelho.botao_habilitado)

    def test_vermelho_dura_12s_e_volta_ao_verde_com_botao_vermelho(self) -> None:
        semaforo = SemaforoInteligente(tempos=self.tempos)
        historico = semaforo.simular(duracao=30, dt=0.05, eventos_botao=[4.0])
        volta = _primeiro(
            historico,
            lambda a: a.fase == Fase.VERDE.value and a.t > 12,
        )
        self.assertIsNotNone(volta)
        self.assertAlmostEqual(volta.t, 24.0, delta=0.15)
        self.assertEqual(volta.cor_botao, CorBotao.VERMELHO.value)
        self.assertTrue(volta.botao_habilitado)
        self.assertFalse(volta.pedido_aceito)

    def test_sem_pedido_respeita_verde_maximo(self) -> None:
        semaforo = SemaforoInteligente(tempos=self.tempos)
        historico = semaforo.simular(duracao=52, dt=0.1)
        amarelo = _primeiro(historico, lambda a: a.fase == Fase.AMARELO.value)
        self.assertIsNotNone(amarelo)
        self.assertAlmostEqual(amarelo.t, 45.0, delta=0.15)
        self.assertFalse(any(a.pedido_aceito for a in historico if a.t < 45))

    def test_amarelo_e_vermelho_ignoram_novo_toque(self) -> None:
        semaforo = SemaforoInteligente(tempos=self.tempos)
        historico = semaforo.simular(duracao=20, dt=0.05, eventos_botao=[4.0, 8.0, 14.0])
        amarelo = _em(historico, 9.0)
        vermelho = _em(historico, 15.0)
        self.assertEqual(amarelo.fase, Fase.AMARELO.value)
        self.assertEqual(amarelo.cor_botao, CorBotao.AMARELO.value)
        self.assertIsNone(amarelo.atraso_restante)
        self.assertFalse(amarelo.botao_habilitado)
        self.assertEqual(vermelho.fase, Fase.VERMELHO.value)
        self.assertFalse(vermelho.pedido_aceito)
        self.assertFalse(semaforo.solicitar())

    def test_sensor_opcional_so_na_borda_e_so_no_verde(self) -> None:
        semaforo = SemaforoInteligente(tempos=self.tempos, sensor_instalado=True)
        historico = semaforo.simular(
            duracao=16,
            dt=0.05,
            eventos_sensor=[6.0],
            duracao_pulso=2.0,
        )
        self.assertTrue(_em(historico, 7.0).pedido_aceito)
        amarelo = _primeiro(historico, lambda a: a.fase == Fase.AMARELO.value)
        self.assertAlmostEqual(amarelo.t, 9.0, delta=0.1)

        sem_sensor = SemaforoInteligente(tempos=self.tempos, sensor_instalado=False)
        mudo = sem_sensor.simular(duracao=10, dt=0.1, eventos_sensor=[2.0])
        self.assertTrue(all(a.fase == Fase.VERDE.value and not a.pedido_aceito for a in mudo))

    def test_tempos_invalidos(self) -> None:
        with self.assertRaises(ValueError):
            Tempos(amarelo=0)


if __name__ == "__main__":
    unittest.main()
