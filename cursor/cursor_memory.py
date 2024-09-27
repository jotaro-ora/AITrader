from project_summarizer import load_summary
import json

def generate_project_overview(summary):
    overview = "Project Overview:\n\n"
    
    overview += "1. Project Structure:\n"
    overview += json.dumps(summary["structure"], indent=2, ensure_ascii=False)
    overview += "\n\n"
    
    overview += "2. File Summaries:\n"
    for file in summary["files"]:
        overview += f"File: {file['path']}\n"
        overview += f"  Functions: {', '.join(func['name'] for func in file['functions'])}\n"
        overview += f"  Classes: {', '.join(cls['name'] for cls in file['classes'])}\n"
        overview += "\n"
    
    return overview

def cursor_recall():
    summary = load_summary("project_summary.json")
    overview = generate_project_overview(summary)
    print(overview)
    return overview

if __name__ == "__main__":
    cursor_recall()