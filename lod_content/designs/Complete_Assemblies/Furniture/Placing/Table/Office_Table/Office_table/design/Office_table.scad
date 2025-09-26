// Office table
// Category: Complete Assemblies > Furniture > Placing > Table > Office Table
// Full Path: designs/Complete_Assemblies/Furniture/Placing/Table/Office_Table/Office_table/design/Office_table.scad
// Description: no way that is an office table
// Created by: admin
// Created at: 2025-09-25 12:05:57
// Costs: $Not specified


// OPENSCAD UTILITIES
include <lod_content/designs/utilities/LOD_OPENSCAD_3DPRINT.scad>


// BOM DESIGN IMPORTS


// MODULE
if(assembled == 1)
{
    translate([0, 0, leg_height])
    seat(fillet_x, fillet_y, fillet_z, seat_size, thickness, tool_size);
    translate([0, -thickness / 2, leg_height])
    rotate([-90, 0, 0])
    leg_top(fillet_x, fillet_y, fillet_z, seat_size, leg_height, thickness, tool_size);
    translate([thickness / 2, 0, leg_height])
    rotate([-90, 0, 90])
    leg_btm(fillet_x, fillet_y, fillet_z, seat_size, leg_height, thickness, tool_size);
}


// EXAMPLES
if(assembled == 1)
{
    translate([0, 0, leg_height])
    seat(fillet_x, fillet_y, fillet_z, seat_size, thickness, tool_size);
    translate([0, -thickness / 2, leg_height])
    rotate([-90, 0, 0])
    leg_top(fillet_x, fillet_y, fillet_z, seat_size, leg_height, thickness, tool_size);
    translate([thickness / 2, 0, leg_height])
    rotate([-90, 0, 90])
    leg_btm(fillet_x, fillet_y, fillet_z, seat_size, leg_height, thickness, tool_size);
}

