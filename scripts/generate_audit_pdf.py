#!/usr/bin/env python3
"""Gera PDF da auditoria técnica reversa — Real Estate Mining."""

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "Auditoria_Tecnica_Real_Estate_Mining.pdf"


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontSize=22,
            spaceAfter=12,
            textColor=colors.HexColor("#1e3a5f"),
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontSize=11,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontSize=16,
            spaceBefore=16,
            spaceAfter=8,
            textColor=colors.HexColor("#1e40af"),
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=13,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#334155"),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=10,
            leading=13,
            leftIndent=14,
            bulletIndent=0,
            spaceAfter=3,
        ),
        "mono": ParagraphStyle(
            "Mono",
            parent=base["Code"],
            fontSize=8,
            leading=10,
            fontName="Courier",
            backColor=colors.HexColor("#f1f5f9"),
            leftIndent=8,
            rightIndent=8,
            spaceAfter=8,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.grey,
        ),
    }


def table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return t


def build_story(s):
    story = []
    today = date.today().strftime("%d/%m/%Y")

    story.append(Paragraph("Auditoria Técnica Reversa", s["title"]))
    story.append(Paragraph("Real Estate Mining — Mapeamento Completo do Estado Atual", s["subtitle"]))
    story.append(Paragraph(f"Gerado em: {today} | Arquiteto de Sistemas / Engenharia Cognitiva", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1e40af")))
    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "<b>Resumo executivo:</b> Plataforma de mineração de oportunidades imobiliárias em leilões "
            "(Brasil e EUA): scraping → persistência → extração de PDF → API REST → dashboard React. "
            "Maturidade estimada: <b>35–40%</b> em direção a produção.",
            s["body"],
        )
    )

    # --- 1 ---
    story.append(Paragraph("1. Arquitetura Geral e Stack Tecnológica", s["h1"]))
    story.append(Paragraph("Padrão arquitetural", s["h2"]))
    story.append(
        table(
            [
                ["Camada", "Padrão"],
                ["Backend", "Monólito modular Django (apps: properties, scrapers, pdf_processor)"],
                ["API", "REST via Django REST Framework (ViewSet + Router)"],
                ["Frontend", "SPA React (Create React App)"],
                ["Assíncrono", "Workers Celery (filas scraping, pdf_processing)"],
                ["Deploy", "Docker Compose multi-serviço + Nginx reverse proxy"],
            ],
            [4 * cm, 13 * cm],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Não é microserviços: um codebase Django com processos separados (API, worker, beat). "
            "Separação pragmática por apps + Template Method em BaseScraper.",
            s["body"],
        )
    )

    story.append(Paragraph("Stack — Backend (requirements.txt)", s["h2"]))
    story.append(
        table(
            [
                ["Pacote", "Versão", "Papel"],
                ["Django", "4.2.9", "ORM, admin, WSGI"],
                ["djangorestframework", "3.14.0", "API REST"],
                ["django-filter", "23.5", "Filtros na API"],
                ["django-cors-headers", "4.3.1", "CORS para React"],
                ["celery", "5.3.6", "Tasks assíncronas"],
                ["django-celery-beat", "2.5.0", "Agendamento (DB scheduler)"],
                ["django-celery-results", "2.5.1", "Resultados no PostgreSQL"],
                ["redis", "5.0.1", "Broker Celery"],
                ["psycopg2-binary", "2.9.9", "PostgreSQL"],
                ["gunicorn", "21.2.0", "Servidor WSGI"],
                ["httpx", "0.26.0", "HTTP async nos scrapers"],
                ["playwright", "1.41.0", "Scraping JS-heavy (EUA)"],
                ["beautifulsoup4", "4.12.2", "Parsing HTML (BR)"],
                ["pdfplumber / pytesseract", "—", "PDF + OCR fallback"],
            ],
            [4.5 * cm, 2.5 * cm, 10 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("Stack — Frontend e Infra", s["h2"]))
    story.append(
        Paragraph(
            "Frontend: React 18, react-scripts 5, Tailwind 3.4. Infra: PostgreSQL 15, Redis 7, "
            "Nginx Alpine, WireGuard (linuxserver), Python 3.11-slim, Node 20-alpine. "
            "Config: .env / .env.example. Ausente: CI/CD, README raiz, pyproject.toml.",
            s["body"],
        )
    )

    # --- 2 ---
    story.append(PageBreak())
    story.append(Paragraph("2. Mapeamento da Estrutura de Diretórios", s["h1"]))
    tree = """real-estate-mining/
├── backend/                 # Monólito Django
│   ├── config/              # settings, urls, celery, wsgi
│   ├── apps/
│   │   ├── properties/      # Modelos, API, admin, filtros
│   │   ├── scrapers/        # Base scraper, fontes BR/US, tasks
│   │   └── pdf_processor/   # Download + OCR + regex dívidas
│   ├── media/pdfs/          # PDFs baixados
│   ├── staticfiles/         # collectstatic (vendor)
│   └── Dockerfile
├── frontend/                # Dashboard React + Tailwind
│   └── src/components/      # Dashboard, filtros, cards, stats
├── nginx/                   # Reverse proxy (:80)
├── vpn/                     # wg0.conf WireGuard
└── docker-compose.yml"""
    story.append(Paragraph(tree.replace("\n", "<br/>"), s["mono"]))

    story.append(
        table(
            [
                ["Pasta", "Papel no ciclo de vida"],
                ["backend/config", "Bootstrap Django/Celery; rotas /api/ e /admin/"],
                ["apps/properties", "Domínio central: imóveis, fontes, API pública"],
                ["apps/scrapers", "Ingestão externa → upsert no banco"],
                ["apps/pdf_processor", "Enriquecimento pós-scrape via PDF"],
                ["frontend", "UI de descoberta, filtros e workflow de status"],
                ["nginx", "Gateway HTTP: API, admin, media, SPA"],
                ["vpn", "Túnel; celery_worker usa network_mode do WireGuard"],
            ],
            [4.5 * cm, 12.5 * cm],
        )
    )

    # --- 3 ---
    story.append(PageBreak())
    story.append(Paragraph("3. Funcionalidades Implementadas", s["h1"]))
    story.append(
        table(
            [
                ["Módulo", "Status", "Descrição"],
                ["Modelagem imóveis", "OK", "Property + enums país/leilão/dívida/status"],
                ["Fontes scraping", "OK", "ScrapingSource + scraper_class dinâmico"],
                ["Scraping BR", "Template", "BRLeiloeiroScraper — URL/seletores exemplo"],
                ["Scraping US", "Template", "USCountyScraper — Playwright + anti-bot básico"],
                ["Persistência", "OK", "update_or_create (source, external_id)"],
                ["Pipeline PDF", "OK", "Download → pdfplumber → OCR → regex PT/EN"],
                ["API REST", "OK", "CRUD + filtros + stats + trigger_pdf"],
                ["Celery Beat", "OK", "06:00 → schedule_active_scrapers"],
                ["Admin Django", "OK", "Gestão fontes e imóveis"],
                ["Dashboard React", "OK", "Listagem, filtros, PATCH status"],
                ["Autenticação", "Ausente", "API aberta (AllowAny)"],
                ["Notificações", "Ausente", "—"],
            ],
            [3.5 * cm, 2 * cm, 11.5 * cm],
        )
    )
    story.append(Spacer(1, 10))
    story.append(Paragraph("Fluxo A — Scraping agendado", s["h2"]))
    story.append(
        Paragraph(
            "Celery Beat (06:00) → schedule_active_scrapers → run_scraper_task [VPN] → "
            "import dinâmico scraper_class → fetch_listings/detail → Property.update_or_create → "
            "(se pdf_url) process_pdf_task.delay",
            s["body"],
        )
    )
    story.append(Paragraph("Fluxo B — Processamento PDF", s["h2"]))
    story.append(
        Paragraph(
            "process_pdf_task → download → media/pdfs/{uuid}.pdf → extract_text → "
            "key_values/debt_mentions → extra_data → preenche minimum_bid se vazio → pdf_processed=True",
            s["body"],
        )
    )
    story.append(Paragraph("Fluxo C — Dashboard", s["h2"]))
    story.append(
        Paragraph(
            "Browser → Nginx :80 → /api/* → Gunicorn → PropertyViewSet → PostgreSQL → JSON → React fetch",
            s["body"],
        )
    )
    story.append(Paragraph("Fluxo D — Workflow manual", s["h2"]))
    story.append(
        Paragraph(
            "PropertyCard → PATCH /api/properties/{id}/ {status} → PropertyUpdateSerializer → refresh lista/stats",
            s["body"],
        )
    )

    # --- 4 ---
    story.append(PageBreak())
    story.append(Paragraph("4. Modelagem de Dados e Entidades", s["h1"]))
    story.append(Paragraph("Relacionamento principal", s["h2"]))
    story.append(
        Paragraph(
            "<b>ScrapingSource</b> (1) —— (N) <b>Property</b>. FK source com SET_NULL. "
            "Unique: (source, external_id). Índices: país/cidade, leilão/data, status/roi, moeda/lance.",
            s["body"],
        )
    )

    story.append(Paragraph("ScrapingSource", s["h2"]))
    for b in [
        "name, url, country, scraper_class (module.Class)",
        "is_active, last_scraped_at, schedule_cron (não usado pelo Beat atual)",
        "config JSON (ex.: county no scraper US)",
    ]:
        story.append(Paragraph(f"• {b}", s["bullet"]))

    story.append(Paragraph("Property — grupos de campos", s["h2"]))
    story.append(
        table(
            [
                ["Grupo", "Campos principais"],
                ["Proveniência", "source, external_id, source_url, scraped_at"],
                ["Localização", "country, state, city, county, address, zip, lat/long"],
                ["Imóvel", "property_type, area_sqm/ft, bedrooms, bathrooms"],
                ["Leilão", "auction_type, auction_date, auction_number, process_number"],
                ["Financeiro", "*_cents (centavos), currency, debt_type, debt_details JSON"],
                ["Análise", "status, estimated_profit_pct (auto), roi_score (manual), notes"],
                ["PDF", "pdf_url, pdf_file, pdf_extracted_text, pdf_processed, extra_data"],
            ],
            [4 * cm, 13 * cm],
        )
    )
    story.append(Spacer(1, 8))
    story.append(Paragraph("Cálculo ROI (implementado no save)", s["h2"]))
    story.append(
        Paragraph(
            "estimated_profit_pct = ((market_value_cents - (minimum_bid_cents + total_debt_cents)) / total_cost) * 100. "
            "Requer market_value_cents preenchido — frequentemente vazio após scrape.",
            s["body"],
        )
    )

    # --- 5 ---
    story.append(PageBreak())
    story.append(Paragraph("5. Infraestrutura, Deploy e Ecossistema", s["h1"]))
    story.append(
        table(
            [
                ["Serviço Docker", "Função"],
                ["postgres", "BD principal + healthcheck"],
                ["redis", "Broker Celery"],
                ["wireguard", "VPN para scraping"],
                ["api", "Gunicorn :8000, 4 workers"],
                ["celery_worker", "network_mode: wireguard — scraping via VPN"],
                ["celery_beat", "Scheduler DB + crontab 06:00 fixo"],
                ["frontend", "CRA dev server :3000"],
                ["nginx", "Gateway :80 — /api, /admin, /media, /"],
            ],
            [4.5 * cm, 12.5 * cm],
        )
    )
    story.append(Spacer(1, 8))
    story.append(Paragraph("Volumes", s["h2"]))
    story.append(Paragraph("postgres_data, redis_data, pdf_storage", s["body"]))
    story.append(Paragraph("Backend Dockerfile", s["h2"]))
    story.append(
        Paragraph(
            "Poppler, Tesseract (por+eng), libs Chromium, playwright install chromium. "
            "Único settings: development (manage.py, wsgi, celery). Sem HTTPS no compose.",
            s["body"],
        )
    )
    story.append(Paragraph("Ausências operacionais", s["h2"]))
    for b in [
        "Pipeline CI/CD",
        "Testes automatizados",
        "Migrations além de 0001_initial",
        "Health endpoints / monitoring",
        "staticfiles/ versionado no repositório",
    ]:
        story.append(Paragraph(f"• {b}", s["bullet"]))

    # --- 6 ---
    story.append(PageBreak())
    story.append(Paragraph("6. Análise Crítica e Próximos Passos", s["h1"]))
    story.append(Paragraph("Pontos fortes", s["h2"]))
    for b in [
        "Domínio bem modelado (centavos, enums, índices, JSON flexível)",
        "Scraping extensível (BaseScraper + carregamento dinâmico)",
        "Filas Celery separadas com retries",
        "VPN dedicada ao worker de scraping",
        "Pipeline PDF dual (texto + OCR + regex bilíngue)",
        "Frontend funcional alinhado à API",
        "Docker Compose reproduzível",
    ]:
        story.append(Paragraph(f"• {b}", s["bullet"]))

    story.append(Paragraph("Gargalos e inconsistências", s["h2"]))
    story.append(
        table(
            [
                ["Área", "Problema"],
                ["Scrapers", "URLs/seletores placeholder — sem dados reais"],
                ["Segurança", "API sem auth; DEBUG no .env.example"],
                ["Produção", "Só development settings; frontend via npm start"],
                ["schedule_cron", "Campo no modelo não usado pelo Beat"],
                ["roi_score", "Ordenação padrão mas nunca calculado automaticamente"],
                ["pdf_file", "FileField não populado pela task"],
                ["Paginação", "page_size=20 no front ignorado pelo DRF"],
                ["Testes / Docs", "Zero testes; sem README raiz; sem OpenAPI"],
            ],
            [4 * cm, 13 * cm],
        )
    )
    story.append(Spacer(1, 10))

    story.append(Paragraph("Checklist — Crítico (bloqueante)", s["h2"]))
    for b in [
        "Scrapers reais por fonte (seletores, rate limit, CAPTCHA)",
        "Autenticação API (JWT/session) + permissões DRF",
        "settings/production.py (DEBUG=False, security headers)",
        "Build estático React no Nginx (não CRA dev)",
        "HTTPS",
        "Testes + CI",
    ]:
        story.append(Paragraph(f"☐ {b}", s["bullet"]))

    story.append(Paragraph("Checklist — Alto impacto", s["h2"]))
    for b in [
        "Regra clara para market_value_cents / roi_score",
        "schedule_cron por fonte ou PeriodicTask",
        "Associar PDF ao pdf_file",
        "Seeds ScrapingSource",
        "Remover staticfiles do git; collectstatic no deploy",
        "Backup PostgreSQL + PDFs",
    ]:
        story.append(Paragraph(f"☐ {b}", s["bullet"]))

    story.append(Paragraph("Checklist — Desejável", s["h2"]))
    for b in [
        "Notificações (ROI > X)",
        "Geocodificação e mapa",
        "Página de detalhe no front",
        "OpenAPI + health /api/health/",
        "Monitoramento (Sentry, Prometheus)",
    ]:
        story.append(Paragraph(f"☐ {b}", s["bullet"]))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(
        Paragraph(
            "<i>Documento gerado automaticamente a partir da auditoria técnica reversa do repositório "
            "real-estate-mining. Conteúdo reflete o estado do código na data de geração.</i>",
            s["footer"],
        )
    )

    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    s = styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Auditoria Técnica - Real Estate Mining",
        author="Auditoria Automatizada",
    )

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2 * cm, 1.2 * cm, f"Real Estate Mining — Auditoria Técnica — Pág. {doc.page}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, date.today().strftime("%d/%m/%Y"))
        canvas.restoreState()

    doc.build(build_story(s), onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF gerado: {OUTPUT}")


if __name__ == "__main__":
    main()
