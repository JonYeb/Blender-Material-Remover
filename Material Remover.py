bl_info = {
    "name": "Material Name Remover",
    "author": "Claude",
    "version": (1, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Material Tab",
    "description": "Remove materials whose names include a specified string",
    "category": "Material",
}

import bpy
from bpy.props import StringProperty, BoolProperty
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
    
    replace_in_objects: BoolProperty(
        name="Replace in Objects",
        description="Replace removed materials with default in all objects",
        default=True
    )
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.materials) > 0
    
    def clean_material_slots(self, material):
        """Remove material from all objects that use it"""
        # For each object in the scene
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and hasattr(obj, 'material_slots'):
                # Check each material slot in the object
                for slot_index, slot in enumerate(obj.material_slots):
                    if slot.material == material:
                        # Remove the material from this slot
                        obj.data.materials[slot_index] = None
    
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
        
        # First clean material references from objects if requested
        if self.replace_in_objects:
            for mat in materials_to_remove:
                self.clean_material_slots(mat)
        
        # Then remove the materials
        for mat in materials_to_remove:
            bpy.data.materials.remove(mat)
        
        # Report success
        self.report({'INFO'}, f"Removed {count} material(s) containing '{pattern}'")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "pattern")
        layout.prop(self, "replace_in_objects")

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
        
        # Show list of materials if there are not too many
        if mat_count <= 20:  # Only show list if there aren't too many materials
            layout.label(text="Materials:")
            box = layout.box()
            col = box.column()
            for mat in bpy.data.materials:
                col.label(text=mat.name)
        
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