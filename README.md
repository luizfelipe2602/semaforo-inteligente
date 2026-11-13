## Demo online (permanente)

- Comparar Cursor vs Argon: https://luizfelipe2602.github.io/semaforo-inteligente/
- Só Cursor: https://luizfelipe2602.github.io/semaforo-inteligente/cursor.html
- Só Argon: https://luizfelipe2602.github.io/semaforo-inteligente/argon.html

# Semáforo inteligente com solicitação de pedestres

Atividade 7 — Sistemas Digitais para Computação.  
Implementação em **Python** (simulador), com testes, diagramas e relatório no modelo parcial N1.

## Exigências atendidas

1. Identificação de entradas, saídas e variáveis  
2. Lógica de programação (Python + pseudocódigo no relatório)  
3. Testes no simulador (`unittest`)  
4. Diagrama de temporização (entrada pedestre × saída verde)  
5. Relação com Sinais e Sistemas (no relatório)

## Entrega

| Artefato | Caminho |
|----------|---------|
| Código-fonte | `src/semaforo.py` |
| Testes | `tests/test_semaforo.py` |
| Diagrama do projeto | `anexos/diagrama_projeto.png` |
| Diagrama de temporização | `anexos/diagrama_temporizacao.png` |
| Relatório (modelo N1) | `Relatorio_Parcial_N1_Semaforo_Inteligente.docx` |

## Como executar

```bash
cd semaforo-inteligente
python3 -m unittest tests.test_semaforo -v
python3 src/semaforo.py
python3 src/gerar_diagrama_temporizacao.py
python3 src/gerar_diagrama_projeto.py
python3 src/gerar_relatorio.py
```

Dependências: Python 3.10+, `matplotlib`, `python-docx`.

## Tempos e botoeira

- Clique no verde → botão verde; amarelo em **3 s**
- Amarelo **5 s** (faixa CONTRAN/MBST: 3–5 s) → botão amarelo, desabilitado
- Vermelho **12 s** → botão verde, desabilitado
- Sem clique, o verde dura no máximo **45 s**
- Permissão: verde veicular → botão vermelho; amarelo → amarelo; vermelho → verde  

Grupo: Luiz Felipe, Luigi Espagnoli, Jeremias, Dioermeson Junior, José Ricardo, Rhyatt Kayck, Guilherme Cavalcante · Turma ENGCO241N01 · 6º semestre.

## Demo no celular

Abra `demo/index.html` no navegador (toque na botoeira para pedir travessia).

```bash
cd semaforo-inteligente/demo
python3 -m http.server 8765
```
