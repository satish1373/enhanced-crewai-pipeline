#!/usr/bin/env python3
"""
Enhanced Code Storage and Management System
Stores, organizes, and manages AI-generated code solutions
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import zipfile

class CodeStorageManager:
    """Manages storage and organization of AI-generated code"""
    
    def __init__(self, base_storage_path: str = "generated_solutions"):
        self.base_path = Path(base_storage_path)
        self.solutions_path = self.base_path / "solutions"
        self.metadata_path = self.base_path / "metadata"
        self.archives_path = self.base_path / "archives"
        self.templates_path = self.base_path / "templates"
        
        # Create directory structure
        self._setup_storage_structure()
        
        # Initialize metadata tracking
        self.solution_index = self._load_solution_index()
        
    def _setup_storage_structure(self):
        """Create the organized directory structure"""
        directories = [
            self.solutions_path,
            self.metadata_path, 
            self.archives_path,
            self.templates_path,
            self.solutions_path / "python",
            self.solutions_path / "javascript", 
            self.solutions_path / "java",
            self.solutions_path / "php",
            self.solutions_path / "general",
            self.solutions_path / "testing",
            self.solutions_path / "documentation",
            self.solutions_path / "configuration"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"📁 Storage structure created at: {self.base_path}")
    
    def store_solution(self, ticket_key: str, solution_data: Dict[str, Any]) -> Dict[str, str]:
        """Store a complete solution with metadata and file organization"""
        
        # Extract solution components
        language = solution_data.get('language', 'general').lower()
        domain = solution_data.get('domain', 'general').lower()
        solution_content = solution_data.get('content', '')
        ticket_title = solution_data.get('title', ticket_key)
        
        # Create solution directory
        solution_id = self._generate_solution_id(ticket_key)
        solution_dir = self.solutions_path / language / solution_id
        solution_dir.mkdir(parents=True, exist_ok=True)
        
        # Store files
        stored_files = {}
        
        # 1. Main solution file
        main_file = self._store_main_solution(solution_dir, solution_content, language)
        stored_files['main_solution'] = str(main_file)
        
        # 2. Extract and store code components
        code_files = self._extract_code_components(solution_dir, solution_content, language)
        stored_files.update(code_files)
        
        # 3. Store metadata
        metadata_file = self._store_solution_metadata(solution_dir, ticket_key, solution_data)
        stored_files['metadata'] = str(metadata_file)
        
        # 4. Create README
        readme_file = self._create_solution_readme(solution_dir, ticket_key, solution_data)
        stored_files['readme'] = str(readme_file)
        
        # 5. Update solution index
        self._update_solution_index(solution_id, ticket_key, solution_data, stored_files)
        
        print(f"💾 Solution stored: {solution_id}")
        print(f"   Location: {solution_dir}")
        print(f"   Files: {len(stored_files)}")
        
        return {
            'solution_id': solution_id,
            'storage_path': str(solution_dir),
            'files': stored_files
        }
    
    def _generate_solution_id(self, ticket_key: str) -> str:
        """Generate unique solution ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{ticket_key}_{timestamp}"
    
    def _store_main_solution(self, solution_dir: Path, content: str, language: str) -> Path:
        """Store the main solution content"""
        
        # Determine file extension
        extensions = {
            'python': '.py',
            'javascript': '.js', 
            'java': '.java',
            'php': '.php',
            'ruby': '.rb',
            'go': '.go',
            'rust': '.rs',
            'general': '.txt'
        }
        
        extension = extensions.get(language, '.txt')
        main_file = solution_dir / f"solution{extension}"
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return main_file
    
    def _extract_code_components(self, solution_dir: Path, content: str, language: str) -> Dict[str, str]:
        """Extract individual code components from solution"""
        stored_files = {}
        
        # Look for code blocks in markdown format
        import re
        
        # Extract code blocks with language specification
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        code_blocks = re.findall(code_block_pattern, content, re.DOTALL)
        
        for i, (block_language, code) in enumerate(code_blocks):
            if code.strip():
                # Determine filename based on content or language
                filename = self._determine_filename(code, block_language or language, i)
                file_path = solution_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code.strip())
                
                stored_files[f'code_block_{i}'] = str(file_path)
        
        # Extract specific file types if mentioned
        file_patterns = {
            'requirements.txt': r'requirements\.txt[:\n](.*?)(?=\n\n|\n#|\Z)',
            'package.json': r'package\.json[:\n](.*?)(?=\n\n|\n#|\Z)',
            'Dockerfile': r'Dockerfile[:\n](.*?)(?=\n\n|\n#|\Z)',
            '.env.example': r'\.env\.example[:\n](.*?)(?=\n\n|\n#|\Z)'
        }
        
        for filename, pattern in file_patterns.items():
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                file_path = solution_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(matches[0].strip())
                stored_files[filename] = str(file_path)
        
        return stored_files
    
    def _determine_filename(self, code: str, language: str, index: int) -> str:
        """Determine appropriate filename for code block"""
        
        # Check for specific patterns in code
        if 'def test_' in code or 'import unittest' in code:
            return f"test_{index}.py"
        elif 'class ' in code and language == 'python':
            # Extract class name
            import re
            class_match = re.search(r'class (\w+)', code)
            if class_match:
                return f"{class_match.group(1).lower()}.py"
        elif 'function ' in code and language == 'javascript':
            return f"functions_{index}.js"
        elif 'public class' in code and language == 'java':
            # Extract class name
            import re
            class_match = re.search(r'public class (\w+)', code)
            if class_match:
                return f"{class_match.group(1)}.java"
        
        # Default naming
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'java': '.java', 
            'php': '.php',
            'html': '.html',
            'css': '.css',
            'sql': '.sql'
        }
        
        extension = extensions.get(language, '.txt')
        return f"component_{index}{extension}"
    
    def _store_solution_metadata(self, solution_dir: Path, ticket_key: str, solution_data: Dict) -> Path:
        """Store comprehensive metadata about the solution"""
        
        metadata = {
            'ticket_key': ticket_key,
            'solution_id': solution_dir.name,
            'created_at': datetime.now().isoformat(),
            'language': solution_data.get('language', 'unknown'),
            'domain': solution_data.get('domain', 'general'),
            'title': solution_data.get('title', ticket_key),
            'description': solution_data.get('description', ''),
            'agent_used': solution_data.get('agent', 'unknown'),
            'processing_time': solution_data.get('processing_time', 0),
            'content_hash': hashlib.md5(solution_data.get('content', '').encode()).hexdigest(),
            'tags': solution_data.get('tags', []),
            'complexity': solution_data.get('complexity', 'medium'),
            'status': 'stored',
            'reusable_components': self._identify_reusable_components(solution_data.get('content', '')),
            'dependencies': self._extract_dependencies(solution_data.get('content', ''))
        }
        
        metadata_file = solution_dir / 'metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata_file
    
    def _create_solution_readme(self, solution_dir: Path, ticket_key: str, solution_data: Dict) -> Path:
        """Create a README file for the solution"""
        
        readme_content = f"""# Solution for {ticket_key}

## Overview
**Title:** {solution_data.get('title', ticket_key)}
**Language:** {solution_data.get('language', 'Unknown')}
**Domain:** {solution_data.get('domain', 'General')}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Description
{solution_data.get('description', 'AI-generated solution for ticket requirements.')}

## Files in this Solution
"""
        
        # List all files in the directory
        for file_path in solution_dir.glob('*'):
            if file_path.is_file() and file_path.name != 'README.md':
                readme_content += f"- **{file_path.name}** - {self._get_file_description(file_path)}\n"
        
        readme_content += f"""
## Usage Instructions
1. Review the main solution file
2. Check dependencies in requirements/package files
3. Follow any setup instructions in the solution
4. Test thoroughly before production use

## Dependencies
{self._format_dependencies(solution_data.get('content', ''))}

## Tags
{', '.join(solution_data.get('tags', ['ai-generated']))}

---
*Generated by Enhanced CrewAI Pipeline*
*Solution ID: {solution_dir.name}*
"""
        
        readme_file = solution_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return readme_file
    
    def _get_file_description(self, file_path: Path) -> str:
        """Get description for a file based on its name and content"""
        descriptions = {
            'solution.py': 'Main Python solution',
            'solution.js': 'Main JavaScript solution', 
            'solution.java': 'Main Java solution',
            'test_': 'Test file',
            'requirements.txt': 'Python dependencies',
            'package.json': 'Node.js dependencies',
            'Dockerfile': 'Docker configuration',
            'metadata.json': 'Solution metadata'
        }
        
        for pattern, description in descriptions.items():
            if pattern in file_path.name:
                return description
        
        return 'Generated code component'
    
    def _identify_reusable_components(self, content: str) -> List[str]:
        """Identify reusable components in the solution"""
        components = []
        
        # Look for common reusable patterns
        patterns = {
            'utility_functions': r'def (\w+_helper|\w+_util)',
            'database_models': r'class (\w+Model|\w+Entity)',
            'api_endpoints': r'@app\.route|@router\.',
            'configuration_classes': r'class (\w+Config|\w+Settings)',
            'validators': r'def validate_\w+',
            'decorators': r'def \w+_decorator'
        }
        
        for component_type, pattern in patterns.items():
            import re
            if re.search(pattern, content):
                components.append(component_type)
        
        return components
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from solution content"""
        dependencies = []
        
        # Python imports
        import re
        python_imports = re.findall(r'import (\w+)|from (\w+)', content)
        for imp in python_imports:
            dep = imp[0] if imp[0] else imp[1]
            if dep and dep not in ['os', 'sys', 'json', 'time', 'datetime']:  # Skip built-ins
                dependencies.append(f"python:{dep}")
        
        # JavaScript requires/imports
        js_imports = re.findall(r'require\([\'"](\w+)[\'"]\)|import .* from [\'"](\w+)[\'"]', content)
        for imp in js_imports:
            dep = imp[0] if imp[0] else imp[1] 
            if dep:
                dependencies.append(f"javascript:{dep}")
        
        return list(set(dependencies))  # Remove duplicates
    
    def _format_dependencies(self, content: str) -> str:
        """Format dependencies for README"""
        deps = self._extract_dependencies(content)
        if not deps:
            return "No external dependencies detected"
        
        formatted = []
        python_deps = [d.split(':')[1] for d in deps if d.startswith('python:')]
        js_deps = [d.split(':')[1] for d in deps if d.startswith('javascript:')]
        
        if python_deps:
            formatted.append(f"**Python:** {', '.join(python_deps)}")
        if js_deps:
            formatted.append(f"**JavaScript:** {', '.join(js_deps)}")
        
        return '\n'.join(formatted)
    
    def _load_solution_index(self) -> Dict:
        """Load the solution index for quick searching"""
        index_file = self.metadata_path / 'solution_index.json'
        if index_file.exists():
            with open(index_file, 'r') as f:
                return json.load(f)
        return {'solutions': {}, 'last_updated': None}
    
    def _update_solution_index(self, solution_id: str, ticket_key: str, solution_data: Dict, files: Dict):
        """Update the searchable solution index"""
        self.solution_index['solutions'][solution_id] = {
            'ticket_key': ticket_key,
            'title': solution_data.get('title', ticket_key),
            'language': solution_data.get('language', 'unknown'),
            'domain': solution_data.get('domain', 'general'),
            'created_at': datetime.now().isoformat(),
            'tags': solution_data.get('tags', []),
            'file_count': len(files),
            'reusable': len(self._identify_reusable_components(solution_data.get('content', ''))) > 0
        }
        
        self.solution_index['last_updated'] = datetime.now().isoformat()
        
        # Save index
        index_file = self.metadata_path / 'solution_index.json'
        with open(index_file, 'w') as f:
            json.dump(self.solution_index, f, indent=2)
    
    def search_solutions(self, query: str = None, language: str = None, 
                        domain: str = None, tags: List[str] = None) -> List[Dict]:
        """Search stored solutions"""
        results = []
        
        for solution_id, metadata in self.solution_index['solutions'].items():
            match = True
            
            # Text search in title and ticket key
            if query:
                search_text = f"{metadata['title']} {metadata['ticket_key']}".lower()
                if query.lower() not in search_text:
                    match = False
            
            # Language filter
            if language and metadata['language'].lower() != language.lower():
                match = False
            
            # Domain filter  
            if domain and metadata['domain'].lower() != domain.lower():
                match = False
            
            # Tags filter
            if tags:
                solution_tags = [tag.lower() for tag in metadata.get('tags', [])]
                if not any(tag.lower() in solution_tags for tag in tags):
                    match = False
            
            if match:
                # Add full path info
                language_dir = metadata['language'].lower()
                solution_path = self.solutions_path / language_dir / solution_id
                metadata['solution_path'] = str(solution_path)
                metadata['solution_id'] = solution_id
                results.append(metadata)
        
        # Sort by creation date (newest first)
        results.sort(key=lambda x: x['created_at'], reverse=True)
        return results
    
    def get_solution(self, solution_id: str) -> Dict[str, Any]:
        """Get complete solution data"""
        if solution_id not in self.solution_index['solutions']:
            raise ValueError(f"Solution {solution_id} not found")
        
        metadata = self.solution_index['solutions'][solution_id]
        language_dir = metadata['language'].lower()
        solution_path = self.solutions_path / language_dir / solution_id
        
        if not solution_path.exists():
            raise FileNotFoundError(f"Solution directory not found: {solution_path}")
        
        # Load full metadata
        metadata_file = solution_path / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                full_metadata = json.load(f)
        else:
            full_metadata = metadata
        
        # List all files
        files = {}
        for file_path in solution_path.glob('*'):
            if file_path.is_file():
                files[file_path.name] = str(file_path)
        
        return {
            'metadata': full_metadata,
            'solution_path': str(solution_path),
            'files': files
        }
    
    def create_solution_archive(self, solution_ids: List[str], archive_name: str) -> str:
        """Create a zip archive of selected solutions"""
        archive_path = self.archives_path / f"{archive_name}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for solution_id in solution_ids:
                try:
                    solution = self.get_solution(solution_id)
                    solution_path = Path(solution['solution_path'])
                    
                    # Add all files from the solution
                    for file_path in solution_path.rglob('*'):
                        if file_path.is_file():
                            arcname = f"{solution_id}/{file_path.relative_to(solution_path)}"
                            zipf.write(file_path, arcname)
                            
                except Exception as e:
                    print(f"⚠️  Error adding solution {solution_id} to archive: {e}")
        
        print(f"📦 Archive created: {archive_path}")
        return str(archive_path)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            'total_solutions': len(self.solution_index['solutions']),
            'by_language': {},
            'by_domain': {},
            'total_size_mb': 0,
            'reusable_solutions': 0
        }
        
        # Calculate stats from index
        for metadata in self.solution_index['solutions'].values():
            # By language
            lang = metadata['language']
            stats['by_language'][lang] = stats['by_language'].get(lang, 0) + 1
            
            # By domain
            domain = metadata['domain']
            stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
            
            # Reusable count
            if metadata.get('reusable', False):
                stats['reusable_solutions'] += 1
        
        # Calculate total size
        try:
            def get_dir_size(path):
                total = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        total += os.path.getsize(filepath)
                return total
            
            total_bytes = get_dir_size(self.base_path)
            stats['total_size_mb'] = round(total_bytes / (1024 * 1024), 2)
        except:
            stats['total_size_mb'] = 0
        
        return stats


def integrate_with_enhanced_main():
    """Integration code for enhanced_main.py"""
    integration_code = '''
# Add this to your enhanced_main.py imports
from code_storage_system import CodeStorageManager

# Initialize storage manager (add after other initializations)
code_storage = CodeStorageManager("generated_solutions")

# Modify your process_single_ticket function to store solutions
def process_single_ticket(ticket):
    """Enhanced single ticket processing with comprehensive storage"""
    ticket_key = ticket.key
    
    try:
        # Mark as processing started
        smart_processor.mark_processing_start(ticket_key)
        
        # Extract ticket information
        title = ticket.fields.summary
        description = ticket.fields.description or "No description provided"
        
        # Detect language and domain
        detected_info = smart_processor.detect_language_and_domain(
            title + " " + description
        )
        
        print(f"🔄 Processing {ticket_key}: {title}")
        print(f"📊 Detected: {detected_info['language']} | {detected_info['domain']}")
        
        # Process with CrewAI (your existing logic)
        start_time = time.time()
        result = process_with_crew_ai(ticket, detected_info)  # Your existing function
        processing_time = time.time() - start_time
        
        if result['success']:
            # ENHANCED: Store the complete solution
            solution_data = {
                'content': result.get('output', ''),
                'language': detected_info['language'],
                'domain': detected_info['domain'],
                'title': title,
                'description': description,
                'agent': result.get('agent_used', 'unknown'),
                'processing_time': processing_time,
                'tags': [detected_info['language'], detected_info['domain'], 'ai-generated'],
                'complexity': 'medium'  # You can enhance this detection
            }
            
            # Store solution with organized file structure
            storage_result = code_storage.store_solution(ticket_key, solution_data)
            
            # Mark as successfully completed (existing logic)
            smart_processor.mark_processing_complete(
                ticket_key, 
                result.get('output', ''),
                detected_info
            )
            
            # Enhanced JIRA comment with storage info
            comment = f"""
✅ **Automated Processing Complete**

**Language Detected:** {detected_info['language']}
**Domain:** {detected_info['domain']}
**Processing Time:** {processing_time:.2f}s

**Solution Stored:**
- **Solution ID:** {storage_result['solution_id']}
- **Storage Path:** {storage_result['storage_path']}
- **Files Generated:** {len(storage_result['files'])}

**Quick Access:**
View complete solution at: `{storage_result['storage_path']}`

**Solution Preview:**
{result.get('output', '')[:500]}{'...' if len(result.get('output', '')) > 500 else ''}

---
*Processed by Enhanced CrewAI Pipeline with Code Storage*
            """
            
            jira.add_comment(ticket, comment)
            
            print(f"✅ Solution stored with ID: {storage_result['solution_id']}")
            
            return {
                "success": True, 
                "ticket": ticket_key, 
                "result": result,
                "storage": storage_result
            }
        else:
            # Handle failures (existing logic)
            smart_processor.mark_processing_failed(
                ticket_key, 
                result.get('error', 'Unknown error'),
                detected_info
            )
            return {"success": False, "ticket": ticket_key, "error": result.get('error')}
            
    except Exception as e:
        # Handle exceptions (existing logic) 
        smart_processor.mark_processing_failed(
            ticket_key, 
            str(e),
            detected_info if 'detected_info' in locals() else {}
        )
        print(f"❌ Error processing {ticket_key}: {e}")
        return {"success": False, "ticket": ticket_key, "error": str(e)}
'''
    
    return integration_code

# Example usage and testing
if __name__ == "__main__":
    # Initialize storage manager
    storage = CodeStorageManager()
    
    # Example: Store a solution
    sample_solution = {
        'content': '''
# Python Flask API Example
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    # Implementation here
    return jsonify([])

@app.route('/api/users', methods=['POST'])  
def create_user():
    """Create new user"""
    data = request.get_json()
    # Validation and creation logic
    return jsonify({'status': 'created'})

if __name__ == '__main__':
    app.run(debug=True)

# requirements.txt
flask>=2.0.0
flask-sqlalchemy>=3.0.0

# test_api.py
import unittest
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
    
    def test_get_users(self):
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        ''',
        'language': 'Python',
        'domain': 'Web Development',
        'title': 'Create REST API for User Management',
        'description': 'Build a Flask API with user CRUD operations',
        'agent': 'Python Development Agent',
        'processing_time': 45.2,
        'tags': ['python', 'flask', 'api', 'rest'],
        'complexity': 'medium'
    }
    
    # Store the solution
    result = storage.store_solution('TEST-123', sample_solution)
    print(f"✅ Sample solution stored: {result['solution_id']}")
    
    # Search solutions
    print("\n🔍 Search Results:")
    results = storage.search_solutions(language='Python')
    for solution in results:
        print(f"   {solution['solution_id']}: {solution['title']}")
    
    # Get storage stats
    print(f"\n📊 Storage Statistics:")
    stats = storage.get_storage_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n💡 Integration code available via integrate_with_enhanced_main()")
