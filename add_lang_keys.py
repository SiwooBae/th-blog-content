#!/usr/bin/env python3
"""
Script to automatically add lang field to all blog posts.
The lang will be determined from the directory structure (es, pt, en).
"""

import os
import re
from pathlib import Path


def extract_frontmatter(content):
    """Extract frontmatter from markdown content."""
    # Match frontmatter between --- delimiters
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        body = match.group(2)
        return frontmatter, body
    return None, content


def add_lang_to_frontmatter(frontmatter, lang):
    """Add lang to frontmatter if it doesn't exist."""
    # Check if lang already exists
    if 'lang:' in frontmatter:
        print(f"  lang already exists, skipping...")
        return frontmatter
    
    # Add lang after the existing fields
    new_frontmatter = frontmatter.rstrip() + f'\nlang: \'{lang}\''
    return new_frontmatter


def get_language_from_path(file_path):
    """Extract language from the file path."""
    path_parts = Path(file_path).parts
    
    # Look for language directories (es, pt, en)
    for part in path_parts:
        if part in ['es', 'pt', 'en']:
            return part
    
    # Default to 'en' if no language found
    return 'en'


def process_markdown_file(file_path):
    """Process a single markdown file to add lang."""
    print(f"Processing: {file_path}")
    
    # Get language from directory path
    lang = get_language_from_path(file_path)
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter and body
        frontmatter, body = extract_frontmatter(content)
        
        if frontmatter is None:
            print(f"  No frontmatter found in {file_path}, skipping...")
            return False
        
        # Add lang to frontmatter
        updated_frontmatter = add_lang_to_frontmatter(frontmatter, lang)
        
        # If frontmatter wasn't changed, skip writing
        if updated_frontmatter == frontmatter:
            return False
        
        # Reconstruct the file content
        updated_content = f"---\n{updated_frontmatter}\n---\n{body}"
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"  Added lang: '{lang}'")
        return True
        
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all blog posts."""
    blog_dir = Path("./") # point to the relative root
    
    if not blog_dir.exists():
        print(f"Blog directory {blog_dir} does not exist!")
        return
    
    processed_count = 0
    total_count = 0
    
    # Process all markdown files recursively
    for md_file in blog_dir.rglob("*.md"):
        total_count += 1
        if process_markdown_file(md_file):
            processed_count += 1
    
    print(f"\nProcessing complete!")
    print(f"Total files found: {total_count}")
    print(f"Files updated: {processed_count}")
    print(f"Files skipped: {total_count - processed_count}")


if __name__ == "__main__":
    main() 