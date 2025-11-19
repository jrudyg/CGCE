#!/usr/bin/env python3
"""
Scanner Bullet Ingestion Script for Project CC

Ingests Scanner bullet output and appends normalized rows to knowledge_base.csv,
de-duplicating by (date, company, product).

Input: JSON file or stdin containing list of scanner bullets
Output: Appends to /02_structured/knowledge_base.csv
"""

import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple


# Field names for the knowledge base CSV
FIELDNAMES = [
    'date',
    'company',
    'product',
    'customer',
    'region',
    'threat_opportunity',
    'source',
    'confidence'
]

# Path to knowledge base CSV
KB_PATH = Path('02_structured/knowledge_base.csv')


def load_existing_keys(kb_path: Path) -> Set[Tuple[str, str, str]]:
    """
    Load existing (date, company, product) tuples from knowledge base.

    Args:
        kb_path: Path to knowledge_base.csv

    Returns:
        Set of (date, company, product) tuples
    """
    existing_keys = set()

    if not kb_path.exists():
        return existing_keys

    try:
        with open(kb_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (
                    row.get('date', '').strip(),
                    row.get('company', '').strip(),
                    row.get('product', '').strip()
                )
                existing_keys.add(key)
    except Exception as e:
        print(f"Warning: Error reading existing knowledge base: {e}", file=sys.stderr)

    return existing_keys


def normalize_bullet(bullet: Dict) -> Dict:
    """
    Normalize a scanner bullet to knowledge base format.

    Args:
        bullet: Dictionary containing scanner bullet data

    Returns:
        Normalized dictionary with standardized field names
    """
    # Handle various possible field name variations
    return {
        'date': bullet.get('date', '').strip(),
        'company': bullet.get('company', '').strip(),
        'product': bullet.get('product', bullet.get('product/capability', bullet.get('capability', ''))).strip(),
        'customer': bullet.get('customer', bullet.get('customer/location', bullet.get('location', ''))).strip(),
        'region': bullet.get('region', '').strip(),
        'threat_opportunity': bullet.get('threat_opportunity', bullet.get('threat/opportunity', bullet.get('threat', bullet.get('opportunity', '')))).strip(),
        'source': bullet.get('source', bullet.get('source link', bullet.get('source_link', ''))).strip(),
        'confidence': bullet.get('confidence', '').strip().upper()
    }


def validate_bullet(bullet: Dict) -> Tuple[bool, str]:
    """
    Validate that a bullet has required fields.

    Args:
        bullet: Normalized bullet dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if not bullet['date']:
        return False, "Missing required field: date"
    if not bullet['company']:
        return False, "Missing required field: company"
    if not bullet['product']:
        return False, "Missing required field: product"

    # Validate confidence level if present
    if bullet['confidence'] and bullet['confidence'] not in ('H', 'M', 'L', ''):
        return False, f"Invalid confidence level: {bullet['confidence']} (must be H, M, or L)"

    return True, ""


def ensure_kb_exists(kb_path: Path) -> None:
    """
    Ensure knowledge base CSV exists with headers.

    Args:
        kb_path: Path to knowledge_base.csv
    """
    # Create directory if it doesn't exist
    kb_path.parent.mkdir(parents=True, exist_ok=True)

    # Create file with headers if it doesn't exist
    if not kb_path.exists():
        with open(kb_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def append_bullets(bullets: List[Dict], kb_path: Path) -> Dict[str, int]:
    """
    Append new bullets to knowledge base CSV.

    Args:
        bullets: List of scanner bullet dictionaries
        kb_path: Path to knowledge_base.csv

    Returns:
        Dictionary with counts: {'added': int, 'skipped': int, 'errors': int}
    """
    stats = {'added': 0, 'skipped': 0, 'errors': 0}

    # Load existing keys for de-duplication
    existing_keys = load_existing_keys(kb_path)

    # Ensure KB file exists
    ensure_kb_exists(kb_path)

    # Process and append bullets
    with open(kb_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)

        for i, bullet in enumerate(bullets, 1):
            try:
                # Normalize the bullet
                normalized = normalize_bullet(bullet)

                # Validate
                is_valid, error_msg = validate_bullet(normalized)
                if not is_valid:
                    print(f"Error in bullet {i}: {error_msg}", file=sys.stderr)
                    stats['errors'] += 1
                    continue

                # Check for duplicate
                key = (normalized['date'], normalized['company'], normalized['product'])
                if key in existing_keys:
                    stats['skipped'] += 1
                    continue

                # Write new row
                writer.writerow(normalized)
                existing_keys.add(key)
                stats['added'] += 1

            except Exception as e:
                print(f"Error processing bullet {i}: {e}", file=sys.stderr)
                stats['errors'] += 1

    return stats


def main():
    """Main entry point for the script."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Input file not found: {input_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)

    # Ensure data is a list
    if isinstance(data, dict):
        bullets = [data]
    elif isinstance(data, list):
        bullets = data
    else:
        print("Error: Input must be a JSON object or array", file=sys.stderr)
        sys.exit(1)

    # Process bullets
    stats = append_bullets(bullets, KB_PATH)

    # Print summary
    print("\n=== Scanner Bullet Ingestion Summary ===")
    print(f"Rows added:   {stats['added']}")
    print(f"Rows skipped: {stats['skipped']} (duplicates)")
    print(f"Errors:       {stats['errors']}")
    print(f"Total processed: {stats['added'] + stats['skipped'] + stats['errors']}")

    if stats['errors'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
