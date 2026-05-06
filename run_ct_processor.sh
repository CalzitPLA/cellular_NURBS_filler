#!/bin/bash

# CT Processor Pipeline
# 1. Process CT-Dataset with ParaView (threshold and extract surface)
# 2. Import result into Blender and apply shrinkwrap

cd /home/nemo/Documents/Sandbox/studienarbeit/code

echo "=========================================="
echo "Step 1: Processing CT-Dataset with ParaView"
echo "=========================================="

# Run ParaView script to create output.stl using pvpython
pvpython paraview_clip.py

# Check if output.stl was created
if [ ! -f "output.stl" ]; then
    echo "Error: output.stl was not created"
    exit 1
fi

echo "ParaView processing completed successfully"
echo "=========================================="
echo "Step 2: Processing STL with Blender"
echo "=========================================="

# Run Blender script with output.stl
blender --background --python blender_stl_import.py output.stl

# Check if output.blend was created (ignore Blender exit code due to spurious error)
if [ ! -f "output.blend" ]; then
    echo "Error: output.blend was not created"
    exit 1
fi

echo "=========================================="
echo "CT Processor Pipeline Completed Successfully"
echo "=========================================="
echo "Output files:"
echo "  - output.stl (ParaView thresholded surface)"
echo "  - output.blend (Blender scene with shrinkwrap)"
