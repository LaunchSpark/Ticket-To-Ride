import os
import importlib.util
from collections import defaultdict


def extract_imports(file_content):
    """
    Extract import lines from the file content.
    """
    import_lines = []
    for line in file_content.splitlines():
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            import_lines.append(stripped)
    return import_lines


def clean_import_block(import_lines):
    """
    Deduplicate and sort import lines, separating 'import' and 'from' blocks.
    """
    import_set = set()
    from_set = set()

    for line in import_lines:
        if line.startswith('import '):
            import_set.add(line)
        elif line.startswith('from '):
            from_set.add(line)

    sorted_imports = sorted(import_set)
    sorted_froms = sorted(from_set)

    if sorted_imports and sorted_froms:
        return '\n'.join(sorted_imports) + '\n\n' + '\n'.join(sorted_froms)
    else:
        return '\n'.join(sorted_imports + sorted_froms)


def test_import_availability(import_line):
    """
    Check if a module can be imported (by checking spec only).
    """
    try:
        if import_line.startswith('import '):
            module = import_line.split('import ')[1].split()[0]
        elif import_line.startswith('from '):
            module = import_line.split('from ')[1].split()[0]
        else:
            return True  # Skip non-standard

        spec = importlib.util.find_spec(module)
        if spec is None:
            return False
        return True
    except Exception:
        return False


def process_file(file_path):
    """
    Process a Python file and return its cleaned import block, found imports, and broken imports.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    import_lines = extract_imports(content)
    if not import_lines:
        return None, [], []

    cleaned_import_block = clean_import_block(import_lines)

    broken_imports = []
    for imp in import_lines:
        if not test_import_availability(imp):
            broken_imports.append(imp)

    return cleaned_import_block, list(set(import_lines)), broken_imports


def walk_and_display(directory):
    """
    Walk through directory and display cleaned imports, broken imports, and global summary.
    """
    project_imports = defaultdict(list)  # Import -> list of files using it
    all_broken_imports = defaultdict(list)  # Import -> files with issues

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                cleaned_imports, raw_imports, broken_imports = process_file(path)
                if cleaned_imports:
                    print(f"\n{'=' * 80}")
                    print(f"📄 {path}")
                    print('-' * 80)
                    print(cleaned_imports)
                    if broken_imports:
                        print("\n⚠️  Broken imports detected:")
                        for bi in broken_imports:
                            print(f"   ❗ {bi}")
                            all_broken_imports[bi].append(path)
                    print('=' * 80)

                    for imp in raw_imports:
                        project_imports[imp].append(path)

    # Global summary
    print(f"\n{'#' * 80}")
    print("📚 GLOBAL IMPORT SUMMARY")
    print(f"{'#' * 80}")
    for imp, files in sorted(project_imports.items()):
        print(f"\n{imp}\n  Used in:")
        for f in files:
            print(f"    - {f}")

    if all_broken_imports:
        print(f"\n{'#' * 80}")
        print("❗ GLOBAL BROKEN IMPORTS SUMMARY")
        print(f"{'#' * 80}")
        for imp, files in sorted(all_broken_imports.items()):
            print(f"\n{imp}\n  Fails in:")
            for f in files:
                print(f"    - {f}")
    else:
        print("\n✅ No broken imports detected!")


if __name__ == "__main__":
    target_dir = input("Enter the path to your project directory: ").strip()
    if os.path.isdir(target_dir):
        walk_and_display(target_dir)
        print("\n🎉 Done analyzing imports and checking for errors!")
    else:
        print("❌ Invalid directory path.")
