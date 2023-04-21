# ---------------------------------------------------------------------------
# File name   : ui.py
# Created By  : Katarina Strenkova
# ---------------------------------------------------------------------------

import bpy
import math

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
                       
from mathutils import Vector  # vertices   

# function from analyser
from .analyser import * 
                       

# custom properties
class Custom_PT(bpy.types.PropertyGroup):
    
    latex_text : bpy.props.StringProperty(name="Latex text", default="")
    
    font_path : StringProperty(
        name = "Font",
        description="Choose a font:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    text_scale : bpy.props.FloatProperty(
        name="Scale:",
        default=1.0,
        min=0.01
    )
    
    text_thickness : bpy.props.FloatProperty(
        name="Thickness:",
        default=0.0,
        min=0.0
    )
    
    text_location : bpy.props.FloatVectorProperty(
        name="Location",
        subtype='XYZ'
    )
    
    text_rotation : bpy.props.FloatVectorProperty(
        name="Rotation",
        subtype='EULER'
    )


# main addon panel
class OBJECT_PT_ME(bpy.types.Panel):
    bl_label = "Mathematical Equations"
    bl_idname = "OBJECT_PT_ME"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Equations'
    
    # drawing main panel
    def draw(self, context):  
        layout = self.layout
        scene = context.scene
        cus_pt = scene.custom_prop
        
        layout.prop(cus_pt, "latex_text")
        layout.prop(cus_pt, "font_path")
        layout.prop(cus_pt, "text_scale")
        layout.prop(cus_pt, "text_thickness")
        
        row = layout.row(align=True)
        
        col = row.column()
        col.prop(cus_pt,'text_location')
        
        col2 = row.column()
        col2.prop(cus_pt,'text_rotation')
              
        row2 = layout.row(align=True)
        props = row2.operator("wm.addtextop")     

        
# add text    
class WM_OT_AddText(bpy.types.Operator):
    bl_label = "Add Text"
    bl_idname = "wm.addtextop"
    
    def execute(self, context):
        scene = context.scene
        cus_pt = scene.custom_prop
        
        # create class for analysis 
        syntax = SyntaxAnalyser(cus_pt.latex_text, context, cus_pt.text_scale, cus_pt.font_path)

        if not syntax.sa_prog():
            warn_msg = 'Mathematical equation was not fully generated. Check system console for more info on this matter.'
            self.report({'WARNING'}, warn_msg)
        
        # all objects in mathematical equation   
        all_obj = context.selected_objects
        
        # add empty object
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
        empty_obj = context.object 
            
        # customize mathematical equation
        for obj in all_obj: 
            # set thickness
            if "Text" in obj.name:
                # for text change extrude parameter
                obj.data.extrude = cus_pt.text_thickness / 2.0       
            else:
                # for other objects apply solidify modifier    
                obj.modifiers["Solidify"].thickness = cus_pt.text_thickness
                obj.modifiers["Solidify"].offset = 0.0

            # set empty object as parent
            obj.parent = empty_obj
            
        # move all objects by moving empty object
        empty_obj.location.x = cus_pt.text_location.x
        empty_obj.location.y = cus_pt.text_location.y
        empty_obj.location.z = cus_pt.text_location.z
           
        # rotate all objects by rotating empty object
        empty_obj.rotation_euler.x = cus_pt.text_rotation.x
        empty_obj.rotation_euler.y = cus_pt.text_rotation.y
        empty_obj.rotation_euler.z = cus_pt.text_rotation.z 
        
        # apply transformation
        bpy.data.objects[empty_obj.name].select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True)
        
        # delete empty object
        bpy.data.objects[empty_obj.name].select_set(True)
        bpy.ops.object.delete()                       
        
        return {'FINISHED'}     
      

# enumeration of all my classes
all_classes = [
    Custom_PT, 
    OBJECT_PT_ME, 
    WM_OT_AddText
]


def register():
    for cls in all_classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.custom_prop = bpy.props.PointerProperty(type=Custom_PT)


def unregister():
    for cls in all_classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.custom_prop
 
