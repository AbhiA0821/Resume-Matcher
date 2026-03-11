# How to Add This Project to GitHub

## Step 1 — Create GitHub Account
Go to https://github.com and create a free account if you don't have one.

## Step 2 — Install Git
Download Git from https://git-scm.com/downloads
After installing, check in terminal:
```
git --version
```

## Step 3 — Configure Git (One Time Setup)
Open terminal in VS Code and run:
```
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## Step 4 — Create New Repository on GitHub
- Go to github.com
- Click the "+" button (top right)
- Click "New repository"
- Name it: resume-matcher
- Keep it Public
- Do NOT check "Add README"
- Click "Create repository"

## Step 5 — Initialize Git in Your Project
Open terminal in VS Code inside Resume Matcher folder and run these commands ONE BY ONE:

```
git init
git add .
git commit -m "Initial commit - AI Resume Job Matcher"
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/resume-matcher.git
git push -u origin main
```

Replace YOURUSERNAME with your actual GitHub username.

## Step 6 — Create .gitignore File
Before pushing, create a .gitignore file in your project to avoid pushing unnecessary files.
Add this content:

```
__pycache__/
*.pkl
*.pyc
data/resume_matcher.db
models/
.env
```

This keeps your repo clean.

## Step 7 — Your Project is Now on GitHub!
Go to https://github.com/YOURUSERNAME/resume-matcher to see your project live.

## How to Update GitHub After Changes
Whenever you make changes to your code:
```
git add .
git commit -m "describe your changes here"
git push
```

That's it!
