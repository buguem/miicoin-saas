import os

# Create main directories
directories = [
    'src',
    'templates',
    'static',
    'src/bot',
    'src/api',
    'src/utils',
    'static/css',
    'static/js'
]

# Create each directory
for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Create empty __init__.py files in Python packages
python_packages = [
    'src',
    'src/bot',
    'src/api',
    'src/utils'
]

for package in python_packages:
    init_file = os.path.join(package, '__init__.py')
    with open(init_file, 'w') as f:
        pass  # Creates an empty file

print("Project structure created successfully!")
