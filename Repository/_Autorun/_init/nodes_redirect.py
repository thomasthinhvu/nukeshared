# -*- coding: utf-8 -*-
# NukeShared - ép menu của plugin trong _AutoInstaller\KIT vào Nodes\<Danh mục>\<tên plugin>
# Đặt file này vào:  Repository\_Autorun\_init\nodes_redirect.py
# (file trong _init được nạp trước khi menu.py của các plugin chạy)
#
# Cách hoạt động: bọc nuke.menu() và nuke.toolbar(). Khi một menu.py/init.py nằm trong KIT
# gọi addCommand/addMenu, script tìm ngược call stack để biết plugin nào đang gọi,
# rồi đổi đường dẫn sang Nodes/<CATEGORY>/<tên plugin>/... Nên không cần sửa code plugin.

import os
import sys
import nuke

# ==== CẤU HÌNH ====
# Tự nhận user: lấy thư mục ~ của máy hiện tại (C:\Users\<user> trên Windows).
# Nếu NukeShared không nằm trong ~\.nuke thì đặt biến môi trường NS_KIT_DIR.
KIT_DIR = os.environ.get("NS_KIT_DIR") or os.path.join(
    os.path.expanduser("~"), ".nuke", "NukeShared 2.6", "Repository", "_AutoInstaller", "KIT")
TARGET_MENU = "Nodes"        # menu đích
CATEGORY = "KIT"             # danh mục gốc bên trong Nodes
# Đổi đường dẫn riêng cho từng plugin (tên = tên folder plugin trong KIT). Không ghi thì dùng CATEGORY/<tên>.
PATH_OVERRIDE = {
    # "TimeTracker": "Tools/TimeTracker",
    # "tabtabtab-nuke-master": "Filter/Tabtabtab",
}
# Plugin nào muốn giữ nguyên menu gốc thì thêm tên folder vào đây
# Plugin tự tra cứu menu gốc (menu('Edit').menu('Stamps')) sẽ lỗi nếu bị đổi đường dẫn,
# nên đưa vào đây. Stamps-1.2.0 đã được thêm sẵn.
PASS_THROUGH = {"Stamps-1.2.0"}
# ==================

_KIT = os.path.normcase(os.path.abspath(KIT_DIR))
_orig_menu = nuke.menu
_orig_toolbar = nuke.toolbar


def _owner_plugin():
    """Tìm ngược call stack: nếu có frame đến từ KIT thì trả về tên folder plugin."""
    f = sys._getframe(2)
    while f is not None:
        fn = os.path.normcase(os.path.abspath(f.f_code.co_filename))
        if fn.startswith(_KIT + os.sep):
            return fn[len(_KIT) + 1:].split(os.sep)[0]
        f = f.f_back
    return None


def _redirect(plugin, path):
    if plugin in PASS_THROUGH:
        return None
    base = PATH_OVERRIDE.get(plugin, CATEGORY + "/" + plugin)
    rest = path.lstrip("/")
    # bỏ tiền tố trùng tên plugin: "TimeTracker/Show Window" -> "KIT/TimeTracker/Show Window"
    if rest.startswith(plugin + "/"):
        rest = rest[len(plugin) + 1:]
    return base + "/" + rest


class _Proxy(object):
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def _add(self, fn_name, path, *args, **kwargs):
        plugin = _owner_plugin()
        new_path = _redirect(plugin, path) if plugin else None
        if new_path is None:
            return getattr(self._obj, fn_name)(path, *args, **kwargs)
        return getattr(_orig_menu(TARGET_MENU), fn_name)(new_path, *args, **kwargs)

    def addCommand(self, path, *args, **kwargs):
        return self._add("addCommand", path, *args, **kwargs)

    def addMenu(self, path, *args, **kwargs):
        return self._add("addMenu", path, *args, **kwargs)


def _menu(name, *a, **k):
    return _Proxy(_orig_menu(name, *a, **k))


def _toolbar(name, *a, **k):
    # toolbar (có icon trên thanh) cũng bị đẩy vào menu Nodes, nên không còn icon rời
    return _Proxy(_orig_menu(TARGET_MENU))


nuke.menu = _menu
nuke.toolbar = _toolbar
print("[nodes_redirect] plugin trong KIT -> Nodes\\%s" % CATEGORY)