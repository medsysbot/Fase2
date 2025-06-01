import os
import re


def check_template_references():
    missing = []
    for root, _, files in os.walk('.'):  # Search all python files
        for fname in files:
            if fname.endswith('.py'):
                path = os.path.join(root, fname)
                with open(path) as f:
                    for line_no, line in enumerate(f, 1):
                        code_line = line.split('#')[0]
                        m = re.search(r'TemplateResponse\("([^"]+)"', code_line)
                        if m:
                            tpl = m.group(1)
                            if not os.path.exists(os.path.join('templates', tpl)):
                                missing.append((path, line_no, tpl))
    if missing:
        for path, line_no, tpl in missing:
            print(f'Falta template: {tpl} referenciado en {path}:{line_no}')
    else:
        print('Todos los templates están presentes.')


if __name__ == '__main__':
    check_template_references()
