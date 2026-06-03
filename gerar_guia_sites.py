from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from datetime import datetime

OUTPUT = "/home/fabianosf/Documents/real-estate-mining/Guia_Como_Adicionar_Sites.pdf"
W_PAGE, H_PAGE = A4
MARGIN = 1.5 * cm
FRAME_W = W_PAGE - 2 * MARGIN

INDIGO      = colors.HexColor('#4F46E5')
INDIGO_DARK = colors.HexColor('#3730A3')
INDIGO_LIGHT= colors.HexColor('#EEF2FF')
GRAY_900    = colors.HexColor('#111827')
GRAY_700    = colors.HexColor('#374151')
GRAY_500    = colors.HexColor('#6B7280')
GRAY_200    = colors.HexColor('#E5E7EB')
GRAY_50     = colors.HexColor('#F9FAFB')
GREEN       = colors.HexColor('#059669')
GREEN_LIGHT = colors.HexColor('#ECFDF5')
RED         = colors.HexColor('#DC2626')
RED_LIGHT   = colors.HexColor('#FEF2F2')
YELLOW      = colors.HexColor('#D97706')
YELLOW_LIGHT= colors.HexColor('#FFFBEB')
ORANGE      = colors.HexColor('#EA580C')
ORANGE_LIGHT= colors.HexColor('#FFF7ED')
CODE_BG     = colors.HexColor('#1E1E2E')
CODE_FG     = colors.HexColor('#CDD6F4')
CODE_ACCENT = colors.HexColor('#89B4FA')
WHITE       = colors.white

def S(name, **kw): return ParagraphStyle(name, **kw)

ST = {
    'title':   S('t', fontName='Helvetica-Bold', fontSize=13, textColor=INDIGO, leading=18, spaceBefore=14, spaceAfter=4),
    'sub':     S('s', fontName='Helvetica-Bold', fontSize=10.5, textColor=GRAY_900, leading=15, spaceBefore=10, spaceAfter=3),
    'body':    S('b', fontName='Helvetica', fontSize=9.5, textColor=GRAY_700, leading=15, spaceAfter=3),
    'bold':    S('bd', fontName='Helvetica-Bold', fontSize=9.5, textColor=GRAY_900, leading=15),
    'step':    S('st', fontName='Helvetica-Bold', fontSize=11, textColor=WHITE, leading=15),
    'code':    S('c', fontName='Courier', fontSize=8.5, textColor=CODE_FG, leading=13),
    'code_dim':S('cd', fontName='Courier-Oblique', fontSize=8, textColor=colors.HexColor('#6C7086'), leading=12),
    'num':     S('n', fontName='Helvetica-Bold', fontSize=22, textColor=INDIGO, leading=26, alignment=TA_CENTER),
    'small':   S('sm', fontName='Helvetica', fontSize=8.5, textColor=GRAY_500, leading=13),
}

def sp(h=6):  return Spacer(1, h)
def hr(c=GRAY_200, t=0.5): return HRFlowable(width='100%', thickness=t, color=c, spaceAfter=6, spaceBefore=4)

def code_block(lines):
    rows = []
    for line in lines:
        if line == '':
            rows.append([Paragraph(' ', ST['code'])])
        elif line.startswith('#'):
            rows.append([Paragraph(line, ST['code_dim'])])
        else:
            rows.append([Paragraph(line, ST['code'])])
    t = Table(rows, colWidths=[FRAME_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), CODE_BG),
        ('LEFTPADDING',  (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING',   (0,0), (0,0),   10),
        ('TOPPADDING',   (0,1), (-1,-1), 3),
        ('BOTTOMPADDING',(0,-1),(-1,-1), 10),
        ('BOTTOMPADDING',(0,0), (-1,-2), 3),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#313244')),
    ]))
    return [t, sp(6)]

def box(text, bg, border):
    t = Table([[Paragraph(text, ST['body'])]], colWidths=[FRAME_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), bg),
        ('LEFTPADDING',  (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING',   (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1.5, border),
    ]))
    return [t, sp(6)]

def info(t):   return box(t, INDIGO_LIGHT, INDIGO)
def warn(t):   return box(t, YELLOW_LIGHT, YELLOW)
def ok(t):     return box(t, GREEN_LIGHT,  GREEN)
def alert(t):  return box(t, ORANGE_LIGHT, ORANGE)

def step_badge(n, label, color=INDIGO):
    t = Table([[
        Paragraph(str(n), ST['num']),
        Paragraph(label, ST['step']),
    ]], colWidths=[1.4*cm, FRAME_W - 1.4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), color),
        ('LEFTPADDING',  (0,0), (0,-1), 4),
        ('LEFTPADDING',  (1,0), (1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING',   (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return [t, sp(8)]


# ── Header/Footer ────────────────────────────────────────────────────────────────
def draw_cover(c):
    c.setFillColor(INDIGO_DARK)
    c.rect(0, 0, W_PAGE, H_PAGE, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#3730A3'))
    c.rect(0, H_PAGE * 0.52, W_PAGE, H_PAGE * 0.48, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#4338CA'))
    c.ellipse(W_PAGE * 0.6, H_PAGE * 0.55, W_PAGE * 1.2, H_PAGE * 1.05, fill=1, stroke=0)

    # Ícone
    c.setFillColor(colors.HexColor('#6366F1'))
    c.roundRect(MARGIN, H_PAGE - 3.8*cm, 1.8*cm, 1.8*cm, 6, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 20)
    c.setFillColor(WHITE)
    c.drawCentredString(MARGIN + 0.9*cm, H_PAGE - 2.8*cm, 'R')

    # Titulo
    c.setFont('Helvetica-Bold', 26)
    c.setFillColor(WHITE)
    c.drawString(MARGIN, H_PAGE - 5.2*cm, 'Como Adicionar Sites')
    c.setFont('Helvetica-Bold', 26)
    c.drawString(MARGIN, H_PAGE - 6.0*cm, 'ao Sistema')
    c.setFont('Helvetica', 13)
    c.setFillColor(colors.HexColor('#C7D2FE'))
    c.drawString(MARGIN, H_PAGE - 6.9*cm, 'Real Estate Mining — Guia Passo a Passo')
    c.setStrokeColor(colors.HexColor('#6366F1'))
    c.setLineWidth(2)
    c.line(MARGIN, H_PAGE - 7.4*cm, W_PAGE - MARGIN, H_PAGE - 7.4*cm)

    # Descricao
    c.setFont('Helvetica', 10)
    c.setFillColor(colors.HexColor('#A5B4FC'))
    linhas = [
        'Este guia explica como funciona o processo completo:',
        'desde receber os links do seu irmao ate ver os imoveis',
        'aparecendo automaticamente no dashboard.',
    ]
    y = H_PAGE - 8.3*cm
    for l in linhas:
        c.drawString(MARGIN, y, l)
        y -= 0.55*cm

    # Caixa fluxo rapido
    bx, by = MARGIN, H_PAGE * 0.34
    bw, bh = W_PAGE - 2*MARGIN, 4.5*cm
    c.setFillColor(colors.HexColor('#312E81'))
    c.rect(bx, by, bw, bh, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor('#6366F1'))
    c.setLineWidth(1)
    c.rect(bx, by, bw, bh, fill=0, stroke=1)

    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(colors.HexColor('#A5B4FC'))
    c.drawString(bx + 0.7*cm, by + 4.0*cm, 'FLUXO RESUMIDO')

    fluxo = [
        ('1', 'Seu irmao passa os links dos sites de leilao'),
        ('2', 'Voce cadastra os sites no Admin do sistema'),
        ('3', 'Voce envia os links para o desenvolvedor configurar'),
        ('4', 'Sistema busca imoveis automaticamente todo dia as 06:00'),
        ('5', 'Imoveis aparecem no dashboard para revisar e classificar'),
    ]
    yf = by + 3.3*cm
    for num, txt in fluxo:
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(colors.HexColor('#89B4FA'))
        c.drawString(bx + 0.7*cm, yf, f'{num}.')
        c.setFont('Helvetica', 9)
        c.setFillColor(WHITE)
        c.drawString(bx + 1.2*cm, yf, txt)
        yf -= 0.58*cm

    # Rodape
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#6366F1'))
    c.drawString(MARGIN, 1.4*cm, f'Real Estate Mining  |  {datetime.now().strftime("%d/%m/%Y")}')
    c.drawRightString(W_PAGE - MARGIN, 1.4*cm, 'Guia de Operacao')


def on_first_page(canvas, doc):
    draw_cover(canvas)


def on_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INDIGO)
    canvas.rect(0, H_PAGE - 1.1*cm, W_PAGE, 1.1*cm, fill=1, stroke=0)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(WHITE)
    canvas.drawString(MARGIN, H_PAGE - 0.73*cm, 'Real Estate Mining')
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#A5B4FC'))
    canvas.drawRightString(W_PAGE - MARGIN, H_PAGE - 0.73*cm, 'Como Adicionar Sites ao Sistema')
    canvas.setFillColor(GRAY_200)
    canvas.rect(0, 0, W_PAGE, 0.9*cm, fill=1, stroke=0)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawString(MARGIN, 0.33*cm, f'Gerado em {datetime.now().strftime("%d/%m/%Y")}')
    canvas.drawCentredString(W_PAGE/2, 0.33*cm, 'Real Estate Mining')
    canvas.drawRightString(W_PAGE - MARGIN, 0.33*cm, f'Pagina {doc.page - 1}')
    canvas.restoreState()


# ── Conteúdo ──────────────────────────────────────────────────────────────────
def intro():
    e = []
    e.append(Paragraph('Por que o dashboard esta vazio?', ST['title']))
    e.append(hr(INDIGO, 1.2))
    e += info(
        '<b>O sistema esta funcionando corretamente.</b> O dashboard esta vazio porque '
        'os scrapers ainda nao sabem quais sites acessar. Eles precisam ser configurados '
        'com os enderecos reais dos sites de leilao que o seu irmao usa no curso.'
    )
    e.append(sp(6))
    e += [Paragraph(
        'Pense assim: o sistema e como um funcionario muito eficiente que sabe exatamente '
        'como pesquisar imoveis — mas ainda nao recebeu a lista de sites para pesquisar. '
        'Este guia explica como dar essa lista para ele.', ST['body'])]
    return e


def fluxo_completo():
    e = []
    e.append(Paragraph('O fluxo completo explicado', ST['title']))
    e.append(hr(INDIGO, 1.2))

    data = [
        ['Quem faz', 'O que faz', 'Resultado'],
        ['Seu irmao',       'Passa os links dos sites do curso',              'Voce recebe as URLs'],
        ['Voce',            'Cadastra os sites no Admin do sistema',          'Sites salvos no banco'],
        ['Voce',            'Envia os links para o desenvolvedor',            'Desenvolvedor configura'],
        ['Desenvolvedor',   'Programa o scraper para aquele site especifico', 'Scraper funcionando'],
        ['Sistema',         'Acessa os sites todo dia as 06:00',              'Imoveis no dashboard'],
        ['Voce / VA',       'Revisa, classifica e anota os imoveis',         'Oportunidades identificadas'],
    ]
    t = Table(data, colWidths=[4*cm, 7.5*cm, 6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), INDIGO),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8.5),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTNAME',    (0,1), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (0,1), (0,3), GRAY_900),
        ('TEXTCOLOR',   (0,4), (0,4), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR',   (0,5), (0,5), GREEN),
        ('TEXTCOLOR',   (0,6), (0,6), colors.HexColor('#0891B2')),
        ('TEXTCOLOR',   (1,1), (1,-1), GRAY_700),
        ('TEXTCOLOR',   (2,1), (2,-1), GREEN),
        ('FONTNAME',    (2,1), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE',    (2,1), (2,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
    ]))
    e += [t, sp(10)]

    e += warn(
        '<b>Importante:</b> Cada site de leilao tem uma estrutura diferente. '
        'Por isso, alem de cadastrar o site no sistema, voce precisa enviar o link '
        'para o desenvolvedor configurar o scraper especifico para aquele site.'
    )
    return e


def passo1():
    e = []
    e += step_badge(1, 'Receber os links do seu irmao', INDIGO)
    e += [Paragraph(
        'Peca para o seu irmao passar os links dos sites que ele usa no curso. '
        'Pode ser um site de condado americano, um site de leilao judicial brasileiro, '
        'ou qualquer outro portal que liste imoveis para leilao.', ST['body'])]
    e.append(sp(6))

    e += [Paragraph('Exemplos de tipos de sites que o curso pode indicar:', ST['sub'])]
    data = [
        ['Tipo de site',          'Exemplo de URL',                        'Pais'],
        ['Condado americano',     'https://www.miamidade.gov/taxcollector', 'EUA'],
        ['Portal de tax lien',    'https://www.bid4assets.com',             'EUA'],
        ['Portal de tax deed',    'https://www.realauction.com',            'EUA'],
        ['Leiloeiro judicial BR', 'https://www.leilaovip.com.br',           'BR'],
        ['Portal de leiloes BR',  'https://www.megaleiloes.com.br',         'BR'],
    ]
    t = Table(data, colWidths=[5*cm, 8*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), GRAY_900),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8.5),
        ('FONTNAME',    (0,1), (0,-1), 'Helvetica'),
        ('FONTNAME',    (1,1), (1,-1), 'Courier'),
        ('FONTNAME',    (2,1), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (1,1), (1,-1), INDIGO),
        ('TEXTCOLOR',   (0,1), (0,-1), GRAY_700),
        ('TEXTCOLOR',   (2,1), (2,3), colors.HexColor('#0369A1')),
        ('TEXTCOLOR',   (2,4), (2,5), GREEN),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ]))
    e += [t, sp(8)]
    e += info(
        '<b>Dica:</b> Quanto mais informacoes o seu irmao passar sobre o site '
        '(ex: "neste site os imoveis ficam na aba Tax Lien do condado Broward"), '
        'mais rapido o desenvolvedor consegue configurar o scraper.'
    )
    return e


def passo2():
    e = []
    e += step_badge(2, 'Cadastrar o site no Admin do sistema', colors.HexColor('#7C3AED'))

    e += [Paragraph(
        'Com o link em maos, acesse o painel administrativo do sistema '
        'e cadastre o site como uma nova "Fonte de Scraping".', ST['body'])]
    e.append(sp(8))

    # Sub: acessar o admin
    e += [Paragraph('2.1  Acessar o Admin', ST['sub'])]
    e += code_block(['http://localhost:8000/admin/'])
    e += [Paragraph(
        'Faca login com: <font name="Courier">fabiano.freitas@gmail.com</font> / '
        '<font name="Courier">260281xx</font>', ST['body'])]
    e.append(sp(8))

    # Sub: navegar
    e += [Paragraph('2.2  Navegar ate Scraping Sources', ST['sub'])]
    e += [Paragraph(
        'Na tela inicial do Admin, localize a secao <b>Properties</b> e clique em '
        '<b>Scraping sources</b>. Em seguida clique no botao '
        '<b>"Add scraping source"</b> no canto superior direito.', ST['body'])]
    e.append(sp(8))

    # Sub: preencher
    e += [Paragraph('2.3  Preencher o formulario', ST['sub'])]
    data = [
        ['Campo',          'O que colocar',                                         'Exemplo'],
        ['Name',           'Um nome para identificar este site',                    'Bid4Assets - Florida'],
        ['Url',            'O endereco completo do site',                           'https://bid4assets.com'],
        ['Country',        'Selecione o pais: US ou BR',                            'US'],
        ['Scraper class',  'Deixe como esta (desenvolvedor vai ajustar)',            'apps.scrapers.sources.us_county.USCountyScraper'],
        ['Is active',      'Deixe DESMARCADO por enquanto',                         '(desmarcado)'],
        ['Schedule cron',  'Horario de execucao — pode deixar o padrao',            '0 6 * * *'],
        ['Config',         'Se o site e de um condado especifico, informe qual',    '{"county": "broward"}'],
    ]
    t = Table(data, colWidths=[3.2*cm, 7.5*cm, 6.8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), GRAY_900),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8),
        ('FONTNAME',    (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (1,1), (1,-1), 'Helvetica'),
        ('FONTNAME',    (2,1), (2,-1), 'Courier'),
        ('FONTSIZE',    (2,1), (2,-1), 7.2),
        ('TEXTCOLOR',   (0,1), (0,-1), GRAY_900),
        ('TEXTCOLOR',   (1,1), (1,-1), GRAY_700),
        ('TEXTCOLOR',   (2,1), (2,-1), INDIGO),
        # linha Is active em amarelo
        ('BACKGROUND',  (0,4), (-1,4), YELLOW_LIGHT),
        ('TEXTCOLOR',   (2,4), (2,4), YELLOW),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('BACKGROUND',  (0,4), (-1,4), YELLOW_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING',  (0,0), (-1,-1), 7),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    e += [t, sp(8)]
    e += warn(
        '<b>Deixe "Is active" DESMARCADO</b> ate o desenvolvedor configurar o scraper. '
        'Se marcar ativo antes, o sistema vai tentar rodar e vai dar erro.'
    )
    return e


def passo3():
    e = []
    e += step_badge(3, 'Enviar os links para o desenvolvedor', colors.HexColor('#0891B2'))
    e += [Paragraph(
        'Apos cadastrar o site no Admin, envie as informacoes para o desenvolvedor '
        'configurar o scraper. Quanto mais detalhes voce passar, mais rapido fica pronto.', ST['body'])]
    e.append(sp(8))

    e += [Paragraph('O que enviar para o desenvolvedor:', ST['sub'])]
    data = [
        ['Informacao',           'Por que e importante'],
        ['Link do site',         'Endereco completo que o sistema vai acessar'],
        ['Pagina da lista',      'Onde ficam os imoveis listados (ex: aba "Auctions")'],
        ['O que extrair',        'Preco, divida, data do leilao, link do PDF etc.'],
        ['Login necessario?',    'Se o site exige conta para ver os dados'],
        ['Captcha ou bloqueio?', 'Se o site tem alguma protecao contra robos'],
        ['Exemplo de imovel',    'Um link de um imovel especifico para testar'],
    ]
    t = Table(data, colWidths=[5*cm, 12.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), colors.HexColor('#0891B2')),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8.5),
        ('FONTNAME',    (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (1,1), (1,-1), 'Helvetica'),
        ('TEXTCOLOR',   (0,1), (0,-1), GRAY_900),
        ('TEXTCOLOR',   (1,1), (1,-1), GRAY_700),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
    ]))
    e += [t, sp(8)]
    e += ok(
        '<b>Modelo de mensagem para o desenvolvedor:</b><br/>'
        '"Oi! Cadastrei o site [NOME] no sistema. '
        'O link e [URL]. Os imoveis ficam em [DESCRICAO DA PAGINA]. '
        'Precisa extrair: lance minimo, valor avaliado, divida e PDF do edital. '
        'Segue um exemplo de imovel: [LINK DO IMOVEL]."'
    )
    return e


def passo4():
    e = []
    e += step_badge(4, 'Desenvolvedor configura o scraper', colors.HexColor('#7C3AED'))
    e += [Paragraph(
        'Com as informacoes recebidas, o desenvolvedor vai:', ST['body'])]
    e.append(sp(6))

    itens = [
        ('Inspecionar o site', 'Entrar no site e mapear onde ficam cada informacao (preco, divida, PDF...)'),
        ('Programar o scraper', 'Escrever o codigo que vai entrar no site e extrair os dados automaticamente'),
        ('Testar', 'Rodar o scraper e conferir se os dados chegam corretos no dashboard'),
        ('Ativar a fonte', 'Marcar o site como "Is active" no Admin para comecar a rodar todo dia'),
    ]
    for titulo, desc in itens:
        bloco = Table([[
            Paragraph('✓', ParagraphStyle('chk', fontName='Helvetica-Bold', fontSize=12,
                                           textColor=GREEN, leading=16)),
            Paragraph(f'<b>{titulo}</b><br/>{desc}', ST['body']),
        ]], colWidths=[0.8*cm, FRAME_W - 0.8*cm])
        bloco.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING',  (0,0), (-1,-1), 4),
            ('BOTTOMPADDING',(0,0),(-1,-1), 4),
        ]))
        e += [bloco]

    e.append(sp(8))
    e += info(
        '<b>Tempo estimado por site:</b> Entre 1 e 4 horas dependendo da complexidade do site. '
        'Sites simples com dados visiveis ficam prontos rapidamente. '
        'Sites com protecao anti-robos ou login podem demorar mais.'
    )
    return e


def passo5():
    e = []
    e += step_badge(5, 'Sistema roda automaticamente e imoveis aparecem', GREEN)
    e += [Paragraph(
        'Apos o desenvolvedor ativar o site, o sistema passa a coletar imoveis '
        'automaticamente. Veja o que acontece nos bastidores:', ST['body'])]
    e.append(sp(8))

    data = [
        ['Horario',  'O que o sistema faz'],
        ['06:00',    'Sistema acessa todos os sites cadastrados e ativos'],
        ['06:00-07:00', 'Baixa a lista de imoveis de cada site'],
        ['Em paralelo', 'Faz download dos PDFs dos editais'],
        ['Em paralelo', 'Extrai informacoes dos PDFs (preco, divida, data do leilao)'],
        ['Ao final',    'Imoveis aparecem no dashboard com status "Novo"'],
        ['Dia seguinte','Repete o processo — so adiciona imoveis novos, nao duplica'],
    ]
    t = Table(data, colWidths=[4*cm, 13.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), GREEN),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8.5),
        ('FONTNAME',    (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (1,1), (1,-1), 'Helvetica'),
        ('TEXTCOLOR',   (0,1), (0,-1), GRAY_900),
        ('TEXTCOLOR',   (1,1), (1,-1), GRAY_700),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
    ]))
    e += [t, sp(8)]
    e += ok(
        'A partir deste ponto o sistema trabalha sozinho. '
        'Voce e o VA so precisam entrar no dashboard, revisar os imoveis novos e classificar as oportunidades.'
    )
    return e


def workflow_va():
    e = []
    e.append(Paragraph('Como trabalhar no dashboard apos ter imoveis', ST['title']))
    e.append(hr(INDIGO, 1.2))
    e += [Paragraph(
        'Quando os imoveis comecar a aparecer, siga este fluxo de trabalho:', ST['body'])]
    e.append(sp(8))

    passos_va = [
        ('1', INDIGO,   'Filtrar por Status: Novo',
         'Todo dia, acesse o dashboard e filtre por "Novo" no painel de filtros. '
         'Esses sao os imoveis que o sistema encontrou e ainda nao foram analisados.'),
        ('2', colors.HexColor('#0891B2'), 'Abrir o painel de detalhe',
         'Clique em qualquer card de imovel para abrir o painel lateral. '
         'Ali voce ve todos os dados, o PDF do edital e as informacoes extraidas automaticamente.'),
        ('3', YELLOW,   'Preencher o Valor de Mercado',
         'No painel de detalhe, insira o valor de mercado estimado para o imovel. '
         'O sistema calcula o ROI automaticamente: '
         'ROI = ((Valor de Mercado - Total Dividas) / Total Dividas) x 100'),
        ('4', GREEN,    'Classificar o imovel',
         'Use os botoes para classificar: '
         '[Estrela] Oportunidade = ROI bom, vale investigar. '
         '[Lupa] Em Analise = precisa pesquisar mais. '
         '[X] Descartar = nao vale a pena.'),
        ('5', GRAY_700, 'Adicionar notas',
         'No campo "Notas do VA", registre observacoes importantes: '
         'pontos de atencao, checklist, informacoes adicionais que pesquisou. '
         'Clique em Salvar alteracoes.'),
    ]

    for num, cor, titulo, desc in passos_va:
        badge = Table([[
            Paragraph(num, ParagraphStyle('nb', fontName='Helvetica-Bold', fontSize=14,
                                           textColor=WHITE, leading=18, alignment=TA_CENTER)),
            Paragraph(f'<b>{titulo}</b><br/><br/>{desc}', ST['body']),
        ]], colWidths=[1*cm, FRAME_W - 1*cm])
        badge.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), cor),
            ('BACKGROUND', (1,0), (1,-1), GRAY_50),
            ('LEFTPADDING', (0,0), (0,-1), 4),
            ('LEFTPADDING', (1,0), (1,-1), 10),
            ('RIGHTPADDING',(0,0), (-1,-1), 8),
            ('TOPPADDING',  (0,0), (-1,-1), 8),
            ('BOTTOMPADDING',(0,0),(-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.5, GRAY_200),
        ]))
        e += [badge, sp(6)]

    return e


def dicas():
    e = []
    e.append(Paragraph('Dicas importantes', ST['title']))
    e.append(hr(INDIGO, 1.2))

    dicas_list = [
        (YELLOW, '!', 'Um scraper por site',
         'Cada site de leilao precisa de um scraper proprio porque cada um organiza '
         'os dados de forma diferente. Nao existe um scraper generico que funciona em todos.'),
        (colors.HexColor('#0891B2'), 'i', 'Sites com login',
         'Alguns sites exigem que voce tenha uma conta para ver os imoveis. '
         'Nestes casos, informe o login e senha para o desenvolvedor configurar o acesso.'),
        (GREEN, 'v', 'Adicionando varios sites de uma vez',
         'Voce pode cadastrar quantos sites quiser no Admin. '
         'O sistema vai acessar todos eles todo dia as 06:00. '
         'Cada site novo = mais imoveis no dashboard.'),
        (RED, '!', 'Sites que mudam com frequencia',
         'Alguns sites de condado atualizam o layout periodicamente. '
         'Se o scraper parar de funcionar do nada, provavelmente o site mudou. '
         'Avise o desenvolvedor para ele ajustar o codigo.'),
        (ORANGE, 'i', 'Escalar para outros clientes do curso',
         'Quando o sistema estiver funcionando, voce pode oferecer o servico de VA '
         'para outras pessoas do curso do seu irmao. Cada cliente pode ter seus proprios '
         'sites cadastrados e ver apenas os seus imoveis.'),
    ]

    for cor, icon, titulo, desc in dicas_list:
        t = Table([[
            Paragraph(f'<b>[{icon}]</b>', ST['bold']),
            Paragraph(f'<b>{titulo}</b><br/>{desc}', ST['body']),
        ]], colWidths=[0.8*cm, FRAME_W - 0.8*cm])
        t.setStyle(TableStyle([
            ('LEFTPADDING',  (0,0), (0,-1), 10),
            ('LEFTPADDING',  (1,0), (1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING',   (0,0), (-1,-1), 8),
            ('BOTTOMPADDING',(0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TEXTCOLOR', (0,0), (0,-1), cor),
            ('BOX', (0,0), (-1,-1), 1.5, cor),
            ('BACKGROUND', (0,0), (-1,-1), GRAY_50),
        ]))
        e += [t, sp(6)]

    return e


def resumo_rapido():
    e = []
    e.append(Paragraph('Resumo — o que voce precisa fazer agora', ST['title']))
    e.append(hr(INDIGO, 1.2))

    data = [
        ['#', 'Acao',                                             'Quem faz',    'Status'],
        ['1', 'Pedir os links dos sites para o seu irmao',        'Voce',         'Fazer'],
        ['2', 'Cadastrar os sites em localhost:8000/admin/',       'Voce',         'Fazer'],
        ['3', 'Enviar os links e detalhes para o desenvolvedor',   'Voce',         'Fazer'],
        ['4', 'Configurar o scraper para cada site',               'Desenvolvedor','Aguardar'],
        ['5', 'Testar e ativar o site',                            'Desenvolvedor','Aguardar'],
        ['6', 'Imoveis aparecem no dashboard',                     'Sistema',      'Automatico'],
        ['7', 'Revisar e classificar imoveis diariamente',         'Voce / VA',    'Rotina diaria'],
    ]
    t = Table(data, colWidths=[0.8*cm, 8.5*cm, 4*cm, 4.2*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), GRAY_900),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8.5),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('TEXTCOLOR',   (0,1), (0,-1), GRAY_500),
        ('TEXTCOLOR',   (1,1), (1,-1), GRAY_900),
        ('TEXTCOLOR',   (2,1), (2,-1), GRAY_700),
        # status colors
        ('TEXTCOLOR',   (3,1), (3,3), colors.HexColor('#0369A1')),
        ('FONTNAME',    (3,1), (3,3), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (3,4), (3,5), YELLOW),
        ('FONTNAME',    (3,4), (3,5), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (3,6), (3,6), GREEN),
        ('FONTNAME',    (3,6), (3,6), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (3,7), (3,7), INDIGO),
        ('FONTNAME',    (3,7), (3,7), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING',  (0,0), (-1,-1), 7),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
    ]))
    e += [t, sp(10)]
    e += ok(
        '<b>O proximo passo e seu:</b> Peca os links dos sites para o seu irmao e '
        'cadastre em <font name="Courier">http://localhost:8000/admin/</font>. '
        'Depois e so enviar para o desenvolvedor configurar e o sistema comeca a trabalhar sozinho.'
    )
    return e


# ── Build ────────────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.6*cm, bottomMargin=1.3*cm,
        title='Como Adicionar Sites — Real Estate Mining',
        author='Real Estate Mining',
    )

    story = (
        [PageBreak()]
        + intro()         + [sp(10)]
        + fluxo_completo()+ [PageBreak()]
        + passo1()        + [sp(10)]
        + passo2()        + [PageBreak()]
        + passo3()        + [sp(10)]
        + passo4()        + [PageBreak()]
        + passo5()        + [sp(10)]
        + workflow_va()   + [PageBreak()]
        + dicas()         + [PageBreak()]
        + resumo_rapido()
    )

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f'PDF gerado: {OUTPUT}')


if __name__ == '__main__':
    build()
