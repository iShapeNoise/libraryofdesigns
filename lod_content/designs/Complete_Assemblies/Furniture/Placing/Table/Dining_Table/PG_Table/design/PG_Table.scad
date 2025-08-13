// PG Table
// Category: Complete Assemblies > Furniture > Placing > Table > Dining Table
// Full Path: designs/Complete_Assemblies/Furniture/Placing/Table/Dining_Table/PG_Table/design/PG_Table.scad
// Description: A table
// Created by: admin
// Created at: 2025-08-12 15:41:35
// Costs: $50.0


// OPENSCAD UTILITIES
include <lod_content/utilities/LOD_OPENSCAD_3DPRINT.scad>


// BOM DESIGN IMPORTS


// MODULE
//Name the part of the design
//Please help with commenting the code, so other people and you yourself can follow the code easier
//Create module for Leg parts
module tabletop(fillet_x, fillet_y, fillet_z, length, width, thickness, tool_size)
{
    difference()
    {
        //Basis board element
        translate([0, 0, thickness / 2])
        cube([length, width, thickness], center=true);
        //Cut out connectors
        union()
        {
            translate([leg_distance / 2 - thickness, width / 2, 0])
            rotate([0, 0, 90])
            tbone_slot(leg_size * 3, fillet_y, thickness, tool_size, roughness, resolution);
            translate([-leg_distance / 2 + thickness, width / 2, 0])
            rotate([0, 0, 90])
            tbone_slot(leg_size * 3, fillet_y, thickness, tool_size, roughness, resolution);
            mirror([0, -1, 0])
            {
                translate([leg_distance / 2 - thickness, width / 2, 0])
                rotate([0, 0, 90])
                tbone_slot(leg_size * 3, fillet_y, thickness, tool_size, roughness);
                translate([-leg_distance / 2 + thickness, width / 2, 0])
                rotate([0, 0, 90])
                tbone_slot(leg_size * 3, fillet_y, thickness, tool_size, roughness);
            }
        }
    }
}


// EXAMPLES
//Parametric values
// Parameters for overall design
tool_size = 2;
thickness = 8;
length = 200;
width = 130;
height = 100;
leg_distance = length - length * 0.2;
leg_size = 20;
bridge_height = leg_size;
resolution = 100;
assembled = 1;   // [0:No, 1:Yes]
dxf = true; // This is necessary to export flat cutouts in dxf format

