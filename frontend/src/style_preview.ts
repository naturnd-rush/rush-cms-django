/*****************************************************************
 * This script generates a map style preview for a single style. *
 *****************************************************************/

import { Point } from "leaflet";
import { getStyleById } from "./graphql";
import { getCentroid } from "./utils/math";
import { expectEl, expectQuerySelector, waitForElementById } from "./utils/timing";

/**
 * Data used to draw the preview.
 */
type PreviewState = {
    // Draw the stroke-line
    drawStroke: boolean,
    strokeOptions: {
        color: string,
        weight: number,
        opacity: number,
        lineJoin: string,
        lineCap: string,
        dashOffset: string | null,
        dashArray: string | null,
    },
    // Draw the polygon fill
    drawFill: boolean,
    fillOptions: {
        color: string,
        opacity: number,
    },
    // Draw the icon marker
    drawMarker: boolean,
    markerOptions: {
        data: string | null, // blob icon data
        bgColor: string,
        bgOpacity: number,
        markerOpacity: number,
        markerSize: number,
    },
};

/**
 * Declarative source for preview updates.
 */
type UpdateSource = {
    groupName: "Toggle" | "Stroke" | "Fill" | "Marker", // For collapsing and expanding admin field groups
    eventName: "input" | "change", // For registering HTMLInputElement event listeners
    el: HTMLInputElement | null, // The element to listen to for updates
    update: (el: HTMLInputElement) => void, // A function that knows how to update the preview state based on the data from an HTMLInputElement.
};

/**
 * Build "points string" to use in SVG <polygon> element.
 * @param points the array of points to return in string-representation.
 */
function getPointsAsString(points: Array<Point>): string{
    let result = "";
    for (let point of points){
        result += point.x + "," + point.y + " ";
    }
    return result;
}

/**
 * Get a style-preview HTML code as a string.
 * @param state the style-preview state used to generate the HTML code.
 */
function getPreviewHTML(state: PreviewState): string {
    const svgWidth = 400;
    const svgHeight = 400;
    const markerImageWidth = state.markerOptions.markerSize;
    const markerRadius = Math.sqrt(Math.pow(markerImageWidth / 2, 2) + Math.pow(markerImageWidth / 2, 2));
    const polygonPoints: Array<Point> = [
        new Point(40, 40),
        new Point(200, 80),
        new Point(280, 160),
        new Point(120, 240),
        new Point(40, 160),
    ];

    // Declare SVG header and polygon with points
    let html = `
    <svg
        width="${svgWidth}px"
        height="${svgHeight}px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${getPointsAsString(polygonPoints)}"
    `

    // Add stroke styling
    if (state.drawStroke){
        html += `
            stroke="${state.strokeOptions.color}"
            stroke-width="${state.strokeOptions.weight}"
            stroke-opacity="${state.strokeOptions.opacity}"
            stroke-linecap="${state.strokeOptions.lineCap}"
            stroke-linejoin="${state.strokeOptions.lineJoin}"
            stroke-dasharray="${state.strokeOptions.dashArray}"
            stroke-dashoffset="${state.strokeOptions.dashOffset}"
        `
    }

    // Add fill styling
    if (state.drawFill){
        html += `
            fill="${state.fillOptions.color}"
            fill-opacity="${state.fillOptions.opacity}"
        `
    } else {
        html += 'fill="none"'
    }
    html += '/>'; // End of polygon

    // Add marker circle / background
    const centroid = getCentroid(polygonPoints);
    if (state.drawMarker){
        // refX and Y should be HALF the width & height to center the image on the actual point
        html += `
        <circle 
            id="marker-centroid"
            r="${markerRadius}px"
            fill=${state.markerOptions.bgColor}
            opacity=${state.markerOptions.bgOpacity}
            cx=${centroid.x}
            cy=${centroid.y}
        />
        `
    }
    html += '</svg>' // End of SVG

    // Add marker icon inside circle / background
    if (state.drawMarker && state.markerOptions.data !== null){
        html += `
        <img 
            id="marker-image"
            src="${state.markerOptions.data}"
            width="${markerImageWidth}"
            height="${markerImageWidth}"
            style='
                position: absolute;
                left: ${centroid.x - markerImageWidth/2}px;
                top: ${centroid.y - markerImageWidth/2}px;
                opacity: ${state.markerOptions.markerOpacity}
            '
        />'
        `
    }
    //console.log("Drawing svg from preview state: ", html, state);
    return html
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

/**
 * Collapse a group of Django admin fields.
 * @param toggleEl the input checkbox that toggles a group of admin fields.
 * @param optionsGroup the group of admin fields.
 */
function collapseGroup(groupName: UpdateSource["groupName"], toggleEl: HTMLInputElement, sources: Array<UpdateSource>): void {
    const COLLAPSE_BG_COLOR = "#FFFFFF";
    getFormRow(toggleEl)?.style.setProperty("background-color", COLLAPSE_BG_COLOR);
    for (let element of getGroup(groupName, sources)){
        const row = getFormRow(element);
        if (row !== null){
            row.style.display = "none";
        }
    }
}

/**
 * Expand a group of Django admin fields.
 * @param toggleEl the input checkbox that toggles a group of admin fields.
 * @param optionsGroup the group of admin fields.
 */
function expandGroup(groupName: UpdateSource["groupName"], toggleEl: HTMLInputElement, sources: Array<UpdateSource>): void {
    const EXPAND_BG_COLOR = "#E2DBC4";
    getFormRow(toggleEl)?.style.setProperty("background-color", EXPAND_BG_COLOR);
    for (let element of getGroup(groupName, sources)){
        const row = getFormRow(element);
        if (row !== null){
            row.style.display = "block";
        }
    }
}

/**
 * Get a group of HTMLInputElements given a group name and an array of update sources.
 */
function getGroup(groupName: UpdateSource["groupName"], sources: Array<UpdateSource>): Array<HTMLInputElement>{
    let group = [];
    for (let source of sources){
        if (source.groupName === groupName && source.el !== null){
            group.push(source.el);
        }
    }
    return group;
}

/**
 * Read a file.
 * @param file the file to read.
 * @returns a string / blob of the file contents.
 */
export function readFile(file: File | Blob): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
    });
}

document.addEventListener('DOMContentLoaded', () => {(async () => {

    const adminForm = document.querySelector('form');
    if (adminForm) {
        adminForm.addEventListener('submit', function () {
            console.log('Form is being submitted!');  // You can also trigger a spinner, custom callback, etc.
        });
    }

    // Hooks into a preview box provided by the style admin class.
    const previewContainer = expectEl('style_preview') as HTMLDivElement;
    const styleId = expectEl("injected-style-id").innerHTML;
    const baseMediaUrl = expectEl("injected-media-url").innerHTML;
    const stylePreview = expectQuerySelector(document, ".field-style_preview");
    console.log(stylePreview);

    // Define a default preview state (this is temporary because we will update the preview 
    // based on the admin form's currently selected style attributes on page load).
    let previewState: PreviewState = {
        drawStroke: false,
        drawFill: false,
        drawMarker: false,
        strokeOptions: {color: "#FFFFFF", opacity: 1, weight: 1, lineJoin: "", lineCap: "ROUND", dashArray: "", dashOffset: "0"},
        fillOptions: {color: "#FFFFFF", opacity: 1},
        markerOptions: {bgColor: "#FFFFFF", bgOpacity: 1, data: null, markerOpacity: 1, markerSize: 22},
    };

    const sources:  Array<UpdateSource> = [
        
        // Style group toggles
        {
            groupName: "Toggle",
            el: document.querySelector('#id_draw_stroke'),
            update: (el) => {
                el.checked ? expandGroup("Stroke", el, sources) : collapseGroup("Stroke", el, sources);
                previewState.drawStroke = el.checked;
            },
            eventName: "input",
        },
        {
            groupName: "Toggle",
            el: document.querySelector('#id_draw_fill'),
            update: (el) => {
                el.checked ? expandGroup("Fill", el, sources) : collapseGroup("Fill", el, sources);
                previewState.drawFill = el.checked;
            },
            eventName: "input",
        },
        {
            groupName: "Toggle",
            el: document.querySelector('#id_draw_marker'),
            update: (el) => {
                el.checked ? expandGroup("Marker", el, sources) : collapseGroup("Marker", el, sources);
                previewState.drawMarker = el.checked;
            },
            eventName: "input",
        },

        // Stroke fields
        {
            groupName: "Stroke",
            el: document.querySelector('#id_stroke_color'),
            update: (el) => previewState.strokeOptions.color = el.value,
            eventName: "input",
        },
        {
            groupName: "Stroke",
            el: document.querySelector('#id_stroke_weight'),
            update: (el) => previewState.strokeOptions.weight = Number(el.value),
            eventName: "input",
        },
        {
            groupName: "Stroke",
            el: document.querySelector('#id_stroke_opacity'),
            update: (el) => previewState.strokeOptions.opacity = Number(el.value),
            eventName: "input",
        },
        {
            groupName: "Stroke",
            el: document.querySelector('#id_stroke_line_cap'),
            update: (el) => previewState.strokeOptions.lineCap = el.value,
            eventName: "input",
        },
        {
            groupName: "Stroke",
            el: document.querySelector('#id_stroke_line_join'),
            update: (el) => previewState.strokeOptions.lineJoin = el.value,
            eventName: "input",
        },
        {
            groupName: "Stroke",
            el: document.querySelector('#id_stroke_dash_array'),
            update: (el) => previewState.strokeOptions.dashArray = el.value,
            eventName: "input",
        },
        {
            groupName: "Stroke",
            el: document.querySelector('#id_stroke_dash_offset'),
            update: (el) => previewState.strokeOptions.dashOffset = el.value,
            eventName: "input",
        },

        // Fill fields
        {
            groupName: "Fill",
            el: document.querySelector('#id_fill_color'),
            update: (el) => previewState.fillOptions.color = el.value,
            eventName: "input",
        },
        {
            groupName: "Fill",
            el: document.querySelector('#id_fill_opacity'),
            update: (el) => previewState.fillOptions.opacity = Number(el.value),
            eventName: "input",
        },

        // Marker fields
        {
            groupName: "Marker",
            el: document.querySelector('#id_marker_icon'),
            update: async (el) => {

                // Updating the marker icon image is a little more complicated, because the
                // data can come from two places. When a file has been previously saved, we
                // fetch the data and display that, but when a new marker icon file is selected
                // the file object exists directly in the DOM, so we can just use that.

                // Check to see if a new file has been selected
                let file = null;
                if (el.files){
                    file = el.files[0];
                }
                if (file) {
                    // Newly selected file --> read data and update.
                    const markerData = await readFile(file);
                    previewState.markerOptions.data = markerData;
                } else {
                    // Old file --> fetch the data, then read and update.
                    // This is probably not the best way to get the previously saved image data, but
                    // I wanted something that didn't rely on Django's file input's "Currently" section 
                    // link (see the field row in the admin site), which doesn't appear with an ID in the
                    // DOM. This way, I can be sure that the image data (if it exists) is being accessed.
                    if (styleId !== ""){ 
                        const style = await getStyleById(styleId);
                        if (style !== null){
                            const url = baseMediaUrl + style.markerIcon;
                            const response = await fetch(url);
                            const blob = await response.blob();
                            const markerData = await readFile(blob);
                            previewState.markerOptions.data = markerData;
                        }
                    } else {
                        // Style ID is empty when we are rendering an Add form (new style), as opposed to
                        // an Edit form (existing style). If we are adding a new style don't attempt to fetch
                        // the style object from the database and simply set the marker-icon data to null.
                        previewState.markerOptions.data = null;
                    }
                }
            },
            eventName: "change",
        },
        {
            groupName: "Marker",
            el: document.querySelector('#id_marker_icon_opacity'),
            update: (el) => previewState.markerOptions.markerOpacity = Number(el.value),
            eventName: "input",
        },
        {
            groupName: "Marker",
            el: document.querySelector('#id_marker_background_color'),
            update: (el) => previewState.markerOptions.bgColor = el.value,
            eventName: "input",
        },
        {
            groupName: "Marker",
            el: document.querySelector('#id_marker_background_opacity'),
            update: (el) => previewState.markerOptions.bgOpacity = Number(el.value),
            eventName: "input",
        },
        {
            groupName: "Marker",
            el: document.querySelector('#id_marker_size'),
            update: (el) => {
                previewState.markerOptions.markerSize = Number(el.value);

            },
            eventName: "input",
        },
    ];

    // Add event listeners for each update source 
    for (let source of sources){
        const updateFn = async () => {
            if (source.el !== null){
                await source.update(source.el);
                previewContainer.innerHTML = getPreviewHTML(previewState);
            }
        };
        source?.el?.addEventListener(source.eventName, updateFn);
        await updateFn(); // Update from the source to draw the initial preview
    }
    
})();});
