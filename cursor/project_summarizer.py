import os
import json
import ast
from typing import Dict, List, Any

def summarize_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    summary = {
        "path": file_path,
        "content": content,
        "functions": [],
        "classes": []
    }
    
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                summary["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.ClassDef):
                summary["classes"].append({
                    "name": node.name,
                    "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                    "docstring": ast.get_docstring(node)
                })
    except SyntaxError:
        # 如果文件不是有效的 Python 文件,我们只保存内容
        pass
    
    return summary

def summarize_project(project_dir: str) -> Dict[str, Any]:
    project_summary = {
        "structure": {},
        "files": []
    }
    
    for root, dirs, files in os.walk(project_dir):
        if "cursor" in dirs:
            dirs.remove("cursor")  # 不遍历 cursor 目录
        
        structure = project_summary["structure"]
        path_parts = root.split(os.sep)
        for part in path_parts:
            if part not in structure:
                structure[part] = {}
            structure = structure[part]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                file_summary = summarize_file(file_path)
                project_summary["files"].append(file_summary)
    
    return project_summary

def save_summary(summary: Dict[str, Any], output_file: str):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

def load_summary(input_file: str) -> Dict[str, Any]:
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    project_dir = ".."  # Assuming the script is run from the cursor directory
    output_file = "project_summary.json"
    
    summary = summarize_project(project_dir)
    save_summary(summary, output_file)
    print(f"Project summary has been saved to {output_file}")