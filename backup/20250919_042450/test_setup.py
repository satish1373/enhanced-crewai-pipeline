"""
Test script to verify all components are working
Run this before starting the main pipeline
"""

import os
import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import crewai
        import openai
        import github
        import requests
        import jira
        print("✅ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("\nTesting environment variables...")
    required_vars = [
        "OPENAI_API_KEY", "GITHUB_TOKEN", "GITHUB_REPO",
        "JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
        else:
            print(f"✅ {var}: Set")
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("Please set these in Replit Secrets tab")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI connection...")
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ OpenAI API connection successful")
            return True
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

def test_github_connection():
    """Test GitHub API connection"""
    print("\nTesting GitHub connection...")
    try:
        from github import Github
        g = Github(os.getenv("GITHUB_TOKEN"))
        repo = g.get_repo(os.getenv("GITHUB_REPO"))
        print(f"✅ GitHub connection successful - Repository: {repo.full_name}")
        return True
    except Exception as e:
        print(f"❌ GitHub API error: {e}")
        print("Check GITHUB_TOKEN and GITHUB_REPO variables")
        return False

def test_jira_connection():
    """Test Jira API connection"""
    print("\nTesting Jira connection...")
    try:
        from jira import JIRA
        jira_options = {"server": f"https://{os.getenv('JIRA_HOST')}"}
        jira_client = JIRA(
            options=jira_options,
            basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
        )
        
        projects = jira_client.projects()
        project_keys = [p.key for p in projects]
        
        if os.getenv("JIRA_PROJECT_KEY") in project_keys:
            print(f"✅ Jira connection successful - Project found: {os.getenv('JIRA_PROJECT_KEY')}")
            return True
        else:
            print(f"❌ Project {os.getenv('JIRA_PROJECT_KEY')} not found")
            print(f"Available projects: {', '.join(project_keys)}")
            return False
            
    except Exception as e:
        print(f"❌ Jira API error: {e}")
        print("Check JIRA_HOST, JIRA_EMAIL, and JIRA_API_TOKEN variables")
        return False

def test_optional_notifications():
    """Test optional notification settings"""
    print("\nTesting optional notifications...")
    
    # Test Slack webhook
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_url:
        try:
            import requests
            response = requests.post(slack_url, json={"text": "CrewAI pipeline test"}, timeout=5)
            if response.status_code == 200:
                print("✅ Slack webhook test successful")
            else:
                print(f"⚠️ Slack webhook returned status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Slack webhook error: {e}")
    else:
        print("⚠️ SLACK_WEBHOOK_URL not set - Slack notifications disabled")
    
    # Test email settings
    email_vars = ["EMAIL_HOST", "EMAIL_USER", "EMAIL_PASS", "EMAIL_TO"]
    email_set = all(os.getenv(var) for var in email_vars)
    
    if email_set:
        print("✅ Email configuration detected")
        # Note: We don't test actual email sending to avoid spam
    else:
        print("⚠️ Email variables not fully set - Email notifications disabled")

def test_file_permissions():
    """Test file write permissions"""
    print("\nTesting file permissions...")
    try:
        # Test creating required files
        test_files = ["processed_tickets.json", "workflow_summary.json", "pipeline.log"]
        
        for filename in test_files:
            with open(filename, "w") as f:
                f.write("{}")
            print(f"✅ Can write to {filename}")
        
        return True
    except Exception as e:
        print(f"❌ File permission error: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("=" * 50)
    print("CREWAI PIPELINE SETUP TEST")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("OpenAI Connection", test_openai_connection),
        ("GitHub Connection", test_github_connection),
        ("Jira Connection", test_jira_connection),
        ("File Permissions", test_file_permissions),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Test optional notifications (doesn't affect overall result)
    test_optional_notifications()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You can now run the main pipeline.")
        print("Execute: python main.py")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix the issues above before running the pipeline.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()