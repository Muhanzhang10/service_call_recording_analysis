# Deployment Guide

## Deliverables

This project provides a complete service call analysis system with:

1. **Analyzed Transcript** - `data/annotated_transcript.json`
2. **Web Application** - Interactive UI in `/webapp/`
3. **Source Code** - All analysis scripts in `/analysis/`

## 🚀 Running Locally

### Quick Start

```bash
python3 run_webapp.py
```

This will:
- Start a local web server on port 8000
- Automatically open your browser to the web app
- Serve the application with proper CORS headers

### Manual Method

```bash
python3 -m http.server 8000
```

Then navigate to: http://localhost:8000/webapp/

## 🌐 Deployment Options

### Option 1: Vercel (Recommended - Free)

Vercel provides instant static site hosting with global CDN.

**Steps:**

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. From project root:
```bash
vercel
```

3. Follow the prompts:
   - Set root directory to `/webapp`
   - Use default build settings
   - Deploy!

4. Your app will be live at: `https://your-project.vercel.app`

**Pros:**
- Instant deployment
- Free SSL certificate
- Global CDN
- Custom domains supported
- No configuration needed

### Option 2: GitHub Pages (Free)

**Steps:**

1. Create a GitHub repository and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/service-call-analysis.git
git push -u origin main
```

2. Go to repository Settings → Pages
3. Set source to "main" branch
4. Set folder to `/webapp` (or move webapp files to root)
5. Save

Your site will be live at: `https://yourusername.github.io/service-call-analysis/`

**Note:** You may need to adjust the data path in `app.js`:
```javascript
// Change from:
const response = await fetch('../data/annotated_transcript.json');

// To:
const response = await fetch('./annotated_transcript.json');

// And copy annotated_transcript.json to webapp/ folder
```

**Pros:**
- Free
- Easy integration with Git workflow
- Free SSL

**Cons:**
- Requires public repository (or GitHub Pro for private)
- Limited to static sites

### Option 3: Netlify (Free)

**Drag & Drop Method:**

1. Go to https://app.netlify.com/drop
2. Drag the entire `/webapp/` folder into the dropzone
3. Make sure `data/annotated_transcript.json` is accessible

**CLI Method:**

```bash
npm install -g netlify-cli
cd webapp
netlify deploy --prod
```

**Pros:**
- Super easy drag-and-drop
- Free SSL
- Custom domains
- Instant preview URLs

### Option 4: AWS S3 + CloudFront (Advanced)

For production-grade hosting with maximum control.

**Steps:**

1. Create S3 bucket
2. Enable static website hosting
3. Upload `/webapp/` contents
4. Set up CloudFront distribution
5. Configure DNS

**Pros:**
- Highly scalable
- Professional setup
- Full control
- Fast global delivery

**Cons:**
- More complex setup
- Not free (but very cheap for small sites)

### Option 5: Railway (Free Tier)

Good alternative to Vercel with similar features.

```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] `data/annotated_transcript.json` exists and is valid
- [ ] All analysis phases have been run successfully
- [ ] Web app loads correctly locally
- [ ] No console errors in browser (F12)
- [ ] API keys are NOT committed to Git (check `.env` is in `.gitignore`)
- [ ] README.md is up to date
- [ ] File paths in `app.js` are correct for deployment environment

## 🔧 Configuration for Different Environments

### Local Development
```javascript
// app.js - Line ~40
const response = await fetch('../data/annotated_transcript.json');
```

### GitHub Pages (if files in same folder)
```javascript
const response = await fetch('./annotated_transcript.json');
```

### Vercel/Netlify (with original structure)
```javascript
const response = await fetch('../data/annotated_transcript.json');
```

## 🎨 Customization

### Changing Colors

Edit `webapp/styles.css`:
```css
:root {
    --color-primary: #2563eb;  /* Main brand color */
    --color-success: #10b981;  /* Success/compliant */
    --color-warning: #ef4444;  /* Warnings/issues */
    /* ... */
}
```

### Adding Company Logo

Edit `webapp/index.html` header section:
```html
<header class="header">
    <div class="container">
        <img src="logo.png" alt="Company Logo" style="height: 40px;">
        <h1>Service Call Recording Analysis</h1>
        ...
    </div>
</header>
```

## 🐛 Troubleshooting

### Issue: Data not loading

**Cause:** CORS restrictions or incorrect path

**Solution:**
- Always use a web server (not file:// protocol)
- Check browser console for errors
- Verify path to JSON file is correct

### Issue: Blank page

**Cause:** JavaScript error

**Solution:**
- Open browser console (F12)
- Check for error messages
- Verify `annotated_transcript.json` is valid JSON

### Issue: Styling looks wrong

**Cause:** CSS not loading

**Solution:**
- Verify `styles.css` is in same folder as `index.html`
- Check for typos in `<link>` tag
- Clear browser cache

## 📊 Performance

The web app is highly optimized:
- No build step required
- No external dependencies
- Single JSON file load
- Vanilla JavaScript (no frameworks)
- CSS variables for theming
- Mobile responsive

**Expected Load Time:** < 1 second on modern connections

**Data Size:** ~400-600KB for typical analysis (including all annotations)

## 🔒 Security Considerations

- Never commit API keys (`.env` should be in `.gitignore`)
- The web app is read-only (no data submission)
- No external API calls from frontend
- Safe to deploy publicly

## 📞 Support

For issues or questions about deployment:
1. Check browser console for errors
2. Verify all files are uploaded correctly
3. Test locally first
4. Check deployment platform's documentation

## 🎉 Success!

Once deployed, share your URL with reviewers. They'll be able to:
- View the complete transcript with annotations
- Navigate between call stages
- See compliance scores and analysis
- Review sales insights
- Click annotations for detailed explanations

The web app provides a professional, intuitive interface for reviewing the service call analysis.

