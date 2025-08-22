// Lalalu table
// Category: Complete Assemblies > Furniture > Placing > Table > Dining Table
// Full Path: designs/Complete_Assemblies/Furniture/Placing/Table/Dining_Table/Lalalu_table/design/Lalalu_table.scad
// Description: Table is a wacky design with weird legs
// Created by: admin
// Created at: 2025-08-19 16:14:09
// Costs: $20.0


// OPENSCAD UTILITIES
include <lod_content/utilities/LOD_OPENSCAD_3DPRINT.scad>


// BOM DESIGN IMPORTS


// MODULE
// Parameters for connectors
fillet_x = thickness * 4;
fillet_y = thickness;
fillet_z = thickness;
roughness = 0.01;

// Display of Desktop CNC Machine range or board size, if flat is active
board_x = 220;
board_y = 320;
board_z = 8;
if(assembled == 0)
{
    %cube([board_x, board_y, board_z]);
}


// EXAMPLES
module leg(fillet_x, fillet_y, fillet_z, height, width, leg_size, thickness, tool_size)
{
    difference()
    {
        difference()
        {
            //Create base element of leg
            translate([0, 0, thickness / 2])
            cube([width, height - thickness, thickness], center=true);
            translate([0, bridge_height / 2, thickness / 2])
            cube([width - leg_size * 2, height - thickness - bridge_height, thickness], center=true);
        }
        union()
        {
            //Cutout middle slot for leg bridge
            translate([0, -height / 2 + thickness / 2, 0])
            rotate([0, 0, 90])
            tbone_slot(bridge_height, fillet_y, thickness, tool_size, edged=0, roughness);
            //Cut out placeholder for connector plugs
            translate([-width/2 + leg_size * 0.75 , -height / 2 + thickness / 2, 0])
            placeholder(leg_size * 1.5, fillet_y, fillet_z, tool_size); 
            mirror([1, 0, 0])
            translate([-width / 2 + leg_size * 0.75, -height / 2 + thickness / 2, 0])
            placeholder(leg_size * 1.5, fillet_y, fillet_z, tool_size); 
        }
    }
    //Add connector plugs
    translate([-width / 2 + leg_size * 0.75, -height / 2 + thickness / 2, 0])
    tbone_plug(leg_size * 1.5, fillet_y, thickness, tool_size, edged=-1, roughness);  
    mirror([1, 0, 0])
    translate([-width / 2 + leg_size * 0.75, -height / 2 + thickness / 2, 0])
    tbone_plug(leg_size * 1.5, fillet_y, thickness, tool_size, edged=-1, roughness);  
}

