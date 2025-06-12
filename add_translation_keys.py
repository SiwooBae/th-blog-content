#!/usr/bin/env python3
"""
Script to automatically add translationKey to all blog posts.
The translationKey will be set to the filename without the .md extension.
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


def add_translation_key_to_frontmatter(frontmatter, translation_key):
    """Add translationKey to frontmatter if it doesn't exist."""
    # Check if translationKey already exists
    if 'translationKey:' in frontmatter:
        print(f"  translationKey already exists, skipping...")
        return frontmatter
    
    # Add translationKey after the existing fields
    new_frontmatter = frontmatter.rstrip() + f'\ntranslationKey: "{translation_key}"'
    return new_frontmatter


def process_markdown_file(file_path):
    """Process a single markdown file to add translationKey."""
    print(f"Processing: {file_path}")
    
    # Get filename without extension as translationKey
    filename = Path(file_path).stem
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter and body
        frontmatter, body = extract_frontmatter(content)
        
        if frontmatter is None:
            print(f"  No frontmatter found in {file_path}, skipping...")
            return False
        
        # Add translationKey to frontmatter
        updated_frontmatter = add_translation_key_to_frontmatter(frontmatter, filename)
        
        # If frontmatter wasn't changed, skip writing
        if updated_frontmatter == frontmatter:
            return False
        
        # Reconstruct the file content
        updated_content = f"---\n{updated_frontmatter}\n---\n{body}"
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"  Added translationKey: {filename}")
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