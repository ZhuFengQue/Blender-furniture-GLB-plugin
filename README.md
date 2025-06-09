# 家具项目定制插件使用说明

## 📦 插件功能概览

| 功能 | 说明 |
|------|------|
| 设置单位(英寸) | 点击设置Blender单位系统为“英寸"，长度单位设置为"英寸" |
| 创建材质并加载贴图 | 根据选中的网格的命名，自动添加命名为"网格名_mat"的材质球; 然后选择贴图(根据后缀_D/_N/_ORM)自动创建并连接材质节点 |
| 更新贴图 | 修改过贴图后，点击刷新 |
| 导出GLB | 自动导出GLB文件，位置在贴图所在文件夹，文件命名为贴图文件名的 **纯数字** 部分 |
| 网站查看GLB文件 | 点击打开网站(https://modelviewer.dev/editor/) |
| 复制GLB文件路径到剪贴板 | 复制路径，方便在文件夹中定位文件 |
| ZhuFengQue | 打开作者的GitHub主页查看最新源码和说明 |
---

## ⚙️ 安装与启用（安装插件或拖入文本编辑器）

1. 打开 Blender，编辑>偏好设置>插件>安装，选择“家具项目定制插件.py”文件，成功安装后勾选插件名称以启用
2. 或者，打开 Blender，在文本编辑器中拖入脚本，点击运行。
![image](https://github.com/user-attachments/assets/e8b7e057-dfda-4cb8-85a5-fc97cc7abc7e)
3. 按N键打开侧边栏，选择“快速工具”
![image](https://github.com/user-attachments/assets/d603dfec-8e20-4b0f-ab66-9ac615f23d6e)

---

## 🔧 推荐工作流

### 1. 在Blender中(直接以英寸为单位)处理好模型后，使用桥接插件在RizomUV中处理UV。
![image](https://github.com/user-attachments/assets/56e7edee-a2b4-49f1-81ca-9898eeae5a89)

### 2. 模型UV处理好后，进入Pt(SP)中制作贴图。导出贴图时使用标准命名模板，使用纹理组命名，直接导出到提交文件夹。
![image](https://github.com/user-attachments/assets/de59edcb-2f3d-4ec5-b947-e550338c18fb)

### 3. 准备好提交文件夹结构。在Blender中按要求命名模型，使用插件自动命名和创建材质球和材质节点并导出glb文件，同时打开网站查看，确认或修改。

### 4. 在此流程制作过程中，每个物件只需要手动命名两次（Blender模型和Pt纹理组）。以Blender为中心的软件流转，简化流程。

### 5. 注意，Blender网格（数据）命名内外可能不同，为避免出现问题可以在最后导出时使用插件批量重命名统一内外命名。
![image](https://github.com/user-attachments/assets/bdf77082-e82d-468d-bb29-c4c4a6f380f6)


---

## ❗ 注意事项

- 插件兼容 Blender 3.0 及以上版本

---
