"""
Простой скрипт для анализа текущего репозитория
Запуск: python analyze.py (из корня проекта)
"""

import os
from pathlib import Path

# Исключаемые директории
EXCLUDE_DIRS = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv',
                'node_modules', '.idea', '.vscode', '.egg-info', 'dist', 'build', '.env'}
EXCLUDE_FILES = {'.pyc', '.pyo', '.so', '.exe', '.dll'}

def scan_directory(path, output_file):
    """Сканирует директорию и сохраняет файлы в markdown"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Анализ проекта\n\n")
        f.write(f"**Папка**: `{Path(path).name}`\n\n")

        # Собираем всё дерево
        all_files = []
        for root, dirs, files in os.walk(path):
            # Исключаем директории
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, path)
                all_files.append((filepath, rel_path))

        # Структура файлов
        f.write("## 📁 Структура\n\n```\n")
        for filepath, rel_path in sorted(all_files):
            try:
                size = os.path.getsize(filepath)
                size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
                f.write(f"{rel_path} ({size_str})\n")
            except:
                f.write(f"{rel_path}\n")
        f.write("```\n\n")

        # Исходный код
        f.write("## 📄 Исходный код\n\n")

        code_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.sh',
                          '.md', '.txt', '.sql', '.html', '.css'}
        special_files = {'.gitignore', '.env.example', 'Dockerfile', 'Makefile',
                        'requirements.txt', 'package.json'}

        for filepath, rel_path in sorted(all_files):
            ext = os.path.splitext(filepath)[1]
            filename = os.path.basename(filepath)

            # Проверяем, нужно ли включать файл
            if ext not in code_extensions and filename not in special_files:
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()

                # Определяем язык
                lang_map = {
                    '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                    '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
                    '.sh': 'bash', '.md': 'markdown', '.sql': 'sql',
                    '.html': 'html', '.css': 'css'
                }
                lang = lang_map.get(ext, 'text')

                f.write(f"### `{rel_path}`\n\n")
                f.write(f"```{lang}\n")
                f.write(content)
                f.write("\n```\n\n")
            except Exception as e:
                f.write(f"### `{rel_path}`\n\n[Ошибка чтения: {e}]\n\n")

    print(f"✅ Сохранено в: {output_file}")

if __name__ == "__main__":
    current_dir = Path.cwd()
    output_file = current_dir / "project_analysis.md"

    print(f"📁 Анализирую: {current_dir}")
    scan_directory(current_dir, output_file)
    print(f"📖 Готово! Открой: {output_file}")