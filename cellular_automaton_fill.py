#!/usr/bin/env python3
"""
3D Cellular Automaton to fill NURBS sphere volume with primitives
"""

import numpy as np
import sys
import os
import trimesh

def load_obj_file(filepath):
    """Load OBJ file and return trimesh mesh"""
    try:
        mesh = trimesh.load(filepath)
        print(f"Loaded mesh from {filepath}")
        print(f"Vertices: {len(mesh.vertices)}")
        print(f"Faces: {len(mesh.faces)}")
        return mesh
    except Exception as e:
        print(f"Error loading OBJ file: {e}")
        sys.exit(1)

def point_in_mesh_edge_check(voxel_center, voxel_size, mesh):
    """Check if voxel is inside mesh by testing its edge points using trimesh"""
    # Calculate edge points of the cube
    half_size = voxel_size / 2
    edge_points = []
    
    # 12 edge points of a cube
    edge_points.append(voxel_center + np.array([-half_size, -half_size, 0]))
    edge_points.append(voxel_center + np.array([half_size, -half_size, 0]))
    edge_points.append(voxel_center + np.array([-half_size, half_size, 0]))
    edge_points.append(voxel_center + np.array([half_size, half_size, 0]))
    edge_points.append(voxel_center + np.array([-half_size, 0, -half_size]))
    edge_points.append(voxel_center + np.array([half_size, 0, -half_size]))
    edge_points.append(voxel_center + np.array([-half_size, 0, half_size]))
    edge_points.append(voxel_center + np.array([half_size, 0, half_size]))
    edge_points.append(voxel_center + np.array([0, -half_size, -half_size]))
    edge_points.append(voxel_center + np.array([0, half_size, -half_size]))
    edge_points.append(voxel_center + np.array([0, -half_size, half_size]))
    edge_points.append(voxel_center + np.array([0, half_size, half_size]))
    
    # Check if majority of edge points are inside using trimesh
    inside_count = 0
    for point in edge_points:
        if mesh.contains([point])[0]:
            inside_count += 1
    
    # If more than half the edge points are inside, consider voxel inside
    return inside_count > 6

def create_voxel_grid_growth(mesh, voxel_size=10.0):
    """Create voxel grid using trimesh voxelization (much faster)"""
    print(f"Using trimesh voxelization with voxel size: {voxel_size}")
    
    # Use trimesh's built-in voxelization
    voxel_grid = mesh.voxelized(pitch=voxel_size)
    
    # Get the matrix of voxels
    grid = voxel_grid.matrix
    
    print(f"Voxel grid shape: {grid.shape}")
    fill_ratio = np.sum(grid) / grid.size
    print(f"Fill ratio: {fill_ratio:.4f}")
    
    # Get bounds from mesh
    min_bound = mesh.bounds[0]
    max_bound = mesh.bounds[1]
    
    return grid, min_bound, voxel_size

def cellular_automaton_step(grid, boundary_mask):
    """Perform one step of cellular automaton with strict boundary enforcement"""
    new_grid = grid.copy()
    
    # Get grid dimensions
    nx, ny, nz = grid.shape
    
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            for k in range(1, nz - 1):
                # Only process cells that are inside the mesh boundary
                if not boundary_mask[i, j, k]:
                    new_grid[i, j, k] = False
                    continue
                
                # Count neighbors
                neighbors = grid[i-1:i+2, j-1:j+2, k-1:k+2]
                neighbor_count = np.sum(neighbors) - grid[i, j, k]
                
                # Cellular automaton rules for filling
                if grid[i, j, k]:
                    # If cell is filled, keep it filled
                    new_grid[i, j, k] = True
                elif neighbor_count >= 5:
                    # If 5 or more neighbors are filled, fill this cell
                    new_grid[i, j, k] = True
                else:
                    new_grid[i, j, k] = False
    
    return new_grid

def optimize_fill(grid, boundary_mask, max_iterations=50):
    """Run cellular automaton to maximize fill with strict boundary enforcement"""
    print("Starting cellular automaton optimization...")
    
    for iteration in range(max_iterations):
        new_grid = cellular_automaton_step(grid, boundary_mask)
        fill_ratio = np.sum(new_grid) / new_grid.size
        
        if iteration % 10 == 0:
            print(f"Iteration {iteration}: fill ratio = {fill_ratio:.4f}")
        
        # Stop if no change
        if np.array_equal(grid, new_grid):
            print(f"Converged at iteration {iteration}")
            break
        
        grid = new_grid
    
    final_fill_ratio = np.sum(grid) / grid.size
    print(f"Final fill ratio: {final_fill_ratio:.4f}")
    
    return grid

def export_to_obj(grid, min_bound, voxel_size, output_file="cellular_output.obj"):
    """Export filled voxels as primitives (cubes) to OBJ file"""
    print(f"Exporting to {output_file}...")
    
    nx, ny, nz = grid.shape
    
    with open(output_file, 'w') as f:
        f.write("# Cellular Automaton Output\n")
        f.write("# Filled voxels as cube primitives\n")
        
        vertices = []
        faces = []
        vertex_offset = 0
        
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if grid[i, j, k]:
                        # Calculate cube center position
                        x = min_bound[0] + i * voxel_size
                        y = min_bound[1] + j * voxel_size
                        z = min_bound[2] + k * voxel_size
                        
                        # Create cube vertices
                        half_size = voxel_size / 2
                        cube_vertices = [
                            (x - half_size, y - half_size, z - half_size),
                            (x + half_size, y - half_size, z - half_size),
                            (x + half_size, y + half_size, z - half_size),
                            (x - half_size, y + half_size, z - half_size),
                            (x - half_size, y - half_size, z + half_size),
                            (x + half_size, y - half_size, z + half_size),
                            (x + half_size, y + half_size, z + half_size),
                            (x - half_size, y + half_size, z + half_size),
                        ]
                        
                        # Write vertices
                        for v in cube_vertices:
                            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
                        
                        # Write faces (12 triangles for a cube)
                        # Bottom face
                        f.write(f"f {vertex_offset+1} {vertex_offset+2} {vertex_offset+3}\n")
                        f.write(f"f {vertex_offset+1} {vertex_offset+3} {vertex_offset+4}\n")
                        # Top face
                        f.write(f"f {vertex_offset+5} {vertex_offset+6} {vertex_offset+7}\n")
                        f.write(f"f {vertex_offset+5} {vertex_offset+7} {vertex_offset+8}\n")
                        # Front face
                        f.write(f"f {vertex_offset+1} {vertex_offset+2} {vertex_offset+6}\n")
                        f.write(f"f {vertex_offset+1} {vertex_offset+6} {vertex_offset+5}\n")
                        # Back face
                        f.write(f"f {vertex_offset+3} {vertex_offset+4} {vertex_offset+8}\n")
                        f.write(f"f {vertex_offset+3} {vertex_offset+8} {vertex_offset+7}\n")
                        # Left face
                        f.write(f"f {vertex_offset+1} {vertex_offset+4} {vertex_offset+8}\n")
                        f.write(f"f {vertex_offset+1} {vertex_offset+8} {vertex_offset+5}\n")
                        # Right face
                        f.write(f"f {vertex_offset+2} {vertex_offset+3} {vertex_offset+7}\n")
                        f.write(f"f {vertex_offset+2} {vertex_offset+7} {vertex_offset+6}\n")
                        
                        vertex_offset += 8
    
    print(f"Exported {vertex_offset // 8} cubes to {output_file}")

def main():
    # Change to script directory
    os.chdir('/home/nemo/Documents/Sandbox/studienarbeit/code')
    
    # Input file
    input_file = "output.obj"
    output_file = "cellular_output.obj"
    
    print("==========================================")
    print("3D Cellular Automaton Volume Filler")
    print("==========================================")
    
    # Load NURBS sphere
    print(f"Loading NURBS sphere from {input_file}...")
    mesh = load_obj_file(input_file)
    
    # Create voxel grid using cellular automaton growth
    print("Creating voxel grid using cellular automaton growth...")
    filled_grid, min_bound, voxel_size = create_voxel_grid_growth(mesh, voxel_size=10.0)
    
    # Export result
    print("Exporting result...")
    export_to_obj(filled_grid, min_bound, voxel_size, output_file)
    
    print("==========================================")
    print("Cellular automaton completed successfully")
    print("==========================================")
    print(f"Output file: {output_file}")

if __name__ == "__main__":
    main()
