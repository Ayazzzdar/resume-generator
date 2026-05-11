# Quick Start Checklist ✓

Use this checklist to get your resume generator running in 15 minutes.

## ☐ Step 1: Prepare Your Master Resume (5 min)

1. Create or update your comprehensive resume with ALL experience
2. Save as `master_resume.docx`
3. Place in the same folder as `resume_generator.py`
4. See `master_resume_template.docx` for format reference

**Tip:** Include everything - Claude will pick what's relevant for each job.

---

## ☐ Step 2: Set Up Google Cloud (5 min - one time only)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project: "Resume Generator"
3. Enable APIs:
   - Google Docs API
   - Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`
6. Move `credentials.json` to app folder

**Detailed instructions:** See `GOOGLE_SETUP_GUIDE.md`

---

## ☐ Step 3: Get Anthropic API Key (2 min)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / Log in
3. Navigate to "API Keys"
4. Create new key
5. Copy it (you'll paste it in the app)

**Cost:** ~$0.10-0.30 per resume

---

## ☐ Step 4: Install & Run (3 min)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run resume_generator.py
```

**First run only:** Browser will open for Google authentication

---

## ☐ Step 5: Generate Your First Resume! (2 min)

1. Paste Anthropic API key in sidebar
2. Enter job posting URL (or paste description)
3. Add context (optional): "Emphasize X" or "Transitioning from Y to Z"
4. Click "Generate Tailored Resume"
5. Get Google Doc link - edit directly!

---

## Your Folder Should Look Like This:

```
resume-generator/
├── resume_generator.py          ✓ Main app
├── requirements.txt             ✓ Dependencies
├── master_resume.docx          ✓ YOUR comprehensive resume
├── credentials.json            ✓ From Google Cloud Console
├── GOOGLE_SETUP_GUIDE.md       ✓ Detailed setup instructions
├── QUICK_START.md              ✓ This file
└── master_resume_template.docx ✓ Example format
```

After first run, you'll also see:
```
├── token.pickle                 ✓ Auto-generated (keeps you logged in)
```

---

## Common Issues & Fixes

### "Master resume not found"
→ Make sure the file is named exactly `master_resume.docx` and in the same folder

### "Google credentials not found"  
→ Download `credentials.json` from Google Cloud Console and place in app folder

### "Authentication failed"
→ Delete `token.pickle` and run again - browser will open for re-authentication

### "Job scraping failed"
→ Use the "paste directly" option instead of URL

### "API Key Invalid"
→ Get a fresh key from console.anthropic.com - make sure you have billing set up

---

## Test It Out

### Good First Test Job:
Any recent LinkedIn job posting in your field. Example searches:
- "performance marketing manager Sydney"  
- "e-commerce consultant remote"
- "paid media specialist"

### What to Look For:
✓ Keywords from job appear naturally in your resume
✓ Most relevant experience is highlighted first  
✓ Achievements are quantified  
✓ Skills match the job requirements
✓ Google Doc is editable

---

## Next Steps

Once it's working:

### For Personal Use:
- Generate resumes for all your job applications
- Keep a folder in Google Drive with all versions
- Edit directly in Google Docs before submitting

### For Paula's Job Search:
- Save her master resume as `master_resume.docx`
- Focus context on QA → Lab transition
- Example: "Transitioning from pharmaceutical QA to laboratory roles. Emphasize analytical skills, lab equipment experience, attention to detail, and hands-on work. Highlight university lab work and technical competencies."

### To Share with Clients:
- Deploy to Streamlit Cloud (free)
- Or run locally and generate resumes for them
- Charge $20-50 per tailored resume as a service

### To Automate Further:
- Build email alerts for new jobs
- Auto-generate resumes for saved searches
- Integrate with LinkedIn Easy Apply

---

## Pro Tips

**Master Resume Best Practices:**
- Include metrics everywhere (%, $, numbers)
- Use action verbs (Developed, Managed, Achieved)
- Don't worry about length - Claude will trim
- Update after each project/role

**Context Examples:**
- "Emphasize leadership and team management"
- "Focus on remote work experience"  
- "Highlight technical skills over soft skills"
- "Downplay career gap, emphasize recent projects"

**For Best Results:**
- Be specific in job title field ("Senior PM at Google" not just "PM")
- Use the job analysis preview to verify Claude understood the role
- Make final edits directly in Google Doc
- Download as PDF from Google Docs when submitting

---

## Cost Tracking

Keep an eye on your usage:
- **Anthropic API:** Check dashboard at console.anthropic.com
- Each resume costs ~$0.10-0.30
- Set spending limits if desired

Example: 50 resumes = $5-15 total

---

## You're Ready! 🚀

Everything you need is in this folder. The app does the heavy lifting - you just provide:
1. Job URL/description
2. Optional context
3. Your Anthropic API key (in the app)

The rest is automatic. Good luck with the job search!

---

## Questions?

Check the guides:
- **Full setup:** `GOOGLE_SETUP_GUIDE.md`
- **Google API issues:** `GOOGLE_SETUP_GUIDE.md` → Troubleshooting section
- **Customization:** `GOOGLE_SETUP_GUIDE.md` → Customization Ideas section
