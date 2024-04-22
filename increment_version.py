import re
from pathlib import Path

def increment_version():
    setup_path = Path('setup.py')
    content = setup_path.read_text()
    # This regex now supports single or double quotes and variable whitespace
    version_match = re.search(r"version\s*=\s*['\"](\d+\.\d+\.\d+)['\"]", content)
    if version_match:
        current_version = version_match.group(1)
        major, minor, patch = map(int, current_version.split('.'))
        new_version = f"{major}.{minor}.{patch + 1}"
        new_content = re.sub(r"version\s*=\s*['\"]\d+\.\d+\.\d+['\"]", f"version='{new_version}'", content)
        setup_path.write_text(new_content)
        print(f"Version updated to: {new_version}")
    else:
        raise ValueError("Version string not found in setup.py")

if __name__ == "__main__":
    increment_version()
