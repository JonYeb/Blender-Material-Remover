bl_info = {
    "name": "Material Name Remover",
    "author": "Claude",
    "version": (1, 2),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Material Tab",
    "description": "Remove materials whose names include a specified string",
    "category": "Material",
}

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
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
    
    cleanup_method: EnumProperty(
        name="Material Slot Cleanup",
        description="How to handle material slots in objects",
        items=[
            ('NONE', "Don't Clean", "Keep material slots intact (may leave empty slots)"),
            ('CLEAR', "Clear Slots", "Set material slots to None"),
            ('REMOVE', "Remove Slots", "Remove material slots completely")
        ],
        default='REMOVE'
    )
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.materials) > 0
    
    def clean_material_slots(self, material):
        """Remove material from all objects that use it"""
        # For each object in the scene
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and hasattr(obj, 'material_slots'):
                if self.cleanup_method == 'NONE':
                    continue
                
                # We need to work from the end to start for removal
                # to avoid index shifting problems
                slots_to_process = []
                
                # First identify slots with the material
                for slot_index, slot in enumerate(obj.material_slots):
                    if slot.material == material:
                        slots_to_process.append(slot_index)
                
                # Process them in reverse order (important for REMOVE method)
                for slot_index in reversed(slots_to_process):
                    if self.cleanup_method == 'CLEAR':
                        obj.data.materials[slot_index] = None
                    elif self.cleanup_method == 'REMOVE':
                        # We need to set context object for this operation
                        old_active = bpy.context.view_layer.objects.active
                        bpy.context.view_layer.objects.active = obj
                        
                        # Make sure we're in object mode
                        old_mode = obj.mode
                        bpy.ops.object.mode_set(mode='OBJECT')
                        
                        # Select the slot we want to remove
                        obj.active_material_index = slot_index
                        
                        # Remove the slot
                        bpy.ops.object.material_slot_remove()
                        
                        # Restore previous state
                        if old_mode != 'OBJECT':
                            bpy.ops.object.mode_set(mode=old_mode)
                        bpy.context.view_layer.objects.active = old_active
    
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
        
        # First clean material references from objects
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
        layout.prop(self, "cleanup_method")

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
                row = col.row()
                row.label(text=mat.name)
                # Show user count (how many objects use this material)
                row.label(text=f"Used: {mat.users}")
        
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