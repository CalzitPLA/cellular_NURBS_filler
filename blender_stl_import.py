import bpy
import sys
import os

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Get STL filename from command line argument
stl_file = sys.argv[-1] if len(sys.argv) > 1 else "face_dif_clogged.stl"

print(f"Importing STL file: {stl_file}")

# Import STL file
try:
    bpy.ops.wm.stl_import(filepath=stl_file)
    print("STL imported successfully")
    
    # Get the imported object
    imported_obj = bpy.context.selected_objects[0]
    print(f"Imported object: {imported_obj.name}")
    print(f"Vertices: {len(imported_obj.data.vertices)}")
    print(f"Polygons: {len(imported_obj.data.polygons)}")
    
except Exception as e:
    print(f"Error importing STL: {e}")
    sys.exit(1)

# Create NURBS sphere with hard-coded parameters
print("Creating NURBS sphere...")
# Hard-coded values: Y = -300, scale = 140 in all axes
sphere_location = (0, -300, 0)  # Hard-coded Y = -300
sphere_scale = 140  # Hard-coded scale in all axes

# Create a NURBS sphere using surface primitive
bpy.ops.surface.primitive_nurbs_surface_sphere_add(radius=1.0, location=sphere_location)
nurbs_sphere = bpy.context.selected_objects[0]
nurbs_sphere.name = "NURBS_Sphere"

# Set U and V resolution to 60
nurbs_sphere.data.resolution_u = 60
nurbs_sphere.data.resolution_v = 60

# Scale the sphere by 140 in all axes
nurbs_sphere.scale = (sphere_scale, sphere_scale, sphere_scale)

print(f"Created NURBS sphere at Y={sphere_location[1]} with scale={sphere_scale}")

# Apply shrinkwrap modifier to the NURBS sphere using the imported mesh as target
print("Applying shrinkwrap modifier to NURBS sphere...")
bpy.context.view_layer.objects.active = nurbs_sphere
shrinkwrap_mod = nurbs_sphere.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
shrinkwrap_mod.target = imported_obj  # Target is the imported mesh
shrinkwrap_mod.wrap_method = 'PROJECT'  # Project mode (uses normal direction when no axis specified)
shrinkwrap_mod.use_positive_direction = True
shrinkwrap_mod.use_negative_direction = True  # Bidirectional

print(f"Shrinkwrap modifier applied to NURBS sphere: target={imported_obj.name}, method=PROJECT (no axis)")

# Generate output .blend filename
base_name = os.path.splitext(os.path.basename(stl_file))[0]
blend_file = f"{base_name}.blend"

# Save as .blend file
print(f"Saving to {blend_file}...")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)
print(f"Successfully saved to {blend_file}")

print("Blender headless operation completed successfully")
