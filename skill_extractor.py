import os
import re
import logging
from typing import List, Set

try:
    import docx
except ImportError:
    docx = None
    
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class SkillExtractor:
    """Extract skills from resume documents."""
    
    def __init__(self):
        """Initialize the skill extractor with predefined skill patterns."""
        # Common technical skills to look for
        self.technical_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 
            'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell',
            'bash', 'powershell', 'vba', 'sql', 'html', 'css', 'xml', 'json', 'yaml',
            
            # Frameworks and Libraries
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 
            'spring', 'rails', 'laravel', 'symfony', 'asp.net', 'jquery', 'bootstrap',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'matplotlib', 'seaborn', 'opencv', 'nltk', 'spacy',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite',
            'oracle', 'sql server', 'cassandra', 'dynamodb', 'firebase',
            
            # Cloud and DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins',
            'gitlab', 'github', 'git', 'terraform', 'ansible', 'puppet', 'chef',
            'nagios', 'prometheus', 'grafana', 'elk stack', 'ci/cd',
            
            # Data Science and ML
            'machine learning', 'deep learning', 'data science', 'data analysis',
            'data visualization', 'statistics', 'regression', 'classification',
            'clustering', 'neural networks', 'natural language processing', 'nlp',
            'computer vision', 'recommendation systems', 'big data', 'hadoop', 'spark',
            
            # Web Technologies
            'rest api', 'graphql', 'microservices', 'web services', 'soap', 'http',
            'oauth', 'jwt', 'websockets', 'ajax', 'responsive design', 'seo',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic',
            
            # Other Technologies
            'blockchain', 'cryptocurrency', 'agile', 'scrum', 'kanban', 'jira',
            'confluence', 'slack', 'teams', 'linux', 'unix', 'windows', 'macos',
            'networking', 'security', 'cybersecurity', 'penetration testing',
            'ethical hacking', 'encryption', 'ssl', 'https', 'firewall'
        }
        
        # Initialize vectorizer if sklearn is available
        if SKLEARN_AVAILABLE:
            try:
                self.vectorizer = TfidfVectorizer(
                    lowercase=True,
                    stop_words='english',
                    ngram_range=(1, 2),
                    max_features=1000
                )
                logging.info("Initialized TF-IDF vectorizer successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize vectorizer: {e}")
                self.vectorizer = None
        else:
            self.vectorizer = None
            logging.warning("scikit-learn not available, using basic keyword matching only")
    
    def extract_text_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF file."""
        if PyPDF2 is None:
            raise Exception("PyPDF2 is not installed. Please install it to process PDF files.")
            
        try:
            text = ""
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
            raise Exception(f"Failed to read PDF file: {str(e)}")
    
    def extract_text_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX file."""
        if docx is None:
            raise Exception("python-docx is not installed. Please install it to process DOCX files.")
            
        try:
            doc = docx.Document(filepath)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting text from DOCX: {e}")
            raise Exception(f"Failed to read DOCX file: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep alphanumeric and common punctuation
        text = re.sub(r'[^\w\s\.\-\+\#]', ' ', text)
        return text.strip()
    
    def extract_skills_keyword_matching(self, text: str) -> Set[str]:
        """Extract skills using keyword matching."""
        found_skills = set()
        text_lower = text.lower()
        
        for skill in self.technical_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return found_skills
    
    def extract_skills_context_based(self, text: str) -> Set[str]:
        """Extract skills using context-based matching."""
        found_skills = set()
        
        # Look for common patterns that indicate skills
        skill_patterns = [
            r'(?:experience|proficient|skilled|knowledge|familiar)\s+(?:in|with)\s+([^.]+)',
            r'(?:technologies|tools|languages|frameworks):\s*([^.]+)',
            r'(?:programming|coding)\s+(?:languages|skills):\s*([^.]+)',
            r'(?:technical|software)\s+skills:\s*([^.]+)',
        ]
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                skill_text = match.group(1).lower()
                # Check if any of our known skills appear in this context
                for skill in self.technical_skills:
                    if skill in skill_text:
                        found_skills.add(skill)
        
        return found_skills
    
    def extract_skills(self, filepath: str) -> List[str]:
        """Extract skills from resume file."""
        try:
            # Determine file type and extract text
            file_extension = filepath.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                text = self.extract_text_from_pdf(filepath)
            elif file_extension == 'docx':
                text = self.extract_text_from_docx(filepath)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            if not text.strip():
                raise Exception("No text could be extracted from the file")
            
            # Clean the extracted text
            cleaned_text = self.clean_text(text)
            logging.debug(f"Extracted text length: {len(cleaned_text)} characters")
            
            # Extract skills using multiple methods
            keyword_skills = self.extract_skills_keyword_matching(cleaned_text)
            context_skills = self.extract_skills_context_based(cleaned_text)
            
            # Combine results
            all_skills = keyword_skills.union(context_skills)
            
            # Convert to sorted list for consistent output
            skills_list = sorted(list(all_skills))
            
            logging.info(f"Extracted {len(skills_list)} skills: {skills_list}")
            return skills_list
            
        except Exception as e:
            logging.error(f"Error in extract_skills: {e}")
            raise
