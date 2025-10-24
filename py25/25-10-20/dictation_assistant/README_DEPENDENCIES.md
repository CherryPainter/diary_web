可选依赖（推荐用于更现代的 UI 样式）：

- ttkbootstrap：现代化的 ttk 主题库，提供一组漂亮的主题（如 flatly、cosmo 等）。

安装（在 PowerShell 中）：

```powershell
python -m pip install -r requirements.txt
```

如果你只想安装 `ttkbootstrap`：

```powershell
python -m pip install ttkbootstrap
```

说明：

- 如果 `ttkbootstrap` 已安装，程序会优先使用它的主题（`flatly`），UI 会更现代；
- 如果未安装，程序会回退到原始的 `ttk.Style()`，仍可正常运行（但样式稍微不同）。
