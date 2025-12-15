import re
from pathlib import Path
from typing import List, Dict, Optional
import pypdf
from bs4 import BeautifulSoup
import html2text
from app.models.schemas import Metadata, DocumentChunk
from app.utils.logger import get_logger

logger = get_logger(__name__)

# OCR imports (opcional)
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR não disponível - instale pytesseract e pdf2image para suporte a PDFs escaneados")


class DocumentParser:
    """Parser para documentos PDF e HTML do Bacen"""
    
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
    
    def parse_pdf_with_ocr(self, file_path: Path) -> str:
        """Extrai texto de PDF usando OCR (para PDFs escaneados)"""
        if not OCR_AVAILABLE:
            logger.error("OCR não disponível - instale pytesseract e pdf2image")
            return ""
        
        try:
            logger.info("Tentando extrair texto com OCR", file=str(file_path))
            
            # Converter PDF para imagens
            images = convert_from_path(str(file_path), dpi=300)
            
            text = ""
            total_pages = len(images)
            
            for page_num, image in enumerate(images, 1):
                try:
                    # Extrair texto da imagem usando Tesseract
                    page_text = pytesseract.image_to_string(image, lang='por')
                    
                    if page_text and len(page_text.strip().replace('\n', '').replace(' ', '')) > 10:
                        text += page_text + "\n"
                        
                        if page_num == 1:
                            logger.debug(
                                "Primeira página extraída com OCR",
                                file=str(file_path),
                                page_text_length=len(page_text),
                                page_text_preview=page_text[:300] if page_text else ""
                            )
                except Exception as e:
                    logger.warning(
                        "Erro ao processar página com OCR",
                        file=str(file_path),
                        page_num=page_num,
                        error=str(e)
                    )
                    continue
            
            text = text.strip()
            text_non_whitespace = text.replace('\n', '').replace(' ', '').replace('\t', '').strip()
            
            if not text or len(text_non_whitespace) < 50:
                logger.warning(
                    "OCR extraiu texto vazio ou muito curto",
                    file=str(file_path),
                    text_length=len(text),
                    text_non_whitespace_length=len(text_non_whitespace),
                    total_pages=total_pages
                )
                return ""
            
            logger.info(
                "PDF extraído com OCR com sucesso",
                file=str(file_path),
                text_length=len(text),
                text_non_whitespace_length=len(text_non_whitespace),
                total_pages=total_pages
            )
            
            return text
            
        except Exception as e:
            logger.error("Erro ao extrair texto com OCR", file=str(file_path), error=str(e))
            return ""
    
    def parse_pdf(self, file_path: Path) -> str:
        """Extrai texto de PDF preservando estrutura. Tenta pypdf primeiro, depois OCR se necessário."""
        try:
            text = ""
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                total_pages = len(pdf_reader.pages)
                
                pages_with_text = 0
                pages_without_text = 0
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    
                    # Remover apenas quebras de linha excessivas, mas manter conteúdo
                    # Se a página só tem quebras de linha, considerar vazia
                    page_text_clean = page_text.strip() if page_text else ""
                    
                    if page_text_clean and len(page_text_clean.replace('\n', '').replace(' ', '')) > 10:
                        # Página tem conteúdo real (mais de 10 caracteres não-whitespace)
                        text += page_text + "\n"
                        pages_with_text += 1
                        
                        # Log da primeira página com conteúdo para debug
                        if pages_with_text == 1:
                            logger.debug(
                                "Primeira página com conteúdo extraída",
                                file=str(file_path),
                                page_num=page_num,
                                page_text_length=len(page_text),
                                page_text_preview=page_text[:300] if page_text else ""
                            )
                    else:
                        # Página só tem whitespace
                        pages_without_text += 1
                        if page_num <= 3:  # Log apenas das primeiras páginas vazias
                            logger.debug(
                                "Página sem conteúdo real (apenas whitespace)",
                                file=str(file_path),
                                page_num=page_num,
                                page_text_length=len(page_text) if page_text else 0
                            )
            
            text = text.strip()
            
            # Validar que o texto não está vazio ou só tem whitespace
            text_non_whitespace = text.replace('\n', '').replace(' ', '').replace('\t', '').strip()
            
            # Se pypdf não extraiu texto suficiente, tentar OCR
            if not text or len(text_non_whitespace) < 50:
                logger.warning(
                    "pypdf extraiu texto vazio, tentando OCR",
                    file=str(file_path),
                    text_length=len(text),
                    text_non_whitespace_length=len(text_non_whitespace),
                    total_pages=total_pages,
                    pages_with_text=pages_with_text,
                    pages_without_text=pages_without_text
                )
                
                # Tentar OCR como fallback
                if OCR_AVAILABLE:
                    ocr_text = self.parse_pdf_with_ocr(file_path)
                    if ocr_text and len(ocr_text.replace('\n', '').replace(' ', '').replace('\t', '').strip()) >= 50:
                        logger.info(
                            "OCR conseguiu extrair texto do PDF",
                            file=str(file_path),
                            ocr_text_length=len(ocr_text)
                        )
                        return ocr_text
                    else:
                        logger.error(
                            "OCR também não conseguiu extrair texto suficiente",
                            file=str(file_path)
                        )
                        return ""
                else:
                    logger.error(
                        "PDF extraído com texto vazio e OCR não disponível",
                        file=str(file_path),
                        text_length=len(text),
                        text_non_whitespace_length=len(text_non_whitespace),
                        total_pages=total_pages,
                        pages_with_text=pages_with_text,
                        pages_without_text=pages_without_text
                    )
                    return ""
            
            logger.info(
                "PDF parseado com sucesso (pypdf)",
                file=str(file_path),
                text_length=len(text),
                text_non_whitespace_length=len(text_non_whitespace),
                total_pages=total_pages,
                pages_with_text=pages_with_text,
                pages_without_text=pages_without_text
            )
            
            return text
        except Exception as e:
            logger.error("Erro ao parsear PDF", file=str(file_path), error=str(e))
            # Se pypdf falhar completamente, tentar OCR
            if OCR_AVAILABLE:
                logger.info("Tentando OCR após erro no pypdf", file=str(file_path))
                return self.parse_pdf_with_ocr(file_path)
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
    
    def parse_json_normativo(self, file_path: Path) -> tuple[str, Dict]:
        """
        Parse arquivo JSON de normativo normalizado do Bacen.
        
        Args:
            file_path: Caminho do arquivo JSON
        
        Returns:
            tuple: (texto, metadados)
        """
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            text = data.get("text", "")
            metadata = data.get("metadata", {})
            
            # Construir base_metadata no formato esperado
            base_metadata = {
                "fonte": metadata.get("fonte", file_path.name),
                "tema": metadata.get("tema", "pix"),
                "norma": metadata.get("tipo", "Normativo"),
                "numero_norma": metadata.get("numero", ""),
                "ano": metadata.get("ano", 2023),
                "url": metadata.get("url"),
            }
            
            # Artigo já está no metadata, será usado pelo chunker
            
            logger.info(
                "JSON normativo parseado",
                file=str(file_path),
                norma=base_metadata["norma"],
                numero=base_metadata["numero_norma"],
                artigo=metadata.get("artigo")
            )
            
            return text, base_metadata
            
        except Exception as e:
            logger.error("Erro ao parsear JSON normativo", file=str(file_path), error=str(e))
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
        Suporta PDF, HTML e JSON (normativos normalizados do Bacen).
        """
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            text = self.parse_pdf(file_path)
        elif suffix in [".html", ".htm"]:
            text = self.parse_html(file_path)
        elif suffix == ".json":
            # Arquivo JSON de normativo normalizado do Bacen
            text, base_metadata = self.parse_json_normativo(file_path)
            return text, base_metadata
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

