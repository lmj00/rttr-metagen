import os
import re


def generate_cpp_code(class_name, functions, properties):
    cpp_code = f"""
RTTR_REGISTRATION
{{
    using namespace rttr;

    registration::class_<{class_name}>("{class_name}")
        .constructor<const std::wstring&>()
    (
        policy::ctor::as_std_shared_ptr
    )
"""
    for f in functions:
        cpp_code += f"        .method(\"{f}\", &{class_name}::{f})\n"

    property_lines = [f"        .property(\"{p}\", &{class_name}::{p})" for p in properties]
    cpp_code += '\n'.join(property_lines) + ';\n'

    cpp_code += "}\n"
    return cpp_code


def process_header_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    class_ptn = r'\[CLASS\]\s*class\s+(\w+)'
    function_ptn = r'\[FUNCTION\]\s*\n(?:.*?\s+)*?(\w+)\s*\(.*?\)'
    property_ptn = r'\[PROPERTY\]\s*\n\s*(.*?);'

    class_matches = re.findall(class_ptn, content)
    function_matches = re.findall(function_ptn, content)
    property_matches = re.findall(property_ptn, content)

    print(class_matches)
    print(function_matches)
    print(property_matches)

    if not class_matches and (function_matches or property_matches):
        class_name = os.path.splitext(os.path.basename(file_path))[0]
        print(class_name)
    elif not class_matches and not function_matches and not property_matches:
        print(f'Skip {file_path}')
        return
    else:
        class_name = class_matches[0]

    property_names = [prop.split()[-1] for prop in property_matches]

    generated_code = generate_cpp_code(class_name, function_matches, property_names)

    cpp_file_path = os.path.splitext(file_path)[0] + ".cpp"

    if os.path.exists(cpp_file_path):
        with open(cpp_file_path, 'r', encoding='utf-8') as cpp_file:
            cpp_content = cpp_file.read()

        rttr_ptn = r'RTTR_REGISTRATION\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        cpp_content = re.sub(rttr_ptn, '', cpp_content).strip()

        cpp_content += '\n\n' + generated_code

        with open(cpp_file_path, 'w', encoding='utf-8') as cpp_file:
            cpp_file.write(cpp_content)

        print(f"Updated {cpp_file_path}")

    else:
        with open(cpp_file_path, 'w', encoding='utf-8') as cpp_file:
            cpp_file.write(generated_code)
        print(f"Generated {cpp_file_path}")


base_directories = ['Game', 'Engine']

for base_dir in base_directories:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.h'):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}...")
                process_header_file(file_path)
