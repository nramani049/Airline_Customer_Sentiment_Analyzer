"""
modules/report_generator.py

Yeh module ReportLab aur Matplotlib ka use karke analyzed reviews ka
ek professional aur clean PDF summary report in-memory generate karta hai.
"""

import io
from datetime import datetime

# Headless backend set karte hain taaki server par koi GUI window issue na aaye
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

from modules.analytics import calculate_kpis, get_airline_sentiment_summary


def create_sentiment_chart_image(kpis):
    """
    Matplotlib se sentiment distribution ka ek static chart image buffer banata hai.
    
    Hinglish explanation:
    Yeh function Matplotlib se Positive, Negative aur Neutral counts ka clean bar chart
    memory buffer (BytesIO) me banata hai taaki ReportLab PDF me embed kar sake.
    """
    labels = ["Positive", "Negative", "Neutral"]
    counts = [kpis["positive"], kpis["negative"], kpis["neutral"]]
    chart_colors = ["#2ecc71", "#e74c3c", "#95a5a6"]

    fig, ax = plt.subplots(figsize=(5, 2.5), dpi=150)
    bars = ax.bar(labels, counts, color=chart_colors, width=0.55)

    # Values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_title("Overall Sentiment Counts", fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel("Number of Reviews", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer


def generate_pdf_report(df):
    """
    Analyzed reviews DataFrame se ek complete PDF report in-memory generate karta hai.
    
    Hinglish explanation:
    Yeh function ReportLab ka use karke title, KPIs, airline breakdown table,
    chart image aur methodology notes ko ek downloadable PDF file me convert karta hai.
    """
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1A365D"),
            alignment=1,  # Center
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#4A5568"),
            alignment=1,  # Center
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=8,
            spaceAfter=4,
        )

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#2D3748"),
        )

        callout_style = ParagraphStyle(
            "Callout",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#742A2A"),
        )

        # 1. Header & Metadata
        elements.append(Paragraph("Airline Customer Sentiment Analyzer", title_style))
        elements.append(Paragraph("College Project Report | Social Media Analytics", subtitle_style))
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meta_text = f"Generated On: {now_str} &nbsp;|&nbsp; Demonstration Dataset (Synthetic Reviews)"
        elements.append(Paragraph(meta_text, subtitle_style))
        elements.append(Spacer(1, 12))

        # 2. KPI Summary
        kpis = calculate_kpis(df)
        elements.append(Paragraph("1. Executive Summary & KPIs", section_heading))

        kpi_table_data = [
            ["Metric", "Count", "Percentage"],
            ["Total Reviews Analyzed", str(kpis["total"]), "100.0%"],
            ["Positive Reviews", str(kpis["positive"]), f"{kpis['pos_percent']}%"],
            ["Negative Reviews", str(kpis["negative"]), f"{kpis['neg_percent']}%"],
            ["Neutral Reviews", str(kpis["neutral"]), f"{kpis['neu_percent']}%"],
        ]

        kpi_table = Table(kpi_table_data, colWidths=[200, 100, 100])
        kpi_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#EDF2F7")),
                    ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#22543D")),
                    ("TEXTCOLOR", (0, 3), (-1, 3), colors.HexColor("#742A2A")),
                    ("TEXTCOLOR", (0, 4), (-1, 4), colors.HexColor("#4A5568")),
                ]
            )
        )
        elements.append(kpi_table)
        elements.append(Spacer(1, 10))

        # 3. Static Chart
        if kpis["total"] > 0:
            chart_buffer = create_sentiment_chart_image(kpis)
            elements.append(Image(chart_buffer, width=320, height=160))
            elements.append(Spacer(1, 10))

        # 4. Airline-wise Breakdown Table
        elements.append(Paragraph("2. Airline-wise Sentiment Breakdown", section_heading))
        airline_summary = get_airline_sentiment_summary(df)

        if not airline_summary.empty:
            pivot = airline_summary.pivot(index="airline", columns="sentiment", values="count").fillna(0)
            for col in ["Positive", "Negative", "Neutral"]:
                if col not in pivot.columns:
                    pivot[col] = 0
            pivot = pivot[["Positive", "Negative", "Neutral"]].astype(int)
            pivot["Total"] = pivot["Positive"] + pivot["Negative"] + pivot["Neutral"]

            airline_table_data = [["Airline", "Positive", "Negative", "Neutral", "Total"]]
            for airline_name, row in pivot.iterrows():
                airline_table_data.append([
                    airline_name,
                    str(row["Positive"]),
                    str(row["Negative"]),
                    str(row["Neutral"]),
                    str(row["Total"]),
                ])

            airline_table = Table(airline_table_data, colWidths=[160, 80, 80, 80, 80])
            airline_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A5568")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            elements.append(airline_table)
        else:
            elements.append(Paragraph("No airline records available for the selected filters.", body_style))

        elements.append(Spacer(1, 12))

        # 5. Methodology & Limitations Notes
        elements.append(Paragraph("3. Methodology & Thresholds", section_heading))
        methodology_text = (
            "<b>Sentiment Engine:</b> VADER (Valence Aware Dictionary and sEntiment Reasoner).<br/>"
            "VADER computes a normalized compound polarity score ranging from -1.0 (most negative) to +1.0 (most positive).<br/>"
            "<b>Classification Thresholds:</b><br/>"
            "&bull; <b>Positive:</b> Compound score &ge; +0.05<br/>"
            "&bull; <b>Negative:</b> Compound score &le; -0.05<br/>"
            "&bull; <b>Neutral:</b> -0.05 &lt; Compound score &lt; +0.05"
        )
        elements.append(Paragraph(methodology_text, body_style))
        elements.append(Spacer(1, 8))

        elements.append(Paragraph("4. Important Limitations & Disclaimer", section_heading))
        disclaimer_text = (
            "<b>Disclaimer:</b> Sentiment predictions are automated estimates using rule-based lexical matching. "
            "VADER may misclassify sarcasm, colloquial Indian English expressions, double negatives, or complex flight delay contexts. "
            "This report is generated for academic demonstration purposes only."
        )
        elements.append(Paragraph(disclaimer_text, callout_style))

        # Build PDF into in-memory buffer
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue(), None

    except Exception as e:
        # User-friendly error message if PDF generation fails
        return None, f"PDF generation error: {str(e)}"
