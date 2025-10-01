/*  
    Copyright (C) 2014-2015  H3XL, Inc  
  
    This program is free software: you can redistribute it and/or modify  
    it under the terms of the GNU General Public License as published by  
    the Free Software Foundation, either version 3 of the License, or  
    (at your option) any later version.  
  
    This program is distributed in the hope that it will be useful,  
    but WITHOUT ANY WARRANTY; without even the implied warranty of  
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the  
    GNU General Public License for more details.  
  
    You should have received a copy of the GNU General Public License  
    along with this program.  If not, see <http://www.gnu.org/licenses/>.  
*/  
  
// This file holds the html for the main page  
var openscadpage = {};  
openscadpage.start = function() {  
  var output = "";  
  
output += '  <div id="main">\n';  
output += '    <nav class="navbar navbar-default" id="top-navigation-bar">\n';  
output += '      <div class="container-fluid">\n';  
output += '        <a href="#" class="pull-left"><img src="imgs/bslogo.png" style="max-height:50px"></a>\n';  
output += '        <ul class="nav navbar-nav">\n';  
output += '          <li class="dropdown">\n';  
output += '            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false"><img src="imgs/globe.png" style="width:20px"><span class="caret"></span></a>\n';  
output += '            <ul id="languageMenu" class="dropdown-menu" role="menu">\n';  
output += '            </ul>\n';  
output += '          </li>\n';  
  
output += '          <li class="dropdown"> \n';  
output += '            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">'+OpenSCAD.Msg.PROJECT_MENU+'<span class="caret"></span></a>\n';  
output += '            <ul id="file-menu" class="dropdown-menu" role="menu">\n';  
output += '              <li><a href="#" class="new-project">'+OpenSCAD.Msg.NEW+'</a></li>\n';  
output += '              <li class="divider"></li>\n';  
output += '              <li><a href="#" id="saveLocal">'+OpenSCAD.Msg.SAVE_BLOCKS_LOCAL+'</a></li>\n';  
output += '              <li>\n';  
output += '                <input type="file" accept=".xml" id="loadLocal" style="visibility: hidden; width: 1px; height: 1px" />\n';  
output += '                <a href="#" onclick="document.getElementById(\'loadLocal\').click(); return false">'+OpenSCAD.Msg.LOAD_BLOCKS_LOCAL+'</a>\n';  
output += '              </li>\n';  
output += '              <li class="divider"></li>\n';  
output += '              <li>\n';  
output += '                <input type="file" accept=".xml" id="importLocal" style="visibility: hidden; width: 1px; height: 1px" />\n';  
output += '                <a href="#" onclick="document.getElementById(\'importLocal\').click(); return false">'+OpenSCAD.Msg.IMPORT_BLOCKS_LOCAL+'</a>\n';  
output += '              </li>\n';  
output += '              <li>\n';  
output += '                <input type="file" accept=".stl" id="importStl" style="visibility: hidden; width: 1px; height: 1px" />\n';  
output += '                <a href="#" onclick="document.getElementById(\'importStl\').click(); return false">'+OpenSCAD.Msg.IMPORT_STL_MENU +'</a>\n';  
output += '              </li>\n';  
output += '              <li class="divider"></li>\n';  
output += '              <li><a href="#" id="saveOpenscad">' + OpenSCAD.Msg.SAVE_SCAD_LOCAL + '</a></li>\n';  
output += '            </ul>\n';  
output += '          </li>\n';  
output += '          <li class="dropdown">\n';  
output += '            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">' + OpenSCAD.Msg.OPTIONS_MENU + '<span class="caret"></span></a>\n';  
output += '            <ul id="options-menu" class="dropdown-menu" role="menu">\n';  
output += '              <li><a href="#" id="simpleToolbox">' + OpenSCAD.Msg.SIMPLE_TOOLBOX + '</a></li>\n';  
output += '              <li><a href="#" id="advancedToolbox">' + OpenSCAD.Msg.ADVANCED_TOOLBOX + '</a></li>\n';  
output += '              <li>\n';  
output += '                <a class="trigger right-caret">' + OpenSCAD.Msg.BLOCK_COLORS + '</a>\n';  
output += '                <ul class="dropdown-menu sub-menu">\n';  
output += '                  <li><a href="#" id="colors_one">' + OpenSCAD.Msg.CLASSIC_COLORS + '</a></li>\n';  
output += '                  <li><a href="#" id="colors_two">' + OpenSCAD.Msg.PALE_COLORS + '</a></li>\n';  
output += '                </ul>\n';  
output += '              </li>\n';  
output += '            </ul>\n';  
output += '          </li>\n';  
output += '          <li class="dropdown">\n';  
output += '            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">' + OpenSCAD.Msg.HELP_MENU + '<span class="caret"></span></a>\n';  
output += '            <ul id="help-menu" class="dropdown-menu" role="menu">\n';  
output += '              <li><a href="docs/" target="_blank">' + OpenSCAD.Msg.DOCUMENTATION_LINK + '</a></li>\n';  
output += '              <li class="divider"></li>\n';  
output += '              <li><a href="#" data-toggle="modal" data-target="#about-modal">' + OpenSCAD.Msg.ABOUT_LINK + '</a></li>\n';  
output += '            </ul>\n';  
output += '          </li>\n';  
output += '          <li class="dropdown">\n';  
output += '            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">' + OpenSCAD.Msg.EXAMPLES_MENU + '<span class="caret"></span></a>\n';  
output += '            <ul id="examples-menu" class="dropdown-menu" role="menu">\n';  
output += '              <li><a href="#" id="examples_cube_with_cutouts">' + OpenSCAD.Msg.EXAMPLE_CUBE_WITH_CUTOUTS + '</a></li>\n';  
output += '              <li><a href="#" id="examples_anthias_fish">' + OpenSCAD.Msg.EXAMPLE_ANTHIAS_FISH +'</a></li>\n';  
output += '              <li><a href="#" id="examples_torus">' + OpenSCAD.Msg.TORUS + '</a></li>\n';  
output += '              <li><a href="#" id="examples_box">' + OpenSCAD.Msg.EXAMPLE_PARAMETRIC_BOX + '</a></li>\n';  
output += '              <li><a href="#" id="examples_linear_extrude">' + OpenSCAD.Msg.LINEAR_EXTRUDE + '</a></li>\n';  
output += '              <li><a href="#" id="examples_rotate_extrude">' + OpenSCAD.Msg.ROTATE_EXTRUDE + '</a></li>\n';  
output += '              <li><a href="#" id="examples_hulled_loop_sun">' + OpenSCAD.Msg.EXAMPLE_LOOP_SUN + '</a></li>\n';  
output += '              <li><a href="#" id="examples_sine_function_with_loop">' + OpenSCAD.Msg.EXAMPLE_LOOP_SINE + '</a></li>\n';  
output += '              <li><a href="#" id="examples_trefoil_knot_param_eq">' + OpenSCAD.Msg.EXAMPLE_PARAMETRIC_EQ_KNOT + '</a></li>\n';  
output += '            </ul>\n';  
output += '          </li>\n';  
output += '             <a type="button" class="btn btn-default btn-lg" style="margin-top:2px" href="https://youtu.be/5RNKVn7lijM" target="_blank">'+ OpenSCAD.Msg.GET_STARTED_VIDEO + '</a>';  
output += '        </ul>\n';  
output += '        <div id="login-area" class="navbar-right">\n';  
output += '        </div>\n';  
output += '      </div>  <!-- /.container-fluid -->\n';  
output += '    </nav>\n';  
  
// Continue with the rest of the file content...  
output += '            </div>\n';  
output += '          </div>\n';  
output += '          <button id="trashButton" class="btn btn-default notext" title="' + OpenSCAD.Msg.MOUSEOVER_TRASHCAN + '">\n';  
output += '            <img src="blockly/media/1x1.gif" class="trash icon21">\n';  
output += '          </button>\n';  
output += '        </div> <!-- undo/redo/trash div --> \n';  
output += '      </nav> <!-- end second nav row -->\n';  
output += '      <!-- End of the header content -->\n';  
output += '\n';  
output += '      <!-- beginning of page content (blockly + viewer) -->\n';  
output += '      <div class="tab-content">\n';  
output += '        <div class="tab-pane active" id="blocklyContainer">\n';  
output += '          <div id="blocklyDiv">\n';  
output += '\n';  
output += '            <div class="resizableDiv">\n';  
output += '              <div id="renderDiv">\n';  
output += '                <!-- <input type="text" id="colorButton"/> -->\n';  
output += '              </div> <!--renderDiv -->\n';  
output += '              <div id="paneContainer">\n';  
output += '                <div id="viewerButtons">\n';  
output += '                  <div class="btn-group">\n';  
output += '                    <input type="text" id="defColor"/>\n';  
output += '                  </div>\n';  
output += '                  <div class="btn-group">\n';  
output += '                    <button id="axesButton" type="button" title="' + OpenSCAD.Msg.AXES_BUTTON + '" class="btn vbut btn-default">\n';  
output += '                      <svg viewbox="0 0 26 26">\n';  
output += '                           <path style="stroke:#777;stroke-width:1.6;fill:none" d="m9 0.5v15h15"/>\n';  
output += '                           <path style="stroke:#777;stroke-width:1.6;fill:none" d="m9 15-9 9"/>\n';  
output += '                      </svg>\n';  
output += '                    </button>\n';  
output += '                  </div>\n';  
output += '                  <div class="btn-group">\n';  
output += '                    <button id="zInButton" type="button" title="' + OpenSCAD.Msg.ZOOM_IN_BUTTON + '" class="btn vbut btn-default">\n';  
output += '                      <svg viewbox="0 0 26 26">\n';  
output += '                           <path style="stroke:#777;stroke-width:1.6;fill:none" d="m13 6v14m-7-7h14"/>\n';  
output += '                      </svg>\n';  
output += '                    </button>\n';  
output += '                  </div>\n';  
output += '                  <div class="btn-group">\n';  
output += '                    <button id="zOutButton" type="button" title="' + OpenSCAD.Msg.ZOOM_OUT_BUTTON + '" class="btn vbut btn-default">\n';  
output += '                      <svg viewbox="0 0 26 26">\n';  
output += '                           <path style="stroke:#777;stroke-width:1.6;fill:none" d="m6 13h14"/>\n';  
output += '                      </svg>\n';  
output += '                    </button>\n';  
output += '                  </div>\n';  
output += '                  <div class="btn-group">\n';  
output += '                    <button id="viewReset" type="button" title="' + OpenSCAD.Msg.RESET_VIEW_BUTTON + '" class="btn vbut btn-default">\n';  
output += '                      <svg viewbox="0 0 26 26">\n';  
output += '                           <path style="stroke:#777;stroke-width:1.6;fill:none" d="m13 6v14m-7-7h14"/>\n';  
output += '                      </svg>\n';  
output += '                    </button>\n';  
output += '                  </div>\n';  
output += '                </div>\n';  
output += '                <div id="renderPane">\n';  
output += '                  <button type="button" class="btn btn-default btn-lg changeable" id="renderButton">' + OpenSCAD.Msg.RENDER_BUTTON + '</button>\n';  
output += '                  <button type="button" class="btn btn-default btn-lg btn-danger " id="abortButton">' + OpenSCAD.Msg.ABORT_BUTTON + '</button>\n';  
output += '                  <div id="stl_buttons" class="pull-right" style="padding:5px 5px;">\n';  
output += '                    <select id="render-type" style="padding:2px 4px;"></select>\n';  
output += '                    <button type="button" class="btn btn-default btn-lg changeable" id="stlButton">' + OpenSCAD.Msg.GENERATE_STL + '</button>\n';  
output += '                  </div>\n';  
output += '                  <div id="render-ongoing">' + OpenSCAD.Msg.PARSE_IN_PROGRESS + '  <img id=busy src="imgs/busy2.gif"></div>\n';  
output += '                  <div id="error-message"></div>\n';  
output += '                </div>\n';
output += '                <div id="renderPane">\n';  
output += '                  <button type="button" class="btn btn-default btn-lg changeable" id="renderButton">' + OpenSCAD.Msg.RENDER_BUTTON + '</button>\n';  
output += '                  <button type="button" class="btn btn-default btn-lg btn-danger " id="abortButton">' + OpenSCAD.Msg.ABORT_BUTTON + '</button>\n';  
output += '                  <div id="stl_buttons" class="pull-right" style="padding:5px 5px;">\n';  
output += '                    <select id="render-type" style="padding:2px 4px;"></select>\n';  
output += '                    <button type="button" class="btn btn-default btn-lg changeable" id="stlButton">' + OpenSCAD.Msg.GENERATE_STL + '</button>\n';  
output += '                  </div>\n';  
output += '                  <div id="render-ongoing">' + OpenSCAD.Msg.PARSE_IN_PROGRESS + '  <img id=busy src="imgs/busy2.gif"></div>\n';  
output += '                  <div id="error-message"></div>\n';  
output += '                </div>\n';  
output += '              </div> <!-- paneContainer -->\n';  
output += '            </div> <!-- resizable div -->\n';  
output += '          </div> <!-- blocklyDiv -->\n';  
output += '        </div>\n';  
output += '        <!-- Blockly Container (tab pane)-->\n';  
output += '        <pre class="tab-pane content" id="openScadPre"></pre>';  
  
// Continue with modal dialogs and project tables  
output += '      </div> <!-- tab-content -->\n';  
output += '    </div> <!-- editView -->\n';  
output += '  </div> <!-- main -->\n';  
  
// Modal dialogs  
output += '  <!-- About Modal -->\n';  
output += '  <div class="modal fade" id="about-modal" tabindex="-1" role="dialog">\n';  
output += '    <div class="modal-dialog" role="document">\n';  
output += '      <div class="modal-content">\n';  
output += '        <div class="modal-header">\n';  
output += '          <button type="button" class="close" data-dismiss="modal">&times;</button>\n';  
output += '          <h4 class="modal-title">' + OpenSCAD.Msg.ABOUT_TITLE + '</h4>\n';  
output += '        </div>\n';  
output += '        <div class="modal-body">\n';  
output += '          <p>' + OpenSCAD.Msg.ABOUT_TEXT + '</p>\n';  
output += '          <p>Version ' + OpenSCAD.version + '</p>\n';  
output += '        </div>\n';  
output += '        <div class="modal-footer">\n';  
output += '          <button type="button" class="btn btn-default" data-dismiss="modal">' + OpenSCAD.Msg.CLOSE + '</button>\n';  
output += '        </div>\n';  
output += '      </div>\n';  
output += '    </div>\n';  
output += '  </div>\n';  
  
// Project management modals and tables would continue here...  
output += '  <!-- Additional modals and project tables -->\n';  
  
// Close the function  
return output;  
};  
  
// Initialize the openscad page namespace  
var openscadpage = openscadpage || {};
