document.addEventListener('DOMContentLoaded', () => {
    console.log('JS LOADED!');
    const strokeColor = document.querySelector('#id_stroke_color');
    const strokeWeight = document.querySelector('#id_stroke_weight');
    const textInput = document.querySelector('#id_text_color');
    const fontSizeInput = document.querySelector('#id_font_size');
    const previewBox = document.getElementById('style_preview');

    console.log(previewBox);

    function updatePreview() {
        if (!previewBox) return;
        let svg = '<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">'
        svg += '<polygon points="20,20 100,40 140,80 60,120 20,80"'
        svg += 'fill="none"'
        svg += 'stroke="' + strokeColor.value + '"'
        svg += 'stroke-width="' + strokeWeight.value + '"'
        svg += 'stroke-opacity="1"'
        svg += 'stroke-linecap="round"'
        svg += 'stroke-dasharray="4 1"'
        svg += 'stroke-linejoin="round"/>'
        //{'stroke-dasharray="'+stroke_dash_array+'"' if stroke_dash_array else ''}
        svg += '</svg>'

        previewBox.innerHTML = svg;
    }

    [strokeColor, strokeWeight].forEach(input => {
        input.addEventListener('input', updatePreview);
    });

    updatePreview();
});
