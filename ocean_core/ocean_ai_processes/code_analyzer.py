"""
Code Analyzer - Multi-language code analysis
Analyzes Python, JavaScript, TypeScript, and other languages
Extracts metrics, patterns, and potential issues
"""

import ast
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CodeMetrics:
    """Code quality metrics"""
    lines_of_code: int
    blank_lines: int
    comment_lines: int
    functions: int
    classes: int
    imports: int
    complexity: float
    documentation_ratio: float


@dataclass
class CodeIssue:
    """Potential code issue"""
    type: str  # "warning", "error", "style", "security"
    message: str
    line: int
    severity: str  # "low", "medium", "high", "critical"
    suggestion: Optional[str] = None


@dataclass
class CodeAnalysisResult:
    """Complete code analysis result"""
    language: str
    metrics: CodeMetrics
    issues: List[CodeIssue]
    functions_found: List[Dict[str, Any]]
    classes_found: List[Dict[str, Any]]
    imports: List[str]
    score: float  # 0-100


class CodeAnalyzer:
    """
    Multi-language code analyzer
    Supports Python, JavaScript, TypeScript, Go, and more
    """
    
    # Language detection patterns
    LANGUAGE_PATTERNS = {
        "python": [r'^\s*def\s+\w+', r'^\s*import\s+\w+', r'^\s*from\s+\w+\s+import', 
                   r'^\s*class\s+\w+\s*[:\(]', r'^\s*@\w+', r'if\s+__name__\s*==', r'self\.'],
        "javascript": [r'^\s*const\s+\w+\s*=', r'^\s*let\s+\w+\s*=', r'^\s*var\s+\w+\s*=',
                       r'^\s*function\s+\w+', r'^\s*export\s+', r'=>', r'require\s*\('],
        "typescript": [r':\s*(string|number|boolean|any|void)\b', r'interface\s+\w+',
                       r'type\s+\w+\s*=', r'<\w+>', r'generic\s+'],
        "go": [r'^\s*package\s+\w+', r'^\s*func\s+\w+', r'^\s*import\s+\(', r':='],
        "java": [r'public\s+class', r'private\s+\w+', r'void\s+\w+\s*\(', 
                 r'System\.out', r'@Override'],
        "sql": [r'SELECT\s+', r'FROM\s+', r'WHERE\s+', r'INSERT\s+INTO', r'CREATE\s+TABLE'],
    }
    
    # Security patterns
    SECURITY_PATTERNS = {
        "hardcoded_secret": [
            (r'(?:password|passwd|pwd|secret|api_key|apikey|token|auth)\s*=\s*["\'][^"\']{8,}["\']', 
             "Potential hardcoded secret", "critical"),
        ],
        "sql_injection": [
            (r'execute\s*\(\s*["\'].*%s', "Possible SQL injection vulnerability", "high"),
            (r'cursor\.execute\s*\([^)]*\+[^)]*\)', "String concatenation in SQL query", "high"),
        ],
        "command_injection": [
            (r'os\.system\s*\([^)]*\+', "Potential command injection", "critical"),
            (r'subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True', 
             "Shell=True can lead to command injection", "high"),
        ],
        "path_traversal": [
            (r'open\s*\([^)]*\+', "Path concatenation - check for traversal", "medium"),
        ],
    }
    
    # Code smells
    CODE_SMELLS = {
        "long_function": (50, "Function is too long (>{} lines)"),
        "complex_function": (10, "Function is too complex (cyclomatic complexity > {})"),
        "too_many_params": (5, "Too many parameters ({} > {})"),
        "magic_number": (r'\b\d{3,}\b', "Magic number detected"),
        "global_variable": (r'^[A-Z_]+\s*=', "Global variable detected"),
    }
    
    def __init__(self):
        self.custom_rules: List[Dict] = []
    
    def detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        scores = {lang: 0 for lang in self.LANGUAGE_PATTERNS}
        
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
                    scores[lang] += 1
        
        if max(scores.values()) == 0:
            return "unknown"
        
        return max(scores.keys(), key=lambda k: scores[k])
    
    def analyze(self, code: str, language: Optional[str] = None) -> CodeAnalysisResult:
        """
        Analyze code and return comprehensive results
        
        Args:
            code: Source code to analyze
            language: Programming language (auto-detected if None)
            
        Returns:
            CodeAnalysisResult with metrics, issues, and extracted info
        """
        if language is None:
            language = self.detect_language(code)
        
        # Calculate metrics
        metrics = self._calculate_metrics(code, language)
        
        # Find issues
        issues = self._find_issues(code, language)
        
        # Extract functions and classes
        functions = self._extract_functions(code, language)
        classes = self._extract_classes(code, language)
        imports = self._extract_imports(code, language)
        
        # Calculate score
        score = self._calculate_score(metrics, issues)
        
        return CodeAnalysisResult(
            language=language,
            metrics=metrics,
            issues=issues,
            functions_found=functions,
            classes_found=classes,
            imports=imports,
            score=score
        )
    
    def _calculate_metrics(self, code: str, language: str) -> CodeMetrics:
        """Calculate code metrics"""
        lines = code.split('\n')
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        
        # Comment patterns by language
        if language in ["python"]:
            comment_pattern = r'^\s*#'
        elif language in ["javascript", "typescript", "java", "go"]:
            comment_pattern = r'^\s*(?://|/\*|\*)'
        else:
            comment_pattern = r'^\s*(?:#|//|/\*)'
        
        comment_lines = sum(1 for line in lines if re.match(comment_pattern, line))
        
        # Count functions, classes, imports
        functions = len(self._extract_functions(code, language))
        classes = len(self._extract_classes(code, language))
        imports = len(self._extract_imports(code, language))
        
        # Calculate complexity (simplified cyclomatic complexity)
        complexity = self._calculate_complexity(code, language)
        
        # Documentation ratio
        doc_ratio = comment_lines / max(total_lines - blank_lines, 1)
        
        return CodeMetrics(
            lines_of_code=total_lines - blank_lines - comment_lines,
            blank_lines=blank_lines,
            comment_lines=comment_lines,
            functions=functions,
            classes=classes,
            imports=imports,
            complexity=complexity,
            documentation_ratio=doc_ratio
        )
    
    def _calculate_complexity(self, code: str, language: str) -> float:
        """Calculate cyclomatic complexity"""
        # Count decision points
        decision_patterns = [
            r'\bif\b', r'\belif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
            r'\btry\b', r'\bexcept\b', r'\bcatch\b', r'\bcase\b',
            r'\band\b', r'\bor\b', r'&&', r'\|\|', r'\?'
        ]
        
        complexity = 1  # Base complexity
        
        for pattern in decision_patterns:
            complexity += len(re.findall(pattern, code))
        
        return complexity
    
    def _find_issues(self, code: str, language: str) -> List[CodeIssue]:
        """Find code issues and security problems"""
        issues = []
        lines = code.split('\n')
        
        # Security checks
        for category, patterns in self.SECURITY_PATTERNS.items():
            for pattern, message, severity in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(CodeIssue(
                            type="security",
                            message=message,
                            line=i,
                            severity=severity,
                            suggestion=f"Review this line for {category.replace('_', ' ')}"
                        ))
        
        # Code smells
        issues.extend(self._check_code_smells(code, language))
        
        # Language-specific checks
        if language == "python":
            issues.extend(self._check_python_issues(code))
        elif language in ["javascript", "typescript"]:
            issues.extend(self._check_javascript_issues(code))
        
        # Custom rules
        for rule in self.custom_rules:
            for i, line in enumerate(lines, 1):
                if re.search(rule["pattern"], line):
                    issues.append(CodeIssue(
                        type=rule.get("type", "warning"),
                        message=rule["message"],
                        line=i,
                        severity=rule.get("severity", "low")
                    ))
        
        return issues
    
    def _check_code_smells(self, code: str, language: str) -> List[CodeIssue]:
        """Check for code smells"""
        issues = []
        
        # Magic numbers
        for match in re.finditer(r'(?<!["\'\w])(\d{3,})(?!["\'\w])', code):
            line_num = code[:match.start()].count('\n') + 1
            issues.append(CodeIssue(
                type="style",
                message=f"Magic number {match.group(1)} detected",
                line=line_num,
                severity="low",
                suggestion="Consider using a named constant"
            ))
        
        return issues
    
    def _check_python_issues(self, code: str) -> List[CodeIssue]:
        """Python-specific checks"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check function complexity
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_lines > 50:
                        issues.append(CodeIssue(
                            type="style",
                            message=f"Function '{node.name}' is too long ({func_lines} lines)",
                            line=node.lineno,
                            severity="medium",
                            suggestion="Consider breaking into smaller functions"
                        ))
                    
                    # Check parameter count
                    param_count = len(node.args.args)
                    if param_count > 5:
                        issues.append(CodeIssue(
                            type="style",
                            message=f"Function '{node.name}' has too many parameters ({param_count})",
                            line=node.lineno,
                            severity="low",
                            suggestion="Consider using a configuration object"
                        ))
                
                # Check for bare except
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append(CodeIssue(
                        type="warning",
                        message="Bare except clause (catches all exceptions)",
                        line=node.lineno,
                        severity="medium",
                        suggestion="Specify the exception type to catch"
                    ))
        except SyntaxError as e:
            issues.append(CodeIssue(
                type="error",
                message=f"Syntax error: {e.msg}",
                line=e.lineno or 1,
                severity="critical"
            ))
        except Exception:
            pass  # Skip AST parsing errors for non-Python code
        
        return issues
    
    def _check_javascript_issues(self, code: str) -> List[CodeIssue]:
        """JavaScript/TypeScript-specific checks"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for var usage
            if re.search(r'\bvar\s+\w+', line):
                issues.append(CodeIssue(
                    type="style",
                    message="Use 'let' or 'const' instead of 'var'",
                    line=i,
                    severity="low",
                    suggestion="Replace 'var' with 'let' or 'const'"
                ))
            
            # Check for == instead of ===
            if re.search(r'[^=!]={2}[^=]', line):
                issues.append(CodeIssue(
                    type="style",
                    message="Use '===' instead of '==' for type-safe comparison",
                    line=i,
                    severity="low",
                    suggestion="Replace '==' with '==='"
                ))
            
            # Check for console.log in production code
            if re.search(r'console\.(log|warn|error)', line):
                issues.append(CodeIssue(
                    type="warning",
                    message="Console statement found",
                    line=i,
                    severity="low",
                    suggestion="Remove console statements in production"
                ))
        
        return issues
    
    def _extract_functions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        if language == "python":
            pattern = r'^\s*(?:async\s+)?def\s+(\w+)\s*\((.*?)\)'
        elif language in ["javascript", "typescript"]:
            pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))'
        elif language == "go":
            pattern = r'func\s+(\w+)\s*\((.*?)\)'
        else:
            pattern = r'(?:function|def|func)\s+(\w+)'
        
        for match in re.finditer(pattern, code, re.MULTILINE):
            name = match.group(1) or (match.group(2) if match.lastindex >= 2 else "anonymous")
            line_num = code[:match.start()].count('\n') + 1
            
            functions.append({
                "name": name,
                "line": line_num,
                "parameters": match.group(2) if match.lastindex >= 2 else ""
            })
        
        return functions
    
    def _extract_classes(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        if language == "python":
            pattern = r'^\s*class\s+(\w+)\s*(?:\((.*?)\))?:'
        elif language in ["javascript", "typescript"]:
            pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        elif language == "java":
            pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        else:
            pattern = r'class\s+(\w+)'
        
        for match in re.finditer(pattern, code, re.MULTILINE):
            name = match.group(1)
            parent = match.group(2) if match.lastindex >= 2 else None
            line_num = code[:match.start()].count('\n') + 1
            
            classes.append({
                "name": name,
                "line": line_num,
                "parent": parent
            })
        
        return classes
    
    def _extract_imports(self, code: str, language: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        if language == "python":
            patterns = [r'^\s*import\s+(\S+)', r'^\s*from\s+(\S+)\s+import']
        elif language in ["javascript", "typescript"]:
            patterns = [r'import\s+.*?\s+from\s+["\'](.+?)["\']', r'require\s*\(["\'](.+?)["\']\)']
        elif language == "go":
            patterns = [r'import\s+["\'](.+?)["\']', r'import\s+\((.*?)\)']
        else:
            patterns = [r'import\s+(\S+)']
        
        for pattern in patterns:
            for match in re.finditer(pattern, code, re.MULTILINE | re.DOTALL):
                module = match.group(1)
                if module:
                    imports.append(module.strip())
        
        return list(set(imports))
    
    def _calculate_score(self, metrics: CodeMetrics, issues: List[CodeIssue]) -> float:
        """Calculate overall code quality score (0-100)"""
        score = 100.0
        
        # Deduct for issues
        for issue in issues:
            if issue.severity == "critical":
                score -= 15
            elif issue.severity == "high":
                score -= 10
            elif issue.severity == "medium":
                score -= 5
            else:
                score -= 2
        
        # Bonus for documentation
        if metrics.documentation_ratio > 0.15:
            score += 5
        elif metrics.documentation_ratio < 0.05:
            score -= 5
        
        # Deduct for high complexity
        avg_complexity = metrics.complexity / max(metrics.functions, 1)
        if avg_complexity > 15:
            score -= 10
        elif avg_complexity > 10:
            score -= 5
        
        return max(0, min(100, score))
    
    def add_custom_rule(self, pattern: str, message: str, type: str = "warning", severity: str = "low") -> None:
        """Add a custom analysis rule"""
        self.custom_rules.append({
            "pattern": pattern,
            "message": message,
            "type": type,
            "severity": severity
        })
    
    def analyze_batch(self, files: Dict[str, str]) -> Dict[str, CodeAnalysisResult]:
        """Analyze multiple code files"""
        return {path: self.analyze(code) for path, code in files.items()}
    
    def get_summary(self, result: CodeAnalysisResult) -> Dict[str, Any]:
        """Get summary of analysis result"""
        issue_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in result.issues:
            issue_counts[issue.severity] = issue_counts.get(issue.severity, 0) + 1
        
        return {
            "language": result.language,
            "score": result.score,
            "lines_of_code": result.metrics.lines_of_code,
            "functions": result.metrics.functions,
            "classes": result.metrics.classes,
            "issue_counts": issue_counts,
            "total_issues": len(result.issues)
        }
