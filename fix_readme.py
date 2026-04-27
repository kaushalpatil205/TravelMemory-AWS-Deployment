import re

with open('old_readme.md', 'r') as f:
    lines = f.readlines()

new_lines = []
in_architecture = False
for line in lines:
    if line.startswith('## 📐 Architecture Diagram'):
        in_architecture = True
        new_lines.append(line)
        continue
    
    if in_architecture and line.startswith('!['):
        new_lines.append('![TravelMemory AWS Architecture](architecture/travelmemory_draxil_site_architecture.png)\n')
        new_lines.append('![TravelMemory Web Architecture](architecture/preview.webp)\n')
        in_architecture = False
        continue
    
    if '![TravelMemory AWS Architecture]' in line and in_architecture:
        continue # Skip the old one if it didn't start with ![
    
    if line.startswith('### How Traffic Flows'):
        in_architecture = False
        
    # Skip any line that contains an image from screenshots
    if re.search(r'!\[.*\]\(screenshots/.*\)', line):
        continue
        
    new_lines.append(line)

with open('README.md', 'w') as f:
    f.writelines(new_lines)

