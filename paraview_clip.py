#!/usr/bin/env python3
"""
ParaView Python script to threshold a CT-Dataset
"""

import sys
import os

try:
    from paraview.simple import *
except ImportError:
    print("Error: ParaView Python modules not found")
    print("This script must be run from within ParaView or with paraview --script")
    sys.exit(1)

# Hard-coded input file for testing
input_file = "9 Gesichtsschdel  2.0   MPR  kor - imageType DERIVED-PRIMARY-AXIAL-CT_SOM5 MPR.vtk"
output_file = "/home/nemo/Documents/Sandbox/studienarbeit/code/output.stl"

print(f"Loading CT-Dataset from: {input_file}")

# Load the CT-Dataset
try:
    # Try to load the file (ParaView auto-detects format)
    reader = None
    if input_file.endswith('.vtk') or input_file.endswith('.vtu'):
        reader = LegacyVTKReader(FileNames=[input_file])
    elif input_file.endswith('.vtp'):
        reader = XMLPolyDataReader(FileNames=[input_file])
    elif input_file.endswith('.vti'):
        reader = XMLImageDataReader(FileNames=[input_file])
    elif input_file.endswith('.vtr'):
        reader = XMLRectilinearGridReader(FileNames=[input_file])
    elif input_file.endswith('.stl'):
        reader = STLReader(FileNames=[input_file])
    elif input_file.endswith('.ply'):
        reader = PLYReader(FileNames=[input_file])
    else:
        # Try generic reader
        reader = LegacyVTKReader(FileNames=[input_file])
    
    print("Dataset loaded successfully")
    # Note: Point/cell counts require data fetch which may not work in headless mode
    
except Exception as e:
    print(f"Error loading dataset: {e}")
    sys.exit(1)

# Apply threshold filter
print("Applying threshold filter...")
threshold = Threshold(Input=reader)

# Set threshold range (adjust these values based on your data)
# For CT data, typical Hounsfield units range from -1000 (air) to +3000 (bone)
threshold.Scalars = 'scalars'  # Set to scalars
threshold.LowerThreshold = -100.0  # Lower threshold value in HU
threshold.UpperThreshold = 3071.0  # Upper threshold value in HU
threshold.ThresholdMethod = 'Between'  # Threshold between lower and upper values

# You can also specify different scalar arrays:
# threshold.Scalars = ['POINTS', 'scalars']
# threshold.Scalars = ['CELLS', 'scalars']

print(f"Threshold applied successfully")
print(f"Threshold range: {threshold.LowerThreshold} to {threshold.UpperThreshold}")

# Extract surface from the thresholded data
print("Extracting surface...")
surface = ExtractSurface(Input=threshold)
print("Surface extracted successfully")

# Save the result if output file is specified
if output_file:
    print(f"Saving surface to: {output_file}")
    SaveData(output_file, surface, FileType='Binary')
    print("Output saved successfully")
else:
    print("No output file specified. Use paraview --script paraview_clip.py <input> <output> to save result")

print("ParaView threshold script completed successfully")
