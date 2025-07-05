# 20250705更新：
## - 可执行程序：家具项目小工具.exe
### 这是个Python小程序，已打包环境，可以在电脑上直接运行。
| 小工具功能 | 说明 |
|------|------|
| 复制文件夹结构 | 选择**源文件夹**会将文件夹名及其子文件夹结构列出来(方便复制)，选择**目标文件夹**，点击**开始复制**将文件夹及其子文件夹结构(**不包含文件**)复制到指定位置。 |
| 文件命名检测 | 点击**选择工具**，选择文件命名检测；可以检测**源文件夹**中的文件命名中的数字部分与其所在的文件夹名是否一样。不匹配的文件将会在**结果检测**中标注为红色。  |
![image](https://github.com/user-attachments/assets/eead41cd-2c69-42a3-9727-fde97c67c724)
![image](https://github.com/user-attachments/assets/5866df55-b03c-4232-a71e-9c2c66633f40)



# 20250625更新：
## - 导出GLB功能优化：
#### 1. 在我使用的Blender3.4版本中，导出glb文件时使用默认选项可能会包含关键帧信息，与标准要求不符。所以为导出GLB添加了关闭动画的逻辑。
        # 导出GLB并禁用动画
        try:
            bpy.ops.export_scene.gltf(
                filepath=export_path,
                export_format='GLB',
                use_selection=True,
                export_animations=False
            )
#### 2. 在实际使用过程中由于贴图的修改更新，可能会经常重复地导出glb，但是新导出的文件无法覆盖旧文件，只能在每次导出前删除旧文件。 添加了删除旧文件的逻辑，确保每次导出的glb文件都是最新的。
        # ✅ 强制删除已有文件（防止覆盖失败）
        try:
            if os.path.exists(export_path):
                os.remove(export_path)
        except Exception as e:
            self.report({'ERROR'}, f"无法删除旧文件（可能被占用）: {str(e)}")
            return {'CANCELLED'}
## - 添加了两个新功能：
| 新增功能 | 说明 |
|------|------|
| 创建空对比图 | 点击会在贴图所在文件夹创建一个100*100的空白png图片，其命名为贴图名的纯数字部分+“_对比图”，方便在PS导出时直接覆盖。 |
| 创建尺寸说明 | 点击会在贴图所在文件夹创建一个命名为“尺寸制作不协调，已在两尺寸正确的情况下，适当修改”的空白txt文件。 |

---

# 20250611更新：
## 修改分离颜色节点错误导致GLB文件在预览网站渲染异常。
![image](https://github.com/user-attachments/assets/1c13df49-d574-46b9-a719-9cb586cf5b2f)


# 家具项目定制插件使用说明

## 📦 插件功能概览

| 功能 | 说明 |
|------|------|
| 设置单位(英寸) | 点击设置Blender单位系统为“英制"，长度单位设置为"英寸" |
| 创建材质并加载贴图 | 根据选中的网格的命名，自动添加命名为"网格名_mat"的材质球; 然后选择贴图(根据后缀_D/_N/_ORM) **自动创建并连接** 材质节点 |
| 更新贴图 | 修改过贴图后，点击刷新 |
| 导出GLB | 自动导出GLB文件，位置在 **贴图所在** 文件夹，文件命名为贴图文件名的 **纯数字** 部分 |
| 网站查看GLB文件 | 点击打开预览网站(https://modelviewer.dev/editor/) |
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
![image](https://github.com/user-attachments/assets/1033d0d0-549f-4e7b-ab49-84925db9bea5)

### 4. 在此流程制作过程中，每个物件只需要手动命名两次（Blender模型和Pt纹理组）。以Blender为中心的软件流转，简化流程。

### 5. 注意，Blender网格（数据）命名内外可能不同，为避免出现问题可以在最后导出时使用插件批量重命名统一内外命名。
![image](https://github.com/user-attachments/assets/bdf77082-e82d-468d-bb29-c4c4a6f380f6)


---

## ❗ 注意事项

- 插件兼容 Blender 3.0 及以上版本

---
