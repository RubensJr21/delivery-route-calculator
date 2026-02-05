# gerar_pdf_rotas.py
import json
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)


def gerar_pdf_rotas(json_path: str, output_pdf: str) -> None:
  with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

  doc = SimpleDocTemplate(
      output_pdf,
      pagesize=landscape(A4),
      rightMargin=1 * cm,
      leftMargin=1 * cm,
      topMargin=1 * cm,
      bottomMargin=1 * cm,
  )

  styles = getSampleStyleSheet()
  titulo_style = ParagraphStyle(
      "Titulo",
      parent=styles["Heading1"],
      alignment=1,
      fontSize=20,
      textColor=colors.HexColor("#1f4788"),
      spaceAfter=0.5 * cm,
  )

  elems = []

  # Cabeçalho geral
  elems.append(Paragraph("Rotas de Entrega", titulo_style))
  elems.append(
      Paragraph(
          f"<i>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>",
          styles["Normal"],
      )
  )
  elems.append(Spacer(1, 0.5 * cm))

  # Uma seção por veículo
  first_time_vehicle = True
  for vehicle_id, rotas in data.items():
    #########################################################
    """
    Agrupamento atômico:
      Label Rota +
      Tabela de Endereços +
      Tabela de Famílias p/ Analista na Rota
    """
    #########################################################
    if not first_time_vehicle:
      elems.append(PageBreak())
    first_time_vehicle = False

    elems.append(Paragraph(f"Veículo: {vehicle_id}", styles["Heading2"]))
    elems.append(Spacer(1, 0.3 * cm))

    for idx, rota in enumerate(rotas, start=1):
      pontos = rota["pontos"]
      analistas = rota["analistas"]
      total_load = rota["total_load"]

      block = []  # tudo que precisa ficar junto

      # 1. Label da rota
      block.append(
          Paragraph(
              f"Rota {idx} - Carga total: {total_load} cestas", styles["Heading3"])
      )
      block.append(Spacer(1, 0.2 * cm))

      # 2. Tabela de endereços
      header = ["ID Família", "Analista", "Bairro", "Endereço atualizado"]
      linhas = [
          [
              p["id"],
              p["analista"],
              Paragraph(p["bairro"], styles["Normal"]),
              Paragraph(p["endereco_atualizado"], styles["Normal"])
          ]
          for p in pontos
      ]

      # Procurar como quebrar o as linhas e não estourar
      tabela = Table(
          [header] + linhas,
          colWidths=[2.5 * cm, 4 * cm, 4.5 * cm, 8 * cm],
          repeatRows=1  # cabeçalhos repete se a tabela em si quebrar
      )

      # PRECISO ESTUDAR PARA ENTENDER
      tabela.setStyle(
          TableStyle([
              ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
              ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
              ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
              ("ALIGN", (0, 0), (-1, 0), "CENTER"),
              # Centraliza TODAS as células
              ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ]))
      block.append(tabela)
      block.append(Spacer(1, 0.3 * cm))

      # 3. Tabela de famílias por analista
      resumo_header = ["Analista", "Qtd famílias"]
      resumo_linhas = [[a["name"], a["count"]] for a in analistas]
      tabela_resumo = Table(
          [resumo_header] + resumo_linhas, colWidths=[4 * cm, 2.5 * cm]
      )

      # PRECISO ESTUDAR PARA ENTENDER
      tabela_resumo.setStyle(
          TableStyle(
              [
                  ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                  ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                  ("ALIGN", (1, 1), (-1, -1), "CENTER"),
              ]
          )
      )
      block.append(tabela_resumo)
      block.append(Spacer(1, 0.5 * cm))

      # adiciona o bloco atômico
      elems.append(KeepTogether(block))

  doc.build(elems)


if __name__ == "__main__":
  gerar_pdf_rotas("resolved_routes.json", "relatorio_rotas.pdf")
