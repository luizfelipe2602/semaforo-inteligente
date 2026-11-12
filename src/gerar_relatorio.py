"""Gera Relatório Parcial N1 no formato do modelo RAD (adaptado ao aluno)."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Relatorio_Parcial_N1_Semaforo_Inteligente.docx"
ANEXOS = ROOT / "anexos"


def _set_cell_shading(cell, hex_color: str) -> None:
    tc = cell._tePr if hasattr(cell, "_tePr") else cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def _shade(cell, hex_color: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def _header_row(row, fill="1F4E79") -> None:
    for cell in row.cells:
        _shade(cell, fill)
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.bold = True
                run.font.size = Pt(10)


def _set_run(paragraph, text, *, bold=False, size=11, color=None):
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Calibri"
    if color:
        run.font.color.rgb = color
    return run


def _add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    return p


def _p(doc, text, *, bold=False, space_after=6):
    p = doc.add_paragraph()
    _set_run(p, text, bold=bold)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    return p


def _bullet(doc, text):
    p = doc.add_paragraph(text, style="List Bullet")
    return p


def gerar() -> Path:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)

    # ===== CAPA / IDENTIFICAÇÃO (modelo N1) =====
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_run(title, "RELATÓRIO PARCIAL N1 — ATIVIDADE ACADÊMICA", bold=True, size=14)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_run(sub, "Desenvolvimento de projetos · Sistemas Digitais para Computação", size=11)

    # Tabela identificação (espelha o modelo RAD)
    t = doc.add_table(rows=6, cols=2)
    t.style = "Table Grid"
    dados = [
        ("IDENTIFICAÇÃO", "Grupo / disciplina"),
        (
            "Estudante(s):",
            "Luiz Felipe; Luigi Espagnoli; Jeremias; Dioermeson Junior; "
            "José Ricardo; Rhyatt Kayck; Guilherme Cavalcante",
        ),
        ("Curso:", "Engenharia da Computação"),
        ("Disciplina:", "Sistemas Digitais para Computação"),
        ("Professor:", "Rodrigo de Almeida Magalhães"),
        ("Turma / Ano / Semestre:", "ENGCO241N01 / 2026 / 6º semestre"),
    ]
    for i, (a, b) in enumerate(dados):
        t.rows[i].cells[0].text = a
        t.rows[i].cells[1].text = b
    _header_row(t.rows[0])

    doc.add_paragraph()

    # Natureza
    nat = doc.add_table(rows=2, cols=1)
    nat.style = "Table Grid"
    nat.rows[0].cells[0].text = "NATUREZA DA ATIVIDADE ACADÊMICA REALIZADA"
    _header_row(nat.rows[0])
    nat.rows[1].cells[0].text = (
        "( ) Pesquisa   ( ) Extensão   ( ) Atividades Interdisciplinares   "
        "( ) Atividades Transversais   ( X ) Atividades Acadêmicas — Desenvolvimento de projetos"
    )

    doc.add_paragraph()

    obj = doc.add_table(rows=4, cols=1)
    obj.style = "Table Grid"
    obj.rows[0].cells[0].text = "ATIVIDADES DESENVOLVIDAS"
    _header_row(obj.rows[0])
    obj.rows[1].cells[0].text = (
        "Objetivo: Desenvolver e documentar a lógica de um semáforo veicular inteligente "
        "com solicitação de pedestres (botoeira e sensor opcional), identificando entradas/"
        "saídas, implementando a sequência temporizada, testando em simulador e relacionando "
        "o comportamento aos conceitos de Sinais e Sistemas."
    )
    obj.rows[2].cells[0].text = (
        "Resultados alcançados: Foi implementada em Python uma máquina de estados com "
        "detecção de borda na botoeira, variável de solicitação pendente e temporizadores "
        "(atraso de 3 s até o amarelo, 5 s de amarelo e 12 s de vermelho). Os testes "
        "passaram no simulador; foram gerados o diagrama do projeto e o diagrama de "
        "temporização. A botoeira mostra a permissão: verde veicular deixa o botão "
        "vermelho e habilitado; o clique torna o botão verde; amarelo e vermelho bloqueiam novo pedido."
    )
    obj.rows[3].cells[0].text = (
        "Público-alvo: Alunos dos cursos de computação, elétrica e automação."
    )

    doc.add_paragraph()
    meta = doc.add_table(rows=5, cols=1)
    meta.style = "Table Grid"
    meta.rows[0].cells[0].text = (
        "Pessoas envolvidas: Luiz Felipe, Luigi Espagnoli, Jeremias, Dioermeson Junior, "
        "José Ricardo, Rhyatt Kayck, Guilherme Cavalcante"
    )
    meta.rows[1].cells[0].text = "Professor: Rodrigo Magalhães"
    meta.rows[2].cells[0].text = "Turmas/Total de alunos beneficiados: ENGCO241N01 (7 alunos no grupo)"
    meta.rows[3].cells[0].text = "Carga utilizada (estimativa de desenvolvimento): 6 horas"
    meta.rows[4].cells[0].text = (
        "Como foi desenvolvido: Em etapas — (1) identificação de I/O e variáveis; "
        "(2) definição da máquina de estados e temporização; (3) programação em Python; "
        "(4) testes automatizados no simulador; (5) geração dos diagramas e redação deste relatório."
    )

    # ===== RELATO =====
    _add_heading(doc, "RELATO DAS ATIVIDADES", 1)
    _add_heading(doc, "PROJETO 1: Semáforo inteligente com solicitação de pedestres", 2)

    _p(
        doc,
        "O projeto consiste em um sistema de controle no qual o fluxo veicular opera em "
        "ciclo periódico (verde → amarelo → vermelho → verde) e uma solicitação externa "
        "(botoeira de pedestres, com sensor de presença opcional) pode alterar essa sequência "
        "de forma temporizada e previsível.",
    )
    _p(
        doc,
        "O pedido só é aceito com o semáforo verde. Nesse instante a botoeira muda de "
        "vermelho para verde e fica desabilitada. O semáforo entra em amarelo em até 3 s, "
        "permanece 5 s no amarelo e 12 s no vermelho de travessia. No amarelo o botão fica "
        "amarelo e bloqueado; no vermelho fica verde e bloqueado, sinalizando a travessia.",
    )

    _add_heading(doc, "1. Entradas, saídas e variáveis", 2)
    _p(doc, "1.1 Entradas", bold=True)
    tin = doc.add_table(rows=3, cols=3)
    tin.style = "Table Grid"
    tin.rows[0].cells[0].text = "Identificador"
    tin.rows[0].cells[1].text = "Dispositivo"
    tin.rows[0].cells[2].text = "Descrição"
    _header_row(tin.rows[0])
    tin.rows[1].cells[0].text = "B_Pedestre"
    tin.rows[1].cells[1].text = "Botoeira de pedestres"
    tin.rows[1].cells[2].text = "Registra nova solicitação de travessia quando acionada."
    tin.rows[2].cells[0].text = "S_Presenca (opc.)"
    tin.rows[2].cells[1].text = "Sensor de presença"
    tin.rows[2].cells[2].text = "Pode registrar presença conforme tipo/configuração."

    _p(doc, "1.2 Saídas", bold=True)
    tout = doc.add_table(rows=4, cols=3)
    tout.style = "Table Grid"
    tout.rows[0].cells[0].text = "Identificador"
    tout.rows[0].cells[1].text = "Saída física"
    tout.rows[0].cells[2].text = "Função"
    _header_row(tout.rows[0])
    for i, (a, b, c) in enumerate(
        [
            ("L_Verde", "Luz verde", "Autoriza fluxo de veículos na fase normal."),
            ("L_Amarela", "Luz amarela", "Transição entre verde e vermelho."),
            ("L_Vermelha", "Luz vermelha", "Interrompe o fluxo na travessia/transição."),
        ],
        start=1,
    ):
        tout.rows[i].cells[0].text = a
        tout.rows[i].cells[1].text = b
        tout.rows[i].cells[2].text = c

    _p(doc, "1.3 Variáveis internas", bold=True)
    _bullet(doc, "estado: VERDE | AMARELO | VERMELHO_PEDESTRE | VERMELHO_NORMAL")
    _bullet(doc, "solicitacaoPendente: pedido ainda não atendido")
    _bullet(doc, "botaoAnterior / sensorAnterior: detecção de borda")
    _bullet(doc, "temporizadores: tempo decorrido em cada fase")

    _p(doc, "1.4 Temporização (valores didáticos)", bold=True)
    tt = doc.add_table(rows=6, cols=3)
    tt.style = "Table Grid"
    tt.rows[0].cells[0].text = "Parâmetro"
    tt.rows[0].cells[1].text = "Valor"
    tt.rows[0].cells[2].text = "Finalidade"
    _header_row(tt.rows[0])
    for i, row in enumerate(
        [
            ("T_Atraso", "3 s", "Do clique no verde até o amarelo"),
            ("T_Amarelo", "5 s", "Amarelo (faixa CONTRAN/MBST: 3–5 s)"),
            ("T_Vermelho", "12 s", "Vermelho de travessia"),
            ("T_Verde_Max", "45 s", "Verde máximo se ninguém solicitar"),
            ("Botoeira", "por fase", "Verde→vermelho; amarelo→amarelo; vermelho→verde"),
        ],
        start=1,
    ):
        for j, val in enumerate(row):
            tt.rows[i].cells[j].text = val

    _add_heading(doc, "2. Lógica de programação (Python)", 2)
    _p(
        doc,
        "A lógica foi implementada como máquina de estados em Python (arquivo src/semaforo.py), "
        "equivalente ao pseudocódigo acadêmico. Em cada varredura: (1) detecta borda nas entradas; "
        "(2) atualiza solicitacaoPendente; (3) avalia o estado atual e os temporizadores; "
        "(4) aciona as saídas luminosas.",
    )
    _bullet(doc, "VERDE + clique → botão verde; amarelo em até 3 s")
    _bullet(doc, "AMARELO (5 s, botão amarelo desabilitado) → VERMELHO")
    _bullet(doc, "VERMELHO (12 s, botão verde desabilitado) → VERDE")
    _bullet(doc, "Sem clique, o verde segue até T_Verde_Max e então cumpre amarelo e vermelho")

    _add_heading(doc, "3. Testes no simulador", 2)
    _p(
        doc,
        "Os testes automatizados (tests/test_semaforo.py) cobrem os seis cenários do projeto. "
        "Execução: python -m unittest tests.test_semaforo -v",
    )
    ttest = doc.add_table(rows=7, cols=3)
    ttest.style = "Table Grid"
    ttest.rows[0].cells[0].text = "Teste"
    ttest.rows[0].cells[1].text = "Condição"
    ttest.rows[0].cells[2].text = "Resultado esperado"
    _header_row(ttest.rows[0])
    cenarios = [
        ("1. Clique no verde", "Botoeira aos 4 s", "Botão verde; amarelo em 3 s; vermelho após +5 s"),
        ("2. Duração do vermelho", "Após o amarelo", "12 s de vermelho e retorno ao verde"),
        ("3. Sem solicitação", "Nenhum toque", "Amarelo só ao fim do verde máximo (45 s)"),
        ("4. Toque no amarelo", "Botoeira desabilitada", "Cor amarela; pedido ignorado"),
        ("5. Toque no vermelho", "Botoeira desabilitada", "Cor verde; pedido ignorado"),
        ("6. Sensor opcional", "Borda no verde", "Mesma sequência do clique; nível contínuo não repete"),
    ]
    for i, row in enumerate(cenarios, start=1):
        for j, val in enumerate(row):
            ttest.rows[i].cells[j].text = val

    _add_heading(doc, "4. Diagrama de temporização", 2)
    _p(
        doc,
        "Foi gerado o diagrama anexos/diagrama_temporizacao.png para um clique aos 4 s. "
        "O verde segue até os 7 s (atraso de 3 s), o amarelo ocupa 5 s e o vermelho 12 s, "
        "com retorno ao verde aos 24 s.",
    )
    img_t = ANEXOS / "diagrama_temporizacao.png"
    if img_t.exists():
        doc.add_picture(str(img_t), width=Inches(6.2))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_run(cap, "Figura — Diagrama de temporização (entrada pedestre × saída verde)", size=9)

    _add_heading(doc, "5. Relação com Sinais e Sistemas", 2)
    _bullet(
        doc,
        "Sinais periódicos: na ausência de pedido, o ciclo verde–amarelo–vermelho se repete "
        "com período determinado pelos temporizadores (comportamento quase periódico).",
    )
    _bullet(
        doc,
        "Temporização: os parâmetros T_* definem janelas em que as saídas permanecem em nível "
        "alto/baixo; são a base da resposta temporal do sistema.",
    )
    _bullet(
        doc,
        "Sequência lógica: a máquina de estados impõe uma ordem válida de comutação "
        "(nunca verde→vermelho direto), garantindo transição segura via amarelo.",
    )
    _bullet(
        doc,
        "Entrada impulsiva: o pulso da botoeira é um evento discreto que, memorizado em "
        "solicitacaoPendente, modifica a fase seguinte do sinal de saída — exemplo didático "
        "de como uma excitação externa altera a resposta de um sistema sequencial.",
    )

    _add_heading(doc, "6. Considerações", 2)
    _bullet(doc, "Temporizadores não bloqueiam a varredura: entradas são lidas em todas as fases.")
    _bullet(doc, "Detecção de borda evita múltiplos pedidos com botão mantido pressionado.")
    _bullet(doc, "Tempos são ilustrativos; uso real exigiria projeto de engenharia e normas.")
    _bullet(doc, "O protótipo controla as três luzes veiculares; não inclui foco exclusivo de pedestre.")

    _add_heading(doc, "7. Conclusão", 2)
    _p(
        doc,
        "A implementação demonstra, de forma testável, como uma solicitação de pedestres "
        "altera a sequência normal de um semáforo mediante estados, temporizadores e memória "
        "de pedido. Os artefatos de código, diagrama do projeto e diagrama de temporização "
        "atendem às exigências de desenvolvimento e entrega da atividade.",
    )

    # ===== ANEXO =====
    _add_heading(doc, "ANEXO", 1)
    _p(doc, "A. Diagrama do projeto (esquema de I/O)", bold=True)
    svg = ANEXOS / "diagrama_projeto.svg"
    png_alt = ANEXOS / "diagrama_projeto.png"
    if png_alt.exists():
        doc.add_picture(str(png_alt), width=Inches(6.2))
    else:
        _p(
            doc,
            f"Arquivo vetorial disponível em: {svg.name} (pasta anexos/). "
            "Também há versão PNG se gerada pelo script de conversão.",
        )

    _p(doc, "B. Código-fonte principal", bold=True)
    _p(
        doc,
        "Localização: semaforo-inteligente/src/semaforo.py · testes: tests/test_semaforo.py · "
        "geração do gráfico: src/gerar_diagrama_temporizacao.py",
    )
    _p(
        doc,
        "Trecho essencial: no verde, solicitar() só é aceito com a botoeira habilitada; "
        "o amarelo começa quando o atraso de 3 s se esgota.",
    )

    _p(doc, "C. Como reproduzir", bold=True)
    _bullet(doc, "cd semaforo-inteligente")
    _bullet(doc, "python -m unittest tests.test_semaforo -v")
    _bullet(doc, "python src/semaforo.py")
    _bullet(doc, "python src/gerar_diagrama_temporizacao.py")

    doc.add_paragraph()
    assin = doc.add_table(rows=2, cols=2)
    assin.style = "Table Grid"
    assin.rows[0].cells[0].text = "Data: ____/____/______"
    assin.rows[0].cells[1].text = "Assinatura do estudante: ____________________"
    assin.rows[1].cells[0].text = "Data da aprovação: ____/____/______"
    assin.rows[1].cells[1].text = "Assinatura do professor: ____________________"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    path = gerar()
    print(f"Relatório gerado: {path}")
