from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractCliOcrOptions
from docling.document_converter import DocumentConverter, ImageFormatOption

class OCREngine:
    """Configures, builds, and maintains the isolated Docling layout-parsing infrastructure."""
    
    def __init__(self):
        self.converter = self._build_converter()

    def _build_converter(self) -> DocumentConverter:
        """Sets up custom Docling pipeline parameters forcing local Tesseract execution."""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.ocr_options = TesseractCliOcrOptions()

        return DocumentConverter(
            format_options={
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options)
            }
        )
        
    def convert_file(self, full_path: str):
        """Converts an absolute asset target path to a standard Docling conversion object."""
        return self.converter.convert(full_path)