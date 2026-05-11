# Google Docs Integration Setup Guide

## Overview

Your updated resume generator now:
- ✅ Uses a **master resume file** (no uploads needed)
- ✅ Creates **Google Docs** you can edit directly
- ✅ Returns **shareable links** to each resume
- ✅ Uses **Claude API** to tailor resumes

## How It Works

1. **You store one master resume** (`master_resume.docx`) with ALL your experience
2. **Paste a job URL** → Claude scrapes and analyzes it
3. **Claude tailors your resume** using the Anthropic API (your API key)
4. **Google Doc is created** with full editing permissions
5. **You get a link** to edit/download/share

---

## Setup Steps

### 1. Get Your Master Resume Ready

Create a comprehensive Word document with:
- All your work experience (even old jobs)
- All your skills
- All education, certifications, projects
- Full contact information

Save it as `master_resume.docx` in the same folder as the Streamlit app.

**Why?** Claude will pull the most relevant parts for each job and reorder/rewrite them.

---

### 2. Set Up Google Cloud Project (One-Time)

#### Step A: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Name it: "Resume Generator" 
4. Click "Create"

#### Step B: Enable Required APIs

1. In your new project, go to "APIs & Services" → "Library"
2. Search and enable:
   - **Google Docs API**
   - **Google Drive API**

#### Step C: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: "Resume Generator"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `../auth/documents` and `../auth/drive.file`
   - Test users: Add your email
   - Click "Save and Continue"

4. Back to "Create OAuth client ID":
   - Application type: **Desktop app**
   - Name: "Resume Generator Desktop"
   - Click "Create"

5. **Download** the credentials:
   - Click the download icon on your new OAuth 2.0 Client ID
   - Save as `credentials.json`
   - Move this file to your app directory (same folder as the .py file)

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. First Run - Authenticate

```bash
streamlit run resume_generator.py
```

**First time only:**
1. Your browser will open for Google OAuth
2. Sign in with your Google account
3. Grant permissions for Docs and Drive
4. Token will be saved as `token.pickle` for future use

**After first time:**
- No authentication needed
- Token auto-refreshes

---

### 5. Get Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Go to "API Keys"
4. Create new key
5. Copy and paste into the Streamlit app sidebar

**Cost:** ~$0.10-0.30 per resume (very affordable)

---

## File Structure

```
your-project-folder/
├── resume_generator.py          # Main app
├── requirements.txt             # Python dependencies
├── master_resume.docx          # YOUR master resume (all experience)
├── credentials.json            # Google OAuth credentials (from step 2)
└── token.pickle               # Auto-generated after first auth
```

---

## How to Use

1. **Start the app:** `streamlit run resume_generator.py`
2. **Enter Anthropic API key** in sidebar (one time per session)
3. **Paste job URL** or job description
4. **Add context** (optional): "Focus on leadership", "Transitioning to PM", etc.
5. **Click Generate**
6. **Get Google Doc link** - fully editable!

---

## What Happens Behind the Scenes

### Step 1: Job Analysis (Claude API)
```
Job URL → Web Scraping → Claude analyzes:
- Key required skills
- Experience requirements  
- 20-30 ATS keywords
- Responsibilities
```

### Step 2: Resume Tailoring (Claude API)
```
Master Resume + Job Analysis → Claude:
- Reorders experience by relevance
- Naturally incorporates keywords
- Quantifies achievements
- Emphasizes matching skills
- Keeps your formatting style
```

### Step 3: Google Doc Creation (Google API)
```
Tailored content → Google Docs API:
- Creates new document
- Applies formatting
- Sets sharing to "anyone can edit"
- Returns shareable link
```

**Yes, all the work is done by the Claude API using YOUR API key.** The Google API just creates the final document.

---

## Deployment Options

### Option 1: Run Locally (Easiest)
- Keep running on your computer
- Free
- Best for personal use

### Option 2: Streamlit Cloud
- Host online for free
- Accessible from anywhere
- Good for sharing with clients

**Streamlit Cloud Setup:**
1. Push code to GitHub (include `requirements.txt` and `resume_generator.py`)
2. **DO NOT commit** `credentials.json`, `token.pickle`, or `master_resume.docx`
3. Go to [share.streamlit.io](https://share.streamlit.io)
4. Deploy from your repo
5. Add secrets in Streamlit settings:
   - Add your Google credentials as secrets
   - Add master resume via file upload in app

### Option 3: Your Own Server
- AWS, Digital Ocean, etc.
- Full control
- Can handle multiple users

---

## Troubleshooting

### "Master resume not found"
- Make sure `master_resume.docx` is in the same folder as the Python script
- Check the filename is exactly `master_resume.docx`

### "Google credentials not found"
- Download `credentials.json` from Google Cloud Console
- Place it in the same folder as your app

### "Failed to create Google Doc"
- Check you completed OAuth authentication
- Verify Google Docs and Drive APIs are enabled in your project
- Try deleting `token.pickle` and re-authenticating

### "API Key Error"
- Verify your Anthropic API key is correct
- Check you have credits/billing set up at console.anthropic.com

### "Job scraping failed"
- Some sites block automated scraping
- Use the "paste directly" option instead
- LinkedIn works best when logged in manually first

---

## Security Notes

- **credentials.json**: Contains OAuth client secrets - don't commit to GitHub
- **token.pickle**: Contains your access token - don't share
- **master_resume.docx**: Contains your personal info - keep private
- **API key**: Keep secret - don't hardcode in the script

Add to `.gitignore`:
```
credentials.json
token.pickle
master_resume.docx
*.pickle
```

---

## Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| **Anthropic API** | ~$0.10-0.30 per resume | Pay as you go |
| **Google APIs** | Free | Included in free tier |
| **Streamlit Cloud** | Free | Community tier |
| **Local hosting** | Free | Run on your computer |

**Example:** Generate 100 resumes = $10-30 total

---

## Tips for Best Results

### Master Resume Best Practices
- Include ALL jobs, even old ones
- List every skill you have
- Keep bullet points detailed
- Use action verbs and metrics
- Don't worry about length (Claude will trim)

### Context Examples
Good context:
- "Emphasize my product management experience over technical"
- "Transitioning from finance to tech, highlight transferable skills"
- "Focus on remote work and async communication experience"
- "Downplay career gap, emphasize recent projects"

### Job URLs That Work Best
- ✅ LinkedIn job posts
- ✅ Indeed listings  
- ✅ Company career pages
- ✅ Direct job descriptions
- ⚠️ Login-required pages (use "paste directly")

---

## Customization Ideas

### Change Output Tone
Edit the `generate_tailored_resume()` function prompt:
- More formal: Add "Use extremely formal, corporate language"
- More casual: Add "Use conversational but professional tone"
- Industry-specific: Add "Use terminology common in [industry]"

### Adjust Formatting
Edit the `create_google_doc()` function:
- Change font sizes
- Adjust spacing
- Add color to headers
- Include company logo

### Add Company Research
Enhance the prompt to research the company:
- Add a web search for company info
- Include company values in the resume
- Match company culture in tone

---

## FAQs

**Q: Do I need to upload my resume every time?**
No! You store one master resume file, and the app uses it automatically.

**Q: Can I edit the resume after it's generated?**
Yes! The Google Doc is fully editable. Make any final tweaks directly.

**Q: What format is the output?**
Google Docs (editable online). You can also download as Word, PDF, etc. from Google Docs.

**Q: Does this work for Paula's pharmaceutical QA → lab transition?**
Absolutely! Add context like: "Transitioning from QA to laboratory work, emphasize analytical skills, lab equipment experience, and attention to detail. Downplay QC paperwork, highlight hands-on lab work from university."

**Q: Can I use this for multiple people?**
Yes, just swap out the `master_resume.docx` file. Or create different folders for each person.

**Q: How do I track all my generated resumes?**
All created Google Docs appear in your Google Drive. They're searchable by the job title you provide.

---

## Support

If you run into issues:
1. Check this guide first
2. Verify all files are in the right place
3. Check Google Cloud Console for API status
4. Review Streamlit logs for error messages

The app is fully functional locally and can be shared/deployed as needed!
