from flask import render_template, current_app
from flask_login import login_required

from pathlib import Path
import markdown2
import re

from itnsa.note import note

# define nessary variables
note_folder = Path(current_app.config['NOTE_FOLDER'])

markdown2_extras = [
    "metadata",
    "tables",
    "code-friendly",
    "fenced-code-blocks",
    "break-on-newline",
    "footnotes",
]

# List all note folders as a list of html
@note.route('/')
@login_required
def list_note_folders():
    """List all subfolder in note_folder  as a list of html."""
    subfolders = [folder.name for folder in note_folder.iterdir() if folder.is_dir()]
    print(subfolders)
    return render_template('note/list_folders.html', subfolders=subfolders, title='笔记列表')
  
# @note.route('<path:directory>')
# @login_required
# def list_notes(directory):
#     """List all markdown files in note_folder as a list of html."""
#     files = list_markdown_files(note_folder)
#     return render_template('note/list_notes.html', files=files, title='笔记列表')

# Show README.md as html
# ignore case for README.md
def find_readme_file(directory):
    """Find README.md file in directory."""
    for file in Path(directory).iterdir():
        if file.name.lower() == 'readme.md':
            return file
    return None

def convert_links(md_content, directory):
    # 替换README.md中笔记文件的相对链接为Flask路由
    # 例如：[Ansible Getting Started](ansible-getting-started.md) -> [Ansible Getting Started](teaching-notes-Ansible/ansible-getting-started)
    def replace_link(match):
        text, href = match.groups()
        new_href = str(Path(directory).joinpath(href).with_suffix(''))
        return f"[{text}]({new_href})"
    return re.sub(r"\[(.*?)\]\((.*?)\)", replace_link, md_content)

@note.route('<path:directory>')
@login_required
def view_readme(directory):
    """Show README.md as html."""
    readme_file_path = find_readme_file(note_folder.joinpath(directory))
    if readme_file_path:
        with open(readme_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        content = convert_links(md_content, directory)
        html = markdown2.markdown(content, extras=markdown2_extras) 
        return render_template('note/view_readme.html', html=html, title=directory)
    else:
        return "README.md not found", 404

# Convert markdown to html
def markdown_to_html(markdown_file):
    """Convert markdown to html."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    html = markdown2.markdown(content, extras=markdown2_extras)
    return html

# Show markdown file as html
@note.route('<path:directory>/<file>')
@login_required
def view_note(directory, file):
    """Show markdown file as html."""
    markdown_file = note_folder.joinpath(directory, file + '.md')
    if not markdown_file.exists():
        return "File not found", 404
    html = markdown_to_html(markdown_file)
    return render_template('note/view_note.html', html=html, title=file)