from flask import render_template, current_app, send_from_directory, flash, redirect, url_for
from flask_login import login_required, current_user

from pathlib import Path
import re

import markdown2
import markdown
import mistune
# import frontmatter
from frontmatter import Frontmatter
from bs4 import BeautifulSoup

from itnsa.note import note

# define nessary variables
note_folder = Path(current_app.config['NOTE_FOLDER'])

# Create note_folder if it doesn't exist
note_folder.mkdir(parents=True, exist_ok=True)

markdown2_extras = [
        # "breaks", # Convert '\n' in paragraphs into <br>
        "code-friendly", # Disable _ and __ for em and strong
        "cuddled-lists", # Allow lists to be cuddled to the preceding paragraph
        "fenced-code-blocks", # Allow code blocks to be fenced by ```
        "metadata", # Parse metadata at the beginning of the markdown content
        "footnotes", # Parse footnotes
        "highlightjs-lang", # Highlight code blocks with language
        "numbering", # Create counters to number tables,figures, equations and graphs
        "tables", # Parse tables
        "toc", # Generate a table of contents
        "header-ids", # Adds "id" attribute to headers
        "task_list", # Parse task lists
]

markdown_extras = [
    # "extra",
    # "meta",
    # "nl2br",
    # # "sane_lists",
    # "toc",
    # "smarty",
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

# 替换README.md中笔记文件的相对链接为Flask路由
# 例如：[Ansible Getting Started](ansible-getting-started.md) -> [Ansible Getting Started](teaching-notes-Ansible/ansible-getting-started)
def convert_links(md_content, directory):
    def replace_link(match):
        text, href = match.groups()
        new_href = str(Path(directory).joinpath(href).with_suffix(''))
        return f"[{text}]({new_href})"
    return re.sub(r"\[(.*?)\]\((.*?)\)", replace_link, md_content)


# Show README.md as html when the note folder is accessed
@note.route('<path:directory>')
@login_required
def view_readme(directory):
    """Show README.md as html."""
    # Only Competitors or Admin can view the note
    if not current_user.has_role('competitor') and not current_user.has_role('admin'):
        flash("You don't have permission to view the note", 'danger')
        return redirect(url_for('main.index')) 
    readme_file_path = find_readme_file(note_folder.joinpath(directory))
    if readme_file_path:
        with open(readme_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        content = convert_links(md_content, directory)
        html = markdown2.markdown(content, extras=markdown2_extras) 
        return render_template('note/view_readme.html', html=html, title=directory)
    else:
        return "README.md not found", 404

# 通过send_from_directory发送图片来显示markdown中的图片
@note.route('<path:directory>/images/<path:filename>')
@login_required
def send_image(directory, filename):
    return send_from_directory(note_folder.joinpath(directory, 'images'), filename)

# Convert markdown to html using markdown2 module
def markdown2_to_html(markdown_file):
    """Convert markdown to html."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    html = markdown2.markdown(content, extras=markdown2_extras)
    metadata = html.metadata
    metadata = {k.lower(): v for k, v in metadata.items() } if metadata else "OK"
    return html, metadata

# Convert markdown to html using markdown module
def markdown_to_html(markdown_file):
    """Convert markdown to html."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    html = markdown.markdown(content, extensions=markdown_extras)
    return html

# Convert markdown to html using mistune module and frontmatter
# frontmatter is used to parse metadata in markdown file which is in the format like this:
# ---
# title: "Ansible Getting Started"
# date: "2021-08-01"
# tags: ["ansible", "getting started"]
# ---
# mistune is used to convert markdown to html, it is faster than markdown2 and markdown module
def mistune_to_html(markdown_file):
    """Convert markdown to html."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # metadata, content = frontmatter.parse(content)
        post = Frontmatter.read(content)
        metadata = post['attributes']
        metadata = {k.lower(): v for k, v in metadata.items() } if metadata else None
        content = post['body']        
        html = mistune.html(content)

    return html, metadata

# Show markdown file as html
@note.route('<path:directory>/<file>')
@login_required
def view_note(directory, file):
    """Show markdown file as html."""
    markdown_file = note_folder.joinpath(directory, file + '.md')
    if not markdown_file.exists():
        return "File not found", 404
    # html = markdown_to_html(markdown_file)
    # html, metadata = mistune_to_html(markdown_file)
    html, metadata = markdown2_to_html(markdown_file)
    soup = BeautifulSoup(html, 'html.parser')
    h1_text = soup.h1.string if soup.h1 else ''
    return render_template('note/view_note.html', meta=metadata, html=html, title=h1_text)