import bpy
import bmesh
import random
import mathutils
import re

def create_custom_maze(
    seed_input=2938742934792437, 
    width=30, 
    height=30, 
    path_width=4.5,          
    wall_thickness=0.2, 
    wall_height=8.0, 
    center_room_radius=3,
    baseboard_height=0.35, 
    baseboard_outset=0.08,
    separate_baseboard=True, 
    has_exit=True            
):
    seed_str = re.sub(r'\D', '', str(seed_input))
    if len(seed_str) > 16:
        seed_str = seed_str[:16]
    if not seed_str:
        seed_str = str(random.randint(10000000, 99999999))
        
    final_seed = int(seed_str)
    random.seed(final_seed)
    
    grid_w = 2 * width + 1
    grid_h = 2 * height + 1
    grid = [[1 for _ in range(grid_w)] for _ in range(grid_h)]
    
    start_cx = (width // 2) * 2 + 1
    start_cy = (height // 2) * 2 + 1
    
    def carve_passages_from(cx, cy):
        grid[cy][cx] = 0
        directions = [(0, -2), (0, 2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 1 <= nx < grid_w - 1 and 1 <= ny < grid_h - 1 and grid[ny][nx] == 1:
                grid[cy + dy // 2][cx + dx // 2] = 0
                carve_passages_from(nx, ny)

    carve_passages_from(start_cx, start_cy)
    
    for y in range(start_cy - center_room_radius*2, start_cy + center_room_radius*2 + 1):
        for x in range(start_cx - center_room_radius*2, start_cx + center_room_radius*2 + 1):
            if 1 <= x < grid_w - 1 and 1 <= y < grid_h - 1:
                grid[y][x] = 0
                
    if has_exit:
        exit_side = random.choice(['N', 'S', 'E', 'W'])
        if exit_side == 'N': 
            exit_x = random.randrange(1, grid_w, 2)
            grid[grid_h - 1][exit_x] = 0
            grid[grid_h - 2][exit_x] = 0 
        elif exit_side == 'S': 
            exit_x = random.randrange(1, grid_w, 2)
            grid[0][exit_x] = 0
            grid[1][exit_x] = 0
        elif exit_side == 'E': 
            exit_y = random.randrange(1, grid_h, 2)
            grid[exit_y][grid_w - 1] = 0
            grid[exit_y][grid_w - 2] = 0
        elif exit_side == 'W': 
            exit_y = random.randrange(1, grid_h, 2)
            grid[exit_y][0] = 0
            grid[exit_y][1] = 0

    x_centers, x_sizes = [], []
    current_x = 0.0
    for x in range(grid_w):
        size = path_width if x % 2 == 1 else wall_thickness
        x_sizes.append(size)
        x_centers.append(current_x + size / 2.0)
        current_x += size
        
    y_centers, y_sizes = [], []
    current_y = 0.0
    for y in range(grid_h):
        size = path_width if y % 2 == 1 else wall_thickness
        y_sizes.append(size)
        y_centers.append(current_y + size / 2.0)
        current_y += size
        
    offset_x = -current_x / 2.0
    offset_y = -current_y / 2.0

    maze_mesh = bpy.data.meshes.new(f"Maze_{final_seed}_Mesh")
    maze_obj = bpy.data.objects.new(f"Maze_{final_seed}", maze_mesh)
    bpy.context.collection.objects.link(maze_obj)
    bm_maze = bmesh.new()
    
    if separate_baseboard and baseboard_height > 0:
        bb_mesh = bpy.data.meshes.new(f"Baseboard_{final_seed}_Mesh")
        bb_obj = bpy.data.objects.new(f"Baseboard_{final_seed}", bb_mesh)
        bpy.context.collection.objects.link(bb_obj)
        bm_bb = bmesh.new()
    else:
        bm_bb = bm_maze

    for y in range(grid_h):
        for x in range(grid_w):
            if grid[y][x] == 1: 
                pos_x = x_centers[x] + offset_x
                pos_y = y_centers[y] + offset_y
                
                pos_z_wall = wall_height / 2.0
                loc_wall = mathutils.Vector((pos_x, pos_y, pos_z_wall))
                scale_wall = mathutils.Vector((x_sizes[x] / 2.0, y_sizes[y] / 2.0, wall_height / 2.0))
                mat_wall = mathutils.Matrix.LocRotScale(loc_wall, None, scale_wall)
                bmesh.ops.create_cube(bm_maze, size=2.0, matrix=mat_wall)
                
                if baseboard_height > 0 and baseboard_outset > 0:
                    pos_z_bb = baseboard_height / 2.0
                    loc_bb = mathutils.Vector((pos_x, pos_y, pos_z_bb))
                    bb_size_x = (x_sizes[x] / 2.0) + baseboard_outset
                    bb_size_y = (y_sizes[y] / 2.0) + baseboard_outset
                    bb_size_z = baseboard_height / 2.0
                    
                    scale_bb = mathutils.Vector((bb_size_x, bb_size_y, bb_size_z))
                    mat_bb = mathutils.Matrix.LocRotScale(loc_bb, None, scale_bb)
                    bmesh.ops.create_cube(bm_bb, size=2.0, matrix=mat_bb)
                
    bmesh.ops.remove_doubles(bm_maze, verts=bm_maze.verts, dist=0.001)
    bm_maze.to_mesh(maze_mesh)
    bm_maze.free()
    
    if separate_baseboard and baseboard_height > 0:
        bmesh.ops.remove_doubles(bm_bb, verts=bm_bb.verts, dist=0.001)
        bm_bb.to_mesh(bb_mesh)
        bm_bb.free()
    
    bpy.context.view_layer.objects.active = maze_obj
    maze_obj.select_set(True)


# CONFIGURATION

create_custom_maze(
    seed_input = 2938742934792437924739,  # Seed number (max 16 digits)
    width = 30,                             # Maze grid width
    height = 30,                            # Maze grid length
    path_width = 4.5,                       # Corridor width
    wall_thickness = 0.2,                   # Wall thickness
    wall_height = 8.0,                      # Wall height
    center_room_radius = 3,                 # Center spawn room size
    separate_baseboard = True,              # True: Baseboard as separate object
    has_exit = False,                       # True: Open random exit wall
    baseboard_height = 0.35,                # Baseboard height
    baseboard_outset = 0.08                 # Baseboard thickness offset
)
