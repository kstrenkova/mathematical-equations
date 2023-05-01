# ---------------------------------------------------------------------------
# File name   : generator.py
# Created By  : Katarina Strenkova
# ---------------------------------------------------------------------------

import bpy
import math
from bpy_extras.object_utils import object_data_add  # add sqrt symbol

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
                       
from mathutils import Vector  # vertices

# unicode characters database
from .unicode_db import unicode_chars                             


# function generates text in given font
# special case for sum and integral symbol when the scaling is 3.5 bigger
def gen_text(context, text, font):
    # generate basic text
    bpy.ops.object.text_add(enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.font.delete(type='PREVIOUS_WORD')
    bpy.ops.font.text_insert(text=text)
    bpy.ops.object.editmode_toggle()
    
    # generated text
    active_obj = context.active_object
    
    # set text font if one is chosen
    if not font == "":
        active_obj.data.font = font
        active_obj.data.size = 1.0
    
    # sum, prod and integral symbols
    if text == '\u2211' or text == '\u222b' or text == '\u220f':
        # scale and move symbol
        active_obj.scale.x = 3.5
        active_obj.scale.y = 3.5
        # apply scale
        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
    
    # apply changes
    bpy.ops.object.select_all(action='DESELECT') # deselect all objects
    bpy.data.objects[active_obj.name].select_set(True)
    

# function positions text according to given parameters
def gen_position(param, move):
    
    obj = bpy.context.active_object  # save active object
    
    # scale object
    obj.scale.x = param.scale
    obj.scale.y = param.scale
    
    obj.location.x = param.width  # move by width (x)
    obj.location.y = param.height  # move by height (y)
    obj.location.z = 0.0
    
    # add text width
    if move:
        # get corners of bounding box
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        obj_dimension = bbox[4].x * param.scale
        param.width += obj_dimension + (0.1 * param.scale)  # space


# function gets object into collection
def gen_collection(context, collection, base_collection):
    # active object
    active_obj = bpy.context.active_object
    
    for obj in bpy.data.collections[collection].objects:
        # object is already in collection
        if obj.name == active_obj.name:
            return
        
    bpy.data.collections[collection].objects.link(active_obj)
    bpy.data.collections[base_collection].objects.unlink(active_obj)
    

# function creates new collection    
def gen_new_collection(context, coll_name, parent_collection):
    # add new collection
    collection = bpy.data.collections.new(coll_name)
    bpy.data.collections[parent_collection].children.link(collection)
    return collection.name      


# function joins collections into parent collection and removes child collection
def gen_join_collections(context, collection, parent_collection):
    # join all objects into one parent collection
    for obj in bpy.data.collections[collection.name].all_objects:
        bpy.data.collections[parent_collection].objects.link(obj)
        bpy.data.collections[collection.name].objects.unlink(obj)
        
    # remove child collection
    bpy.data.collections.remove(collection)    
    

# function generates given mathematic symbol
def gen_math_sym(context, command_name, font):

    # find unicode representation of character
    for char in unicode_chars:
        if char[0] == command_name:
            text = char[1]
            # generate mathematical symbol    
            gen_text(context, text, font)

            return True
        
    # command is not in unicode database
    print("Error, command '" + command_name + "' is not in unicode database!")
    print("It's a possible misspelling or this command is not implemented in this version of addon.")
    return False


# function generates square root symbol
def gen_sqrt_sym(context):

    # symbol vertices
    verts = [
        Vector((-0.5266461968421936, -0.13621671915054321, 0.0)), 
        Vector((-0.40451911091804504, -0.21025631248950958, 0.0)), 
        Vector((-0.3643374443054199, -0.13621671915054321, 0.0)), 
        Vector((-0.15997552871704102, -0.7838898515701294, 0.0)), 
        Vector((-0.15997552871704102, -0.6396166300773621, 0.0)), 
        Vector((0.36744120717048645, 0.35296740531921387, 0.0)), 
        Vector((0.32928138971328735, 0.4122579336166382, 0.0)), 
        Vector((0.4593656659126282, 0.35296740531921387, 0.0)), 
        Vector((0.4593656659126282, 0.4122579336166382, 0.0))
    ]

    edges = []
    faces = [[0, 1, 2], [1, 2, 4, 3], [4, 3, 5, 6], [5, 6, 8, 7]]

    mesh = bpy.data.meshes.new(name="Sqrt")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh)
    
    # location of 3D cursor
    cursor_3D = bpy.context.scene.cursor.location
    
    # set origin for sqrt
    bpy.context.scene.cursor.location += Vector((-0.5266461968421936, -0.8238898515701294, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # set 3D cursor back
    bpy.context.scene.cursor.location = cursor_3D 
    
    # add solidify modifier
    bpy.ops.object.modifier_add(type='SOLIDIFY') 
    
    # recalculate normals in editmode
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.editmode_toggle()


# function moves sqrt symbol according to given parameters
def gen_sqrt_move(context, param, sqrt_param, move):
    
    # position sqrt
    param.height -= 0.25 * param.scale
    gen_position(param, False)
    param.height += 0.25 * param.scale
    
    # apply scale
    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
    
    # don't modify square root symbol
    if not move:
        return
    
    # data of created sqrt symbol
    obj_data = context.active_object.data
    
    # finding most right vertices
    max_x = obj_data.vertices[0].co.x
    for i in obj_data.vertices:
        max_x = max(i.co.x, max_x)                    
    
    # changing length of the upper line of sqrt
    for i in obj_data.vertices:
        new_location = i.co
        if i.co.x == max_x:
            new_location[0] = sqrt_param['x_pos'] - param.width  # x position     
        i.co = new_location  
        
    # finding the heighest vertices
    max_y = obj_data.vertices[0].co.y
    for i in obj_data.vertices:
        max_y = max(i.co.y, max_y)           
        
    line_size = 0.05929052829742433 * param.scale  # size of upper line
    text_height =  param.height - (0.2 * param.scale)  # text height
    move_by = sqrt_param['y_max'] - text_height + (0.2 * param.scale)  # y location and space 
    
    # leave function if height of sqrt is right
    if (max_y - 0.06) > (sqrt_param['y_max'] - text_height + (0.2 * param.scale)):
        return      
        
    # changing height of sqrt symbol
    for i in obj_data.vertices:
        new_location = i.co 
        if i.co.y == max_y:
            new_location[1] = move_by + line_size  # y position upper vertices
        elif i.co.y >= (max_y - (0.06 * param.scale)):
            new_location[1] = move_by  # y position lower vertices     
        i.co = new_location  
        
    # finding the lowest vertices
    min_y = obj_data.vertices[0].co.y
    for i in obj_data.vertices:
        min_y = min(i.co.y, min_y)
        
    line_size = 0.14427322149276733 * param.scale  #  space between lowest points
    move_by = sqrt_param['y_min'] - text_height  
    
    # leave function if low point of sqrt is right
    if min_y < (sqrt_param['y_min'] - text_height):
        return 
    
    # changing lowest point of sqrt symbol
    for i in obj_data.vertices:
        new_location = i.co 
        if i.co.y == min_y:
            new_location[1] = move_by  # y position upper vertice
        elif i.co.y <= (min_y + (0.15 * param.scale)):
            new_location[1] = move_by + line_size # y position lower vertice   
        i.co = new_location   


# function generates line for fractions    
def gen_frac_line(context, param, x_pos):  
    
    verts = [
        Vector((0.0, -0.025 * param.scale, 0.0)), 
        Vector((0.0, 0.025 * param.scale, 0.0)),
        Vector((1.0, 0.025 * param.scale, 0.0)), 
        Vector((1.0, -0.025 * param.scale, 0.0))
    ]

    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name="Line")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh)
    
    # location of 3D cursor
    cursor_3D = bpy.context.scene.cursor.location
    
    # set origin for fraction line
    bpy.context.scene.cursor.location += Vector((0.0, 0.0, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # set 3D cursor back
    bpy.context.scene.cursor.location = cursor_3D
    
    # add solidify modifier
    bpy.ops.object.modifier_add(type='SOLIDIFY')   
    
    # location of line
    bpy.context.active_object.location.x = param.width
    bpy.context.active_object.location.y = param.height + 0.3 * param.scale
    bpy.context.active_object.location.z = 0.0
    
    # data of created fraction line
    obj_data = bpy.context.object.data
    
    # moving fraction line
    for i in obj_data.vertices:
        new_location = i.co
        if i.co.x == 1.0:
            new_location[0] = x_pos - param.width + 0.1 * param.scale  # x position      
        i.co = new_location   
  

# function calculates the scaling and height of text
def gen_calculate(param, text_scale, levels):
    
    lvl_exp = 0  # exponent lvl
    lvl_ix = 0  # index lvl

    # starting height is line height and scale is user given scale
    param.height = param.line
    param.scale = text_scale
    
    # specific scaling in fraction
    if levels.frac == 2:
        param.scale = 0.65 * text_scale
    elif levels.frac > 2:
        param.scale = 0.45 * text_scale  

    # iterating through array of exponents and indexes
    for item in levels.ei_array:
        
        # deciding scaling
        if (lvl_exp + lvl_ix) == 0:
            # depending on fraction level
            if levels.frac < 2:
                param.scale = 0.65 * text_scale 
            else:
                param.scale = 0.45 * text_scale     
        else:
            param.scale = 0.45 * text_scale 

        # adding number of exponent or index
        if item == "exp":
            lvl_exp += 1
            if lvl_exp == 1:
                param.height += (0.75 * param.scale)  # first lvl exponent
            else:
                param.height += (0.5 * param.scale)
        else:
            lvl_ix += 1
            if lvl_ix == 1:
                param.height -= (0.5 * param.scale)  # first lvl index
            else:
                param.height -= (0.25 * param.scale)             


# function moves sum symbol according to given parameters
def gen_move_sum(context, param, collection, sum):
    
    # save sum symbol
    sum_symbol = bpy.data.objects[sum.name]
    
    # get corners of bounding box
    bbox = [sum_symbol.matrix_world @ Vector(corner) for corner in sum_symbol.bound_box]
        
    # parameters of objects in collection
    min_x = gen_min_x(context, collection)
    min_y = gen_min_y(context, collection) 
    max_y = gen_group_height(context, collection)  
    
    # iterate through objects
    for obj in bpy.data.collections[collection].all_objects:
        # add object to array
        sum.array.append(obj.name)
        # move object depending on index or exponent mode
        obj.location.x += bbox[0].x - min_x
        if "SumUpCollection" in collection:
            obj.location.y += bbox[2].y - min_y + 0.25 * param.scale
        else:
            obj.location.y += bbox[0].y - max_y - 0.25 * param.scale
    
    # center text above sum symbol
    exp_ix_width = gen_group_width(context, collection)        
    gen_center_sum(context, sum, collection, exp_ix_width, bbox[4].x)  # sum width        
            
            
# function centers exponent and index for sum symbol
def gen_center_sum(context, sum, collection, exp_ix_width, sum_width):
    
    # find bigger width and calculate movement size
    if exp_ix_width > sum_width:
        diff = exp_ix_width - sum_width
        move_by = (-1) * diff / 2.0 
    else:
        diff = sum_width - exp_ix_width  
        move_by = diff / 2.0

    # move all objects
    for obj in bpy.data.collections[collection].all_objects:
        obj.location.x += move_by   
        

# move sum symbol if index or exponent is longer then symbol
def gen_fin_sum(context, sum, up_collection, down_collection):
    # save sum symbol
    sum_symbol = bpy.data.objects[sum.name]
    
    # get corners of bounding box
    bbox = [sum_symbol.matrix_world @ Vector(corner) for corner in sum_symbol.bound_box]
    
    # find biggest width
    up_width = gen_group_width(context, up_collection)
    down_width = gen_group_width(context, down_collection)
    fin_width = max(up_width, down_width, bbox[4].x)  # sum symbol width
    diff = fin_width - bbox[4].x
    
    # index or exponent is longer than sum symbol
    if diff > 0:
        # select all objects
        bpy.data.objects[sum.name].select_set(True)  # sum symbol
        for item in sum.array:
             bpy.data.objects[item].select_set(True)
             
        # move objects     
        for obj in context.selected_objects: 
            obj.location.x += diff    
            
        fin_width += diff
    
    return fin_width       
                     

# function moves objects in fraction numerator           
def gen_frac_num(context, param, collection):
    
    # get lowest point in collection
    min_y = gen_min_y(context, collection)
    move_by = param.height - min_y + 0.6 * param.scale
    
    # select and move all objects in numerator
    for obj in bpy.data.collections[collection].all_objects:
        obj.select_set(True)  
        obj.location.y += move_by                          


# function moves objects in fraction denominator 
def gen_frac_den(context, param, collection):
    
    # get highest point in collection
    max_y = gen_group_height(context, collection)
    move_by = param.height - max_y + 0.1 * param.scale
    
    # select and move all objects in denominator
    for obj in bpy.data.collections[collection].all_objects:
        obj.select_set(True) 
        obj.location.y += move_by


# function centers objects on x axis
def gen_center(context, obj1, obj2, collection):
    # find wider text
    if obj1 > obj2:
        diff = obj1 - obj2
    else:
        diff = obj2 - obj1
    
    move_by = diff / 2.0 # space between x positions div 2
    
    # move all objects
    for obj in bpy.data.collections[collection].all_objects:
        obj.location.x += move_by 
    

# function returns the furthest x position
def gen_group_width(context, collection):
    
    bpy.ops.object.select_all(action='DESELECT') # deselect all objects
    is_init = False  # set initialisation flag
    
    # select all objects in collection
    for obj in bpy.data.collections[collection].all_objects:  
        obj.select_set(True)
        # get corners of bounding box
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        if not is_init:
            max_x = bbox[4].x
            is_init = True
        else:
            max_x = max(max_x, bbox[4].x)  # finding max x position     
         
    # no objects selected
    if not is_init:
        return 0
        
    return max_x


# function returns the closest x position
def gen_min_x(context, collection):
    
    bpy.ops.object.select_all(action='DESELECT') # deselect all objects
    is_init = False  # set initialisation flag
    
    # select all objects in collection
    for obj in bpy.data.collections[collection].all_objects:  
        obj.select_set(True)
        # get corners of bounding box
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        if not is_init:
            min_x = bbox[0].x
            is_init = True
        else:
            min_x = min(min_x, bbox[0].x)  # finding min x position     
         
    # no objects selected
    if not is_init:
        return 0
        
    return min_x 


# function returns the highest y position      
def gen_group_height(context, collection):
    
    bpy.ops.object.select_all(action='DESELECT') # deselect all objects
    is_init = False  # set initialisation flag
    
    # select all objects in collection
    for obj in bpy.data.collections[collection].all_objects:  
        obj.select_set(True)
        # get corners of bounding box
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        if not is_init:
            max_y = bbox[2].y
            is_init = True
        else:
            max_y = max(max_y, bbox[2].y)  # finding max y position     
         
    # no objects selected
    if not is_init:
        return 0
        
    return max_y 
  
  
# function returns the lowest y position
def gen_min_y(context, collection):
    
    bpy.ops.object.select_all(action='DESELECT') # deselect all objects
    is_init = False  # set initialisation flag
    
    # select all objects in collection
    for obj in bpy.data.collections[collection].all_objects:  
        obj.select_set(True)
        # get corners of bounding box
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        if not is_init:
            min_y = bbox[0].y
            is_init = True
        else:
            min_y = min(min_y, bbox[0].y)  # finding min y position     
         
    # no objects selected
    if not is_init:
        return 0
        
    return min_y
            
            
# function positions matrix figure
def gen_matrix_pos(context, obj_array, param):
    
    # return if matrix has no objects
    if not len(obj_array):
        return
    
    # get maximum number of cells in row
    max_cell_x = 0
    for row in obj_array:
        max_cell_x = max(max_cell_x, len(row))
    
    gen_matrix_x(context, obj_array, param, max_cell_x)  # center by x axis 
    gen_matrix_y(context, obj_array, param, max_cell_x)  # move by y axis     
  
  
# function centers matrix horizontally
def gen_matrix_x(context, obj_array, param, max_cell_x):
     
    i = 0  # collumn number
    while i < max_cell_x:

        max_width = 0
        # iterate through rows
        for row in obj_array:
            # getting maximum width in collumn 'i'
            if i >= len(row):
                cell_width = 0
            else:    
                collection = row[i]
                cell_width = gen_group_width(context, collection)
                
            max_width = max(max_width, cell_width)         
        
        # iterate through rows    
        for row in obj_array: 
            # deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            
            # move objects in next collumn
            if (i+1) < len(row):  
                collection = row[i+1]  
                
                # select objects and find minimum x position
                min_x = gen_min_x(context, collection)          
                       
            # set x position
            for obj in context.selected_objects:
                old_location = obj.location.x
                obj.location.x = max_width + (old_location - min_x) + 0.5 * param.scale
        
        # iterate through rows
        for row in obj_array:
            # center objects in row
            if len(row) > i:    
                collection = row[i]
                cell_width = gen_group_width(context, collection)
                gen_center(context, cell_width, max_width, collection)
                     
        i += 1  # next collumn
     
  
# function moves matrix vertically
def gen_matrix_y(context, obj_array, param, max_cell_x): 
    
    is_init = False  # set initialisation flag
     
    # iterate through rows
    for row in obj_array: 
        # if the row is not empty
        if len(row):
            # getting maximum height in row    
            i = 0  # collumn number
            while i < max_cell_x:
                # first collumn 
                if i == 0:
                    collection = row[i]
                    cell_height = gen_group_height(context, collection) 
                    max_height = cell_height
                # less collumns than maximum    
                elif i >= len(row):
                    cell_height = max_height
                else:    
                    collection = row[i]
                    cell_height = gen_group_height(context, collection)
                    
                max_height = max(max_height, cell_height)
                i += 1  # next cell 
            
            # first iteration    
            if not is_init:
                min_height = max_height + 0.1 * param.scale
                is_init = True        
            
            # move row if its highest point cuts into the upper row
            if max_height > (min_height - 0.1 * param.scale):
                i = 0  # collumn number
                while i < max_cell_x: 
                    # row is not empty
                    if i < len(row):
                        collection = row[i]
                        move_by = max_height - min_height + 0.5 * param.scale  # space
                        
                        # move objects lower
                        for obj in bpy.data.collections[collection].all_objects:
                            obj.location.y -= move_by
                        
                    i += 1  # next cell
            
            # getting minimum height in row 
            i = 0  # collumn number
            while i < max_cell_x: 
                # first collumn 
                if i == 0:
                    collection = row[i]
                    cell_height = gen_min_y(context, collection) 
                    min_height = cell_height
                # less collumns than maximum 
                elif i >= len(row):
                    cell_height = min_height
                else:    
                    collection = row[i]
                    cell_height = gen_min_y(context, collection)
                    
                min_height = min(min_height, cell_height)
                i += 1  # next cell                
 
 
# function calculates position of matrix brackets 
def gen_matrix_param(context, param, collection, xy_size):
    
    # left bracket
    if len(xy_size) == 1:
        # get matrix height
        min_y = gen_min_y(context, collection)
        max_y = gen_group_height(context, collection)
        xy_size.insert(0, max_y)
        xy_size.insert(0, min_y)
    # right bracket    
    else: 
        # get width of bracket
        bracket_width = xy_size.pop()
        # get x_min
        x_min = xy_size.pop()
        # get matrix width 
        matrix_width = gen_group_width(context, collection) + bracket_width - x_min
        xy_size.append(matrix_width)
    
    return xy_size
     
        
# function generates matrix brackets
def gen_brackets(context, param, collection, base_collection, xy_size, left):
    
    # xy_size -> y_min, y_max, x
    
    # move bracket to position
    bpy.context.active_object.location.x = xy_size[2]  # x
    bpy.context.active_object.location.y = xy_size[0]  # y_min
    
    # scale
    matrix_height = xy_size[1] - xy_size[0]  # y_max - y_min
    scale = (matrix_height + 0.5 * param.scale) / context.active_object.dimensions.y
    context.active_object.scale.x = scale / 3.0
    context.active_object.scale.y = scale
    
    # apply changes
    obj_name = context.active_object.name
    bpy.ops.object.select_all(action='DESELECT') # deselect all objects
    bpy.data.objects[obj_name].select_set(True)
    
    # move bracket to align to text
    context.active_object.location.y += context.active_object.dimensions.y / 12.0
    
    # the width of bracket
    bracket_width = context.active_object.location.x + context.active_object.dimensions.x
    
    # left bracket
    if left:
        # move objects
        for obj in bpy.data.collections[collection].all_objects:
            obj.location.x += bracket_width - xy_size[2] + 0.25 * param.scale
            
        # save bracket_width
        xy_size.append(bracket_width)    
    
    # add bracket to collection
    bpy.data.objects[obj_name].select_set(True)  
    gen_collection(context, collection, base_collection)
    
    
# function centers matrix
def gen_matrix_center(param, collection, xy_size, bracket):
    
    # calculate center location
    matrix_height = xy_size[1] - xy_size[0]  # y_max - y_min
    center_loc = xy_size[1] - matrix_height / 2.0 - 0.3 * param.scale
     
    # center matrix into row
    for obj in bpy.data.collections[collection].all_objects:
        obj.location.y -= center_loc            
            
    
          
