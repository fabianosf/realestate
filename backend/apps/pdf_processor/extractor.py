import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx
import pdfplumber

logger = logging.getLogger(__name__)

DEBT_KEYWORDS_EN = [
    r'property\s+tax(?:es)?',
    r'tax\s+lien',
    r'delinquent\s+tax',
    r'amount\s+(?:due|owed)',
    r'outstanding\s+balance',
    r'foreclosure\s+amount',
    r'hoa\s+(?:dues?|fees?)',
    r'special\s+assessment',
    r'penalties?\s+(?:and|&)\s+interest',
    r'tax\s+certificate',
    r'redemption\s+amount',
    r'bid\s+(?:opening|minimum|starting)',
    r'appraised\s+value',
    r'assessed\s+value',
    r'certificate\s+of\s+title',
    r'judgment\s+lien',
]

DEBT_KEYWORDS_PT = [
    r'iptu',
    r'd[ée]vida\s+(?:total|fiscal|tribut[áa]ria)',
    r'valor\s+(?:total\s+)?d(?:a|o)\s+d[ée]vida',
    r'valor\s+de\s+avalia[çc][ãa]o',
    r'lance\s+m[íi]nimo',
    r'valor\s+m[íi]nimo',
    r'condom[íi]nio',
    r'taxa(?:s)?\s+condominiais',
    r'execu[çc][ãa]o\s+fiscal',
    r'cr[ée]dito\s+tribut[áa]rio',
    r'multa\s+(?:e\s+)?juros',
    r'hasta\s+p[úu]blica',
    r'sinal\s+de\s+arremata[çc][ãa]o',
    r'auto\s+de\s+infra[çc][ãa]o',
]

CURRENCY_BRL = re.compile(r'R\$\s*([\d.]+(?:,\d{2})?)')
CURRENCY_USD = re.compile(r'\$\s*([\d,]+(?:\.\d{2})?)')


class PDFExtractor:

    def download_pdf(self, url: str, dest: Path) -> bool:
        try:
            with httpx.Client(timeout=60, follow_redirects=True) as client:
                r = client.get(url)
                r.raise_for_status()
                dest.write_bytes(r.content)
            return True
        except Exception as e:
            logger.error(f"PDF download failed {url}: {e}")
            return False

    def _extract_pdfplumber(self, pdf_path: Path) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return "\n".join(p.extract_text() or '' for p in pdf.pages)
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
            return ""

    def _extract_ocr(self, pdf_path: Path) -> str:
        try:
            import pytesseract
            import pdf2image
            images = pdf2image.convert_from_path(pdf_path, dpi=300)
            return "\n".join(
                pytesseract.image_to_string(img, lang='por+eng') for img in images
            )
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""

    def extract_text(self, pdf_path: Path) -> str:
        text = self._extract_pdfplumber(pdf_path)
        if len(text.strip()) < 100:
            text = self._extract_ocr(pdf_path)
        return text

    def detect_language(self, text: str) -> str:
        pt = sum(1 for p in DEBT_KEYWORDS_PT if re.search(p, text, re.IGNORECASE))
        en = sum(1 for p in DEBT_KEYWORDS_EN if re.search(p, text, re.IGNORECASE))
        return 'pt' if pt >= en else 'en'

    def find_debt_mentions(self, text: str, language: str) -> List[Dict]:
        keywords = DEBT_KEYWORDS_PT if language == 'pt' else DEBT_KEYWORDS_EN
        mentions = []
        for pattern in keywords:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                mentions.append({
                    'keyword': m.group(0),
                    'context': text[max(0, m.start() - 60):m.end() + 200].strip(),
                })
        return mentions

    def extract_key_values(self, text: str, language: str) -> Dict:
        patterns = {
            'pt': {
                'lance_minimo': r'lance\s+m[íi]nimo[:\s]+R?\$?\s*([\d.,]+)',
                'valor_avaliacao': r'valor\s+de\s+avalia[çc][ãa]o[:\s]+R?\$?\s*([\d.,]+)',
                'iptu': r'iptu[:\s]+R?\$?\s*([\d.,]+)',
                'divida_total': r'(?:d[ée]vida|valor)\s+total[:\s]+R?\$?\s*([\d.,]+)',
                'data_leilao': r'data[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                'numero_processo': r'processo\s+n[º°\.]?\s*([\d\.\-\/]+)',
            },
            'en': {
                'minimum_bid': r'(?:minimum|starting|opening)\s+bid[:\s]+\$?\s*([\d,]+(?:\.\d{2})?)',
                'assessed_value': r'assessed\s+value[:\s]+\$?\s*([\d,]+(?:\.\d{2})?)',
                'tax_due': r'(?:total\s+)?tax(?:es)?\s+due[:\s]+\$?\s*([\d,]+(?:\.\d{2})?)',
                'total_owed': r'total\s+(?:amount\s+)?owed[:\s]+\$?\s*([\d,]+(?:\.\d{2})?)',
                'penalties_interest': r'penalties\s+(?:and|&)\s+interest[:\s]+\$?\s*([\d,]+(?:\.\d{2})?)',
                'auction_date': r'auction\s+date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                'parcel_id': r'parcel\s+(?:id|number|#)[:\s]+([A-Z0-9\-]+)',
                'certificate_number': r'certificate\s+(?:no|number|#)[:\s]+([A-Z0-9\-]+)',
            },
        }
        result = {}
        for key, pattern in patterns.get(language, {}).items():
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                result[key] = m.group(1).strip()
        return result

    def parse_to_cents(self, value_str: str, currency: str) -> Optional[int]:
        if not value_str:
            return None
        cleaned = re.sub(r'[^\d,.]', '', value_str)
        if currency == 'BRL':
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
        try:
            return int(float(cleaned) * 100)
        except (ValueError, TypeError):
            return None

    def process(self, pdf_path: Path, currency: str = 'auto') -> Dict:
        text = self.extract_text(pdf_path)
        language = self.detect_language(text)
        return {
            'raw_text': text,
            'language': language,
            'key_values': self.extract_key_values(text, language),
            'debt_mentions': self.find_debt_mentions(text, language),
            'char_count': len(text),
        }
