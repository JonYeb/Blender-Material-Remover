bl_info = {
    "name": "Material Name Remover",
    "author": "Claude",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Material Tab",
    "description": "Remove materials whose names include a specified string",
    "category": "Material",
}

import bpy
from bpy.props import StringProperty
from bpy.types import Operator, Panel

class MATERIAL_OT_remove_by_name_pattern(Operator):
    """Remove all materials that include the specified string in their names"""
    bl_idname = "material.remove_by_name_pattern"
    bl_label = "Remove Materials By Name Pattern"
    bl_options = {'REGISTER', 'UNDO'}
    
    pattern: StringProperty(
        name="Pattern",
        description="String pattern to search for in material names",
        default=""
    )
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.materials) > 0
    
    def execute(self, context):
        pattern = self.pattern.strip()
        
        if not pattern:
            self.report({'ERROR'}, "Please enter a search pattern")
            return {'CANCELLED'}
        
        # Find materials with names containing the pattern
        materials_to_remove = [mat for mat in bpy.data.materials if pattern in mat.name]
        
        if not materials_to_remove:
            self.report({'INFO'}, f"No materials found containing '{pattern}'")
            return {'CANCELLED'}
        
        # Count how many materials will be removed
        count = len(materials_to_remove)
        
        # Remove the materials
        for mat in materials_to_remove:
            mat_name = mat.name  # Store name before removal
            bpy.data.materials.remove(mat)
        
        # Report success
        self.report({'INFO'}, f"Removed {count} material(s) containing '{pattern}'")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class MATERIAL_PT_remove_panel(Panel):
    """Panel for material removal operations"""
    bl_label = "Material Remover"
    bl_idname = "MATERIAL_PT_remover"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Material"
    
    def draw(self, context):
        layout = self.layout
        
        # Display count of materials
        mat_count = len(bpy.data.materials)
        layout.label(text=f"Materials in scene: {mat_count}")
        
        # Operator button
        layout.operator("material.remove_by_name_pattern")

classes = (
    MATERIAL_OT_remove_by_name_pattern,
    MATERIAL_PT_remove_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()