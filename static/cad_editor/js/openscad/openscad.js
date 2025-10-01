/**  
 * OpenSCAD Text Editor - Pure text-based CAD editor  
 * Converted from BlocksCAD to work without Blockly dependencies  
 */  
  
// OpenSCAD Editor namespace (renamed from Blockscad)  
var OpenSCAD = OpenSCAD || {};  
  
// Version and configuration  
OpenSCAD.version = "1.0.0";  
OpenSCAD.offline = true;  
OpenSCAD.drawAxes = 1;  
OpenSCAD.resolution = 1;  
OpenSCAD.editor = null;  
OpenSCAD.viewer = null;  
  
// Picture settings for rendering  
OpenSCAD.picSize = [450, 450];  
OpenSCAD.rpicSize = [250, 250];  
OpenSCAD.picQuality = 0.85;  
OpenSCAD.numRotPics = 13;  
  
// Initialize OpenSCAD Editor - text-only version  
OpenSCAD.init = function() {  
    console.log('Initializing OpenSCAD text editor...');  
      
    // Initialize CodeMirror text editor  
    OpenSCAD.initTextEditor();  
      
    // Initialize 3D viewer  
    OpenSCAD.initViewer();  
      
    // Setup event handlers  
    OpenSCAD.setupEventHandlers();  
      
    console.log('OpenSCAD text editor initialized successfully');  
};  
  
// Initialize CodeMirror text editor  
OpenSCAD.initTextEditor = function() {  
    const editorElement = document.getElementById('codeEditor');  
    if (editorElement) {  
        OpenSCAD.editor = CodeMirror.fromTextArea(editorElement, {  
            mode: 'text/x-csrc',  
            theme: 'monokai',  
            lineNumbers: true,  
            autoCloseBrackets: true,  
            matchBrackets: true,  
            lineWrapping: true,  
            indentUnit: 2,  
            tabSize: 2  
        });  
          
        // Set default OpenSCAD code if empty  
        if (!OpenSCAD.editor.getValue().trim()) {  
            OpenSCAD.editor.setValue(`// OpenSCAD Text Editor  
// Create your 3D designs here  
  
// Example: Simple cube  
cube([10, 10, 10]);  
  
// Example: Cylinder  
translate([15, 0, 0])  
    cylinder(h=10, r=5);  
  
// Example: Sphere  
translate([0, 15, 0])  
    sphere(r=5);`);  
        }  
          
        console.log('CodeMirror editor initialized');  
    } else {  
        console.error('Error: codeEditor element not found');  
    }  
};  
  
// Initialize 3D viewer  
OpenSCAD.initViewer = function() {  
    const renderDiv = document.getElementById('renderDiv');  
    if (!renderDiv) {  
        console.error('Error: renderDiv not found');  
        return;  
    }  
      
    // Set viewer dimensions  
    if (renderDiv.offsetWidth === 0 || renderDiv.offsetHeight === 0) {  
        renderDiv.style.width = '100%';  
        renderDiv.style.height = '100%';  
        renderDiv.style.minHeight = '400px';  
    }  
      
    try {  
        // Create viewer directly (using existing viewer component)  
        OpenSCAD.viewer = new OpenSCAD.Viewer(  
            renderDiv,  
            renderDiv.offsetWidth,  
            renderDiv.offsetHeight,  
            100  
        );  
          
        // Configure viewer settings  
        OpenSCAD.viewer.plate = true;  
        OpenSCAD.viewer.onDraw();  
          
        console.log('3D viewer initialized successfully');  
    } catch (e) {  
        console.error('3D viewer initialization error: ' + e.message);  
        // Fallback: try with Blockscad namespace if OpenSCAD.Viewer doesn't exist  
        try {  
            if (typeof Openscad !== 'undefined' && Openscad.Viewer) {  
                OpenSCAD.viewer = new Openscad.Viewer(  
                    renderDiv,  
                    renderDiv.offsetWidth,  
                    renderDiv.offsetHeight,  
                    100  
                );  
                OpenSCAD.viewer.plate = true;  
                OpenSCAD.viewer.onDraw();  
                console.log('3D viewer initialized with fallback');  
            }  
        } catch (fallbackError) {  
            console.error('Fallback viewer initialization failed: ' + fallbackError.message);  
        }  
    }  
};  
  
// Setup event handlers for buttons and controls  
OpenSCAD.setupEventHandlers = function() {  
    // Preview button  
    const previewBtn = document.getElementById('previewBtn');  
    if (previewBtn) {  
        previewBtn.addEventListener('click', OpenSCAD.previewCode);  
    }  
      
    // Save button    
    const saveBtn = document.getElementById('saveBtn');  
    if (saveBtn) {  
        saveBtn.addEventListener('click', OpenSCAD.saveDesign);  
    }  
      
    // New button  
    const newBtn = document.getElementById('newBtn');  
    if (newBtn) {  
        newBtn.addEventListener('click', OpenSCAD.newDesign);  
    }  
      
    // Export button  
    const exportBtn = document.getElementById('exportBtn');  
    if (exportBtn) {  
        exportBtn.addEventListener('click', OpenSCAD.exportSTL);  
    }  
      
    // Render button  
    const renderBtn = document.getElementById('renderBtn');  
    if (renderBtn) {  
        renderBtn.addEventListener('click', OpenSCAD.renderCode);  
    }  
      
    console.log('Event handlers setup complete');  
};  
  
// Preview function for OpenSCAD code  
OpenSCAD.previewCode = function() {  
    if (!OpenSCAD.editor || !OpenSCAD.viewer) {  
        console.error('Editor or viewer not initialized');  
        OpenSCAD.addConsoleMessage('Editor or viewer not ready', 'error');  
        return;  
    }  
      
    const code = OpenSCAD.editor.getValue();  
    if (!code.trim()) {  
        OpenSCAD.addConsoleMessage('Please enter some OpenSCAD code first', 'warning');  
        return;  
    }  
      
    console.log('Previewing OpenSCAD code...');  
    OpenSCAD.addConsoleMessage('Previewing OpenSCAD code...', 'info');  
      
    try {  
        // Parse OpenSCAD code and render  
        const parsedCode = openscadOpenJscadParser.parse(code);  
        const csgObject = eval('(' + parsedCode + ')')();  
          
        if (csgObject && (csgObject instanceof CSG || csgObject instanceof CAG)) {  
            OpenSCAD.viewer.setCsg(csgObject);  
            OpenSCAD.addConsoleMessage('Preview completed successfully', 'success');  
            console.log('Preview completed successfully');  
        } else {  
            OpenSCAD.addConsoleMessage('No valid 3D object generated', 'error');  
            console.error('No valid 3D object generated');  
        }  
    } catch (e) {  
        OpenSCAD.addConsoleMessage('Preview error: ' + e.message, 'error');  
        console.error('Preview error: ' + e.message);  
    }  
};  
  
// Render function (similar to preview but with different processing)  
OpenSCAD.renderCode = function() {  
    if (!OpenSCAD.editor) {  
        console.error('Editor not initialized');  
        return;  
    }  
      
    const code = OpenSCAD.editor.getValue();  
    if (!code.trim()) {  
        OpenSCAD.addConsoleMessage('Please enter some OpenSCAD code first', 'warning');  
        return;  
    }  
      
    OpenSCAD.addConsoleMessage('Rendering OpenSCAD code...', 'info');  
    console.log('Rendering OpenSCAD code...');  
      
    try {  
        // Use the same preview logic for now  
        OpenSCAD.previewCode();  
    } catch (e) {  
        OpenSCAD.addConsoleMessage('Render error: ' + e.message, 'error');  
        console.error('Render error: ' + e.message);  
    }  
};  
  
// Save design function  
OpenSCAD.saveDesign = function() {  
    if (!OpenSCAD.editor) {  
        console.error('Editor not initialized');  
        return;  
    }  
      
    const code = OpenSCAD.editor.getValue();  
    const filename = prompt('Enter filename:', 'design.scad') || 'design.scad';  
      
    try {  
        const blob = new Blob([code], { type: 'text/plain' });  
        if (typeof saveAs === 'function') {  
            saveAs(blob, filename);  
            OpenSCAD.addConsoleMessage('Design saved as ' + filename, 'success');  
        } else {  
            // Fallback download method  
            const url = URL.createObjectURL(blob);  
            const a = document.createElement('a');  
            a.href = url;  
            a.download = filename;  
            document.body.appendChild(a);  
            a.click();  
            document.body.removeChild(a);  
            URL.revokeObjectURL(url);  
            OpenSCAD.addConsoleMessage('Design downloaded as ' + filename, 'success');  
        }  
    } catch (e) {  
        OpenSCAD.addConsoleMessage('Save error: ' + e.message, 'error');  
        console.error('Save error: ' + e.message);  
    }  
};  
  
// New design function  
OpenSCAD.newDesign = function() {  
    if (!OpenSCAD.editor) {  
        console.error('Editor not initialized');  
        return;  
    }  
      
    if (confirm('Create new design? Unsaved changes will be lost.')) {  
        OpenSCAD.editor.setValue(`// New OpenSCAD design  
// Start creating your 3D model here  
  
cube([10, 10, 10]);`);  
        OpenSCAD.addConsoleMessage('New design created', 'info');  
    }  
};  
  
// Export STL function  
OpenSCAD.exportSTL = function() {  
    OpenSCAD.addConsoleMessage('Exporting STL...', 'info');  
      
    try {  
        if (OpenSCAD.viewer && OpenSCAD.viewer.meshes && OpenSCAD.viewer.meshes.length > 0) {  
            // Get current CSG object and export as STL  
            const currentObject = OpenSCAD.viewer.currentObject || OpenSCAD.viewer.meshes[0];  
            if (currentObject && typeof currentObject.toStlString === 'function') {  
                const stlData = currentObject.toStlString();  
                const blob = new Blob([stlData], { type: 'application/octet-stream' });  
                  
                if (typeof saveAs === 'function') {  
                    saveAs(blob, 'model.stl');  
                } else {  
                    // Fallback download  
                    const url = URL.createObjectURL(blob);  
                    const a = document.createElement('a');  
                    a.href = url;  
                    a.download = 'model.stl';  
                    document.body.appendChild(a);  
                    a.click();  
                    document.body.removeChild(a);  
                    URL.revokeObjectURL(url);  
                }  
                  
                OpenSCAD.addConsoleMessage('STL exported successfully', 'success');  
            } else {  
                OpenSCAD.addConsoleMessage('No valid 3D model to export', 'error');  
            }  
        } else {  
            OpenSCAD.addConsoleMessage('3D viewer not ready for export', 'error');  
        }  
    } catch (e) {  
        OpenSCAD.addConsoleMessage('Export error: ' + e.message, 'error');  
        console.error('Export error: ' + e.message);  
    }  
};  
  
// Console message helper function  
OpenSCAD.addConsoleMessage = function(message, type) {  
    type = type || 'info';  
    const consoleOutput = document.getElementById('consoleOutput');  
    if (consoleOutput) {  
        const div = document.createElement('div');  
        div.className = `text-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'}`;  
        div.textContent = new Date().toLocaleTimeString() + ': ' + message;  
        consoleOutput.appendChild(div);  
        consoleOutput.scrollTop = consoleOutput.scrollHeight;  
    }  
    console.log(type.toUpperCase() + ': ' + message);  
};  
  
// Initialize when DOM is ready (text-editor version)  
document.addEventListener('DOMContentLoaded', function() {  
    // Wait for all scripts to load  
    setTimeout(function() {  
        OpenSCAD.init();  
    }, 1000);  
});  
  
// Keyboard shortcuts  
document.addEventListener('keydown', function(e) {  
    if (e.key === 'F5') {  
        e.preventDefault();  
        OpenSCAD.previewCode();  
    } else if (e.key === 'F6') {  
        e.preventDefault();  
        OpenSCAD.renderCode();  
    } else if (e.ctrlKey && e.key === 's') {  
        e.preventDefault();  
        OpenSCAD.saveDesign();  
    }  
});  
  
// Export OpenSCAD namespace for global access  
window.OpenSCAD = OpenSCAD;
