with open(r'C:\Users\Pro\Desktop\EmballageProject\backend\products\templates\products\home.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r'C:\Users\Pro\Desktop\EmballageProject\backend\products\templates\products\home.html', 'w', encoding='utf-8') as f:
    f.writelines(lines[:240])

print("File fixed - kept first 240 lines")
