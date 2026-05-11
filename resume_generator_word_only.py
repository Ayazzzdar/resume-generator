import streamlit as st
import anthropic
import requests
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Resume Tailor",
    page_icon="📄",
    layout="centered"  # Changed to centered
)

# Path to your master resume
MASTER_RESUME_PATH = "master_resume.docx"

# Custom CSS for centered card design with gradient
st.markdown("""
<style>
    /* Hide Streamlit branding and elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Purple gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Center everything */
    .main .block-container {
        max-width: 800px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }
    
    /* Remove default streamlit padding/margins */
    .main > div {
        padding-top: 0;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #718096;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* White card background for inputs */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    /* Input styling - white background with dark text */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #1a202c !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0aec0 !important;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: white !important;
        color: #1a202c !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #a0aec0 !important;
    }
    
    /* Label text - dark on white background */
    .stTextInput label,
    .stTextArea label,
    .stFileUploader label {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background-color: white !important;
    }
    
    .stFileUploader section {
        background-color: #f7fafc !important;
        border: 2px dashed #e2e8f0 !important;
        border-radius: 10px !important;
    }
    
    .stFileUploader section button {
        background-color: #667eea !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem 2rem !important;
        border-radius: 10px !important;
        border: none !important;
        font-size: 1.1rem !important;
        margin-top: 1rem !important;
        transition: all 0.3s !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Feature badges */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid #e2e8f0;
    }
    
    .feature-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
        color: #4a5568;
    }
    
    .feature-check {
        width: 24px;
        height: 24px;
        background: #48bb78;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
    }
    
    /* API Key gate styling */
    .api-gate {
        text-align: center;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    /* Remove any fade-in animations */
    * {
        animation: none !important;
        transition: none !important;
    }
    
    .stButton > button,
    .stButton > button:hover {
        transition: all 0.3s !important;
    }
    
    /* Fix for any dark backgrounds appearing */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Ensure all text is dark on white backgrounds */
    .stMarkdown, p, span, div {
        color: #1a202c !important;
    }
    
    /* Footer text in white */
    .footer-text {
        color: white !important;
        text-align: center;
        padding: 2rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def scrape_job_posting(url):
    """Scrape job posting content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text[:15000]
    except Exception as e:
        st.error(f"Error scraping job posting: {str(e)}")
        return None

def analyze_job_posting(job_content, api_key):
    """Use Claude to extract key requirements from job posting"""
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Analyze this job posting and extract the following information in a structured format:

Job Posting:
{job_content}

Extract:
1. Job Title
2. Company Name (if mentioned)
3. Key Required Skills (list 5-10 most important)
4. Required Experience (years and type)
5. Required Qualifications (education, certifications)
6. Key Responsibilities (top 5-7)
7. Important Keywords for ATS (20-30 keywords that should appear in the resume)
8. Soft Skills mentioned

Format your response as a clear, structured summary."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        st.error(f"Error analyzing job posting: {str(e)}")
        return None

def extract_resume_content(uploaded_file):
    """Extract content from uploaded resume"""
    try:
        doc = Document(uploaded_file)
        content = {'full_text': [], 'sections': {}}
        current_section = None
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                content['full_text'].append(text)
                if para.runs and (para.runs[0].bold or text.isupper()):
                    current_section = text
                    content['sections'][current_section] = []
                elif current_section:
                    content['sections'][current_section].append(text)
        
        return '\n'.join(content['full_text'])
    except Exception as e:
        st.error(f"Error reading resume: {str(e)}")
        return None

def generate_tailored_resume(original_resume, job_analysis, additional_context, api_key):
    """Generate tailored resume using Claude"""
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""You are an expert resume writer and career coach. Create a tailored resume based on the following:

ORIGINAL RESUME:
{original_resume}

JOB REQUIREMENTS ANALYSIS:
{job_analysis}

ADDITIONAL CONTEXT FROM USER:
{additional_context if additional_context else "None provided"}

YOUR TASK:
1. Rewrite the resume to align perfectly with the job requirements
2. Incorporate ALL important keywords naturally throughout the resume
3. Emphasize relevant experience and skills that match the job
4. Quantify achievements where possible (use realistic metrics if needed)
5. Reorder bullet points to highlight most relevant items first
6. Adjust the professional summary to target this specific role
7. Ensure ATS-friendly formatting (no tables, clear sections)
8. Keep the same personal information (name, contact details)

CRITICAL REQUIREMENTS:
- Use keywords from the job posting naturally in context
- Match the tone and style of the job description
- Prioritize experiences that align with job requirements
- Make every bullet point achievement-oriented and quantifiable
- Keep total length to 1-2 pages worth of content
- Maintain honesty - enhance but don't fabricate

OUTPUT FORMAT:
Provide the complete resume in a clean, well-structured format with clear sections:
- Header (Name, Contact Info)
- Professional Summary
- Core Skills
- Professional Experience (with bullet points)
- Education
- Certifications (if applicable)
- Additional Sections as needed

Make this resume stand out to both ATS systems and human recruiters."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        st.error(f"Error generating resume: {str(e)}")
        return None

def create_docx_from_text(resume_text):
    """Create a formatted Word document from resume text"""
    doc = Document()
    
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
    
    lines = resume_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        is_header = (
            line.isupper() or 
            any(keyword in line.upper() for keyword in [
                'PROFESSIONAL SUMMARY', 'EXPERIENCE', 'EDUCATION', 
                'SKILLS', 'CERTIFICATIONS', 'PROJECTS', 'CORE SKILLS'
            ])
        )
        
        is_name = len(doc.paragraphs) == 0 and not line.startswith('-')
        
        para = doc.add_paragraph()
        run = para.add_run(line)
        
        if is_name:
            run.font.size = Pt(16)
            run.bold = True
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif is_header:
            run.font.size = Pt(12)
            run.bold = True
            run.font.color.rgb = RGBColor(0, 0, 0)
            para.space_before = Pt(12)
            para.space_after = Pt(6)
        elif line.startswith('-') or line.startswith('•'):
            run.font.size = Pt(10)
            para.left_indent = Inches(0.25)
        else:
            run.font.size = Pt(10)
    
    return doc

# Initialize session state
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# API Key Gate
if not st.session_state.api_key_validated:
    st.markdown('<div class="main-header">📄 AI Resume Tailor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate ATS-optimized resumes in seconds</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    api_key_input = st.text_input(
        "Enter your Anthropic API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        help="Get your API key from console.anthropic.com"
    )
    
    if st.button("🚀 Start Using App"):
        if api_key_input and api_key_input.startswith("sk-ant-"):
            try:
                client = anthropic.Anthropic(api_key=api_key_input)
                test = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                st.session_state.api_key = api_key_input
                st.session_state.api_key_validated = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Invalid API key. Please check and try again.")
        else:
            st.error("❌ Please enter a valid Anthropic API key")
    
    st.stop()

# Main App (centered card design)

# Header
st.markdown('<div class="main-header">📄 AI Resume Tailor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate ATS-optimized resumes in seconds</div>', unsafe_allow_html=True)

# Job Posting URL
job_url = st.text_input(
    "Job Posting URL *",
    placeholder="https://www.linkedin.com/jobs/view/...",
    label_visibility="visible"
)

# Resume Upload
uploaded_resume = st.file_uploader(
    "Upload Your Resume (.docx) *",
    type=['docx'],
    help="Max size: 10MB | Format: Microsoft Word"
)

# Additional Context
additional_context = st.text_area(
    "Additional Context (Optional)",
    placeholder="E.g., 'Emphasize my leadership skills' or 'Transitioning from sales to marketing'",
    height=100
)

# Generate Button
if st.button("🚀 Generate Tailored Resume"):
    api_key = st.session_state.api_key
    
    if not job_url:
        st.error("Please enter a job posting URL")
    elif not uploaded_resume:
        st.error("Please upload your resume")
    else:
        with st.spinner("🔍 Analyzing job posting..."):
            job_content = scrape_job_posting(job_url)
            
            if not job_content:
                st.error("Failed to retrieve job posting. Please try again.")
                st.stop()
            
            job_analysis = analyze_job_posting(job_content, api_key)
            
            if not job_analysis:
                st.stop()
            
            st.success("✅ Job posting analyzed!")
        
        with st.spinner("📄 Processing your resume..."):
            original_resume = extract_resume_content(uploaded_resume)
            
            if not original_resume:
                st.stop()
            
            st.success("✅ Resume processed!")
        
        with st.spinner("✨ Generating tailored resume... (30-60 seconds)"):
            tailored_resume = generate_tailored_resume(
                original_resume,
                job_analysis,
                additional_context,
                api_key
            )
            
            if not tailored_resume:
                st.stop()
            
            st.success("✅ Tailored resume generated!")
        
        # Create Word document
        doc = create_docx_from_text(tailored_resume)
        doc_bytes = io.BytesIO()
        doc.save(doc_bytes)
        doc_bytes.seek(0)
        
        filename = f"Tailored_Resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        # Download button
        st.download_button(
            label="⬇️ Download Word Document",
            data=doc_bytes.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
        
        st.balloons()

# Feature badges
st.markdown("""
<div class="feature-grid">
    <div class="feature-badge">
        <div class="feature-check">✓</div>
        <span>ATS Optimized</span>
    </div>
    <div class="feature-badge">
        <div class="feature-check">✓</div>
        <span>Keyword Matching</span>
    </div>
    <div class="feature-badge">
        <div class="feature-check">✓</div>
        <span>Smart Tailoring</span>
    </div>
    <div class="feature-badge">
        <div class="feature-check">✓</div>
        <span>Instant Results</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(
    "<div class='footer-text'>"
    "Built with Claude API | Tailor your resume for every opportunity"
    "</div>",
    unsafe_allow_html=True
)
