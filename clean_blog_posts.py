#!/usr/bin/env python3
"""
Script to clean up erroneous code block markers from blog posts and fix YAML frontmatter.

This script:
- Removes opening code block markers like ```yaml, ```markdown, etc. at the beginning of files
- Removes closing code block markers like ``` at the end of files- Fixes YAML frontmatter by quoting values that contain colons (but preserves dates properly)
- Handles various patterns that LLMs might generate incorrectly
"""

import os
import re
from pathlib import Path

def is_date_string(value):
    """Check if a value looks like an ISO date string."""
    # Match ISO 8601 date format
    return re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$', value.strip())

def fix_yaml_frontmatter(content):
    """
    Fix YAML frontmatter by properly quoting values that contain colons.
    
    Args:
        content (str): The file content
        
    Returns:
        str: Content with fixed YAML frontmatter
    """
    lines = content.split('\n')
    
    # Find YAML frontmatter boundaries
    yaml_start = -1
    yaml_end = -1
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if yaml_start == -1:
                yaml_start = i
            else:
                yaml_end = i
                break
    
    # If no valid YAML frontmatter found, return as is
    if yaml_start == -1 or yaml_end == -1:
        return content
    
    # Process YAML lines
    for i in range(yaml_start + 1, yaml_end):
        line = lines[i]
        
        # Match YAML key-value pairs
        match = re.match(r'^(\s*)([^:]+):\s*(.*)$', line)
        if match:
            indent, key, value = match.groups()
            key = key.strip()
            value = value.strip()
            
            # Skip if value is empty
            if not value:
                continue
            
            # Skip if already quoted or if it's an array
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")) or \
               value.startswith('['):
                # If it's quoted but has trailing spaces, fix it
                if value.startswith('"') and value.endswith('"'):
                    inner_value = value[1:-1].strip()
                    lines[i] = f'{indent}{key}: "{inner_value}"'
                continue
            
            # Don't quote date strings - they should remain unquoted for Astro
            if key.lower() == 'pubdate' or is_date_string(value):
                lines[i] = f'{indent}{key}: {value}'
                continue
            
            # If value contains a colon and isn't already quoted, quote it
            if ':' in value:
                # Use double quotes and escape any existing double quotes
                escaped_value = value.replace('"', '\\"')
                lines[i] = f'{indent}{key}: "{escaped_value}"'
    
    return '\n'.join(lines)

def clean_file_content(content):
    """
    Clean up erroneous code block markers from file content.
    
    Args:
        content (str): The original file content
        
    Returns:
        str: Cleaned content
    """
    lines = content.split('\n')
    
    # Remove opening code block markers at the beginning
    while lines and re.match(r'^```+\w*`*$', lines[0].strip()):
        lines.pop(0)
    
    # Remove trailing empty lines and closing code block markers at the end
    while lines and (not lines[-1].strip() or re.match(r'^```+$', lines[-1].strip())):
        lines.pop()
    
    return '\n'.join(lines)

def process_blog_directory(directory_path):
    """
    Process all markdown files in a directory and clean them up.
    
    Args:
        directory_path (str): Path to the directory containing blog posts
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Directory {directory_path} does not exist")
        return
    
    md_files = list(directory.glob("*.md"))
    
    if not md_files:
        print(f"No markdown files found in {directory_path}")
        return
    
    print(f"Found {len(md_files)} markdown files in {directory_path}")
    
    cleaned_count = 0
    yaml_fixed_count = 0
    
    for md_file in md_files:
        try:
            # Read the file
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Clean code block markers
            cleaned_content = clean_file_content(original_content)
            
            # Fix YAML frontmatter
            yaml_fixed_content = fix_yaml_frontmatter(cleaned_content)
            
            # Only write if content changed
            if yaml_fixed_content != original_content:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_fixed_content)
                
                # Track what was fixed
                if cleaned_content != original_content:
                    print(f"Cleaned code blocks: {md_file.name}")
                    cleaned_count += 1
                if yaml_fixed_content != cleaned_content:
                    print(f"Fixed YAML frontmatter: {md_file.name}")
                    yaml_fixed_count += 1
                
                if cleaned_content == original_content and yaml_fixed_content != cleaned_content:
                    # Only YAML was fixed
                    print(f"Fixed YAML only: {md_file.name}")
            
        except Exception as e:
            print(f"Error processing {md_file.name}: {e}")
    
    print(f"Cleaned code blocks in {cleaned_count} files")
    print(f"Fixed YAML frontmatter in {yaml_fixed_count} files")
    print(f"Total files processed: {len(md_files)} in {directory_path}")

def main():
    """Main function to process all blog directories."""
    blog_directories = [
        "en",
        "pt", 
        "es"
    ]
    
    for directory in blog_directories:
        print(f"\nProcessing {directory}...")
        if os.path.exists(directory):
            process_blog_directory(directory)
        else:
            print(f"Directory {directory} not found, skipping...")
    
    print("\nCleaning completed!")

if __name__ == "__main__":
    main() 