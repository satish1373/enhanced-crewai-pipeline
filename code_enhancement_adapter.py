#!/usr/bin/env python3
"""
Code Enhancement Adapter for Existing Applications
Extends the enhanced CrewAI pipeline to analyze and improve existing codebases
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enhanced_ticket_tracking import SmartTicketProcessor, EnhancedTicketTracker

class CodeAnalyzer:
    """Analyzes existing code and identifies enhancement opportunities"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analysis_results = {}
        
        # Enhancement patterns to look for
        self.enhancement_patterns = {
            'performance': [
                'nested loops', 'inefficient queries', 'redundant calculations',
                'memory leaks', 'blocking operations', 'unoptimized algorithms'
            ],
            'security': [
                'hardcoded credentials', 'sql injection vulnerabilities', 
                'cross-site scripting', 'insecure file operations', 'weak encryption'
            ],
            'maintainability': [
                'duplicate code', 'large functions', 'complex conditionals',
                'missing documentation', 'unclear variable names', 'tight coupling'
            ],
            'modernization': [
                'deprecated functions', 'outdated libraries', 'legacy patterns',
                'missing type hints', 'old syntax', 'compatibility issues'
            ],
            'testing': [
                'missing unit tests', 'low test coverage', 'untested edge cases',
                'missing integration tests', 'manual testing only'
            ],
            'documentation': [
                'missing docstrings', 'outdated comments', 'missing readme',
                'unclear api documentation', 'missing examples'
            ]
        }
    
    def scan_codebase(self) -> Dict[str, Any]:
        """Scan the codebase and identify enhancement opportunities"""
        print(f"🔍 Scanning codebase: {self.project_path}")
        
        analysis = {
            'project_info': self._get_project_info(),
            'file_analysis': self._analyze_files(),
            'enhancement_opportunities': self._identify_enhancements(),
            'priority_recommendations': self._prioritize_enhancements(),
            'scan_timestamp': datetime.now().isoformat()
        }
        
        self.analysis_results = analysis
        return analysis
    
    def _get_project_info(self) -> Dict[str, Any]:
        """Get basic project information"""
        info = {
            'project_path': str(self.project_path),
            'total_files': 0,
            'languages': {},
            'file_types': {},
            'size_mb': 0
        }
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                info['total_files'] += 1
                
                # Count by language
                extension = file_path.suffix.lower()
                language = self._get_language_from_extension(extension)
                info['languages'][language] = info['languages'].get(language, 0) + 1
                
                # Count by file type
                info['file_types'][extension] = info['file_types'].get(extension, 0) + 1
                
                # Add to total size
                try:
                    info['size_mb'] += file_path.stat().st_size / (1024 * 1024)
                except:
                    pass
        
        info['size_mb'] = round(info['size_mb'], 2)
        return info
    
    def _analyze_files(self) -> List[Dict[str, Any]]:
        """Analyze individual files for enhancement opportunities"""
        file_analyses = []
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                if self._is_code_file(file_path):
                    analysis = self._analyze_single_file(file_path)
                    if analysis['issues_found'] > 0:
                        file_analyses.append(analysis)
        
        return sorted(file_analyses, key=lambda x: x['priority_score'], reverse=True)
    
    def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for enhancement opportunities"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return {'file_path': str(file_path), 'error': 'Could not read file', 'issues_found': 0}
        
        lines = content.split('\n')
        issues = []
        
        # Analyze content for various patterns
        issues.extend(self._check_performance_issues(content, lines))
        issues.extend(self._check_security_issues(content, lines))
        issues.extend(self._check_maintainability_issues(content, lines))
        issues.extend(self._check_modernization_opportunities(content, lines))
        issues.extend(self._check_testing_gaps(file_path, content))
        issues.extend(self._check_documentation_issues(content, lines))
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(issues)
        
        return {
            'file_path': str(file_path.relative_to(self.project_path)),
            'language': self._get_language_from_extension(file_path.suffix),
            'lines_of_code': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'total_lines': len(lines),
            'issues_found': len(issues),
            'issues': issues,
            'priority_score': priority_score,
            'enhancement_categories': list(set(issue['category'] for issue in issues))
        }
    
    def _check_performance_issues(self, content: str, lines: List[str]) -> List[Dict]:
        """Check for performance-related issues"""
        issues = []
        
        # Check for nested loops
        loop_depth = 0
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in ['for ', 'while ']):
                loop_depth += 1
                if loop_depth > 2:
                    issues.append({
                        'category': 'performance',
                        'type': 'nested_loops',
                        'line': i + 1,
                        'description': 'Deep nested loops detected - consider optimization',
                        'severity': 'medium'
                    })
            elif line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                loop_depth = 0
        
        # Check for inefficient patterns
        inefficient_patterns = [
            ('SELECT *', 'Avoid SELECT * queries'),
            ('time.sleep(', 'Blocking sleep operations found'),
            ('eval(', 'Potentially dangerous eval() usage'),
            ('exec(', 'Potentially dangerous exec() usage')
        ]
        
        for i, line in enumerate(lines):
            for pattern, message in inefficient_patterns:
                if pattern in line:
                    issues.append({
                        'category': 'performance',
                        'type': 'inefficient_pattern',
                        'line': i + 1,
                        'description': message,
                        'severity': 'medium'
                    })
        
        return issues
    
    def _check_security_issues(self, content: str, lines: List[str]) -> List[Dict]:
        """Check for security-related issues"""
        issues = []
        
        security_patterns = [
            ('password', 'Potential hardcoded password'),
            ('api_key', 'Potential hardcoded API key'),
            ('secret', 'Potential hardcoded secret'),
            ('token', 'Potential hardcoded token'),
            ('md5(', 'Weak hashing algorithm (MD5)'),
            ('sha1(', 'Weak hashing algorithm (SHA1)'),
            ('subprocess.call', 'Potential command injection risk'),
            ('os.system', 'Dangerous system call usage')
        ]
        
        for i, line in enumerate(lines):
            for pattern, message in security_patterns:
                if pattern.lower() in line.lower() and '=' in line:
                    issues.append({
                        'category': 'security',
                        'type': 'security_risk',
                        'line': i + 1,
                        'description': message,
                        'severity': 'high'
                    })
        
        return issues
    
    def _check_maintainability_issues(self, content: str, lines: List[str]) -> List[Dict]:
        """Check for maintainability issues"""
        issues = []
        
        # Check function length
        in_function = False
        function_start = 0
        function_name = ""
        
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                if in_function and i - function_start > 50:
                    issues.append({
                        'category': 'maintainability',
                        'type': 'large_function',
                        'line': function_start + 1,
                        'description': f'Function {function_name} is too long ({i - function_start} lines)',
                        'severity': 'medium'
                    })
                
                in_function = True
                function_start = i
                function_name = line.split('def ')[1].split('(')[0]
            
            elif line.strip().startswith('class '):
                in_function = False
        
        # Check for complex conditionals
        for i, line in enumerate(lines):
            if line.count(' and ') + line.count(' or ') > 3:
                issues.append({
                    'category': 'maintainability',
                    'type': 'complex_conditional',
                    'line': i + 1,
                    'description': 'Complex conditional statement - consider simplification',
                    'severity': 'low'
                })
        
        return issues
    
    def _check_modernization_opportunities(self, content: str, lines: List[str]) -> List[Dict]:
        """Check for modernization opportunities"""
        issues = []
        
        # Check for deprecated patterns
        deprecated_patterns = [
            ('print ', 'Consider using logging instead of print'),
            ('string.format(', 'Consider using f-strings for formatting'),
            ('% ', 'Consider modern string formatting'),
            ('dict.has_key(', 'Deprecated has_key() method'),
            ('urllib2', 'Use requests library instead of urllib2')
        ]
        
        for i, line in enumerate(lines):
            for pattern, message in deprecated_patterns:
                if pattern in line:
                    issues.append({
                        'category': 'modernization',
                        'type': 'deprecated_pattern',
                        'line': i + 1,
                        'description': message,
                        'severity': 'low'
                    })
        
        return issues
    
    def _check_testing_gaps(self, file_path: Path, content: str) -> List[Dict]:
        """Check for testing gaps"""
        issues = []
        
        # Check if test files exist
        if not str(file_path).startswith('test_') and 'test' not in str(file_path):
            test_file_exists = False
            potential_test_paths = [
                file_path.parent / f"test_{file_path.name}",
                file_path.parent / "tests" / file_path.name,
                file_path.parent / "test" / file_path.name
            ]
            
            for test_path in potential_test_paths:
                if test_path.exists():
                    test_file_exists = True
                    break
            
            if not test_file_exists:
                issues.append({
                    'category': 'testing',
                    'type': 'missing_tests',
                    'line': 1,
                    'description': 'No corresponding test file found',
                    'severity': 'medium'
                })
        
        return issues
    
    def _check_documentation_issues(self, content: str, lines: List[str]) -> List[Dict]:
        """Check for documentation issues"""
        issues = []
        
        # Check for missing docstrings
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                # Look for docstring in next few lines
                has_docstring = False
                for j in range(i + 1, min(i + 5, len(lines))):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        has_docstring = True
                        break
                
                if not has_docstring:
                    function_name = line.split()[1].split('(')[0]
                    issues.append({
                        'category': 'documentation',
                        'type': 'missing_docstring',
                        'line': i + 1,
                        'description': f'Missing docstring for {function_name}',
                        'severity': 'low'
                    })
        
        return issues
    
    def _calculate_priority_score(self, issues: List[Dict]) -> int:
        """Calculate priority score based on issues found"""
        score = 0
        severity_weights = {'high': 10, 'medium': 5, 'low': 1}
        
        for issue in issues:
            score += severity_weights.get(issue['severity'], 1)
        
        return score
    
    def _identify_enhancements(self) -> Dict[str, List[Dict]]:
        """Identify and categorize enhancement opportunities"""
        enhancements = {category: [] for category in self.enhancement_patterns.keys()}
        
        for file_analysis in self.analysis_results.get('file_analysis', []):
            for issue in file_analysis['issues']:
                category = issue['category']
                if category in enhancements:
                    enhancements[category].append({
                        'file': file_analysis['file_path'],
                        'line': issue['line'],
                        'description': issue['description'],
                        'severity': issue['severity'],
                        'type': issue['type']
                    })
        
        return enhancements
    
    def _prioritize_enhancements(self) -> List[Dict]:
        """Create prioritized list of enhancement recommendations"""
        recommendations = []
        
        # Security issues (highest priority)
        security_issues = self.analysis_results.get('enhancement_opportunities', {}).get('security', [])
        if security_issues:
            recommendations.append({
                'priority': 1,
                'category': 'security',
                'title': 'Address Security Vulnerabilities',
                'description': f'Found {len(security_issues)} security issues that need immediate attention',
                'effort': 'high',
                'impact': 'critical',
                'issues_count': len(security_issues)
            })
        
        # Performance issues
        performance_issues = self.analysis_results.get('enhancement_opportunities', {}).get('performance', [])
        if performance_issues:
            recommendations.append({
                'priority': 2,
                'category': 'performance',
                'title': 'Optimize Performance',
                'description': f'Found {len(performance_issues)} performance optimization opportunities',
                'effort': 'medium',
                'impact': 'high',
                'issues_count': len(performance_issues)
            })
        
        # Testing gaps
        testing_issues = self.analysis_results.get('enhancement_opportunities', {}).get('testing', [])
        if testing_issues:
            recommendations.append({
                'priority': 3,
                'category': 'testing',
                'title': 'Improve Test Coverage',
                'description': f'Found {len(testing_issues)} files missing tests',
                'effort': 'high',
                'impact': 'high',
                'issues_count': len(testing_issues)
            })
        
        # Maintainability improvements
        maintainability_issues = self.analysis_results.get('enhancement_opportunities', {}).get('maintainability', [])
        if maintainability_issues:
            recommendations.append({
                'priority': 4,
                'category': 'maintainability',
                'title': 'Improve Code Maintainability',
                'description': f'Found {len(maintainability_issues)} maintainability improvements',
                'effort': 'medium',
                'impact': 'medium',
                'issues_count': len(maintainability_issues)
            })
        
        return recommendations
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored during analysis"""
        ignore_patterns = [
            '.git/', '__pycache__/', '.cache/', 'node_modules/',
            '.env', '.log', '.tmp', '.backup'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in ignore_patterns)
    
    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file worth analyzing"""
        code_extensions = ['.py', '.js', '.java', '.php', '.rb', '.go', '.rs', '.cpp', '.c', '.cs']
        return file_path.suffix.lower() in code_extensions
    
    def _get_language_from_extension(self, extension: str) -> str:
        """Get programming language from file extension"""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.html': 'HTML',
            '.css': 'CSS',
            '.sql': 'SQL'
        }
        return language_map.get(extension.lower(), 'Other')
    
    def generate_enhancement_report(self, output_file: str = None) -> str:
        """Generate a comprehensive enhancement report"""
        if not self.analysis_results:
            self.scan_codebase()
        
        report = f"""
# Code Enhancement Analysis Report

**Project:** {self.analysis_results['project_info']['project_path']}
**Scan Date:** {self.analysis_results['scan_timestamp']}

## Project Overview
- **Total Files:** {self.analysis_results['project_info']['total_files']}
- **Project Size:** {self.analysis_results['project_info']['size_mb']} MB
- **Languages:** {', '.join(self.analysis_results['project_info']['languages'].keys())}

## Enhancement Summary
"""
        
        # Add priority recommendations
        for rec in self.analysis_results['priority_recommendations']:
            report += f"""
### {rec['priority']}. {rec['title']} ({rec['category'].title()})
- **Impact:** {rec['impact'].title()}
- **Effort:** {rec['effort'].title()}
- **Issues Found:** {rec['issues_count']}
- **Description:** {rec['description']}
"""
        
        # Add detailed findings
        report += "\n## Detailed Findings\n"
        
        for category, issues in self.analysis_results['enhancement_opportunities'].items():
            if issues:
                report += f"\n### {category.title()} Issues ({len(issues)})\n"
                for issue in issues[:10]:  # Show top 10 per category
                    report += f"- **{issue['file']}:{issue['line']}** - {issue['description']} ({issue['severity']})\n"
                
                if len(issues) > 10:
                    report += f"- ... and {len(issues) - 10} more issues\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"📄 Enhancement report saved to: {output_file}")
        
        return report


class CodeEnhancementOrchestrator:
    """Orchestrates the code enhancement process using CrewAI pipeline"""
    
    def __init__(self, project_path: str, jira_project_key: str = None):
        self.project_path = project_path
        self.analyzer = CodeAnalyzer(project_path)
        
        # Initialize tracking components
        if jira_project_key:
            self.tracker = EnhancedTicketTracker(jira_project_key)
            self.processor = SmartTicketProcessor(self.tracker, None, None)
        else:
            self.tracker = None
            self.processor = None
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the codebase and identify enhancement opportunities"""
        print("🔍 Starting codebase analysis...")
        analysis = self.analyzer.scan_codebase()
        
        print(f"✅ Analysis complete!")
        print(f"   Files analyzed: {analysis['project_info']['total_files']}")
        print(f"   Issues found: {sum(len(issues) for issues in analysis['enhancement_opportunities'].values())}")
        print(f"   Priority recommendations: {len(analysis['priority_recommendations'])}")
        
        return analysis
    
    def create_enhancement_tickets(self, analysis: Dict[str, Any] = None) -> List[Dict]:
        """Create JIRA tickets for enhancement opportunities"""
        if not self.tracker:
            print("⚠️  No JIRA integration configured - skipping ticket creation")
            return []
        
        if not analysis:
            analysis = self.analyze_codebase()
        
        tickets = []
        
        for rec in analysis['priority_recommendations']:
            category = rec['category']
            issues = analysis['enhancement_opportunities'].get(category, [])
            
            # Group issues by file for better ticket organization
            files_affected = {}
            for issue in issues:
                file_path = issue['file']
                if file_path not in files_affected:
                    files_affected[file_path] = []
                files_affected[file_path].append(issue)
            
            # Create ticket for this enhancement category
            ticket_data = {
                'summary': f"Code Enhancement: {rec['title']}",
                'description': self._create_ticket_description(rec, files_affected),
                'category': category,
                'priority': rec['priority'],
                'effort_estimate': rec['effort'],
                'impact_level': rec['impact'],
                'files_count': len(files_affected),
                'issues_count': rec['issues_count']
            }
            
            tickets.append(ticket_data)
        
        print(f"📋 Created {len(tickets)} enhancement tickets")
        return tickets
    
    def _create_ticket_description(self, recommendation: Dict, files_affected: Dict) -> str:
        """Create detailed ticket description"""
        description = f"""
## Enhancement Overview
{recommendation['description']}

**Category:** {recommendation['category'].title()}
**Priority:** {recommendation['priority']}
**Estimated Effort:** {recommendation['effort'].title()}
**Expected Impact:** {recommendation['impact'].title()}

## Files Affected ({len(files_affected)})
"""
        
        for file_path, issues in list(files_affected.items())[:10]:  # Limit to 10 files
            description += f"\n### {file_path}\n"
            for issue in issues[:5]:  # Limit to 5 issues per file
                description += f"- Line {issue['line']}: {issue['description']} ({issue['severity']})\n"
            
            if len(issues) > 5:
                description += f"- ... and {len(issues) - 5} more issues\n"
        
        if len(files_affected) > 10:
            description += f"\n... and {len(files_affected) - 10} more files\n"
        
        description += f"""
## Recommended Actions
1. Review the identified issues in each file
2. Prioritize fixes based on severity levels
3. Test thoroughly after implementing changes
4. Update documentation as needed

## Success Criteria
- All {recommendation['category']} issues resolved
- Code quality metrics improved
- No new issues introduced
"""
        
        return description
    
    def generate_enhancement_plan(self, analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a comprehensive enhancement plan"""
        if not analysis:
            analysis = self.analyze_codebase()
        
        plan = {
            'project_overview': analysis['project_info'],
            'enhancement_phases': [],
            'timeline_estimate': self._estimate_timeline(analysis),
            'resource_requirements': self._estimate_resources(analysis),
            'success_metrics': self._define_success_metrics(analysis)
        }
        
        # Create enhancement phases
        phases = [
            {'name': 'Security Hardening', 'category': 'security', 'priority': 1},
            {'name': 'Performance Optimization', 'category': 'performance', 'priority': 2},
            {'name': 'Test Coverage Improvement', 'category': 'testing', 'priority': 3},
            {'name': 'Code Maintainability', 'category': 'maintainability', 'priority': 4},
            {'name': 'Modernization', 'category': 'modernization', 'priority': 5},
            {'name': 'Documentation Enhancement', 'category': 'documentation', 'priority': 6}
        ]
        
        for phase in phases:
            category_issues = analysis['enhancement_opportunities'].get(phase['category'], [])
            if category_issues:
                phase_plan = {
                    'phase_name': phase['name'],
                    'priority': phase['priority'],
                    'issues_count': len(category_issues),
                    'estimated_effort': self._estimate_phase_effort(category_issues),
                    'key_deliverables': self._define_phase_deliverables(phase['category'], category_issues),
                    'success_criteria': self._define_phase_success_criteria(phase['category'])
                }
                plan['enhancement_phases'].append(phase_plan)
        
        return plan
    
    def _estimate_timeline(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Estimate timeline for the enhancement project"""
        total_issues = sum(len(issues) for issues in analysis['enhancement_opportunities'].values())
        
        if total_issues < 50:
            duration = "4-6 weeks"
        elif total_issues < 100:
            duration = "8-12 weeks"
        else:
            duration = "3-6 months"
        
        return {
            'total_duration': duration,
            'parallel_development': "Possible for independent modules",
            'recommendations': "Implement in phases for manageable progress"
        }
    
    def _estimate_resources(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        languages = analysis['project_info']['languages']
        
        return {
            'team_size': "2-4 developers",
            'required_skills': list(languages.keys()),
            'specialist_needs': ["Security expert", "Performance testing", "QA engineer"],
            'tools_needed': ["Static analysis tools", "Testing frameworks", "CI/CD pipeline"]
        }
    
    def _define_success_metrics(self, analysis: Dict[str, Any]) -> List[str]:
        """Define success metrics for the enhancement project"""
        return [
            "Zero high-severity security vulnerabilities",
            "90%+ test coverage achieved",
            "Performance improved by 20%+",
            "Code maintainability index increased",
            "All critical issues resolved",
            "Documentation coverage > 80%"
        ]
    
    def _estimate_phase_effort(self, issues: List[Dict]) -> str:
        """Estimate effort for a specific phase"""
        high_severity = sum(1 for issue in issues if issue['severity'] == 'high')
        medium_severity = sum(1 for issue in issues if issue['severity'] == 'medium')
        
        if high_severity > 5 or medium_severity > 15:
            return "high"
        elif high_severity > 2 or medium_severity > 8:
            return "medium"
        else:
            return "low"
    
    def _define_phase_deliverables(self, category: str, issues: List[Dict]) -> List[str]:
        """Define deliverables for each phase"""
        deliverables_map = {
            'security': [
                "Security vulnerability assessment report",
                "Fixed security issues with patches",
                "Updated security guidelines",
                "Security testing procedures"
            ],
            'performance': [
                "Performance baseline measurements",
                "Optimized algorithms and queries",
                "Performance monitoring setup",
                "Load testing results"
            ],
            'testing': [
                "Test strategy document",
                "Unit test suites for all modules",
                "Integration test frameworks",
                "Test coverage reports"
            ],
            'maintainability': [
                "Code refactoring plan",
                "Simplified complex functions",
                "Consistent coding standards",
                "Code review checklists"
            ],
            'modernization': [
                "Technology upgrade plan",
                "Updated dependencies",
                "Modern syntax implementations",
                "Compatibility testing"
            ],
            'documentation': [
                "API documentation",
                "Code comments and docstrings",
                "User guides and tutorials",
                "Architecture documentation"
            ]
        }
        
        return deliverables_map.get(category, ["Category-specific improvements"])
    
    def _define_phase_success_criteria(self, category: str) -> List[str]:
        """Define success criteria for each phase"""
        criteria_map = {
            'security': ["All security issues resolved", "Security scan passes"],
            'performance': ["Performance benchmarks met", "No performance regressions"],
            'testing': ["Target test coverage achieved", "All tests passing"],
            'maintainability': ["Code complexity reduced", "Maintainability metrics improved"],
            'modernization': ["All deprecated code updated", "Modern practices adopted"],
            'documentation': ["Documentation coverage target met", "Documentation quality approved"]
        }
        
        return criteria_map.get(category, ["Phase objectives completed"])


def main():
    """Example usage of the Code Enhancement system"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
Code Enhancement Analyzer
========================

Usage: python code_enhancement_adapter.py <project_path> [jira_project_key]

Examples:
  python code_enhancement_adapter.py /path/to/your/app
  python code_enhancement_adapter.py /path/to/your/app MY_JIRA_PROJECT
        """)
        return
    
    project_path = sys.argv[1]
    jira_project_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Create orchestrator
    orchestrator = CodeEnhancementOrchestrator(project_path, jira_project_key)
    
    # Analyze codebase
    print("🚀 Starting code enhancement analysis...")
    analysis = orchestrator.analyze_codebase()
    
    # Generate reports
    report = orchestrator.analyzer.generate_enhancement_report("enhancement_report.md")
    print("\n📄 Enhancement report generated: enhancement_report.md")
    
    # Generate enhancement plan
    plan = orchestrator.generate_enhancement_plan(analysis)
    
    print(f"\n📋 Enhancement Plan Summary:")
    print(f"   Phases: {len(plan['enhancement_phases'])}")
    print(f