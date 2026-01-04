# Service Call Analysis Web Application

## Overview

This is a single-page web application that displays the analyzed service call transcript with inline annotations, compliance scores, and sales insights.

## Features

- ✅ Side-by-side transcript and analysis view
- ✅ Interactive stage navigation
- ✅ Color-coded compliance indicators
- ✅ Inline annotations with detailed explanations
- ✅ Click annotations for more details
- ✅ Comprehensive sales insights section
- ✅ Responsive design
- ✅ No build tools required - pure HTML/CSS/JS

## Running Locally

### Option 1: Python HTTP Server (Recommended)

From the project root directory:

```bash
python3 -m http.server 8000
```

Then open your browser to: http://localhost:8000/webapp/

### Option 2: Node.js HTTP Server

If you have Node.js installed:

```bash
npx http-server -p 8000
```

Then open: http://localhost:8000/webapp/

### Option 3: VS Code Live Server

If using VS Code:
1. Install the "Live Server" extension
2. Right-click on `webapp/index.html`
3. Select "Open with Live Server"

## Deployment

### GitHub Pages

1. Push your code to GitHub
2. Go to repository Settings → Pages
3. Set source to "main" branch, "/webapp" folder (or root if you move files)
4. Your site will be live at `https://yourusername.github.io/repository-name/`

**Note:** Make sure the path to `annotated_transcript.json` in `app.js` is correct for your deployment.

### Vercel (Recommended)

1. Install Vercel CLI: `npm i -g vercel`
2. From the project root: `vercel`
3. Follow prompts
4. Your site will be live instantly with a URL

### Netlify

1. Go to https://app.netlify.com/drop
2. Drag and drop the entire `webapp` folder
3. Your site is live immediately

### Static Hosting (Cloudflare Pages, AWS S3, etc.)

Simply upload the contents of the `webapp` folder to any static hosting service.

## File Structure

```
webapp/
├── index.html          # Main HTML structure
├── styles.css          # All styling
├── app.js              # Application logic
└── README.md           # This file

data/
└── annotated_transcript.json  # Data file (loaded by app.js)
```

## Customization

### Change Colors

Edit the `:root` CSS variables in `styles.css`:

```css
:root {
    --color-primary: #2563eb;
    --color-success: #10b981;
    --color-warning: #ef4444;
    /* ... */
}
```

### Modify Stages

Edit the `STAGE_CONFIG` object in `app.js`:

```javascript
const STAGE_CONFIG = {
    'introduction': {
        name: 'Introduction',
        icon: '👋',
        color: '#3b82f6'
    },
    // ...
};
```

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile: ✅ Responsive design

## Troubleshooting

### Data not loading

- Ensure you're running a local server (not opening the HTML file directly)
- Check browser console for errors (F12)
- Verify `annotated_transcript.json` exists in the `data/` folder
- Check CORS settings if deploying

### Styling issues

- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check that `styles.css` is loading correctly

### Layout problems on mobile

- The design is responsive but optimized for desktop viewing
- On mobile, the three-column layout stacks vertically

## License

This project is part of a take-home assignment demonstration.


