import os


def list_files(startpath):
    to_remove = ['.vscode', '__pycache__', '.venv', '.git', 'build', 'dist']
    for root, dirs, files in os.walk(startpath):
        # Exclure le dossier .venv
        for remove in to_remove:
            if remove in dirs:
                dirs.remove(remove)

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')

if __name__ == "__main__":
    list_files('.')
