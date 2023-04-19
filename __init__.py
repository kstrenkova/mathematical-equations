bl_info = {
    "name": "Mathematical Equation Generator",
    "author": "Katarina Strenkova",
    "version": (1, 0, 1),
    "blender": (3, 3, 0),
    "location": "3D Viewport",
    "description": "Addon generates 3D mathematical equations from Latex mathematical notation.",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}


if "bpy" in locals():
    import importlib
    importlib.reload(analyser)
    importlib.reload(generator)
    importlib.reload(unicode_db)
    importlib.reload(ui)
else:
    from . import analyser
    from . import generator
    from . import ui
    from . import unicode_db 
    
import bpy     


# register
def register():
    ui.register()


# unregister
def unregister():
    ui.unregister()
 
    
if __name__ == "__main__":
    register()    
        
          

