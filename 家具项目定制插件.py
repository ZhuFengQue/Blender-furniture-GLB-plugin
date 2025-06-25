bl_info = {
    "name": "快速创建材质并应用贴图",
    "author": "Your Name",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "location": "View3D > N Panel > 快速工具",
    "description": "为选中的对象创建材质、启用节点、加载贴图并自动连接",
    "category": "Object",
}

import bpy
import os
import re
import webbrowser

# 添加全局属性用于显示 GLB 路径
bpy.types.Scene.glb_file_path = bpy.props.StringProperty(
    name="GLB 文件路径",
    description="最近一次导出的 GLB 文件路径"
)

# Operator: 创建材质并加载贴图
class OBJECT_OT_create_material_with_texture(bpy.types.Operator):
    bl_idname = "object.create_material_with_texture"
    bl_label = "创建材质并加载贴图"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "没有选中任何对象")
            return {'CANCELLED'}

        for obj in selected_objects:
            mat_name = f"{obj.name}_mat"

            if mat_name in bpy.data.materials:
                material = bpy.data.materials[mat_name]
            else:
                material = bpy.data.materials.new(name=mat_name)

            material.use_nodes = True
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            nodes.clear()

            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            output = nodes.new('ShaderNodeOutputMaterial')
            bsdf.location = (0, 0)
            output.location = (200, 0)
            links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

            # Texture Coordinate + Mapping
            tex_coord = nodes.new('ShaderNodeTexCoord')
            mapping = nodes.new('ShaderNodeMapping')
            tex_coord.location = (-700, 0)
            mapping.location = (-550, 0)
            links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

            texture_map = {"_D": None, "_N": None, "_ORM": None}

            for file in self.files:
                fullpath = os.path.join(os.path.dirname(self.filepath), file.name)
                base_name = os.path.splitext(os.path.basename(fullpath))[0]

                suffix = None
                for key in texture_map:
                    if base_name.endswith(key):
                        suffix = key
                        break

                if not suffix:
                    continue

                img = bpy.data.images.load(fullpath)
                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.image = img
                tex_node.label = suffix
                tex_node.location = (-400, 0)
                if suffix in ("_N", "_ORM"):
                    tex_node.image.colorspace_settings.name = 'Non-Color'
                links.new(mapping.outputs['Vector'], tex_node.inputs['Vector'])
                texture_map[suffix] = tex_node

            mix_node = None
            if texture_map["_D"] and texture_map["_ORM"]:
                mix_node = nodes.new('ShaderNodeMixRGB')
                mix_node.blend_type = 'MULTIPLY'
                mix_node.inputs['Fac'].default_value = 1.0
                mix_node.location = (-100, 0)

                separate = nodes.new('ShaderNodeSeparateColor')
                separate.location = (-250, -100)

                links.new(texture_map["_ORM"].outputs['Color'], separate.inputs['Color'])
                links.new(separate.outputs['Red'], mix_node.inputs['Color2'])
                links.new(texture_map["_D"].outputs['Color'], mix_node.inputs['Color1'])
                links.new(mix_node.outputs['Color'], bsdf.inputs['Base Color'])

            elif texture_map["_D"]:
                links.new(texture_map["_D"].outputs['Color'], bsdf.inputs['Base Color'])

            if texture_map["_N"]:
                normal_map = nodes.new('ShaderNodeNormalMap')
                normal_map.location = (-200, -200)
                links.new(texture_map["_N"].outputs['Color'], normal_map.inputs['Color'])
                links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

            if texture_map["_ORM"]:
                separate = nodes.new('ShaderNodeSeparateColor')
                separate.location = (-250, -100)
                links.new(texture_map["_ORM"].outputs['Color'], separate.inputs['Color'])
                links.new(separate.outputs['Green'], bsdf.inputs['Roughness'])
                links.new(separate.outputs['Blue'], bsdf.inputs['Metallic'])

            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)

        self.report({'INFO'}, "材质和贴图已成功创建并连接")
        return {'FINISHED'}

# Operator: 刷新贴图
class OBJECT_OT_reload_textures(bpy.types.Operator):
    bl_idname = "object.reload_textures"
    bl_label = "更新贴图"
    bl_description = "重新加载所有贴图节点中的图像"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "没有选中任何对象")
            return {'CANCELLED'}

        for obj in selected_objects:
            if not obj.data.materials:
                continue
            for material in obj.data.materials:
                if not material.use_nodes:
                    continue
                nodes = material.node_tree.nodes
                texture_nodes = [n for n in nodes if n.type == 'TEX_IMAGE']
                reloaded_count = 0
                for tex_node in texture_nodes:
                    if not tex_node.image:
                        continue
                    image_name = os.path.splitext(tex_node.image.name)[0]
                    if image_name.endswith("_D") or image_name.endswith("_N") or image_name.endswith("_ORM"):
                        tex_node.image.reload()
                        reloaded_count += 1
                self.report({'INFO'}, f"【{obj.name}】已重新加载 {reloaded_count} 张贴图")

        return {'FINISHED'}

# Operator: 设置单位(英寸)
class SCENE_OT_set_unit_to_inches(bpy.types.Operator):
    bl_idname = "scene.set_unit_to_inches"
    bl_label = "设置单位(英寸)"
    bl_description = "将场景单位设置为英制（英寸）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.unit_settings.system = 'IMPERIAL'
        scene.unit_settings.length_unit = 'INCHES'
        self.report({'INFO'}, "单位已设置为：英制（英寸）")
        return {'FINISHED'}

# Operator: 导出GLB(以贴图文件数字部分命名)
class OBJECT_OT_export_selected_to_glb(bpy.types.Operator):
    bl_idname = "object.export_selected_to_glb"
    bl_label = "导出GLB"
    bl_description = "将选中对象导出为GLB文件，文件名为贴图数字命名"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "没有选中任何对象")
            return {'CANCELLED'}

        texture_path = None
        for obj in selected_objects:
            if not obj.data.materials:
                continue
            for material in obj.data.materials:
                if not material.use_nodes:
                    continue
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        image_name = os.path.splitext(node.image.name)[0]
                        if image_name.endswith("_D") or image_name.endswith("_N") or image_name.endswith("_ORM"):
                            texture_path = node.image.filepath_raw
                            break
                if texture_path:
                    break
            if texture_path:
                break

        if not texture_path:
            self.report({'ERROR'}, "未找到贴图路径，请先应用贴图")
            return {'CANCELLED'}

        texture_dir = os.path.dirname(texture_path)
        base_name = os.path.basename(texture_path)
        file_prefix = os.path.splitext(base_name)[0]

        match = re.search(r'\d+', file_prefix)
        glb_name = f"{match.group()}.glb" if match else f"{file_prefix}.glb"
        export_path = os.path.join(texture_dir, glb_name)

        # ✅ 强制删除已有文件（防止覆盖失败）
        try:
            if os.path.exists(export_path):
                os.remove(export_path)
        except Exception as e:
            self.report({'ERROR'}, f"无法删除旧文件（可能被占用）: {str(e)}")
            return {'CANCELLED'}

        # 导出GLB并禁用动画
        try:
            bpy.ops.export_scene.gltf(
                filepath=export_path,
                export_format='GLB',
                use_selection=True,
                export_animations=False
            )
            self.report({'INFO'}, f"已导出 GLB 文件: {export_path}")
        except Exception as e:
            self.report({'ERROR'}, f"导出失败: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Operator: 创建空对比图
class OBJECT_OT_create_blank_comparison_image(bpy.types.Operator):
    bl_idname = "object.create_blank_comparison_image"
    bl_label = "创建空对比图"
    bl_description = "在纹理贴图目录中创建一个空白对比图（100x100px）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "没有选中任何对象")
            return {'CANCELLED'}

        texture_path = None
        for obj in selected_objects:
            if not obj.data.materials:
                continue
            for material in obj.data.materials:
                if not material.use_nodes:
                    continue
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        image_name = os.path.splitext(node.image.name)[0]
                        if image_name.endswith("_D") or image_name.endswith("_N") or image_name.endswith("_ORM"):
                            texture_path = node.image.filepath_raw
                            break
                if texture_path:
                    break
            if texture_path:
                break

        if not texture_path:
            self.report({'ERROR'}, "未找到贴图路径，请先应用贴图")
            return {'CANCELLED'}

        texture_dir = os.path.dirname(texture_path)
        base_name = os.path.basename(texture_path)
        file_prefix = os.path.splitext(base_name)[0]

        # 提取纯数字部分
        match = re.search(r'\d+', file_prefix)
        if not match:
            self.report({'ERROR'}, "文件名不含数字，无法生成对比图名称")
            return {'CANCELLED'}

        comparison_name = f"{match.group()}_对比图.png"
        comparison_path = os.path.join(texture_dir, comparison_name)

        # 使用 Blender 自带 API 创建空白图像
        try:
            # 创建新图像（100x100 像素）
            img = bpy.data.images.new(name="BlankComparisonImage", width=100, height=100)

            # 设置像素数据（RGBA，白色透明背景）
            # 每个像素有4个通道，共100x100像素
            pixels = [1.0] * (100 * 100 * 4)  # RGBA 各通道为1.0（白色+透明）
            img.pixels = pixels  # 将像素数据写入图像

            # 保存为 PNG 文件
            img.filepath_raw = comparison_path
            img.file_format = 'PNG'
            img.save()

            # 删除内存中的临时图像（避免占用资源）
            bpy.data.images.remove(img)

            self.report({'INFO'}, f"已创建空白对比图: {comparison_path}")
        except Exception as e:
            self.report({'ERROR'}, f"图像创建失败：{str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}
# Operator: 打开网页并显示 GLB 文件路径
class OBJECT_OT_open_glb_viewer(bpy.types.Operator):
    bl_idname = "object.open_glb_viewer"
    bl_label = "网站查看GLB文件"
    bl_description = "打开 modelviewer.dev 并显示 GLB 文件路径"
    bl_options = {'REGISTER'}

    def execute(self, context):
        glb_path = self.get_last_exported_glb_path()

        if not glb_path:
            self.report({'ERROR'}, "未找到 GLB 文件路径")
            return {'CANCELLED'}

        context.scene.glb_file_path = glb_path
        webbrowser.open("https://modelviewer.dev/editor/")
        self.report({'INFO'}, "已打开浏览器")
        return {'FINISHED'}

    def get_last_exported_glb_path(self):
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            return None

        texture_path = None
        for obj in selected_objects:
            if not obj.data.materials:
                continue
            for material in obj.data.materials:
                if not material.use_nodes:
                    continue
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        image_name = os.path.splitext(node.image.name)[0]
                        if image_name.endswith("_D") or image_name.endswith("_N") or image_name.endswith("_ORM"):
                            texture_path = node.image.filepath_raw
                            break
                if texture_path:
                    break
            if texture_path:
                break

        if not texture_path:
            return None

        texture_dir = os.path.dirname(texture_path)
        base_name = os.path.basename(texture_path)
        file_prefix = os.path.splitext(base_name)[0]

        match = re.search(r'\d+', file_prefix)
        glb_name = f"{match.group()}.glb" if match else f"{file_prefix}.glb"
        export_path = os.path.join(texture_dir, glb_name)
        return bpy.path.abspath(export_path)

# Operator: 复制 GLB 路径
class OBJECT_OT_copy_glb_path(bpy.types.Operator):
    bl_idname = "object.copy_glb_path"
    bl_label = "复制 GLB 路径"
    bl_description = "将当前 GLB 文件路径复制到剪贴板"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        glb_path = context.scene.glb_file_path
        if not glb_path:
            self.report({'ERROR'}, "没有可用的 GLB 文件路径")
            return {'CANCELLED'}

        context.window_manager.clipboard = glb_path
        self.report({'INFO'}, f"已复制路径: {glb_path}")
        return {'FINISHED'}

# Operator: 打开作者 GitHub 页面
class OBJECT_OT_open_author_github(bpy.types.Operator):
    bl_idname = "object.open_author_github"
    bl_label = "ZhuFengQue"
    bl_description = "打开作者的 GitHub 页面"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        webbrowser.open("https://github.com/ZhuFengQue/Blender-furniture-GLB-plugin")
        self.report({'INFO'}, "正在打开 ZhuFengQue 的 GitHub 页面")
        return {'FINISHED'}

# Operator: 创建尺寸说明文件
class OBJECT_OT_create_dimension_note_file(bpy.types.Operator):
    bl_idname = "object.create_dimension_note_file"
    bl_label = "创建尺寸说明"
    bl_description = "尺寸制作不协调，已在两尺寸正确的情况下，适当修改.txt"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "没有选中任何对象")
            return {'CANCELLED'}

        texture_path = None
        for obj in selected_objects:
            if not obj.data.materials:
                continue
            for material in obj.data.materials:
                if not material.use_nodes:
                    continue
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        image_name = os.path.splitext(node.image.name)[0]
                        if image_name.endswith("_D") or image_name.endswith("_N") or image_name.endswith("_ORM"):
                            texture_path = node.image.filepath_raw
                            break
                if texture_path:
                    break
            if texture_path:
                break

        if not texture_path:
            self.report({'ERROR'}, "未找到贴图路径，请先应用贴图")
            return {'CANCELLED'}

        texture_dir = os.path.dirname(texture_path)
        note_filename = "尺寸制作不协调，已在两尺寸正确的情况下，适当修改.txt"
        note_filepath = os.path.join(texture_dir, note_filename)

        # 创建空的 txt 文件
        try:
            with open(note_filepath, 'w', encoding='utf-8') as f:
                f.write("")  # 留空
            self.report({'INFO'}, f"已创建尺寸说明文件：{note_filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"无法创建文件：{str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}


# Panel: 添加到 N 面板
class VIEW3D_PT_quick_material_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '快速工具'
    bl_label = '创建材质'

    def draw(self, context):
        layout = self.layout

        layout.label(text="单位设置:")
        layout.operator(SCENE_OT_set_unit_to_inches.bl_idname, icon='MOD_LENGTH')
        layout.separator()

        layout.operator(OBJECT_OT_create_material_with_texture.bl_idname, icon='MATERIAL')
        layout.separator()
        layout.operator(OBJECT_OT_reload_textures.bl_idname, icon='FILE_REFRESH')
        layout.separator()
        layout.operator(OBJECT_OT_export_selected_to_glb.bl_idname, icon='EXPORT')
        layout.separator()
        layout.operator(OBJECT_OT_open_glb_viewer.bl_idname, icon='URL')

        layout.separator()
        if context.scene.glb_file_path:
            layout.label(text="GLB 文件路径:")
            row = layout.row()
            row.prop(context.scene, "glb_file_path", text="")
            layout.operator("object.copy_glb_path", icon='COPYDOWN', text="复制 GLB 路径到剪贴板")

        layout.separator()
        layout.operator("object.create_blank_comparison_image", icon='IMAGE_DATA', text="创建空对比图")

        layout.separator()
        layout.operator("object.create_dimension_note_file", icon='TEXT', text="创建尺寸说明")

        layout.separator()
        layout.operator("object.open_author_github", text="ZhuFengQue", icon='URL')



classes = (
    SCENE_OT_set_unit_to_inches,
    OBJECT_OT_create_material_with_texture,
    OBJECT_OT_reload_textures,
    OBJECT_OT_export_selected_to_glb,
    OBJECT_OT_open_glb_viewer,
    OBJECT_OT_copy_glb_path,
    OBJECT_OT_open_author_github,  
    OBJECT_OT_create_blank_comparison_image,
    OBJECT_OT_create_dimension_note_file,  
    VIEW3D_PT_quick_material_panel,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.glb_file_path = bpy.props.StringProperty()

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.glb_file_path

if __name__ == "__main__":
    register()