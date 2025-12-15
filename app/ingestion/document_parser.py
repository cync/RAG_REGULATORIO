import re
from pathlib import Path
from typing import List, Dict, Optional
import pypdf
from bs4 import BeautifulSoup
import html2text
from app.models.schemas import Metadata, DocumentChunk
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentParser:
    """Parser para documentos PDF e HTML do Bacen"""
    
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
    
    def parse_pdf(self, file_path: Path) -> str:
        """Extrai texto de PDF preservando estrutura"""
        try:
            text = ""
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                total_pages = len(pdf_reader.pages)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    
                    # Log da primeira página para debug
                    if page_num == 1:
                        logger.debug(
                            "Primeira página extraída",
                            file=str(file_path),
                            page_text_length=len(page_text),
                            page_text_preview=page_text[:200] if page_text else ""
                        )
            
            text = text.strip()
            
            # Validar que o texto não está vazio
            if not text or len(text) < 50:
                logger.warning(
                    "PDF extraído com texto vazio ou muito curto",
                    file=str(file_path),
                    text_length=len(text),
                    total_pages=total_pages,
                    preview=text[:200] if text else ""
                )
            
            logger.info(
                "PDF parseado",
                file=str(file_path),
                text_length=len(text),
                total_pages=total_pages
            )
            
            return text
        except Exception as e:
            logger.error("Erro ao parsear PDF", file=str(file_path), error=str(e))
            raise
    
    def parse_html(self, file_path: Path) -> str:
        """Extrai texto de HTML preservando estrutura"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, "lxml")
            # Remove scripts e styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = self.html_converter.handle(str(soup))
            return text
        except Exception as e:
            logger.error("Erro ao parsear HTML", file=str(file_path), error=str(e))
            raise
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, Optional[str]]:
        """
        Extrai metadados básicos do nome do arquivo.
        Formato esperado: tema_norma_numero_ano.pdf
        Ex: pix_circular_123_2023.pdf
        """
        parts = Path(filename).stem.lower().split("_")
        
        metadata = {
            "tema": None,
            "norma": None,
            "numero_norma": None,
            "ano": None,
        }
        
        if len(parts) >= 4:
            metadata["tema"] = parts[0] if parts[0] in ["pix", "open_finance"] else None
            metadata["norma"] = parts[1].capitalize()
            metadata["numero_norma"] = parts[2]
            try:
                metadata["ano"] = int(parts[3])
            except ValueError:
                pass
        
        return metadata
    
    def extract_metadata_from_text(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrai metadados do conteúdo do texto.
        Procura por padrões normativos.
        """
        metadata = {
            "norma": None,
            "numero_norma": None,
            "ano": None,
        }
        
        # Padrão: Resolução/Circular Nº X de YYYY
        pattern = r'(Resolução|Circular|Comunicado)\s+(?:Nº|nº|n\.?\s*)?(\d+)\s+(?:de\s+)?(\d{4})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["norma"] = match.group(1)
            metadata["numero_norma"] = match.group(2)
            try:
                metadata["ano"] = int(match.group(3))
            except ValueError:
                pass
        
        return metadata
    
    def parse(self, file_path: Path, tema: str, url: Optional[str] = None):
        """
        Parse documento e retorna texto + metadados base.
        """
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            text = self.parse_pdf(file_path)
        elif suffix in [".html", ".htm"]:
            text = self.parse_html(file_path)
        else:
            raise ValueError(f"Formato não suportado: {suffix}")
        
        # Extrair metadados
        filename_meta = self.extract_metadata_from_filename(file_path.name)
        text_meta = self.extract_metadata_from_text(text)
        
        # Combinar metadados (priorizar texto)
        base_metadata = {
            "fonte": file_path.name,
            "tema": tema or filename_meta.get("tema") or "pix",
            "norma": text_meta.get("norma") or filename_meta.get("norma") or "Norma",
            "numero_norma": text_meta.get("numero_norma") or filename_meta.get("numero_norma") or "N/A",
            "ano": text_meta.get("ano") or filename_meta.get("ano") or 2023,
            "url": url,
        }
        
        return text, base_metadata

