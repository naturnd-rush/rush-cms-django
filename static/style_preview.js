/**
 * This script pulls input data from the style change form and injects
 * a preview widget so people can visualize the style in real time.
 */
document.addEventListener('DOMContentLoaded', () => {

    // Stroke options
    const drawStroke = document.querySelector('#id_draw_stroke');
    const strokeColor = document.querySelector('#id_stroke_color');
    const strokeWeight = document.querySelector('#id_stroke_weight');
    const strokeOpacity = document.querySelector('#id_stroke_opacity');
    const strokeLineCap = document.querySelector('#id_stroke_line_cap');
    const strokeLineJoin = document.querySelector('#id_stroke_line_join');
    const strokeDashArray = document.querySelector('#id_stroke_dash_array');
    const strokeDashOffset = document.querySelector('#id_stroke_dash_offset');
    
    // Fill options.
    const drawFill = document.querySelector('#id_draw_fill');
    const fillColor = document.querySelector('#id_fill_color');
    const fillOpacity = document.querySelector('#id_fill_opacity');
    const fillRule = document.querySelector('#id_fill_rule');


    // Hooks into a preview box provided by the style admin class.
    const previewBox = document.getElementById('style_preview');
    function updatePreview() {
        // Abort if no style preview box found.
        if (!previewBox) return;
        let svg = '<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">'
        svg += '<polygon points="20,20 100,40 140,80 60,120 20,80"'
        if (drawStroke.checked === true){
            svg += 'stroke="' + strokeColor.value + '"'
            svg += 'stroke-width="' + strokeWeight.value + '"'
            svg += 'stroke-opacity="' + strokeOpacity.value + '"'
            svg += 'stroke-linecap="' + strokeLineCap.value + '"'
            svg += 'stroke-linejoin="' + strokeLineJoin.value + '"'
            svg += 'stroke-dasharray="' + strokeDashArray.value + '"'
            svg += 'stroke-dashoffset="' + strokeDashOffset.value + '"'
        }
        if (drawFill.checked === true) {
            svg += 'fill="' + fillColor.value + '"'
            svg += 'fill-opacity="' + fillOpacity.value + '"'
            // svg += 'fill-rule="' + fillRule.value + '"' <-- Gonna handle this later, seems like an extreme edge-case for using the admin site.
        } else {
            svg += 'fill="none"'
        }
        svg += '/></svg>'

        previewBox.innerHTML = svg;
    }

    [
        // Stroke event listeners.
        drawStroke, 
        strokeColor, 
        strokeWeight, 
        strokeOpacity, 
        strokeLineCap, 
        strokeLineJoin, 
        strokeDashArray, 
        strokeDashOffset, 
        
        // Fill event listeners.
        drawFill, 
        fillColor, 
        fillOpacity,

    ].forEach(input => {
        input.addEventListener('input', updatePreview);
    });

    // Create preview on initial page-load.
    updatePreview();
});
