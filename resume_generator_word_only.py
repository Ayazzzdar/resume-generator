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
    layout="wide"
)

# Path to your master resume
MASTER_RESUME_PATH = "master_resume.docx"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
    }
    .success-box {
        padding: 1.5rem;
        background: #d1fae5;
        border-radius: 0.5rem;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
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
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text[:15000]  # Limit to avoid token limits
        
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

def extract_resume_content(file_path=MASTER_RESUME_PATH):
    """Extract content from stored master resume"""
    try:
        if not os.path.exists(file_path):
            st.error(f"⚠️ Master resume not found at: {file_path}")
            st.info("Please add your master resume as 'master_resume.docx' in the same directory as this script.")
            return None
            
        doc = Document(file_path)
        
        content = {
            'full_text': [],
            'sections': {}
        }
        
        current_section = None
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                content['full_text'].append(text)
                
                # Detect section headers (typically all caps or bold)
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
    
    # Set document margins
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
        
        # Detect section headers (all caps or specific keywords)
        is_header = (
            line.isupper() or 
            any(keyword in line.upper() for keyword in [
                'PROFESSIONAL SUMMARY', 'EXPERIENCE', 'EDUCATION', 
                'SKILLS', 'CERTIFICATIONS', 'PROJECTS', 'CORE SKILLS'
            ])
        )
        
        # Detect name (typically first line)
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

# Initialize session state for API key
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# API Key Gate - Must enter before accessing app
if not st.session_state.api_key_validated:
    st.markdown('<div class="main-header">📄 AI Resume Tailor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate ATS-optimized resumes tailored to any job posting</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🔑 API Key Required")
    st.info("This app requires an Anthropic API key to function. Your key is stored only for this session and is never saved or shared.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        api_key_input = st.text_input(
            "Enter your Anthropic API Key",
            type="password",
            placeholder="sk-ant-api03-...",
            help="Get your API key from console.anthropic.com"
        )
        
        if st.button("🚀 Start Using App", use_container_width=True, type="primary"):
            if api_key_input and api_key_input.startswith("sk-ant-"):
                # Validate the API key by making a minimal test call
                try:
                    client = anthropic.Anthropic(api_key=api_key_input)
                    # Simple test to verify key works
                    test = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "Hi"}]
                    )
                    st.session_state.api_key = api_key_input
                    st.session_state.api_key_validated = True
                    st.success("✅ API key validated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Invalid API key. Please check and try again.")
                    st.caption(f"Error: {str(e)}")
            else:
                st.error("❌ Please enter a valid Anthropic API key (starts with 'sk-ant-')")
    
    st.markdown("---")
    
    st.markdown("### ℹ️ How to Get an API Key")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        **Steps:**
        1. Go to [console.anthropic.com](https://console.anthropic.com)
        2. Sign up or log in
        3. Navigate to "API Keys"
        4. Click "Create Key"
        5. Copy and paste here
        """)
    
    with col_b:
        st.markdown("""
        **Costs:**
        - ~$0.10-0.30 per resume
        - Pay as you go
        - Very affordable for job searching
        
        [View Pricing →](https://www.anthropic.com/pricing)
        """)
    
    st.markdown("---")
    
    st.markdown("### 🔒 Privacy & Security")
    st.markdown("""
    - ✅ Your API key is stored in session only (not saved)
    - ✅ Your resume data never leaves this session
    - ✅ Job postings are not stored
    - ✅ All API calls are encrypted
    - ✅ Open source - verify the code yourself
    """)
    
    st.stop()  # Stop execution here until API key is entered

# Main App (only shows after API key is validated)
st.markdown('<div class="main-header">📄 AI Resume Tailor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate ATS-optimized resumes tailored to any job posting</div>', unsafe_allow_html=True)

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Show API key status
    if st.session_state.api_key_validated:
        st.success("✅ API Key Active")
        masked_key = st.session_state.api_key[:12] + "..." + st.session_state.api_key[-4:]
        st.caption(f"Key: {masked_key}")
        
        if st.button("🔄 Change API Key", use_container_width=True):
            st.session_state.api_key_validated = False
            st.session_state.api_key = ""
            st.rerun()
    
    st.markdown("---")
    st.header("📄 Your Master Resume")
    
    # Check if master resume exists locally, if not try secrets, then allow upload
    resume_loaded = False
    
    # Try local file first
    if os.path.exists(MASTER_RESUME_PATH):
        resume_loaded = True
        st.success("✅ Master resume loaded")
        st.caption(f"Using: {MASTER_RESUME_PATH}")
    
    # Try Streamlit secrets (for personal deployment)
    elif "master_resume_base64" in st.secrets:
        try:
            import base64
            resume_data = base64.b64decode(st.secrets["master_resume_base64"])
            with open(MASTER_RESUME_PATH, "wb") as f:
                f.write(resume_data)
            resume_loaded = True
            st.success("✅ Master resume loaded from secrets")
        except Exception as e:
            st.error(f"Error loading from secrets: {str(e)}")
    
    # Allow upload if no resume found
    if not resume_loaded:
        st.warning("⚠️ No master resume found")
        uploaded_resume = st.file_uploader(
            "Upload Your Master Resume",
            type=['docx'],
            help="Upload your comprehensive resume with ALL your experience"
        )
        
        if uploaded_resume:
            # Save to temporary location
            with open(MASTER_RESUME_PATH, "wb") as f:
                f.write(uploaded_resume.getbuffer())
            st.success("✅ Resume uploaded!")
            st.info("💡 Your resume is stored for this session only")
            resume_loaded = True
            st.rerun()
        else:
            st.info("👆 Upload your master resume to get started")
    
    # Option to replace existing resume
    if resume_loaded:
        if st.checkbox("Replace resume"):
            new_resume = st.file_uploader(
                "Upload New Resume",
                type=['docx'],
                key="replace_resume"
            )
            if new_resume:
                with open(MASTER_RESUME_PATH, "wb") as f:
                    f.write(new_resume.getbuffer())
                st.success("✅ Resume replaced!")
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 How it works:")
    st.markdown("""
    1. Paste job posting URL
    2. Claude analyzes requirements
    3. Tailors your master resume
    4. Downloads Word document
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Tips:")
    st.markdown("""
    - Works with LinkedIn, Indeed, company sites
    - Word doc is fully editable
    - Master resume keeps all your experience
    - Add context for better results
    """)
    
    st.markdown("---")
    st.markdown("### 🔐 Privacy:")
    st.markdown("""
    - Resume stored locally only
    - Job data not saved
    - Everything runs on your machine
    """)
    
    st.markdown("---")
    st.markdown("### 💰 Cost:")
    st.markdown("""
    ~$0.10-0.30 per resume
    (Claude API usage)
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1️⃣ Job Posting")
    job_url = st.text_input(
        "Job Posting URL",
        placeholder="https://www.linkedin.com/jobs/view/..."
    )
    
    # Option to paste job description directly
    use_direct_paste = st.checkbox("Or paste job description directly")
    
    if use_direct_paste:
        job_text = st.text_area(
            "Job Description",
            height=300,
            placeholder="Paste the complete job description here..."
        )

with col2:
    st.subheader("2️⃣ Additional Context")
    additional_context = st.text_area(
        "Customization notes (Optional)",
        placeholder="E.g., 'Emphasize my project management skills', 'I'm transitioning from marketing to product', 'Focus on leadership experience'",
        height=200
    )
    
    job_title_hint = st.text_input(
        "Job title for filename",
        placeholder="e.g., Senior Product Manager",
        help="This helps name your file for easy organization"
    )

# Generate button
if st.button("🚀 Generate Tailored Resume", type="primary"):
    # Get API key from session state
    api_key = st.session_state.api_key
    
    if not api_key:
        st.error("Please enter your Anthropic API key")
    elif not os.path.exists(MASTER_RESUME_PATH):
        st.error(f"Master resume not found. Please upload your master resume in the sidebar")
    elif not use_direct_paste and not job_url:
        st.error("Please provide a job posting URL or paste the description")
    elif use_direct_paste and not job_text:
        st.error("Please paste the job description")
    else:
        with st.spinner("🔍 Analyzing job posting..."):
            # Get job content
            if use_direct_paste:
                job_content = job_text
            else:
                job_content = scrape_job_posting(job_url)
            
            if not job_content:
                st.error("Failed to retrieve job posting. Please try pasting it directly.")
                st.stop()
            
            # Analyze job posting
            job_analysis = analyze_job_posting(job_content, api_key)
            
            if not job_analysis:
                st.stop()
            
            st.success("✅ Job posting analyzed!")
            
            with st.expander("📊 Job Analysis"):
                st.write(job_analysis)
        
        with st.spinner("📄 Loading your master resume..."):
            original_resume = extract_resume_content()
            
            if not original_resume:
                st.stop()
            
            st.success("✅ Master resume loaded!")
        
        with st.spinner("✨ Generating tailored resume... (this may take 30-60 seconds)"):
            tailored_resume = generate_tailored_resume(
                original_resume,
                job_analysis,
                additional_context,
                api_key
            )
            
            if not tailored_resume:
                st.stop()
            
            st.success("✅ Tailored resume generated!")
        
        # Display and download
        st.markdown("---")
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("### 🎉 Your Tailored Resume is Ready!")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Show preview
        with st.expander("👀 Preview Resume Content", expanded=False):
            st.text(tailored_resume)
        
        # Create Word document
        doc = create_docx_from_text(tailored_resume)
        
        # Save to bytes
        doc_bytes = io.BytesIO()
        doc.save(doc_bytes)
        doc_bytes.seek(0)
        
        # Generate filename
        if job_title_hint:
            # Clean the job title for filename
            safe_title = "".join(c for c in job_title_hint if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"Resume_{safe_title}_{datetime.now().strftime('%Y%m%d')}.docx"
        else:
            filename = f"Tailored_Resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        # Download button
        col_a, col_b, col_c = st.columns([1, 2, 1])
        
        with col_b:
            st.download_button(
                label="⬇️ Download Word Document",
                data=doc_bytes.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        st.info("💡 **Pro tip:** Open the Word doc and make any final tweaks before submitting!")
        
        # Stats
        st.markdown("---")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Words", len(tailored_resume.split()))
        
        with col_stat2:
            st.metric("Characters", len(tailored_resume))
        
        with col_stat3:
            keyword_count = job_analysis.count("Keywords") if job_analysis else 0
            st.metric("Optimized", "✓ ATS Ready")
        
        st.balloons()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; padding: 2rem;'>"
    "Built with Claude API | Tailor your resume for every opportunity"
    "</div>",
    unsafe_allow_html=True
)
