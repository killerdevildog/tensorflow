#!/usr/bin/env python3
"""Update TensorFlow Java version references in documentation files.

This script helps address issue #96799 by providing a tool to update
outdated TensorFlow Java version references from 0.3.3 to the current
version 1.1.0 in documentation files.

Usage:
    python update_java_version_docs.py [--dry-run] <file1> [file2] ...
"""

import argparse
import re
import sys
from pathlib import Path

# Version mappings
OLD_VERSION = "0.3.3"
NEW_VERSION = "1.1.0"
OLD_SNAPSHOT = "0.4.0-SNAPSHOT"
NEW_SNAPSHOT = "1.2.0-SNAPSHOT"

# Patterns to update
VERSION_PATTERNS = [
    # Maven dependency version
    (rf'<version>{re.escape(OLD_VERSION)}</version>', f'<version>{NEW_VERSION}</version>'),
    # Gradle dependency version
    (rf"version: '{re.escape(OLD_VERSION)}'", f"version: '{NEW_VERSION}'"),
    (rf'version: "{re.escape(OLD_VERSION)}"', f'version: "{NEW_VERSION}"'),
    # Generic version references
    (rf'\b{re.escape(OLD_VERSION)}\b', NEW_VERSION),
    # Snapshot versions
    (rf'\b{re.escape(OLD_SNAPSHOT)}\b', NEW_SNAPSHOT),
]

# Common dependency patterns
DEPENDENCY_PATTERNS = [
    # Maven dependencies
    (r'(<dependency>\s*<groupId>org\.tensorflow</groupId>\s*<artifactId>tensorflow-core-platform</artifactId>\s*<version>)0\.3\.3(</version>)',
     r'\g<1>1.1.0\g<2>'),
    # Gradle dependencies
    (r"(compile group: 'org\.tensorflow', name: 'tensorflow-core-platform', version: ')0\.3\.3(')",
     r'\g<1>1.1.0\g<2>'),
]


def update_file_content(content, dry_run=False):
    """Update version references in file content."""
    updated_content = content
    changes_made = []
    
    # Apply version patterns
    for pattern, replacement in VERSION_PATTERNS:
        new_content = re.sub(pattern, replacement, updated_content)
        if new_content != updated_content:
            changes_made.append(f"Updated version reference: {pattern} -> {replacement}")
            updated_content = new_content
    
    # Apply dependency patterns
    for pattern, replacement in DEPENDENCY_PATTERNS:
        new_content = re.sub(pattern, replacement, updated_content, flags=re.MULTILINE | re.DOTALL)
        if new_content != updated_content:
            changes_made.append(f"Updated dependency: {OLD_VERSION} -> {NEW_VERSION}")
            updated_content = new_content
    
    return updated_content, changes_made


def update_java_requirements_section(content):
    """Update Java version requirements if found."""
    # Update Java version requirement from 8 to 11
    java_req_pattern = r'(Java\s+)8(\s+(?:and\s+)?above|(?:\s+or\s+)?higher|\+)'
    replacement = r'\g<1>11\2'
    
    updated = re.sub(java_req_pattern, replacement, content, flags=re.IGNORECASE)
    if updated != content:
        return updated, ["Updated Java requirement from 8+ to 11+"]
    return content, []


def process_file(file_path, dry_run=False):
    """Process a single file for version updates."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Update version references
        updated_content, version_changes = update_file_content(original_content, dry_run)
        
        # Update Java requirements
        updated_content, req_changes = update_java_requirements_section(updated_content)
        
        all_changes = version_changes + req_changes
        
        if updated_content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✓ Updated {file_path}")
            else:
                print(f"✓ Would update {file_path}")
            
            for change in all_changes:
                print(f"  - {change}")
            return True
        else:
            print(f"✗ No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Update TensorFlow Java version references in documentation files"
    )
    parser.add_argument(
        "files", 
        nargs='+', 
        help="Documentation files to update"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be changed without making actual changes"
    )
    
    args = parser.parse_args()
    
    print(f"TensorFlow Java Documentation Version Updater")
    print(f"Updating {OLD_VERSION} -> {NEW_VERSION}")
    print(f"Updating {OLD_SNAPSHOT} -> {NEW_SNAPSHOT}")
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
        print()
    
    files_updated = 0
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"✗ File not found: {file_path}")
            continue
        
        if process_file(path, args.dry_run):
            files_updated += 1
    
    print()
    print(f"Summary: {files_updated} of {len(args.files)} files updated")
    
    if files_updated > 0:
        print()
        print("Changes made:")
        print(f"  - Updated TensorFlow Java version: {OLD_VERSION} -> {NEW_VERSION}")
        print(f"  - Updated snapshot version: {OLD_SNAPSHOT} -> {NEW_SNAPSHOT}")
        print("  - Updated Java requirements where applicable")
        print()
        print("This addresses TensorFlow issue #96799")


if __name__ == "__main__":
    main()
