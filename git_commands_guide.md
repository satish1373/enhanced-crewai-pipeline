# Complete Git Commands Guide - From Our Session

This guide covers all the Git commands we used during the enhanced CrewAI pipeline setup and GitHub integration, with explanations of when and how to use each one.

## 🚀 Repository Setup Commands

### `git init`
**What it does:** Initializes a new Git repository in the current directory
**When to use:** Starting a new project or converting an existing project to use Git
```bash
git init
```
**Our usage:** We used this to create a fresh Git repository after removing the problematic history

---

### `git remote add origin <URL>`
**What it does:** Adds a remote repository (usually GitHub) to your local Git repository
**When to use:** Connecting your local repository to a GitHub repository
```bash
# Basic syntax
git remote add origin https://github.com/username/repository.git

# With authentication token (what we used initially - caused problems)
git remote add origin https://satish1373:YOUR_TOKEN@github.com/satish1373/enhanced-crewai-pipeline.git

# Correct approach (without token in URL)
git remote add origin https://github.com/satish1373/enhanced-crewai-pipeline.git
```
**Our usage:** Connected our Replit project to your GitHub repository

---

### `git remote remove origin`
**What it does:** Removes the remote repository connection
**When to use:** When you need to change the remote URL or fix connection issues
```bash
git remote remove origin
```
**Our usage:** We used this to fix the authentication token issue

---

### `git remote -v`
**What it does:** Shows all configured remote repositories
**When to use:** Checking which remote repositories are connected
```bash
git remote -v
```
**Output example:**
```
origin  https://github.com/satish1373/enhanced-crewai-pipeline.git (fetch)
origin  https://github.com/satish1373/enhanced-crewai-pipeline.git (push)
```

---

## 📝 Basic Staging and Committing

### `git status`
**What it does:** Shows the current status of your working directory and staging area
**When to use:** Before making commits, to see what files have changed
```bash
git status
```
**Our usage:** Used frequently to check what files were modified and ready for commit

**Sample output:**
```
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
    modified:   enhanced_main.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
    auto_sync.py
```

---

### `git add .`
**What it does:** Stages all changes in the current directory for commit
**When to use:** When you want to commit all your changes at once
```bash
git add .
```
**Alternatives:**
```bash
git add filename.py          # Stage specific file
git add *.py                 # Stage all Python files
git add enhanced_*.py        # Stage files matching pattern
```
**Our usage:** Used to stage all our pipeline files for commit

---

### `git commit -m "message"`
**What it does:** Creates a commit with the staged changes and a descriptive message
**When to use:** After staging changes, to save a snapshot of your project
```bash
git commit -m "Add enhanced ticket tracking system"
```
**Best practices for commit messages:**
```bash
# Good commit messages
git commit -m "Add automated retry logic for failed tickets"
git commit -m "Fix: Resolve f-string syntax error in JQL generation"
git commit -m "Update: Enhanced language detection patterns"

# Our actual commit messages
git commit -m "Enhanced CrewAI Pipeline - Production Ready"
git commit -m "Remove test file containing sensitive data"
```

---

## 🔄 Synchronization Commands

### `git push origin main`
**What it does:** Uploads your local commits to the remote repository (GitHub)
**When to use:** After committing changes, to backup and share your code
```bash
git push origin main
```
**Variations:**
```bash
git push -u origin main      # Set upstream tracking (first push)
git push -f origin main      # Force push (overwrites remote - dangerous!)
git push                     # Push to tracked branch (after -u is set)
```
**Our usage:** Used to upload our enhanced pipeline to GitHub

---

### `git pull origin main`
**What it does:** Downloads and merges changes from the remote repository
**When to use:** When you want to get the latest changes from GitHub
```bash
git pull origin main
```
**With merge strategies:**
```bash
git pull origin main --allow-unrelated-histories  # Merge unrelated repos
git pull --rebase origin main                     # Use rebase instead of merge
```
**Our usage:** Used to merge GitHub's initial files with our Replit code

---

## 🔧 Configuration Commands

### `git config`
**What it does:** Sets Git configuration options
**When to use:** Setting up your identity or changing Git behavior
```bash
# Set your identity (required for commits)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set merge strategy (we used this to fix merge conflicts)
git config pull.rebase false

# View current configuration
git config --list
```
**Our usage:** Set the merge strategy to resolve the "divergent branches" error

---

## 🗂️ File Management Commands

### `git rm filename`
**What it does:** Removes a file from both the working directory and Git tracking
**When to use:** When you want to delete a file and stop tracking it
```bash
git rm test_github.py
```
**Alternatives:**
```bash
git rm --cached filename     # Remove from Git but keep local file
git rm -r directory/         # Remove directory recursively
```
**Our usage:** Used to remove the problematic test file with the secret

---

### `git reset`
**What it does:** Undoes changes or moves the repository to a previous state
**When to use:** When you need to undo commits or unstage changes
```bash
# Unstage changes (keep modifications)
git reset filename.py
git reset .                  # Unstage all

# Reset to previous commit (keep changes in working directory)
git reset --soft HEAD~1

# Reset to previous commit (discard all changes - dangerous!)
git reset --hard HEAD~1
git reset --hard HEAD~3      # Go back 3 commits
```
**Our usage:** Used to remove commits containing secrets from the repository history

---

## 🔍 Information and History Commands

### `git log`
**What it does:** Shows the commit history
**When to use:** To view past commits and understand project evolution
```bash
git log                      # Full log
git log --oneline           # Compact view
git log --oneline -10       # Last 10 commits only
git log --graph             # Visual branch representation
```
**Our usage:** Used to identify problematic commits and understand repository history

---

### `git show <commit-hash>`
**What it does:** Shows detailed information about a specific commit
**When to use:** To examine what changed in a particular commit
```bash
git show 488f5467e05fce9be032c2901c47d3e07e3a01b9
```
**Our usage:** Used to investigate the commit that contained the secret

---

### `git diff`
**What it does:** Shows differences between files, commits, or branches
**When to use:** To see what has changed before committing
```bash
git diff                     # Changes in working directory
git diff --cached            # Changes in staging area
git diff HEAD~1              # Changes since last commit
git diff --name-only         # Just show filenames that changed
```

---

## 🚨 Emergency and Recovery Commands

### `git clean`
**What it does:** Removes untracked files from the working directory
**When to use:** To clean up temporary files or reset to a clean state
```bash
git clean -f                 # Remove untracked files
git clean -fd                # Remove untracked files and directories
git clean -n                 # Preview what would be deleted (dry run)
```

---

### `git reflog`
**What it does:** Shows a log of all Git operations (even after reset/rebase)
**When to use:** To recover from accidentally deleted commits
```bash
git reflog
```
**Recovery example:**
```bash
git reflog                   # Find the commit you want to recover
git reset --hard HEAD@{2}   # Reset to that point
```

---

### `rm -rf .git`
**What it does:** Completely removes Git history (nuclear option)
**When to use:** Starting completely fresh (what we did to fix the secret issue)
```bash
rm -rf .git
```
**⚠️ Warning:** This deletes ALL Git history permanently!

---

## 🔄 Advanced Workflow Commands

### `git rebase`
**What it does:** Replays commits on top of another base commit
**When to use:** To clean up commit history or resolve conflicts
```bash
git rebase -i HEAD~3         # Interactive rebase of last 3 commits
git rebase main              # Rebase current branch onto main
```

---

### `git merge`
**What it does:** Combines changes from different branches
**When to use:** Integrating feature branches or resolving pull conflicts
```bash
git merge branch-name
git merge --allow-unrelated-histories  # Merge unrelated repositories
```

---

## 📋 Daily Development Workflow

### **Starting a New Feature:**
```bash
git status                   # Check current state
git pull origin main         # Get latest changes
git checkout -b new-feature  # Create new branch (optional)
# ... make your changes ...
git add .                    # Stage changes
git commit -m "Add new feature"
git push origin main         # or push to feature branch
```

### **Daily Sync Routine:**
```bash
git status                   # See what's changed
git add .                    # Stage all changes
git commit -m "Daily progress: describe changes"
git push origin main         # Backup to GitHub
```

### **Checking Project Health:**
```bash
git status                   # Working directory status
git log --oneline -5         # Recent commit history
git remote -v                # Verify GitHub connection
```

---

## 🎯 Command Combinations We Used

### **Fresh Repository Setup:**
```bash
rm -rf .git                  # Nuclear reset
git init                     # Fresh start
git remote add origin https://github.com/username/repo.git
git add .                    # Stage everything
git commit -m "Initial commit"
git push -u origin main -f   # Force push initial setup
```

### **Merge Conflict Resolution:**
```bash
git config pull.rebase false                    # Set merge strategy
git pull origin main --allow-unrelated-histories # Merge GitHub repo
# ... resolve conflicts in files ...
git add .                                        # Stage resolved files
git commit -m "Merge GitHub repository"          # Complete merge
git push origin main                             # Push merged result
```

### **Secret Removal Process:**
```bash
rm test_github.py            # Remove problematic file
git add .                    # Stage the removal
git commit -m "Remove file with sensitive data"
git push origin main         # Attempt push (might fail due to history)
# If fails due to history:
rm -rf .git                  # Nuclear option
git init                     # Start fresh
# ... repeat setup process ...
```

---

## 🛡️ Best Practices from Our Experience

### **Security:**
- ✅ Never commit secrets, tokens, or passwords
- ✅ Use `.gitignore` to exclude sensitive files
- ✅ Use environment variables for secrets
- ❌ Don't put tokens in remote URLs

### **Commit Messages:**
- ✅ Use descriptive, actionable messages
- ✅ Start with a verb: "Add", "Fix", "Update", "Remove"
- ✅ Keep first line under 50 characters
- ✅ Include context about why, not just what

### **Workflow:**
- ✅ `git status` before every commit
- ✅ Small, frequent commits are better than large ones
- ✅ Pull before pushing when collaborating
- ✅ Test your code before committing

### **Emergency Recovery:**
- ✅ `git reflog` can save you from most disasters
- ✅ Force push (`-f`) only when absolutely necessary
- ✅ Always backup important work before major Git operations

---

## 🔧 Troubleshooting Common Issues

### **"Permission denied" errors:**
```bash
# Use personal access token instead of password
# Set up credential helper
git config credential.helper store
```

### **"Divergent branches" errors:**
```bash
git config pull.rebase false
git pull origin main --allow-unrelated-histories
```

### **"Repository rule violations" (secrets detected):**
```bash
# Remove the secret from current files
rm problematic_file.py
# Remove from Git history
git reset --hard HEAD~1  # or use fresh start approach
```

### **"Nothing to commit" when you expect changes:**
```bash
git status               # Check what Git sees
git add .                # Stage everything
git status               # Verify staging worked
```

---

## 📈 Pro Tips

1. **Use aliases for common commands:**
   ```bash
   git config --global alias.s status
   git config --global alias.a "add ."
   git config --global alias.c commit
   git config --global alias.p "push origin main"
   ```

2. **Check before you commit:**
   ```bash
   git status && git diff --cached
   ```

3. **Safe experimentation:**
   ```bash
   git stash                # Save current work
   # ... experiment ...
   git stash pop            # Restore your work
   ```

4. **Quick commit and push:**
   ```bash
   git add . && git commit -m "Quick update" && git push origin main
   ```

---

This guide covers all the Git commands we used to successfully set up your enhanced CrewAI pipeline with GitHub integration. Keep this as a reference for future Git operations! 🚀