from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from datetime import datetime

OUTPUT = "/home/fabianosf/Documents/real-estate-mining/Manual_Operacao_RealEstateMining.pdf"
W_PAGE, H_PAGE = A4
MARGIN = 1.5 * cm
FRAME_W = W_PAGE - 2 * MARGIN   # ~18 cm

# Cores
INDIGO       = colors.HexColor('#4F46E5')
INDIGO_DARK  = colors.HexColor('#3730A3')
INDIGO_LIGHT = colors.HexColor('#EEF2FF')
GRAY_900     = colors.HexColor('#111827')
GRAY_700     = colors.HexColor('#374151')
GRAY_500     = colors.HexColor('#6B7280')
GRAY_200     = colors.HexColor('#E5E7EB')
GRAY_50      = colors.HexColor('#F9FAFB')
GREEN        = colors.HexColor('#059669')
GREEN_LIGHT  = colors.HexColor('#ECFDF5')
RED          = colors.HexColor('#DC2626')
RED_LIGHT    = colors.HexColor('#FEF2F2')
YELLOW       = colors.HexColor('#D97706')
YELLOW_LIGHT = colors.HexColor('#FFFBEB')
CODE_BG      = colors.HexColor('#1E1E2E')
CODE_FG      = colors.HexColor('#CDD6F4')
CODE_ACCENT  = colors.HexColor('#89B4FA')
WHITE        = colors.white

# Estilos
def S(name, **kw):
    return ParagraphStyle(name, **kw)

STYLES = {
    'section': S('sec', fontName='Helvetica-Bold', fontSize=14, textColor=INDIGO,
                 leading=20, spaceBefore=16, spaceAfter=4),
    'subsection': S('sub', fontName='Helvetica-Bold', fontSize=10.5, textColor=GRAY_900,
                    leading=15, spaceBefore=10, spaceAfter=3),
    'body': S('body', fontName='Helvetica', fontSize=9.5, textColor=GRAY_700,
              leading=15, spaceAfter=4),
    'bold': S('bold', fontName='Helvetica-Bold', fontSize=9.5, textColor=GRAY_900,
              leading=15, spaceAfter=4),
    'code': S('code', fontName='Courier', fontSize=8.5, textColor=CODE_FG, leading=13),
    'code_dim': S('code_dim', fontName='Courier-Oblique', fontSize=8,
                  textColor=colors.HexColor('#6C7086'), leading=12),
    'toc_h': S('toch', fontName='Helvetica-Bold', fontSize=10, textColor=INDIGO, leading=20),
    'toc_b': S('tocb', fontName='Helvetica', fontSize=10, textColor=GRAY_700,
               leading=18, leftIndent=8),
    'toc_pg': S('tocpg', fontName='Helvetica', fontSize=10, textColor=GRAY_500,
                leading=18, alignment=TA_RIGHT),
}

def sp(h=6): return Spacer(1, h)
def hr(): return HRFlowable(width='100%', thickness=1.2, color=INDIGO, spaceAfter=6, spaceBefore=2)


# ── Code block ──────────────────────────────────────────────────────────────────
def code_block(lines):
    col = FRAME_W
    rows = []
    for line in lines:
        if line == '':
            rows.append([Paragraph(' ', STYLES['code'])])
        elif line.startswith('#'):
            rows.append([Paragraph(line, STYLES['code_dim'])])
        else:
            rows.append([Paragraph(line, STYLES['code'])])
    t = Table(rows, colWidths=[col])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CODE_BG),
        ('LEFTPADDING',  (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('TOPPADDING',   (0, 0), (0, 0), 10),
        ('BOTTOMPADDING',(0, -1),(0, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#313244')),
    ]))
    return [t, sp(6)]


# ── Info boxes ──────────────────────────────────────────────────────────────────
def box(text, bg, border, icon='i'):
    t = Table(
        [[Paragraph(f'<b>[{icon}]</b>  {text}', STYLES['body'])]],
        colWidths=[FRAME_W]
    )
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), bg),
        ('LEFTPADDING',  (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1.5, border),
    ]))
    return [t, sp(6)]

def info(text):  return box(text, INDIGO_LIGHT, INDIGO, 'i')
def warn(text):  return box(text, YELLOW_LIGHT, YELLOW, '!')
def ok(text):    return box(text, GREEN_LIGHT,  GREEN,  'v')


# ── Tabelas genéricas ───────────────────────────────────────────────────────────
def header_style(t, n_cols):
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), INDIGO),
        ('TEXTCOLOR',  (0, 0), (-1, 0), WHITE),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1,-1), 8.5),
        ('FONTNAME',   (0, 1), (-1,-1), 'Helvetica'),
        ('TEXTCOLOR',  (0, 1), (-1,-1), GRAY_700),
        ('ROWBACKGROUNDS', (0, 1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID',  (0, 0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING',  (0, 0), (-1,-1), 7),
        ('RIGHTPADDING', (0, 0), (-1,-1), 7),
        ('TOPPADDING',   (0, 0), (-1,-1), 6),
        ('BOTTOMPADDING',(0, 0), (-1,-1), 6),
    ]))
    return t


# ── Callbacks de página ─────────────────────────────────────────────────────────
def draw_cover(c):
    c.setFillColor(INDIGO_DARK)
    c.rect(0, 0, W_PAGE, H_PAGE, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#3730A3'))
    c.rect(0, H_PAGE * 0.55, W_PAGE, H_PAGE * 0.45, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#4338CA'))
    c.ellipse(W_PAGE * 0.65, H_PAGE * 0.58, W_PAGE * 1.25, H_PAGE * 1.08, fill=1, stroke=0)

    # Titulo
    c.setFont('Helvetica-Bold', 30)
    c.setFillColor(WHITE)
    c.drawString(MARGIN, H_PAGE - 5.0 * cm, 'Real Estate Mining')
    c.setFont('Helvetica', 16)
    c.setFillColor(colors.HexColor('#C7D2FE'))
    c.drawString(MARGIN, H_PAGE - 6.0 * cm, 'Manual de Operacao do Sistema')
    c.setStrokeColor(colors.HexColor('#6366F1'))
    c.setLineWidth(2)
    c.line(MARGIN, H_PAGE - 6.5 * cm, W_PAGE - MARGIN, H_PAGE - 6.5 * cm)

    c.setFont('Helvetica', 10)
    c.setFillColor(colors.HexColor('#A5B4FC'))
    linhas = [
        'Guia completo para iniciar, parar, monitorar e administrar',
        'a plataforma de mineracao de oportunidades imobiliarias',
        'em leiloes do Brasil e Estados Unidos.',
    ]
    y = H_PAGE - 7.5 * cm
    for l in linhas:
        c.drawString(MARGIN, y, l)
        y -= 0.55 * cm

    # Caixa credenciais
    bx = MARGIN
    by = H_PAGE * 0.36
    bw = W_PAGE - 2 * MARGIN
    bh = 3.4 * cm
    c.setFillColor(colors.HexColor('#312E81'))
    c.rect(bx, by, bw, bh, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor('#6366F1'))
    c.setLineWidth(1)
    c.rect(bx, by, bw, bh, fill=0, stroke=1)
    c.setFont('Helvetica-Bold', 8.5)
    c.setFillColor(colors.HexColor('#A5B4FC'))
    c.drawString(bx + 0.7 * cm, by + 3.0 * cm, 'ACESSO RAPIDO')
    creds = [('URL:', 'http://localhost'), ('Email:', 'fabiano.freitas@gmail.com'), ('Senha:', '260281xx')]
    yc = by + 2.35 * cm
    for label, val in creds:
        c.setFont('Helvetica', 9)
        c.setFillColor(WHITE)
        c.drawString(bx + 0.7 * cm, yc, label)
        c.setFont('Courier-Bold', 9)
        c.setFillColor(colors.HexColor('#89B4FA'))
        c.drawString(bx + 2.2 * cm, yc, val)
        yc -= 0.62 * cm
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#818CF8'))
    c.drawString(bx + 0.7 * cm, by + 0.18 * cm, 'Altere a senha apos o primeiro acesso')

    # Rodape
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#6366F1'))
    c.drawString(MARGIN, 1.4 * cm, f'Versao 1.0  |  {datetime.now().strftime("%d/%m/%Y")}')
    c.drawRightString(W_PAGE - MARGIN, 1.4 * cm, 'Confidencial  |  Uso interno')


def on_first_page(canvas, doc):
    draw_cover(canvas)


def on_later_pages(canvas, doc):
    # Cabecalho
    canvas.saveState()
    canvas.setFillColor(INDIGO)
    canvas.rect(0, H_PAGE - 1.1 * cm, W_PAGE, 1.1 * cm, fill=1, stroke=0)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(WHITE)
    canvas.drawString(MARGIN, H_PAGE - 0.73 * cm, 'Real Estate Mining')
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#A5B4FC'))
    canvas.drawRightString(W_PAGE - MARGIN, H_PAGE - 0.73 * cm, 'Manual de Operacao')
    # Rodape
    canvas.setFillColor(GRAY_200)
    canvas.rect(0, 0, W_PAGE, 0.9 * cm, fill=1, stroke=0)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawString(MARGIN, 0.33 * cm, f'Gerado em {datetime.now().strftime("%d/%m/%Y")}')
    canvas.drawCentredString(W_PAGE / 2, 0.33 * cm, 'Confidencial  |  Uso interno')
    canvas.drawRightString(W_PAGE - MARGIN, 0.33 * cm, f'Pagina {doc.page - 1}')
    canvas.restoreState()


# ── Sumário ─────────────────────────────────────────────────────────────────────
def toc():
    items = [
        ('1.', 'Visao Geral da Arquitetura'),
        ('2.', 'Pre-requisitos e Diretorio de Trabalho'),
        ('3.', 'Iniciar o Sistema'),
        ('4.', 'Parar o Sistema'),
        ('5.', 'Reiniciar Servicos'),
        ('6.', 'Verificar Status'),
        ('7.', 'Acessar o Sistema (URLs e Credenciais)'),
        ('8.', 'Ver Logs e Monitoramento'),
        ('9.', 'Apos Mudancas no Codigo'),
        ('10.', 'Banco de Dados (backup e acesso)'),
        ('11.', 'Scraping Manual'),
        ('12.', 'Gerenciar Usuarios'),
        ('13.', 'Solucao de Problemas'),
        ('14.', 'Referencia Rapida (cheat sheet)'),
    ]
    rows = [[Paragraph(n, STYLES['toc_h']), Paragraph(t, STYLES['toc_b']),
             Paragraph('', STYLES['toc_pg'])] for n, t in items]
    t = Table(rows, colWidths=[1.2 * cm, 13 * cm, 1.3 * cm])
    t.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, GRAY_200),
        ('TOPPADDING',   (0, 0), (-1,-1), 4),
        ('BOTTOMPADDING',(0, 0), (-1,-1), 4),
        ('VALIGN', (0, 0), (-1,-1), 'MIDDLE'),
    ]))
    return [
        Paragraph('Sumario', STYLES['section']),
        hr(), sp(4), t, PageBreak(),
    ]


# ── Seções ──────────────────────────────────────────────────────────────────────
def sec(n, title): return [Paragraph(f'{n}. {title}', STYLES['section']), hr()]
def sub(title):    return [Paragraph(title, STYLES['subsection'])]
def body(text):    return [Paragraph(text, STYLES['body'])]


def s1():
    e = sec(1, 'Visao Geral da Arquitetura')
    e += body('O sistema e composto por <b>8 servicos Docker</b> que trabalham juntos. '
              'Para o uso diario voce so precisa saber iniciar, parar e verificar o status.')
    e.append(sp(8))
    data = [
        ['Servico',       'Funcao',                                                   'Porta'],
        ['nginx',         'Porta de entrada — e o que o navegador acessa',            ':80'],
        ['frontend',      'Interface visual (dashboard React)',                        ':3000'],
        ['api',           'Backend Django — processa dados e responde ao dashboard',  ':8000'],
        ['postgres',      'Banco de dados — armazena todos os imoveis pesquisados',   'interno'],
        ['redis',         'Fila de tarefas — coordena os workers',                    'interno'],
        ['celery_worker', 'Executa scraping e processamento de PDFs em background',   'interno'],
        ['celery_beat',   'Agendador — dispara scraping automatico as 06:00',         'interno'],
        ['wireguard',     'VPN — protege o IP durante scraping nos EUA',              ':51820'],
    ]
    t = Table(data, colWidths=[3.5 * cm, 10.5 * cm, 3.5 * cm])
    header_style(t, 3)
    e += [t, sp(8)]
    e += info('<b>Uso diario:</b> acesse apenas <font name="Courier">http://localhost</font>. '
              'Todos os servicos internos funcionam automaticamente.')
    return e


def s2():
    e = sec(2, 'Pre-requisitos e Diretorio de Trabalho')
    e += body('Confirme que estes programas estao instalados na maquina:')
    e.append(sp(6))
    data = [
        ['Software',       'Versao minima', 'Como verificar'],
        ['Docker',         '24+',           'docker --version'],
        ['Docker Compose', '2.x (plugin)',  'docker compose version'],
    ]
    t = Table(data, colWidths=[4 * cm, 4 * cm, 9.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GRAY_900),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',   (2,1), (2,-1), 'Courier'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('TEXTCOLOR',  (0,1), (1,-1), GRAY_700),
        ('TEXTCOLOR',  (2,1), (2,-1), INDIGO),
        ('FONTNAME',   (0,1), (1,-1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    e += [t, sp(10)]
    e += sub('Diretorio de trabalho')
    e += body('TODOS os comandos devem ser executados dentro do diretorio do projeto:')
    e += code_block(['cd ~/Documents/real-estate-mining'])
    e += warn('<b>Importante:</b> se voce executar os comandos fora desse diretorio, '
              'o Docker Compose nao encontrara os servicos.')
    return e


def s3():
    e = sec(3, 'Iniciar o Sistema')
    e += sub('3.1  Iniciar tudo (uso normal)')
    e += body('Sobe todos os 8 servicos em background. <b>Use este comando na maioria das vezes.</b>')
    e += code_block([
        'cd ~/Documents/real-estate-mining',
        'docker compose up -d',
    ])
    e += ok('Apos alguns segundos acesse <font name="Courier">http://localhost</font> no navegador.')
    e.append(sp(8))

    e += sub('3.2  Iniciar somente o essencial (sem scraping)')
    e += body('Economiza memoria quando nao precisar do scraping automatico:')
    e += code_block(['docker compose up -d postgres redis api frontend nginx'])
    e += info('Neste modo o dashboard funciona normalmente. Scraping e processamento de PDFs ficam pausados.')
    e.append(sp(8))

    e += sub('3.3  Iniciar com logs visiveis (modo debug)')
    e += body('Para ver o que acontece em tempo real. Pressione <b>Ctrl+C</b> para parar:')
    e += code_block(['docker compose up', '# Ctrl+C para parar e voltar ao terminal'])
    return e


def s4():
    e = sec(4, 'Parar o Sistema')
    e += sub('4.1  Parar tudo (dados preservados)')
    e += body('Para os containers mas <b>preserva o banco de dados e todos os arquivos</b>. '
              'Use sempre este comando.')
    e += code_block(['docker compose down'])
    e += ok('Os dados do banco e os PDFs baixados sao preservados. Pode reiniciar quando quiser.')
    e.append(sp(8))

    e += sub('4.2  Parar um servico especifico')
    e += body('Para apenas um servico sem afetar os demais:')
    e += code_block([
        'docker compose stop api',
        'docker compose stop frontend',
        'docker compose stop celery_worker',
    ])
    e.append(sp(6))
    e += warn('<b>NUNCA USE</b> <font name="Courier">docker compose down -v</font> — '
              'esse comando apaga os volumes e voce <b>perdera TODOS os dados</b> do banco e PDFs.')
    return e


def s5():
    e = sec(5, 'Reiniciar Servicos')
    e += sub('5.1  Reiniciar tudo')
    e += code_block(['docker compose restart'])
    e.append(sp(8))

    e += sub('5.2  Reiniciar um servico especifico')
    e += body('Util quando um servico travar ou apos alterar configuracoes:')
    e += code_block([
        'docker compose restart api',
        'docker compose restart frontend',
        'docker compose restart celery_worker',
        'docker compose restart celery_beat',
        'docker compose restart nginx',
    ])
    e.append(sp(8))

    e += sub('5.3  Restart forcado (parar e subir)')
    e += body('Quando o restart simples nao resolve:')
    e += code_block(['docker compose down', 'docker compose up -d'])
    return e


def s6():
    e = sec(6, 'Verificar Status dos Servicos')
    e += sub('6.1  Ver todos os servicos')
    e += code_block(['docker compose ps'])
    e += body('Na coluna <b>STATUS</b>, cada servico deve mostrar <b>Up</b>. '
              'Se aparecer <b>Exit</b> ou <b>Restarting</b>, ha um problema.')
    e.append(sp(8))

    data = [
        ['Status',       'Significado',                   'O que fazer'],
        ['Up',           'Funcionando normalmente',        'Nada'],
        ['Up (healthy)', 'Funcionando e saudavel',         'Nada'],
        ['Exit (0)',     'Parou sem erro',                 'docker compose start <servico>'],
        ['Exit (1)',     'Parou com erro',                 'docker compose logs <servico>'],
        ['Restarting',   'Reiniciando repetidamente',      'Ver logs imediatamente'],
    ]
    t = Table(data, colWidths=[3.2 * cm, 5.8 * cm, 8.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GRAY_900),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',   (1,1), (1,-1), 'Helvetica'),
        ('FONTNAME',   (2,1), (2,-1), 'Courier'),
        ('FONTSIZE',   (2,1), (2,-1), 7.8),
        ('TEXTCOLOR',  (0,1), (0,2), GREEN),
        ('TEXTCOLOR',  (0,3), (0,4), YELLOW),
        ('TEXTCOLOR',  (0,5), (0,5), RED),
        ('TEXTCOLOR',  (1,1), (1,-1), GRAY_700),
        ('TEXTCOLOR',  (2,1), (2,-1), INDIGO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    e += [t]
    return e


def s7():
    e = sec(7, 'Acessar o Sistema')
    data = [
        ['Interface',         'URL',                              'Quando usar'],
        ['Dashboard',         'http://localhost',                 'Uso diario — pesquisa de imoveis'],
        ['Tela de login',     'http://localhost/login',           'Entrar na conta'],
        ['Cadastro',          'http://localhost/register',        'Criar novo usuario'],
        ['API REST',          'http://localhost:8000/api/',       'Desenvolvedores / debug'],
        ['Admin Django',      'http://localhost:8000/admin/',     'Gestao avancada do banco'],
    ]
    t = Table(data, colWidths=[4 * cm, 6 * cm, 7.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), INDIGO),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('FONTNAME',   (1,1), (1,-1), 'Courier'),
        ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',   (2,1), (2,-1), 'Helvetica'),
        ('TEXTCOLOR',  (1,1), (1,-1), INDIGO),
        ('TEXTCOLOR',  (0,1), (0,-1), GRAY_900),
        ('TEXTCOLOR',  (2,1), (2,-1), GRAY_700),
        ('BACKGROUND', (0,1), (-1,1), GREEN_LIGHT),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING',  (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    e += [t, sp(12)]

    e += sub('Credenciais de acesso')
    cdata = [
        ['Campo',       'Valor'],
        ['Email',       'fabiano.freitas@gmail.com'],
        ['Senha',       '260281xx'],
    ]
    ct = Table(cdata, colWidths=[4 * cm, 13.5 * cm])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GRAY_900),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',   (1,1), (1,-1), 'Courier-Bold'),
        ('FONTNAME',   (0,1), (0,-1), 'Helvetica'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('TEXTCOLOR',  (1,1), (1,-1), INDIGO),
        ('TEXTCOLOR',  (0,1), (0,-1), GRAY_700),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING',  (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    e += [ct, sp(8)]
    e += warn('Altere a senha apos o primeiro acesso em '
              '<font name="Courier">http://localhost/register</font> '
              'ou pelo Admin Django.')
    return e


def s8():
    e = sec(8, 'Ver Logs e Monitoramento')
    e += body('Logs sao o principal recurso para entender o que esta acontecendo '
              'e diagnosticar problemas.')
    e.append(sp(6))

    e += sub('8.1  Todos os servicos ao vivo')
    e += code_block(['docker compose logs -f', '# Ctrl+C para sair'])

    e += sub('8.2  Logs de um servico especifico')
    e += code_block([
        'docker compose logs -f api',
        'docker compose logs -f frontend',
        'docker compose logs -f celery_worker',
        'docker compose logs -f celery_beat',
        'docker compose logs -f postgres',
    ])

    e += sub('8.3  Ultimas N linhas (sem seguir ao vivo)')
    e += code_block([
        'docker compose logs --tail=50 api',
        'docker compose logs --tail=100 celery_worker',
    ])
    e.append(sp(8))

    e += sub('O que observar nos logs')
    data = [
        ['Servico',        'Normal',                           'Sinal de problema'],
        ['api',            'Worker booted, GET/POST 200',      'Error, Exception, 500'],
        ['celery_worker',  'Task received, Task succeeded',    'Task failed, Retry in'],
        ['celery_beat',    'Sending due task (06:00)',         'ERROR, sem mensagens'],
        ['postgres',       'Silencioso',                       'FATAL, could not connect'],
        ['nginx',          'GET / 200',                        '502 Bad Gateway'],
    ]
    t = Table(data, colWidths=[3.2 * cm, 7.5 * cm, 6.8 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GRAY_900),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',   (1,1), (1,-1), 'Helvetica'),
        ('FONTNAME',   (2,1), (2,-1), 'Helvetica'),
        ('TEXTCOLOR',  (0,1), (0,-1), GRAY_900),
        ('TEXTCOLOR',  (1,1), (1,-1), GREEN),
        ('TEXTCOLOR',  (2,1), (2,-1), RED),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    e += [t]
    return e


def s9():
    e = sec(9, 'Apos Mudancas no Codigo')
    e += body('Sempre que o desenvolvedor alterar arquivos do projeto, '
              'atualize os containers para as mudancas entrarem em vigor.')
    e.append(sp(6))

    e += sub('9.1  Mudanca em arquivos Python (backend)')
    e += code_block(['docker compose restart api celery_worker celery_beat'])

    e += sub('9.2  Mudanca em arquivos React (frontend)')
    e += body('Em modo desenvolvimento o frontend atualiza automaticamente no navegador. '
              'Se nao atualizar:')
    e += code_block(['docker compose restart frontend'])

    e += sub('9.3  Novas bibliotecas (requirements.txt ou package.json)')
    e += body('Quando novas bibliotecas sao adicionadas, e necessario rebuildar a imagem:')
    e += code_block([
        '# Backend',
        'docker compose build api',
        'docker compose up -d',
        '',
        '# Frontend',
        'docker compose build frontend',
        'docker compose up -d',
    ])

    e += sub('9.4  Novas migrations do banco de dados')
    e += body('Quando o desenvolvedor alterar o modelo de dados, aplique as migrations:')
    e += code_block(['docker compose run --rm api python manage.py migrate'])
    return e


def s10():
    e = sec(10, 'Banco de Dados')
    e += sub('10.1  Acessar o banco (modo interativo)')
    e += code_block([
        'docker compose exec postgres psql -U postgres -d realestate_mining',
        '# Para sair:  \\q  + Enter',
    ])

    e += sub('10.2  Fazer backup manual')
    e += code_block([
        'docker compose exec postgres pg_dump -U postgres realestate_mining > backup_$(date +%Y%m%d).sql',
    ])
    e += info('Salve o arquivo <font name="Courier">.sql</font> em local seguro '
              '(Google Drive, HD externo). Faca isso regularmente.')
    e.append(sp(6))

    e += sub('10.3  Restaurar backup')
    e += code_block([
        'docker compose exec -T postgres psql -U postgres realestate_mining < backup_20240101.sql',
    ])
    e += warn('Os dados ficam no volume Docker <font name="Courier">postgres_data</font>. '
              'NUNCA use <font name="Courier">docker compose down -v</font> — '
              'apaga o volume e todos os dados.')
    return e


def s11():
    e = sec(11, 'Scraping Manual')
    e += body('O scraping automatico roda todos os dias as <b>06:00</b>. '
              'Mas voce pode disparar manualmente quando precisar:')
    e.append(sp(6))

    e += sub('11.1  Rodar todos os scrapers agora')
    e += code_block([
        'docker compose run --rm api python manage.py shell -c "',
        'from apps.scrapers.tasks import schedule_active_scrapers',
        'schedule_active_scrapers.delay()',
        '"',
    ])

    e += sub('11.2  Processar PDF de um imovel manualmente')
    e += body('No dashboard, clique no card do imovel para abrir o painel de detalhe. '
              'O PDF sera exibido diretamente se ja foi processado. '
              'Caso contrario, o botao de processamento estara disponivel.')
    e.append(sp(6))
    e += info('<b>Atencao:</b> Para o scraping funcionar de verdade, os scrapers precisam ser '
              'configurados com as URLs reais dos condados. Esta e a proxima etapa do desenvolvimento.')
    return e


def s12():
    e = sec(12, 'Gerenciar Usuarios')
    e += sub('12.1  Criar novo usuario (via dashboard)')
    e += body('Acesse <font name="Courier">http://localhost/register</font> '
              'e preencha: nome, email e senha.')
    e.append(sp(6))

    e += sub('12.2  Resetar senha do admin padrao')
    e += code_block([
        'docker compose run --rm api python manage.py seed_admin',
        '# Redefine: fabiano.freitas@gmail.com / 260281xx',
    ])

    e += sub('12.3  Criar usuario via terminal')
    e += code_block([
        'docker compose run --rm api python manage.py shell -c "',
        'from django.contrib.auth import get_user_model',
        'User = get_user_model()',
        "User.objects.create_user(username='email@ex.com', email='email@ex.com',",
        "    password='senhaSegura123', first_name='Nome')",
        '"',
    ])

    e += sub('12.4  Admin Django (gestao visual completa)')
    e += body('Em <font name="Courier">http://localhost:8000/admin/</font> voce gerencia '
              'usuarios, imoveis e fontes de scraping visualmente com login de superusuario.')
    return e


def s13():
    e = sec(13, 'Solucao de Problemas')
    problemas = [
        (
            'Dashboard nao abre (http://localhost sem resposta)',
            'Servicos parados. Verifique e suba novamente.',
            ['docker compose ps', 'docker compose up -d'],
        ),
        (
            'Login retorna "Credenciais invalidas"',
            'Admin com senha incorreta ou username errado. Execute o seed_admin.',
            ['docker compose run --rm api python manage.py seed_admin'],
        ),
        (
            'API retorna erro 500',
            'Erro interno. Veja os logs para detalhes.',
            ['docker compose logs --tail=50 api'],
        ),
        (
            'Banco de dados nao conecta',
            'Postgres parado. Inicie-o e reinicie a API.',
            ['docker compose up -d postgres', 'docker compose restart api'],
        ),
        (
            'Frontend mostra tela em branco',
            'Frontend ainda compilando. Aguarde 1-2 minutos e veja o log.',
            ['docker compose logs -f frontend', '# Aguarde: "Compiled successfully"'],
        ),
        (
            'Scraping nao roda automaticamente',
            'Workers nao estao ativos. Suba-os.',
            ['docker compose up -d celery_worker celery_beat',
             'docker compose logs -f celery_beat'],
        ),
        (
            'Mudanca no codigo nao apareceu',
            'Container ainda usa versao antiga. Rebuild ou restart.',
            ['docker compose build api', 'docker compose up -d'],
        ),
    ]
    for titulo, solucao, cmds in problemas:
        bloco = (sub(f'Problema: {titulo}') +
                 body(f'<b>Solucao:</b> {solucao}') +
                 code_block(cmds) +
                 [sp(4)])
        e += [KeepTogether(bloco)]
    return e


def s14():
    e = sec(14, 'Referencia Rapida — Cheat Sheet')
    e += body('Comandos mais usados no dia a dia:')
    e.append(sp(6))

    data = [
        ['Comando',                                          'O que faz'],
        ['docker compose up -d',                             'Iniciar tudo'],
        ['docker compose down',                              'Parar tudo (dados preservados)'],
        ['docker compose ps',                                'Ver status de todos os servicos'],
        ['docker compose restart api',                       'Reiniciar o backend'],
        ['docker compose restart frontend',                  'Reiniciar o frontend'],
        ['docker compose logs -f api',                       'Ver logs do backend ao vivo'],
        ['docker compose logs -f celery_worker',             'Ver logs do scraping ao vivo'],
        ['docker compose build api',                         'Rebuildar imagem do backend'],
        ['docker compose build frontend',                    'Rebuildar imagem do frontend'],
        ['docker compose run --rm api python manage.py migrate',   'Aplicar migrations'],
        ['docker compose run --rm api python manage.py seed_admin','Resetar usuario admin'],
    ]
    t = Table(data, colWidths=[9.5 * cm, 8 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GRAY_900),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('FONTNAME',   (0,1), (0,-1), 'Courier'),
        ('FONTNAME',   (1,1), (1,-1), 'Helvetica'),
        ('TEXTCOLOR',  (0,1), (0,-1), CODE_ACCENT),
        ('TEXTCOLOR',  (1,1), (1,-1), GRAY_700),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GRAY_50]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    e += [t, sp(14)]

    e += sub('URLs de acesso rapido')
    udata = [
        ['http://localhost',               'Dashboard principal (uso diario)'],
        ['http://localhost/login',         'Tela de login'],
        ['http://localhost/register',      'Cadastro de novo usuario'],
        ['http://localhost:8000/api/',     'API REST (desenvolvedores)'],
        ['http://localhost:8000/admin/',   'Admin Django (gestao avancada)'],
    ]
    ut = Table(udata, colWidths=[9 * cm, 8.5 * cm])
    ut.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (0,-1), 'Courier'),
        ('FONTNAME',   (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('TEXTCOLOR',  (0,0), (0,-1), INDIGO),
        ('TEXTCOLOR',  (1,0), (1,-1), GRAY_700),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [INDIGO_LIGHT, WHITE]),
        ('GRID', (0,0), (-1,-1), 0.3, GRAY_200),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING',  (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    e += [ut]
    return e


# ── Build ───────────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.6 * cm, bottomMargin=1.3 * cm,
        title='Manual de Operacao — Real Estate Mining',
        author='Real Estate Mining',
    )

    def pb(): return [PageBreak()]

    story = (
        [PageBreak()]           # pag 1 = capa (desenhada no on_first_page)
        + toc()                 # pag 2 = sumario
        + s1() + [sp(10)]
        + s2() + pb()
        + s3() + [sp(10)]
        + s4() + pb()
        + s5() + [sp(10)]
        + s6() + pb()
        + s7() + [sp(10)]
        + s8() + pb()
        + s9() + [sp(10)]
        + s10() + pb()
        + s11() + [sp(10)]
        + s12() + pb()
        + s13() + pb()
        + s14()
    )

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f'PDF gerado com sucesso: {OUTPUT}')


if __name__ == '__main__':
    build()
