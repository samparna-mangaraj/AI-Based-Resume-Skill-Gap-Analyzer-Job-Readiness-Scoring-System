import io
import re
import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup

class ResumeParser:
    """
    Professional NLP-driven Resume Parser
    Supports: PDF, DOCX, TXT, HTML
    Cleaning: Level 2 (Normal)
    """

    @staticmethod
    def extract_text(content: bytes, file_ext: str) -> str:
        """Extract raw text based on file format"""
        text = ""
        try:
            if file_ext == ".pdf":
                reader = PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            
            elif file_ext == ".docx":
                doc = Document(io.BytesIO(content))
                text = "\n".join([para.text for para in doc.paragraphs])
            
            elif file_ext == ".html" or file_ext == ".htm":
                soup = BeautifulSoup(content, 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                text = soup.get_text()
            
            elif file_ext == ".txt":
                text = content.decode('utf-8', errors='ignore')
            
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        
        except Exception as e:
            print(f"Extraction Error [{file_ext}]: {e}")
            return ""

        return text

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Level 2 Cleaning Implementation:
        - Convert to lowercase
        - Remove special characters and punctuation
        - Normalize whitespace
        - Handle non-ASCII characters
        """
        if not text:
            return ""

        # 1. Lowercase
        text = text.lower()

        # 2. Handle encoding (Remove non-ASCII characters)
        text = text.encode("ascii", "ignore").decode()

        # 3. Remove punctuation and special characters (keep alphanumeric and spaces)
        # We use a regex that keeps only a-z, 0-9, and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)

        # 4. Normalize Whitespace (replace multiple spaces/newlines with a single space)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def extract_metrics(text: str) -> dict:
        """
        Extract professional metrics from text using Regex.
        - Years of Experience
        - Project Counts
        """
        # 1. Extract Years of Experience
        # Patterns like "5 years", "10+ years", "3 yrs"
        exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
        exp_matches = re.findall(exp_pattern, text.lower())
        years = max([int(y) for y in exp_matches]) if exp_matches else 0

        # 2. Extract Project Counts
        # Patterns like "5 projects", "completed 10 projects"
        proj_pattern = r'(\d+)\+?\s*projects?'
        proj_matches = re.findall(proj_pattern, text.lower())
        projects = sum([int(p) for p in proj_matches]) if proj_matches else 0
        
        # Fallback for projects: count occurrences of "Project:" or list items starting with bullet
        if projects == 0:
            projects = text.lower().count("project:")
            if projects == 0:
                # Heuristic: count list items if they look like project descriptions
                projects = len(re.findall(r'•|\*', text)) // 3 # Mock estimate

        return {
            "years_of_experience": min(years, 20), # Cap at 20
            "project_count": min(projects, 50)    # Cap at 50
        }

    @classmethod
    def parse(cls, content: bytes, filename: str) -> dict:
        """Main entry point for parsing a resume file"""
        file_ext = os.path.splitext(filename)[1].lower()
        
        raw_text = cls.extract_text(content, file_ext)
        cleaned_text = cls.clean_text(raw_text)
        metrics = cls.extract_metrics(raw_text)
        
        return {
            "filename": filename,
            "format": file_ext,
            "raw_content": raw_text[:500] if raw_text else "",
            "cleaned_content": cleaned_text,
            "word_count": len(cleaned_text.split()) if cleaned_text else 0,
            "metrics": metrics,
            "success": bool(cleaned_text)
        }
