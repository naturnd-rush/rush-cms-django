/**
 * This script pulls input data from the style change form and injects
 * a preview widget so people can visualize the style in real time.
 */

function updatePreview(previewContainer: HTMLDivElement, styleOptions: any): void {
    let svg = '<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">'
    if (styleOptions.drawMarker.checked === true) {
        //svg += '<image href="' + iconUr
        //const iconUrl = previewBox.dataset.iconUrl;  // e.g. "/media/icons/myicon.png"l + '" x="80" y="10" width="32" height="32" />';
        console.log(styleOptions.marker.icon);
    }

    svg += '<defs><marker id="img-marker" ';
    svg += 'markerWidth="20" markerHeight="20" ';
    svg += 'refX="10" refY="10" ';
    svg += 'markerUnits="userSpaceOnUse" ';
    svg += 'orient="auto">';
    svg += '<image href="https://upload.wikimedia.org/wikipedia/commons/8/84/Example.svg" x="0" y="0" width="20" height="20" />';
    svg += '</marker></defs>';

    svg += '<polygon points="20,20 100,40 140,80 60,120 20,80"'
    if (styleOptions.drawStroke.checked === true){
        svg += 'stroke="' + styleOptions.stroke.color.value + '"'
        svg += 'stroke-width="' + styleOptions.stroke.weight.value + '"'
        svg += 'stroke-opacity="' + styleOptions.stroke.opacity.value + '"'
        svg += 'stroke-linecap="' + styleOptions.stroke.lineCap.value + '"'
        svg += 'stroke-linejoin="' + styleOptions.stroke.lineJoin.value + '"'
        svg += 'stroke-dasharray="' + styleOptions.stroke.dashArray.value + '"'
        svg += 'stroke-dashoffset="' + styleOptions.stroke.dashOffset.value + '"'
    }
    if (styleOptions.drawFill.checked === true) {
        svg += 'fill="' + styleOptions.fill.color.value + '"'
        svg += 'fill-opacity="' + styleOptions.fill.opacity.value + '"'
    } else {
        svg += 'fill="none"'
    }
    if (styleOptions.drawMarker.checked === true){
        svg += 'marker-start="url(#img-marker)"';
        svg += 'marker-mid="url(#img-marker)"';
        svg += 'marker-end="url(#img-marker)"';
    }
    svg += '/></svg>'

    previewContainer.innerHTML = svg;
}

/**
 * Get the Django form-row parent div element from a (potentially nested) child element.
 * @param childEl the child element (inside a Django form-row).
 * @returns the HTMLDivElement, or null if the parent couldn't be found.
 */
function getFormRow(childEl: HTMLInputElement): HTMLDivElement | null {
    let container = childEl.parentElement;
    while (container !== null && !container.classList.contains("form-row")){
        container = container.parentElement;
    }
    return container as HTMLDivElement;
}

// function disableFormCheckboxRow(formRowEl: HTMLDivElement, formRowCheckbox: HTMLInputElement, disableColor: string): void {
//     formRowCheckbox.checked = false;
//     formRowCheckbox.disabled = true;
//     formRowEl?.style.setProperty("color", disableColor, "important");
//     formRowEl.querySelectorAll('*').forEach(child => {
//         const childHTMLElement = child as HTMLElement;
//         childHTMLElement.style.setProperty('color', 'inherit', 'important')
//     });
// }

// function enableFormCheckboxRow(formRowEl: HTMLDivElement, formRowCheckbox: HTMLInputElement, enableColor: string): void {
//     formRowCheckbox.disabled = false;
//     formRowEl?.style.setProperty("color", enableColor, "important");
//     formRowEl.querySelectorAll('*').forEach(child => {
//         const childHTMLElement = child as HTMLElement;
//         childHTMLElement.style.setProperty('color', 'inherit', 'important')
//     });
// }

function collapseGroup(optionsGroup: Array<HTMLInputElement>): void {
    for (let element of optionsGroup){
        const row = getFormRow(element);
        if (row !== null){
            row.style.display = "none";
        }
    }
}

function expandGroup(optionsGroup: Array<HTMLInputElement>): void {
    for (let element of optionsGroup){
        const row = getFormRow(element);
        if (row !== null){
            row.style.display = "block";
        }
    }
}

/**
 * Collapse and expand options groups for stroke, fill, and marker style options.
 * This function also changes the background color of the toggle rows.
 */
function collapseAndExpandOptionGroups(styleOptions: any): void {

    // Get toggle parent rows for styling the checkbox background colors
    const checkBoxSelectedBgColor = "#E2DBC4";
    const checkBoxUnselectedBgColor = "#FFFFFF";
    const checkBoxDisabledTextColor = "#E0E0E0";
    const checkBoxEnabledTextColor = "#666666";
    const strokeCheckBoxRow = getFormRow(styleOptions.drawStroke);
    const fillCheckBoxRow = getFormRow(styleOptions.drawFill);
    const markerCheckBoxRow = getFormRow(styleOptions.drawMarker);

    // Special-case: when the marker toggle is selected, the fill and stroke checkboxes shall be unselected.
    // if (strokeCheckBoxRow !== null && fillCheckBoxRow !== null){
    //     if (styleOptions.drawMarker.checked === true){
    //         disableFormCheckboxRow(strokeCheckBoxRow, styleOptions.drawStroke, checkBoxDisabledTextColor);
    //         disableFormCheckboxRow(fillCheckBoxRow, styleOptions.drawFill, checkBoxDisabledTextColor);
    //     } else {
    //         enableFormCheckboxRow(strokeCheckBoxRow, styleOptions.drawStroke, checkBoxEnabledTextColor);
    //         enableFormCheckboxRow(fillCheckBoxRow, styleOptions.drawFill, checkBoxEnabledTextColor);
    //     }
    // }
    
    // Collapse
    if (styleOptions.drawStroke.checked === false){
        collapseGroup(Object.values(styleOptions.stroke));
        strokeCheckBoxRow?.style.setProperty("background-color", checkBoxUnselectedBgColor);
    }
    if (styleOptions.drawFill.checked === false){
        collapseGroup(Object.values(styleOptions.fill));
        fillCheckBoxRow?.style.setProperty("background-color", checkBoxUnselectedBgColor);
    }
    if (styleOptions.drawMarker.checked === false){
        collapseGroup(Object.values(styleOptions.marker));
        markerCheckBoxRow?.style.setProperty("background-color", checkBoxUnselectedBgColor);
    }

    // Expand
    if (styleOptions.drawStroke.checked === true){
        expandGroup(Object.values(styleOptions.stroke));
        strokeCheckBoxRow?.style.setProperty("background-color", checkBoxSelectedBgColor);
    }
    if (styleOptions.drawFill.checked === true){
        expandGroup(Object.values(styleOptions.fill));
        fillCheckBoxRow?.style.setProperty("background-color", checkBoxSelectedBgColor);
    }
    if (styleOptions.drawMarker.checked === true){
        expandGroup(Object.values(styleOptions.marker));
        markerCheckBoxRow?.style.setProperty("background-color", checkBoxSelectedBgColor);
    }
}

document.addEventListener('DOMContentLoaded', () => {

    let styleOptions = {
        drawFill: document.querySelector('#id_draw_fill') as HTMLInputElement,
        drawMarker: document.querySelector('#id_draw_marker') as HTMLInputElement,
        drawStroke: document.querySelector('#id_draw_stroke') as HTMLInputElement,
        stroke: {
            color: document.querySelector('#id_stroke_color'),
            weight: document.querySelector('#id_stroke_weight'),
            opacity: document.querySelector('#id_stroke_opacity'),
            lineCap: document.querySelector('#id_stroke_line_cap'),
            lineJoin: document.querySelector('#id_stroke_line_join'),
            dashArray: document.querySelector('#id_stroke_dash_array'),
            dashOffset: document.querySelector('#id_stroke_dash_offset'),
        },
        fill: {
            color: document.querySelector('#id_fill_color'),
            opacity: document.querySelector('#id_fill_opacity'),
        },
        marker: {
            icon: document.querySelector('#live_image_input_marker_icon'),
            opacity: document.querySelector('#id_marker_icon_opacity'),
        },
    };

    const allOptionsAndToggles = [
        styleOptions.drawStroke, ...Object.values(styleOptions.stroke),
        styleOptions.drawFill, ...Object.values(styleOptions.fill),
        styleOptions.drawMarker, ...Object.values(styleOptions.drawMarker),
    ];
    for (let element of allOptionsAndToggles){
        if (element === null){
            console.log(allOptionsAndToggles);
            throw new Error("Missing element!");
        }
    }

    // Hooks into a preview box provided by the style admin class.
    const previewContainer = document.getElementById('style_preview') as HTMLDivElement | null;
    if (previewContainer === null){
        throw new Error("Expected DOM element with id 'style_preview' to exist!");
    }

    // Add event-listeners for redrawing the style preview.
    for (let element of allOptionsAndToggles){
        const input = element as HTMLInputElement;
        input.addEventListener('input', () => updatePreview(previewContainer, styleOptions));
        input.addEventListener('input', () => collapseAndExpandOptionGroups(styleOptions));
    }

    // Add event listeners for collapsing and expanding options groups
    styleOptions.drawStroke.addEventListener("change", () => collapseAndExpandOptionGroups(styleOptions));

    // Draw initial style preview on page-load.
    collapseAndExpandOptionGroups(styleOptions);
    updatePreview(previewContainer, styleOptions);
});
