import os
import sys
import nuke

# 1. Xác định folder gốc chứa file init.py này
# (C:\Users\Administrator\.nuke\nuke\AutoGizmo\yonader_lib)
base_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Khởi tạo biến chứa folder cần load
target_folder = None

# 3. Check đúng điều kiện mày yêu cầu
if nuke.NUKE_VERSION_MAJOR == 13:
    # Nếu là Nuke 13
    target_folder = "pack-sites-partyPY2"
elif nuke.NUKE_VERSION_MAJOR >= 16:
    # Nếu là Nuke 16 trở lên
    target_folder = "site-packagesPY6"

# 4. Thực hiện add path nếu thỏa mãn điều kiện
if target_folder:
    full_path = os.path.join(base_dir, target_folder)
    
    if os.path.exists(full_path):
        if full_path not in sys.path:
            # Chèn lên đầu sys.path để Nuke ưu tiên tìm ở đây trước
            sys.path.insert(0, full_path)
            print(f"--- [Ulaavi] Loaded library for Nuke {nuke.NUKE_VERSION_MAJOR}: {target_folder} ---")
    else:
        print(f"--- [Ulaavi] WARNING: Folder không tồn tại: {full_path} ---")
else:
    print(f"--- [Ulaavi] Nuke version {nuke.NUKE_VERSION_MAJOR} không nằm trong chỉ định load thư viện ---")

# 5. Add luôn cái Required vào plugin path cho chắc
required_path = os.path.join(base_dir, 'Required')
if os.path.exists(required_path):
    nuke.pluginAddPath(required_path)