# ---------------------------------------------------------------------------
# File name   : analyser.py
# Created By  : Katarina Strenkova
# ---------------------------------------------------------------------------

import bpy
import addon_utils
import os.path

# functions from generator
from .generator import *


# class for tokens
class Token:
    def __init__(self, token_type, token_value):
        self.type = token_type
        self.value = token_value


# class for parameters
class Parameters:
    def __init__(self, scale, height, width, line):
        self.scale = scale
        self.height = height
        self.width = width
        self.line = line
        
    def create_copy(self):
        copy = Parameters(self.scale, self.height, self.width, self.line)
        return copy     


# class for levels
class Levels:
    def __init__(self, ei_array, exp_ix, frac, matrix):
        self.ei_array = ei_array
        self.exp_ix = exp_ix
        self.frac = frac
        self.matrix = matrix
        
        
# class fot sum        
class Sum:
    def __init__(self, bool, name, array):
        self.bool = bool
        self.name = name
        self.array = array
        
        
# class for matrix        
class Matrix:
    def __init__(self, obj_array, row_num):
        self.obj_array = obj_array
        self.row_num = row_num


# class for lexical analyser
class LexicalAnalyser:
    def __init__(self, latex_text):
        self.text = latex_text

    # function gets the next token
    def get_token(self):
        state = "STATE_START"
        tmp_string = ""

        token = Token("UNKNOWN", "")

        while True:
            # end of input text
            if state == "STATE_START" and self.text == '':
                token.type = "END"
                return token
            elif self.text == '':
                c = "END"
            else:
                c = self.get_char(self.text[0])  # get first character

            # choose the next state
            if state == "STATE_START":
                if c == "BACKSLASH":
                    state = "STATE_COMMAND"
                    self.text = self.text[1:]  # erase read character
                elif c == "OTHER" or c == "COMMAND_SPACES":
                    state = "STATE_TEXT"
                elif c == "WHITESPACE":
                    self.text = self.text[1:]  # erase read character
                    continue
                elif c == "ANGLE_BRACKETS":
                    token.type = "TEXT"
                    token.value = self.text[0]
                    self.text = self.text[1:]  # erase read character
                    return token
                else:
                    token.type = c
                    token.value = self.text[0]
                    self.text = self.text[1:]  # erase read character
                    return token

            # COMMANDS
            elif state == "STATE_COMMAND":
                if self.is_special_char(c):
                    token.type = "SPECIAL_CHAR"
                    token.value = self.text[0]
                    self.text = self.text[1:]  # erase read character
                    return token
                elif c == "BACKSLASH":
                    token.type = "ENTER"
                    token.value = "\\"
                    self.text = self.text[1:]  # erase read character
                    return token
                elif c == "COMMAND_SPACES":
                    token.type = "COMMAND"
                    token.value = self.text[0]
                    self.text = self.text[1:]  # erase read character
                    return token
                elif c == "OTHER":
                    state = "STATE_COMMAND_NAME"
                else:
                    token.type = "COMMAND"
                    token.value = " "
                    self.text = self.text[1:]  # erase read character
                    return token

            # NAME OF THE COMMAND
            elif state == "STATE_COMMAND_NAME":
                if c == "OTHER" and self.text[0].isalpha():
                    tmp_string = tmp_string + self.text[0]
                    self.text = self.text[1:]  # erase read character
                else:
                    token.type = "COMMAND"
                    token.value = tmp_string
                    return token

            # TEXT
            elif state == "STATE_TEXT":
                if c != "OTHER" and c != "COMMAND_SPACES":
                    token.type = "TEXT"
                    token.value = tmp_string
                    return token
                else:
                    tmp_string = tmp_string + self.text[0]
                    self.text = self.text[1:]
                        
    # end of get_token()

    @staticmethod
    # function gets the current character
    def get_char(input_character):
        
        all_char = [
            ('\\', "BACKSLASH"),
            ('{', "OPEN_BRACKET"),
            ('}', "CLOSE_BRACKET"),
            ('^', "CARET"),
            ('_', "UNDERSCORE"),
            ('&', "AMPERSAND"),
            ('!', "COMMAND_SPACES"),
            (';', "COMMAND_SPACES"),
            (':', "COMMAND_SPACES"),
            (',', "COMMAND_SPACES"),
            ('[', "ANGLE_BRACKETS"),
            (']', "ANGLE_BRACKETS"),
            (' ', "WHITESPACE"),
            ('\n', "WHITESPACE")
        ]
        
         # return input character
        for item in all_char:
            if input_character == item[0]:
                return item[1]
 
        return "OTHER"

    @staticmethod
    # function returns if character is a special character or not
    def is_special_char(char):
        
        special_char = [
            "OPEN_BRACKET",
            "CLOSE_BRACKET",
            "AMPERSAND",
            "UNDERSCORE"
        ]
        
        # return if character is special character
        if char in special_char:
            return True
        
        return False

    # function returns token to latex string
    def return_token(self, token):
        if token.type == "COMMAND" or token.type == "SPECIAL_CHAR" or token.type == "ENTER":
            self.text = '\\' + token.value + self.text
        else:
            self.text = token.value + self.text


class SyntaxAnalyser(LexicalAnalyser):
    def __init__(self, latex_text, context, text_scale, font_path):
        super().__init__(latex_text)

        self.context = context
        self.text_scale = text_scale
        self.font_path = font_path
        self.font = []  # default_font, unicode_font
        self.sqrt = False
        self.sum = Sum(False, "", [])
        self.base_collection = ""
        self.current_collection = ""
        self.parameters = Parameters(text_scale, 0.0, 0.0, 0.0)
        self.levels = Levels([], False, 0, False)
        self.matrix = Matrix([[]], 0)

    @staticmethod
    # function returns if character is a type of space
    def is_space(char):
        # all types of spaces
        all_spaces = [
            '!', ',', ':', ';', ' ', "quad", "qquad"
        ]
        
        if char in all_spaces:
            return True
        
        return False
    
    @staticmethod
    # function returns space size
    def get_space_size(char, scale):
        
        space_sizes = [
            ('!', -0.1),
            (',', 0.15),
            (':', 0.2),
            (';', 0.25),
            (' ', 0.3),
            ("quad", 0.6),
            ("qquad", 1.2)
        ]
        
        # return space size
        for item in space_sizes:
            if char == item[0]:
                return item[1] * scale
            
        return 0.0        
    
    @staticmethod
    # function returns bracket type
    def get_mx_brackets(value):
        
        brackets = [
            ("bmatrix", ('[', ']')),
            ("Bmatrix", ('{', '}')),
            ("pmatrix", ('(', ')')),
            ("vmatrix", ('|', '|')),
            ("Vmatrix", ('||', '||'))
        ]
        
        # return type of brackets
        for item in brackets:
            if value == item[0]:
                return item[1]
        
        return ('', '')

    @staticmethod
    # function returns if token is <CONST>
    def is_const(token):
        all_types = [
            "TEXT", "SPECIAL_CHAR", "UNDERSCORE", "CARET", "ENTER"
        ]
        # <CONST>
        if token.type in all_types:
            return True

        return False

    @staticmethod
    # function returns if token is <COMMAND>
    def is_command(token):
        # <COMMAND>
        if token.type == "OPEN_BRACKET":
            return True

        elif token.type == "COMMAND":
            if token.value != "end":
                return True

        return False

    @staticmethod
    # function returns if token is <BLOCK>
    def is_block(token):
        # <BLOCK>
        if token.type == "COMMAND" and token.value == "begin":
            return True

        return False
    
    # function returns if sequence of tokens is a matrix figure
    # { text }
    def is_matrix_figure(self, mode, parent_collection, xy_size):
        # {
        token = self.get_token()
        if token.type == "OPEN_BRACKET":
            # text
            all_matrix = [
                "bmatrix", "Bmatrix", "matrix", "pmatrix", "Pmatrix", "vmatrix", "Vmatrix"
            ]
            token = self.get_token()
            if token.type == "TEXT" and token.value in all_matrix:
                # gets the bracket symbol
                bracket_type = self.get_mx_brackets(token.value)
                # }
                token = self.get_token()
                if token.type == "CLOSE_BRACKET":
                         
                    # at the end of matrix
                    if mode == "end":
                        # position matrix
                        gen_matrix_pos(self.context, self.matrix.obj_array, self.parameters)
                        
                        # get matrix parameters
                        xy_size = gen_matrix_param(self.context, self.parameters, parent_collection, xy_size)
                        
                        if not bracket_type[0] == '':
                            # generate left bracket of matrix
                            gen_text(self.context, bracket_type[0], self.font[1])
                            gen_brackets(self.context, self.parameters, parent_collection, self.base_collection, xy_size, True)
                            xy_size = gen_matrix_param(self.context, self.parameters, parent_collection, xy_size)
                            
                            # generate right bracket of matrix
                            gen_text(self.context, bracket_type[1], self.font[1])
                            gen_brackets(self.context, self.parameters, parent_collection, self.base_collection, xy_size, False)
                        
                        # center matrix into row
                        gen_matrix_center(self.parameters, parent_collection, xy_size, bracket_type[0])
                        
                        # clear matrix array
                        self.parameters.line = 0.0
                        self.matrix.obj_array = [[]]
                        self.matrix.row_num = 0
                    
                    return True
                else:
                    print("Error, missing closing bracket to command!")

        print("Error in the syntax of enviroment 'matrix'!")
        return False

    # <MATRIX> -> <COMMAND> <MORE_MATRIX>
    #          -> <CONST> <MORE_MATRIX>
    #          -> & <MORE_MATRIX>
    #          -> epsilon
    def sa_matrix(self, tmp_param, parent_collection):
        token = self.get_token()

        if self.is_command(token) or self.is_const(token) or token.type == "AMPERSAND":
            # <COMMAND>
            if self.is_command(token):
                self.return_token(token)
                if self.sa_command():
                    # <MORE_MATRIX>
                    if self.sa_more_matrix(tmp_param, parent_collection):
                        return True

            # <CONST>
            elif self.is_const(token):
                # enter (\\)
                if token.type == "ENTER":
                    # matrix cell collection
                    self.current_collection = gen_new_collection(self.context, "MatrixCellCollection", parent_collection)
                    
                    # add new array that represents row
                    self.matrix.obj_array.append([])
                    self.matrix.row_num += 1
                    self.matrix.obj_array[self.matrix.row_num].append(self.current_collection)
                    
                    # set width to start and height lower
                    self.parameters.width = tmp_param.width
                    self.parameters.line -= 1.0 * self.text_scale
                      
                self.return_token(token)  # return token
            
                if self.sa_const():  
                    # <MORE_MATRIX>
                    if self.sa_more_matrix(tmp_param, parent_collection):
                        return True

            # &
            elif token.type == "AMPERSAND":
                # matrix cell collection
                self.current_collection = gen_new_collection(self.context, "MatrixCellCollection", parent_collection)
                
                # add collection to row
                self.matrix.obj_array[self.matrix.row_num].append(self.current_collection)
                if self.sa_more_matrix(tmp_param, parent_collection):
                    # <MORE_MATRIX>
                    return True  

        else:
            # epsilon
            self.return_token(token)
            return True

        print("Error in the syntax of enviroment 'matrix'!")
        return False
    
    # <MORE_MATRIX> -> <MATRIX> <MORE_MATRIX>
    #               -> epsilon
    def sa_more_matrix(self, tmp_param, parent_collection):
        token = self.get_token()
        if self.is_command(token) or self.is_const(token) or token.type == "AMPERSAND":
            self.return_token(token)
            if not self.sa_matrix(tmp_param, parent_collection):  # <MATRIX>
                return False

            return self.sa_more_matrix(tmp_param, parent_collection)  # <MORE_MATRIX>

        else:
            # epsilon
            self.return_token(token)

        return True

    # <SQRT> -> [ <MORE_TERM> ] { <MORE_TERM> }
    #        -> { <MORE_TERM> }
    def sa_sqrt(self, mode):
        
        self.sqrt = True  # inside sqrt
        token = self.get_token()

        # [
        if token.type == "TEXT" and token.value == "[":
            # creating square root multipliers
            self.levels.ei_array.append("exp")
            self.parameters.width += 0.1  # space before multipliers
            
            # <MORE_TERM>
            if self.sa_more_term():
                # ]
                token = self.get_token()
                if token.type == "TEXT" and token.value == "]":
                    self.sqrt = False
                    self.levels.ei_array.pop()
                    gen_calculate(self.parameters, self.text_scale, self.levels)
                    
                    # {
                    token = self.get_token()
                    if token.type == "OPEN_BRACKET":
                        self.return_token(token)
                        # { <MORE_TERM> }
                        return self.sa_sqrt("multiple")

        # {
        elif token.type == "OPEN_BRACKET":
            # saving parameters
            gen_calculate(self.parameters, self.text_scale, self.levels)
            tmp_param = self.parameters.create_copy()
            
            # saving parent collection to bind children collections to
            parent_collection = self.current_collection
            
            sqrt_width = 0.855927586555481  # width of square root symbol
            
            # mode 'single' doesn't have multipliers
            if mode == "single":
                self.parameters.width += sqrt_width * self.parameters.scale
            else:    
                tmp_param.width -= (sqrt_width - 0.4) * self.parameters.scale
                self.parameters.width += 0.4 * self.parameters.scale
            
            # square root collection
            sqrt_coll = bpy.data.collections.new("SqrtCollection")
            bpy.data.collections[parent_collection].children.link(sqrt_coll)
            self.current_collection = sqrt_coll.name
            
            # <MORE_TERM>
            if self.sa_more_term():
                # }
                token = self.get_token()
                if token.type == "CLOSE_BRACKET":
                    # bool to determine moving of sqrt symbol
                    use_param = False
                    sqrt_param = {
                        "x_pos": 0,
                        "y_min": 0,
                        "y_max": 0
                    }

                    # gets parameters of text under square root
                    if len(bpy.data.collections[self.current_collection].all_objects): 
                        use_param = True
                        sqrt_param['x_pos'] = gen_group_width(self.context, self.current_collection)
                        sqrt_param['y_min'] = gen_min_y(self.context, self.current_collection)
                        sqrt_param['y_max'] = gen_group_height(self.context, self.current_collection)   
                    
                    # generating sqrt symbol
                    gen_sqrt_sym(self.context)
                    gen_collection(self.context, parent_collection, self.base_collection)  # symbol into collection
                    
                    # move sqrt symbol
                    gen_sqrt_move(self.context, tmp_param, sqrt_param, use_param)
                    
                    # join collection into parent collection
                    gen_join_collections(self.context, sqrt_coll, parent_collection)
                    self.current_collection = parent_collection  # set current collection
                    
                    return True
                else:
                    print("Error, missing closing bracket to command!")

        print("Error in the syntax of command 'sqrt'!")
        return False
    
    # function returns if sequence of tokens is a fraction figure
    # { <MORE_TERM >}
    def is_frac_figure(self):
        # {
        token = self.get_token()
        if token.type == "OPEN_BRACKET":
            # <MORE_TERM>
            if self.sa_more_term():
                # }
                token = self.get_token()
                if token.type == "CLOSE_BRACKET":
                    return True
                else:
                    print("Error, missing closing bracket to command!")
                
        return False               
    
    # <FRAC> -> { <MORE_TERM> } { <MORE_TERM> }
    def sa_frac(self):
        # increasing level of fraction
        self.levels.frac += 1
        self.parameters.width += 0.1 * self.parameters.scale  # space before fraction
        
        # saving parent collection to bind children collections to
        parent_collection = self.current_collection
        
        # saving current parameters
        gen_calculate(self.parameters, self.text_scale, self.levels)
        tmp_param = self.parameters.create_copy()
        
        # numerator collection
        num_coll = bpy.data.collections.new("NumeratorCollection")
        bpy.data.collections[parent_collection].children.link(num_coll)
        self.current_collection = num_coll.name
        
        # { <MORE_TERM> }
        if self.is_frac_figure():
            # initiate numerator width
            num_width = 0
                
            # gets the furthest x position
            if len(bpy.data.collections[self.current_collection].all_objects):    
                num_width = gen_group_width(self.context, self.current_collection)    
            
            # move numerator objects
            gen_calculate(self.parameters, self.text_scale, self.levels)
            gen_frac_num(self.context, self.parameters, num_coll.name)
            
            # denominator collection
            den_coll = bpy.data.collections.new("DenominatorCollection")
            bpy.data.collections[parent_collection].children.link(den_coll)
            self.current_collection = den_coll.name
            
            # reloading last width
            self.parameters.width = tmp_param.width
        
            # { <MORE_TERM> }
            if self.is_frac_figure():
                # initiate denominator width
                den_width = 0   
                    
                # gets the furthest x position
                if len(bpy.data.collections[self.current_collection].all_objects):    
                    den_width = gen_group_width(self.context, self.current_collection)
                
                # move denominator objects
                gen_calculate(self.parameters, self.text_scale, self.levels)
                gen_frac_den(self.context, self.parameters, den_coll.name) 
                
                # finding longer text width
                if den_width > num_width:
                    line_length = den_width
                    center_coll = num_coll.name
                else:
                    line_length = num_width
                    center_coll = den_coll.name 
                
                # generating fraction line    
                gen_frac_line(self.context, tmp_param, line_length)    
                
                # center numerator and denominator
                gen_center(self.context, num_width, den_width, center_coll)
                gen_collection(self.context, den_coll.name, self.base_collection)
                
                # join numerator and denominator collections
                gen_join_collections(self.context, den_coll, num_coll.name)
                
                # join denominator collection into parent collection
                gen_join_collections(self.context, num_coll, parent_collection)
                self.current_collection = parent_collection  # set current collection
                
                # set back line width
                self.parameters.width = line_length + 0.2 * self.parameters.scale  # space
                
                # decreasing level of fraction
                self.levels.frac -= 1                 
                    
                return True
            else:
                # remove denominator collection if false         
                bpy.data.collections.remove(den_coll)
                print("Error in the syntax of command 'frac'!")            
                return False
                 
        # remove numerator collection if false         
        bpy.data.collections.remove(num_coll) 
        print("Error in the syntax of command 'frac'!")           
        return False
    
    # <SUM> -> index_exponent
    #       -> epsilon
    def sa_sum(self, symbol):

        # generate sum symbol
        if not gen_math_sym(self.context, symbol, self.font[1]):
            return False
                    
        gen_calculate(self.parameters, self.text_scale, self.levels)
        self.parameters.height -= 0.4 * self.parameters.scale  # move lower
        gen_position(self.parameters, True)        
        gen_collection(self.context, self.current_collection, self.base_collection)
        
        self.sum.name = self.context.active_object.name  # save sum object
        token = self.get_token()  # get next token
        
        # check index or exponent for sum
        if token.type == "UNDERSCORE" or token.type == "CARET":
            self.return_token(token)
            self.sum.bool = True  # index and exponent for sum
            
            # index_exponent
            if self.sa_const():
                # clear variables for sum
                self.sum.bool = False 
                self.sum.array = []
                return True
        else:
            # epsilon
            self.return_token(token) 
            return True
    
    # function finds the wrong use of exponents and indexes
    #          generates index + exponent
    def is_both_ei(self, mode, brackets, saved_width, parent_collection, exp_ix_coll):
        
        token = self.get_token()  # get next token

        # multiple uses of exponent + index
        if self.levels.exp_ix and (token.type == "UNDERSCORE" or token.type == "CARET"):
            print("Error, use of both index and exponent is only permitted once!")
            return False
                    
        # exponent + index
        elif (mode == "CARET" and token.type == "UNDERSCORE") \
            or (mode == "UNDERSCORE" and token.type == "CARET"):
            
            self.return_token(token)
            self.levels.exp_ix = True  # is inside cyclus
            
            # special sum exponent or index
            if self.sum.bool:
                gen_calculate(self.parameters, self.text_scale, self.levels)
                gen_move_sum(self.context, self.parameters, exp_ix_coll.name, self.text_scale, self.levels, self.sum)  
            elif not brackets:
                gen_calculate(self.parameters, self.text_scale, self.levels)
                gen_position(self.parameters, False)
            self.levels.ei_array.pop()
            
            # save first text width    
            first_width = gen_group_width(self.context, self.current_collection)
  
            if brackets:
                self.parameters.width = saved_width
            
            # call const function
            if not self.sa_const():
                return False
            
            self.levels.exp_ix = False  # is out of cyclus
            
            # calculate final width
            sec_width = gen_group_width(self.context, self.current_collection)
            fin_width = max(first_width, sec_width)
            
            # calculate final width for sum symbol
            if self.sum.bool:
                fin_width = gen_fin_sum(self.context, self.sum, fin_width)      
            
            self.parameters.width = fin_width + 0.1 * self.parameters.scale
            
        elif token.type == "UNDERSCORE" or token.type == "CARET":
            print("Error, use brackets to correctly make multiple exponents or indexes!")
            return False
        
        else:
            self.return_token(token)
            
            # special sum exponent or index
            if self.sum.bool:
                gen_calculate(self.parameters, self.text_scale, self.levels)
                gen_move_sum(self.context, self.parameters, exp_ix_coll.name, self.text_scale, self.levels, self.sum)  
            # move when its not already moved
            elif not brackets:
                gen_calculate(self.parameters, self.text_scale, self.levels)
                gen_position(self.parameters, not self.levels.exp_ix)
            self.levels.ei_array.pop()
                
        # join collection into parent collection
        gen_join_collections(self.context, exp_ix_coll, parent_collection)
        self.current_collection = parent_collection  # set current collection
            
        return True    
        

    # <AFTER_EI> -> { <MORE_TERM> }
    #            -> text
    #            -> special_symbols
    #            -> command (special group of commands)
    def sa_after_ei(self, mode):
        # saving parent collection to bind children collections to
        parent_collection = self.current_collection
        
        # exponent or index collection
        exp_ix_coll = bpy.data.collections.new("ExponentIndexCollection")
              
        bpy.data.collections[parent_collection].children.link(exp_ix_coll)
        self.current_collection = exp_ix_coll.name
        
        # {
        token = self.get_token()
        if token.type == "OPEN_BRACKET":
            tmp_width = self.parameters.width
            # <MORE_TERM>
            if self.sa_more_term():
                # }
                token = self.get_token()
                if token.type == "CLOSE_BRACKET":
                    return self.is_both_ei(mode, True, tmp_width, parent_collection, exp_ix_coll)
                else:
                    print("Error, missing closing bracket to command!")

        # text
        # special_symbols
        elif token.type == "TEXT" or token.type == "SPECIAL_CHAR":
            # generate text
            gen_text(self.context, token.value, self.font[0])
            gen_collection(self.context, self.current_collection, self.base_collection)
        
            return self.is_both_ei(mode, False, self.parameters.width, parent_collection, exp_ix_coll)
        
        # command (special group of commands)
        elif token.type == "COMMAND":
            # generate mathematic symbol
            gen_math_sym(self.context, token.value,  self.font[1])
            gen_collection(self.context, self.current_collection, self.base_collection)   
        
            return self.is_both_ei(mode, False, self.parameters.width, parent_collection, exp_ix_coll)
        
        print("Error in creating exponent of index!")
        return False

    # <CONST> -> text
    #         -> special_symbols
    #         -> enter
    #         -> index_exponent <IN_BRACKETS>
    def sa_const(self):
        token = self.get_token()

        # text + special_symbols
        if token.type == "TEXT" or token.type == "SPECIAL_CHAR":
            gen_text(self.context, token.value, self.font[0])
            gen_calculate(self.parameters, self.text_scale, self.levels)
            gen_position(self.parameters, True)
            gen_collection(self.context, self.current_collection, self.base_collection)
            
            return True
        
        # enter
        elif token.type == "ENTER":
            # skip if not in matrix
            return True

        # index_exponent
        elif token.type == "UNDERSCORE":
            self.levels.ei_array.append("ix")
            gen_calculate(self.parameters, self.text_scale, self.levels)
            # <IN_BRACKETS>
            if self.sa_after_ei("UNDERSCORE"):
                return True

        elif token.type == "CARET":
            self.levels.ei_array.append("exp")
            gen_calculate(self.parameters, self.text_scale, self.levels)
            # <IN_BRACKETS>
            if self.sa_after_ei("CARET"):
                return True

        return False

    # <COMMAND> -> { <MORE_TERM> }
    #           -> sqrt <SQRT>
    #           -> frac <FRAC>
    #           -> command <COMM_ARG>
    def sa_command(self):
        # {
        token = self.get_token()
        if token.type == "OPEN_BRACKET":
            # <MORE_TERM>
            if self.sa_more_term():
                # }
                token = self.get_token()
                if token.type == "CLOSE_BRACKET":
                    return True
                else:
                    print("Error, missing closing bracket to command")

        # COMMAND type
        elif token.type == "COMMAND":
            # sqrt
            if token.value == "sqrt":
                # <SQRT>
                if self.sa_sqrt("single"):
                    return True
            
            # frac
            elif token.value == "frac":
                # <FRAC>
                if self.sa_frac():
                    return True 
                
            # sum
            elif token.value == "sum" or token.value == "prod":
                 # <SUM>
                 if self.sa_sum(token.value):
                     return True     
        
            # command spaces    
            elif self.is_space(token.value):
                # get space size and add it to text width
                space = self.get_space_size(token.value, self.parameters.scale)
                self.parameters.width += space
                return True                        

            # command
            else:
                # mathematic symbols
                if not gen_math_sym(self.context, token.value, self.font[1]):
                    return False
                
                gen_calculate(self.parameters, self.text_scale, self.levels)
                gen_position(self.parameters, True)
                
                # move prod and integral symbol
                if token.value == "int":
                    self.context.active_object.location.y -= 0.3 * self.parameters.scale   
                    self.parameters.width -= 0.2 * self.parameters.scale
                
                gen_collection(self.context, self.current_collection, self.base_collection)
                return True

        return False

    # <BLOCK> -> begin { text } <MATRIX> end { text }
    def sa_block(self):
        
        # begin
        token = self.get_token()
        if token.type == "COMMAND" and token.value == "begin":
            
            # saving parent collection to bind children collections to
            parent_collection = self.current_collection
            
            # saving current parameters
            gen_calculate(self.parameters, self.text_scale, self.levels)
            tmp_param = self.parameters.create_copy()
            
            xy_size = [tmp_param.width]  # array for matrix parameters
            
            # matrix collection
            mx_coll = bpy.data.collections.new("MatrixBodyCollection")
            bpy.data.collections[parent_collection].children.link(mx_coll)
            
            # first matrix cell collection
            self.current_collection = gen_new_collection(self.context, "MatrixCellCollection", mx_coll.name)
            self.matrix.obj_array[self.matrix.row_num].append(self.current_collection)
            
            # { text }
            if self.is_matrix_figure("begin", mx_coll.name, xy_size):
                # <MATRIX>
                if self.sa_matrix(tmp_param, mx_coll.name):
                    # end
                    token = self.get_token()
                    if token.type == "COMMAND" and token.value == "end":
                        # { text }
                        if self.is_matrix_figure("end", mx_coll.name, xy_size):
                            # set width of parameters
                            self.parameters.width = gen_group_width(self.context, mx_coll.name) + 0.25
                             
                            # link objects to matrix collection
                            for collection in bpy.data.collections:
                                if "MatrixCellCollection" in collection.name:
                                    # join all objects into one parent collection
                                    for obj in collection.all_objects:
                                        bpy.data.collections[mx_coll.name].objects.link(obj) 
                                        collection.objects.unlink(obj)   
                            
                                    # remove matrix cell collection
                                    bpy.data.collections.remove(collection)
                               
                            # join matrix collection into parent collection
                            gen_join_collections(self.context, mx_coll, parent_collection)
                            self.current_collection = parent_collection  # set current collection
                            
                            return True
        # sa_block()                
        return False

    # <TERM> -> <CONST>
    #        -> <COMMAND>
    #        -> <BLOCK>
    def sa_term(self):
        token = self.get_token()

        # <CONST>
        if self.is_const(token):
            self.return_token(token)
            if not self.sa_const():
                return False

        # <BLOCK>
        elif self.is_block(token):
            self.return_token(token)
            if not self.sa_block():
                return False

        # <COMMAND>
        elif self.is_command(token):
            self.return_token(token)
            if not self.sa_command():
                return False

        # no corresponding terminals
        else:
            print("Error, no corresponding terminals - use of not supported symbol!")
            return False

        return True

    # <MORE_TERM> -> <TERM> <MORE_TERM>
    #             -> epsilon
    def sa_more_term(self):
        token = self.get_token()

        # special sqrt ]
        if self.sqrt and token.type == "TEXT" and token.value == "]":
            self.return_token(token)
            return True

        elif self.is_const(token) or self.is_command(token) or self.is_block(token):
            self.return_token(token)
            if not self.sa_term():  # <TERM>
                return False

            return self.sa_more_term()  # <MORE_TERM>

        else:
            # epsilon
            self.return_token(token)

        return True

    # taking tokens and checking their order
    # <PROG> -> <TERM> <MORE_TERM>
    def sa_prog(self):
        # creating base collection
        collection = bpy.data.collections.new("MathematicalEqCollection")
        bpy.context.scene.collection.children.link(collection)
        
        # set active collection
        layer_collection = bpy.context.view_layer.layer_collection
        # iterate through layer collection
        for layer in layer_collection.children:
            if layer.name == collection.name:
                bpy.context.view_layer.active_layer_collection = layer
        
        self.base_collection = collection.name  # set base collection
        self.current_collection = collection.name  # set current collection
        
        # chosen default font
        if self.font_path == "":
            self.font.append("")
        else:
            default_font = bpy.data.fonts.load(self.font_path)
            self.font.append(default_font)
        
        # find path to addon
        addon_name = "Mathematical Equation Generator"
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == addon_name:
                dir_path = os.path.dirname(mod.__file__)
                # create path to unicode font
                file_path = dir_path + "\\fonts\\Kelvinch-Roman.otf"
                
        # unicode font for mathematical symbols
        unicode_font = bpy.data.fonts.load(file_path)
        self.font.append(unicode_font)
        
        if not self.sa_term():  # <TERM>
            return False

        if not self.sa_more_term():  # <MORE_TERM>
            return False

        token = self.get_token()
        
        if token.type != "END":
            print("Error, not all tokens have been read!")
            print("Value of last token: " + token.value)
            return False
        
        # select all objects in base collection
        for obj in bpy.data.collections[collection.name].all_objects:  
            obj.select_set(True)

        return True
   
