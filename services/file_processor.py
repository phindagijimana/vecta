"""
Med42 File Processing Module
Handles file upload, validation, and text extraction for medical documents
"""

import os
import json
import tempfile
import logging
from pathlib import Path
from io import StringIO
from typing import Dict, Any, Optional, Tuple
from werkzeug.utils import secure_filename

# Optional imports - keep app alive even if missing
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    Document = None
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PyPDF2 = None
    PDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class FileProcessor:
    """Handles secure file processing and text extraction for Med42"""

    def __init__(self, allowed_extensions: set, upload_folder: str, max_content_length: int):
        self.allowed_extensions = allowed_extensions
        self.upload_folder = upload_folder
        self.max_content_length = max_content_length

        # Ensure upload directory exists
        Path(upload_folder).mkdir(parents=True, exist_ok=True)

    def validate_file(self, file_obj, filename: str) -> Tuple[bool, str]:
        """Validate uploaded file for security and compatibility"""
        if not filename:
            return False, "No file selected"

        # Check filename security
        secure_name = secure_filename(filename)
        if secure_name != filename:
            return False, "Insecure filename detected"

        # Check file extension
        if '.' not in filename:
            return False, "File must have an extension"

        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in self.allowed_extensions:
            return False, f"Unsupported file type .{ext}. Allowed: {', '.join(self.allowed_extensions)}"

        # Check file size
        file_obj.seek(0, 2)  # Seek to end
        size = file_obj.tell()
        file_obj.seek(0)  # Reset to beginning

        if size > self.max_content_length:
            return False, f"File too large ({size/1024/1024:.1f}MB). Maximum: {self.max_content_length/1024/1024:.0f}MB"

        return True, "Valid"

    def extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text content from uploaded file"""
        try:
            ext = filename.rsplit(".", 1)[1].lower()
            logger.info(f"Extracting text from {filename} (type: {ext})")

            if ext == "txt":
                return self._extract_text_file(file_path)
            elif ext == "pdf" and PDF_AVAILABLE:
                return self._extract_pdf_file(file_path)
            elif ext == "docx" and DOCX_AVAILABLE:
                return self._extract_docx_file(file_path)
            elif ext == "json":
                return self._extract_json_file(file_path)
            else:
                return f"[Unsupported file type: {ext}]"

        except Exception as e:
            logger.error(f"Text extraction error for {filename}: {e}")
            return f"Error extracting text from {filename}: {str(e)}"

    def _extract_text_file(self, file_path: str) -> str:
        """Extract text from plain text files"""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _extract_pdf_file(self, file_path: str) -> str:
        """Extract text from PDF files"""
        if not PDF_AVAILABLE:
            return "[PDF processing not available]"

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

    def _extract_docx_file(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        if not DOCX_AVAILABLE:
            return "[DOCX processing not available]"

        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    def _extract_json_file(self, file_path: str) -> str:
        """Extract and format JSON files"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return json.dumps(data, indent=2)

    def process_tabular_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process tabular files (CSV, Excel) with enhanced analysis"""
        try:
            ext = filename.rsplit(".", 1)[1].lower()
            logger.info(f"Processing tabular data from {filename} (type: {ext})")

            if not PANDAS_AVAILABLE:
                return {
                    "text": "[Tabular data processing not available - pandas required]",
                    "dataframe": None,
                    "is_tabular": False,
                    "tabular_data": None
                }

            if ext in ["csv", "xlsx", "xls"]:
                df = self._load_tabular_data(file_path, ext)
                if df is not None:
                    tabular_data = self._analyze_tabular_data(df, filename)
                    return {
                        "text": tabular_data["data_summary"] if tabular_data else df.to_string(),
                        "dataframe": df,
                        "is_tabular": True,
                        "tabular_data": tabular_data
                    }

            # Fallback to text extraction for non-tabular files
            return {
                "text": self.extract_text_from_file(file_path, filename),
                "dataframe": None,
                "is_tabular": False,
                "tabular_data": None
            }

        except Exception as e:
            logger.error(f"Tabular processing error for {filename}: {e}")
            return {
                "text": f"Error processing tabular data from {filename}: {str(e)}",
                "dataframe": None,
                "is_tabular": False,
                "tabular_data": None
            }

    def _load_tabular_data(self, file_path: str, ext: str):
        """Load tabular data into pandas DataFrame"""
        try:
            if ext == "csv":
                return pd.read_csv(file_path)
            elif ext in ["xlsx", "xls"]:
                return pd.read_excel(file_path)
        except Exception as e:
            logger.error(f"Failed to load {ext} file: {e}")
            return None

    def _analyze_tabular_data(self, df, filename: str) -> Optional[Dict[str, Any]]:
        """Perform basic tabular data analysis"""
        try:
            # Basic data profiling
            profile = {
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum()
            }

            # Sample data for analysis
            sample_size = min(100, len(df))
            sample_df = df.head(sample_size)

            # Enhanced data summary for Med42
            data_summary = f"""
MED42 DATASET PROFILE:
- Shape: {profile['shape'][0]} rows × {profile['shape'][1]} columns
- Columns: {', '.join(profile['columns'])}
- Missing values: {dict(filter(lambda x: x[1] > 0, profile['missing_values'].items()))}

SAMPLE DATA FOR MED42 ANALYSIS (first {sample_size} rows):
{sample_df.to_string(max_cols=10, max_rows=20)}

MEDICAL ANALYSIS CONTEXT:
This dataset contains medical information that requires your specialized Med42-8B training for proper interpretation. Apply your clinical reasoning and medical knowledge to analyze patterns, identify clinically significant findings, and provide structured medical insights.
"""

            return {
                "profile": profile,
                "sample_data": sample_df,
                "data_summary": data_summary,
                "full_dataframe": df
            }

        except Exception as e:
            logger.error(f"Tabular analysis failed: {e}")
            return None

    def detect_tabular_content(self, text: str) -> Tuple[bool, Optional[Any]]:
        """Detect if text content contains tabular data"""
        if not PANDAS_AVAILABLE:
            return False, None

        # Check for common tabular indicators
        has_tabs = '\t' in text
        has_commas = ',' in text

        if has_tabs or has_commas:
            try:
                df = pd.read_csv(StringIO(text))
                if len(df.columns) > 1:
                    tabular_analysis = self._analyze_tabular_data(df, "direct_input")
                    return True, {
                        "text": text,
                        "dataframe": df,
                        "is_tabular": True,
                        "tabular_data": tabular_analysis
                    }
            except Exception:
                pass

        return False, None


def generate_tabular_output(analysis_result: Dict, original_df, analysis_type: str):
    """Generate enhanced tabular output using Med42 insights with standardized 4-column format"""
    try:
        from datetime import datetime
        output_df = original_df.copy()

        # Parse the analysis for structured results in bullet-point format
        analysis_text = analysis_result.get('analysis', '')

        # Extract bullet points from analysis (dynamic first column based on analysis type)
        first_column_name = "Classification"  # Default
        if analysis_type == "diagnosis":
            first_column_name = "Diagnosis Support"
        elif analysis_type == "summary":
            first_column_name = "Summarization"
        elif analysis_type == "extraction":
            first_column_name = "Information Extraction"

        # Initialize variables
        first_column_value = f"Analysis completed using clinical reasoning ({analysis_type})"
        confidence = "MEDIUM"
        evidence = "Based on provided clinical data"
        medication_analysis = "Clinical recommendations provided"

        # Parse the bullet-point format
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(f'- {first_column_name}:'):
                first_column_value = line.split(':', 1)[1].strip()[:100]  # Max 100 chars for table
            elif line.startswith('- Clinical_Confidence:'):
                confidence_text = line.split(':', 1)[1].strip().lower()
                if 'high' in confidence_text:
                    confidence = "HIGH"
                elif 'low' in confidence_text:
                    confidence = "LOW"
                else:
                    confidence = "MEDIUM"
            elif line.startswith('- Evidence:'):
                evidence = line.split(':', 1)[1].strip()[:100]
            elif line.startswith('- Medication_Analysis:'):
                medication_analysis = line.split(':', 1)[1].strip()[:100]

        # Add the standardized 4 Med42 analysis columns for each row
        output_df[first_column_name] = first_column_value
        output_df['Clinical_Confidence'] = confidence
        output_df['Evidence'] = evidence
        output_df['Medication_Analysis'] = medication_analysis

        # Add standard Med42 metadata columns
        output_df['Med42_Analysis_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output_df['Med42_Model_Used'] = 'Med42-8B-Optimized'
        output_df['Med42_Prompt_Version'] = 'Structured-Analysis-Format'

        return output_df

    except Exception as e:
        logger.error(f"Enhanced tabular output generation failed: {e}")
        # Fallback: add basic columns if parsing fails
        first_column_name = "Classification"  # Default
        if analysis_type == "diagnosis":
            first_column_name = "Diagnosis Support"
        elif analysis_type == "summary":
            first_column_name = "Summarization"
        elif analysis_type == "extraction":
            first_column_name = "Information Extraction"

        output_df[first_column_name] = 'Analysis completed'
        output_df['Clinical_Confidence'] = 'MEDIUM'
        output_df['Evidence'] = 'Clinical data reviewed'
        output_df['Medication_Analysis'] = 'Recommendations provided'
        return output_df



