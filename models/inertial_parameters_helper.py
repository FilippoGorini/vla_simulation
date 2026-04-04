##############################################################################################################
### This script is meant to calculate inertial parameters for a given mesh, assuming a homogeneous density ###
### This script is meant to be run in Blender's scripting environment                                      ###          
##############################################################################################################


# INSTRUCTIONS:
# - Run Blender from within a terminal ($blender)
# - Load the mesh of which you want to compute inertial parameters in Blender,
#   making sure that the axes orientation and scale is consistent with that of the original file
# - Click on the object to make sure it is selected
# - Copy and paste this script into the Scripting window of blender
# - Change the DENSITY variable to a reasonable value for your object (kg/m^3 units)
# - Hit the Play button to run the script
# - Go on the terminal you used to launch Blender to see the result, formatted as the 
#   correct <inertial> block you can copy and paste into the .sdf file for your model


# Change density here (e.g., Water: 1000, PLA: 1250)
DENSITY = 2710.0 

import bpy
import bmesh
import mathutils

def compute_exact_sdf_inertial(obj, density=2710.0):
    # Create a BMesh and ensure it consists only of triangles
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)

    vol_total = 0.0
    com_total = mathutils.Vector((0.0, 0.0, 0.0))
    
    # Safely initialize a 3x3 Zero Matrix (avoids strict scalar math errors)
    C_total = mathutils.Matrix((
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0)
    ))
    
    # Standard tetrahedron covariance matrix (multiplying by 1/120 instead of dividing)
    f = 1.0 / 120.0
    C_std = mathutils.Matrix((
        (2.0 * f, 1.0 * f, 1.0 * f),
        (1.0 * f, 2.0 * f, 1.0 * f),
        (1.0 * f, 1.0 * f, 2.0 * f)
    ))

    # 1. Volumetric Integration
    for f_bm in bm.faces:
        v1, v2, v3 = [v.co for v in f_bm.verts]
        V = mathutils.Matrix((v1, v2, v3)).transposed()
        
        det = V.determinant()
        vol = det / 6.0
        
        vol_total += vol
        com_total += vol * (v1 + v2 + v3) / 4.0
        
        C_tetra = det * (V @ C_std @ V.transposed())
        C_total += C_tetra

    bm.free()

    if abs(vol_total) < 1e-9:
        return "Error: Object has zero volume (or normals are completely broken)."

    # 2. Final Center of Mass
    com = com_total / vol_total
    
    # 3. Shift Covariance to CoM (Parallel Axis Theorem)
    com_mat = mathutils.Matrix((
        (com.x*com.x, com.x*com.y, com.x*com.z),
        (com.y*com.x, com.y*com.y, com.y*com.z),
        (com.z*com.x, com.z*com.y, com.z*com.z)
    ))
    
    # Matrix * float is safely supported
    C_com = C_total - (com_mat * vol_total)
    
    # 4. Calculate Mass
    mass = abs(vol_total) * density
    
    # 5. Convert Covariance Matrix to Inertia Tensor
    sign = 1.0 if vol_total > 0 else -1.0
    C_com = C_com * (density * sign)
    
    ixx = C_com[1][1] + C_com[2][2]
    iyy = C_com[0][0] + C_com[2][2]
    izz = C_com[0][0] + C_com[1][1]
    ixy = -C_com[0][1]
    ixz = -C_com[0][2]
    iyz = -C_com[1][2]

    # Format SDF output
    sdf_output = f"""<inertial>
    <pose>{com.x:.6f} {com.y:.6f} {com.z:.6f} 0 0 0</pose>
    <mass>{mass:.8f}</mass>
    <inertia>
        <ixx>{ixx:.8e}</ixx>
        <ixy>{ixy:.8e}</ixy>
        <ixz>{ixz:.8e}</ixz>
        <iyy>{iyy:.8e}</iyy>
        <iyz>{iyz:.8e}</iyz>
        <izz>{izz:.8e}</izz>
    </inertia>
</inertial>"""
    return sdf_output


# Grab the object you currently have clicked on
active_obj = bpy.context.active_object

if active_obj and active_obj.type == 'MESH':
    print(f"\n--- SDF Inertial Data for: {active_obj.name} ---")
    print(compute_exact_sdf_inertial(active_obj, density=DENSITY))
    print("-" * 40)
else:
    print("\n[!] Please click on a 3D mesh object in the viewport first.")