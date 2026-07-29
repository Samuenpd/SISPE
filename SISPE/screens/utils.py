import os
import re
import unicodedata
from datetime import datetime

from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


# ---------- Visual: sombra suave para dar profundidade calma aos cards ----------

def aplicar_sombra(widget, blur=28, y_offset=6, alpha=28):
    """Aplica uma sombra suave e discreta a um card/frame, para dar sensação
    de profundidade sem pesar visualmente (efeito calmo, não dramático)."""
    sombra = QGraphicsDropShadowEffect(widget)
    sombra.setBlurRadius(blur)
    sombra.setXOffset(0)
    sombra.setYOffset(y_offset)
    sombra.setColor(QColor(46, 58, 70, alpha))  # tom neutro azulado, bem translúcido
    widget.setGraphicsEffect(sombra)


# ---------- Gravidade: mantém consistência entre telas e banco de dados ----------

GRAVIDADE_EXIBIR = {"baixo": "Baixo", "medio": "Médio", "grave": "Grave"}
GRAVIDADE_BANCO = {"baixo": "baixo", "médio": "medio", "medio": "medio", "grave": "grave"}


def gravidade_para_db(texto_combo):
    """Converte o texto do combobox (ex: 'Médio') para o valor salvo no banco (ex: 'medio')."""
    chave = _remover_acentos(texto_combo.strip().lower())
    return GRAVIDADE_BANCO.get(texto_combo.strip().lower(), chave)


def gravidade_para_exibir(valor_db):
    """Converte o valor do banco (ex: 'medio') para o texto exibido (ex: 'Médio')."""
    chave = _remover_acentos(valor_db.strip().lower())
    return GRAVIDADE_EXIBIR.get(chave, valor_db.capitalize())


def _remover_acentos(texto):
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _slugify(texto):
    """Transforma um nome em algo seguro para usar como nome de pasta/arquivo."""
    texto = _remover_acentos(texto).strip().lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_") or "aluno"


# ---------- Geração de PDF do relatório ----------

def pasta_relatorios(nome_aluno):
    """Retorna (e cria, se necessário) a pasta de relatórios do aluno dentro de Documentos."""
    base = os.path.join(os.path.expanduser("~"), "Documents", "SISPE", "Relatorios", _slugify(nome_aluno))
    os.makedirs(base, exist_ok=True)
    return base


def gerar_pdf_relatorio(aluno, texto_relatorio, psicologo_username=None, data_hora=None):
    """
    Gera um PDF do relatório mais recente e salva em Documentos/SISPE/Relatorios/<aluno>/.

    aluno: dict com 'nome', 'sala', 'serie', 'gravidade' (texto já formatado p/ exibição)
    Retorna o caminho completo do arquivo gerado.
    """
    if data_hora is None:
        data_hora = datetime.now()

    pasta = pasta_relatorios(aluno["nome"])
    nome_arquivo = f"relatorio_{data_hora.strftime('%Y-%m-%d_%Hh%M')}.pdf"
    caminho = os.path.join(pasta, nome_arquivo)

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "TituloSISPE", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#1e293b")
    )
    label_style = ParagraphStyle(
        "LabelSISPE", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#64748b")
    )
    corpo_style = ParagraphStyle(
        "CorpoSISPE", parent=styles["Normal"], fontSize=12, leading=18,
        textColor=colors.HexColor("#1e293b")
    )

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm, topMargin=2 * cm, bottomMargin=2 * cm
    )
    story = []

    story.append(Paragraph("Relatório de Atendimento Psicológico", titulo_style))
    story.append(Paragraph("Sistema SISPE", label_style))
    story.append(Spacer(1, 16))

    dados_aluno = [
        ["Aluno", aluno.get("nome", "-")],
        ["Sala", aluno.get("sala", "-")],
        ["Série", aluno.get("serie", "-")],
        ["Gravidade", aluno.get("gravidade", "-")],
        ["Data e hora do relatório", data_hora.strftime("%d/%m/%Y às %H:%M")],
    ]
    if psicologo_username:
        dados_aluno.append(["Psicólogo(a) responsável", psicologo_username])

    tabela = Table(dados_aluno, colWidths=[5 * cm, 10 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Relatório", ParagraphStyle(
        "SubtituloSISPE", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#1e293b")
    )))
    story.append(Spacer(1, 8))

    for paragrafo in texto_relatorio.split("\n"):
        if paragrafo.strip():
            texto_seguro = (
                paragrafo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            story.append(Paragraph(texto_seguro, corpo_style))
            story.append(Spacer(1, 6))

    doc.build(story)
    return caminho
