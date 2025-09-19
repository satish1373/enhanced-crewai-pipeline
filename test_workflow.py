import os
from github import Github

def test_workflow_operations():
    token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('GITHUB_REPO')
    
    if not token or not repo_name:
        print("ERROR: Environment variables not set")
        return False
    
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        print(f"Connected to: {repo.full_name}")
        
        # Test 1: Create a branch
        main_branch = repo.get_branch("main")
        test_branch = "test-replit-integration"
        
        try:
            repo.create_git_ref(f"refs/heads/{test_branch}", main_branch.commit.sha)
            print(f"Created branch: {test_branch}")
        except Exception as e:
            if "already exists" in str(e):
                print(f"Branch {test_branch} already exists")
            else:
                raise e
        
        # Test 2: Create a file in the branch
        content = """# Test File from Replit
print("Hello from CrewAI pipeline!")

def test_function():
    return "This is a test"

if __name__ == "__main__":
    print(test_function())
"""
        
        try:
            repo.create_file(
                "test_code.py",
                "Add test code from Replit",
                content,
                branch=test_branch
            )
            print("Created test_code.py in branch")
        except Exception as e:
            if "already exists" in str(e):
                # Update existing file
                file = repo.get_contents("test_code.py", ref=test_branch)
                repo.update_file(
                    "test_code.py",
                    "Update test code from Replit", 
                    content,
                    file.sha,
                    branch=test_branch
                )
                print("Updated existing test_code.py")
            else:
                raise e
        
        print("SUCCESS: All GitHub operations working!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_workflow_operations()
