import {type Style, type MapData, getStyleById, getMapDataById} from "./graphql"
import type { FeatureCollection, Geometry, Feature, Point, Position, MultiPolygon } from 'geojson';
import type {PathOptions, StyleFunction} from "leaflet"
import * as L from 'leaflet';
import { coerceNumbersDeep, blendHexColors, interpolateNumbers, getCentroid, cyrb53 } from "./utils/math";
import { waitForElementById, expectEl, ThrottledSignalReceiver, expectQuerySelector } from "./utils/timing";
import { Parser } from 'expr-eval';
import Mustache from "mustache";
import { DynamicSubscriberManager } from './utils/events'

/************
 * This script draws a map layer preview based on the currently selected map-data object and
 * the combination of style on layer objects currently being applied to the map layer.
 ************/

export interface StyleOnLayer{
    style: Style,
    feature_mapping: string,
    popupTemplate: string | null,
    inlineRow: Element,
}

export interface MapPreviewState {
    isUpdating: boolean,
    stylesOnLayer: Array<StyleOnLayer>,
    currentLayer: L.GeoJSON<any, Geometry> | null,
    centroidMarkers: L.LayerGroup,
}

/**
 * Represents a change in the map preview state.
 */
export interface MapPreviewUpdate {
    type: "Style" | "MapData",
}
export interface StyleUpdate extends MapPreviewUpdate {
    newStylesOnLayers: Array<StyleOnLayer>,
}
export interface MapDataUpdate extends MapPreviewUpdate {
    newGeoJsonData: FeatureCollection<Geometry, any> | null,
}

interface AppliedStyle{
    style: Style,
    popupTemplate: string | null,
}

interface PopupMetadata {
    __hasPopup: boolean;
    __popupHTML: string | null;
    __popupOptions: object | null;
}

/**
 * Get the currently configured style data for this layer.
 */
export async function getStyleUpdate(): Promise<StyleUpdate> {
    const stylesOnLayers: Array<StyleOnLayer> = [];
    for (let inlineRow of document.querySelectorAll("tr[id*='stylesonlayer_set-']")){
        // for each styleOnLayer inline group
        const styleId = (inlineRow.querySelector("select[id*='-style']") as HTMLSelectElement)?.value;
        const featureMapping = (inlineRow.querySelector("textarea[id*='feature_mapping']") as HTMLInputElement | null)?.value;
        const popupTemplate = (inlineRow.querySelector("textarea[id*='popup']") as HTMLInputElement | null)?.value;
        if (!(styleId && featureMapping)){
            // most likely an empty inline
            continue;
        }
        const style = await getStyleById(styleId);
        if (style !== null){
            stylesOnLayers.push({
                style: style,
                feature_mapping: featureMapping,
                popupTemplate: popupTemplate !== undefined ? popupTemplate : null,
                inlineRow: inlineRow,
            });
        }
    }
    return {
        type: "Style",
        newStylesOnLayers: stylesOnLayers,
    };
}

async function mapDataFromSpan(mapDataSelectSpan: HTMLSpanElement): Promise<MapData | null> {
    let mapDataId = null;
    for (let child of mapDataSelectSpan.childNodes){
        if (child instanceof HTMLOptionElement && child.selected){
            console.log(child);
            mapDataId = child.value;
        }
    }
    if (mapDataId === null || mapDataId === ""){
        return null;
    }
    return await getMapDataById(mapDataId);
}

/**
 * Fetch GeoJSON using the UUID present in the map-data input field.
 */
export async function getMapDataUpdate(mapDataSelectSpan: HTMLSpanElement): Promise<MapDataUpdate>{
    const clearMapData = {type: "MapData", newGeoJsonData: null} as MapDataUpdate;
    const mapData = await mapDataFromSpan(mapDataSelectSpan);
    if (mapData === null){
        return clearMapData;
    } else if (mapData.geojson === null){
        return clearMapData;
    }
    const geojson = JSON.parse(mapData.geojson);
    if (geojson.features === null || geojson.features === undefined){
        return clearMapData;
    }
    return {
        type: "MapData",
        newGeoJsonData: geojson as FeatureCollection,
    }
}


/**
 * Namespaced accessor for adding StyleOnLayer inline element event listeners. 
 * This code isn't the most efficient, but I'm leaving it for now because it works...
 */
export const inlineElements = {
    styles: {
        addEventListener: (callback: (mutation: MutationRecord) => void): void => {
            const inlineGroup = document.getElementById('stylesonlayer_set-group');
            if (inlineGroup !== null) {
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.target instanceof HTMLSelectElement && mutation.type === "childList"){
                            callback(mutation);
                        }
                    });
                });
                observer.observe(inlineGroup, {childList: true, subtree: true});
            }
        },
    },
    featureMappings: {
        addEventListener: (callback: (event: Event) => void): void => {
            document.addEventListener('input', (event) => {
                const target = event.target;
                const featureChanged = target instanceof HTMLTextAreaElement && target.id.includes('feature_mapping');
                if (featureChanged) {
                    callback(event);
                }
            });
        },
    },
    popups: {
         addEventListener: (callback: (mutation: MutationRecord) => void): void => {
            const inlineGroup = document.getElementById('stylesonlayer_set-group');
            if (inlineGroup !== null) {
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.target instanceof HTMLSelectElement && mutation.type === "childList"){
                            callback(mutation);
                        }
                    });
                });
                observer.observe(inlineGroup, {childList: true, subtree: true});
            }
        },
    },
};

/**
 * Find which styles apply to a given GeoJSON feature.
 * @param feature the feature to get applied styles for.
 * @param stylesOnLayer the styles present on the current map layer.
 * @returns an array of styles that should be applied to the given feature. 
 */
function getAppliedStyles(feature: Feature<Geometry, any>, stylesOnLayer: Array<StyleOnLayer>): Array<AppliedStyle>{
    const parser = new Parser();
    let applied: Array<AppliedStyle> = [];
    for (let styleOnLayer of stylesOnLayer){
        const fieldMappingContainer = styleOnLayer.inlineRow.querySelector("td[class*='feature_mapping']");
        const fieldMappingErrors = fieldMappingContainer?.querySelector("div[id*='errors']");
        try{
            const expr = parser.parse(styleOnLayer.feature_mapping);
            if (expr.evaluate(coerceNumbersDeep(feature.properties)) === true){
                applied.push({style: styleOnLayer.style, popupTemplate: styleOnLayer.popupTemplate});
                if (fieldMappingErrors && fieldMappingContainer){
                    fieldMappingContainer.removeChild(fieldMappingErrors);
                }
            }
        } catch (error){
            // TODO: If a variable isn't in ANY of the features then we can display it here, otherwise if it's 
            // being used at least once I don't think I should display an error since the style is technically 
            // being applied.

            // TODO: Error propagating code is NOT efficient! I should probably make this faster...

            // Add an error message above the feature mapping textarea for the user if parsing fails.
            if (fieldMappingErrors && fieldMappingContainer){
                fieldMappingContainer.removeChild(fieldMappingErrors);
            }
            if (fieldMappingContainer && !fieldMappingContainer?.querySelector("div[id*='errors']")){
                const errorEl = document.createElement("div");
                errorEl.textContent = String(error);
                errorEl.id = "errors";
                errorEl.style = "color:rgb(255, 0, 0);";
                fieldMappingContainer.insertBefore(errorEl, fieldMappingContainer.children[0]);
            }   
        }
    }
    return applied;
}

function getDefaultPolygonStyle(): PathOptions{
    return {
        // Path fill options.
        fill: true,
        fillColor: "#4B3EFF",
        fillOpacity: 0.3,
        // Path stroke options.
        stroke: true,
        weight: 1,
        opacity: 1,
        color: "#4B3EFF",
        dashArray: "1 10",
        dashOffset: "0",
        lineCap: "round",
        lineJoin: "round",
    };
}

/**
 * Get a function used to style polygon GeoJSON features on a leaflet map.
 * @param state the MapPreviewState.
 * @returns a leaflet StyleFunction.
 */
function getPolygonStyleFunc(state: MapPreviewState): StyleFunction {
    const func = (feature: Feature<Geometry, any>) => {

        // If no stylesOnLayers are in the map preview state, just return a default polygon styling.
        if (state.stylesOnLayer.length == 0 && !state.isUpdating){
            return getDefaultPolygonStyle();
        }

        // Otherwise, build path options from the styles. If there are multiple
        // styles being applied to the same feature, we just give our
        // best guess at how the user wants their map to look by interpolating them
        // or overriding if they can't be interpolated.
        let appliedStyles = getAppliedStyles(feature, state.stylesOnLayer);
        
        let drawFill = false;
        let fillOpacity = undefined;
        let fillColor = undefined;
        
        let drawStroke = false;
        let strokeOpacity = undefined;
        let strokeColor = undefined;
        let strokeWeight = undefined;

        // Style attributes that can't be interpolated (just take the most recent one from the applied styles)
        let strokeDashArray = "";
        let strokeDashOffset = undefined; // technically can be interpolated but I don't think it would be intuitive for a user
        let strokeLineCap = "round";
        let strokeLineJoin = "round";

        for (let appliedStyle of appliedStyles){
            const style = appliedStyle.style;

            // If one style draws something then the combined style will also draw that thing
            if (style.drawFill === true){
                drawFill = true;
            }
            if (style.drawStroke === true){
                drawStroke = true;
            }

            fillOpacity = interpolateNumbers(fillOpacity, style.fillOpacity);
            strokeOpacity = interpolateNumbers(strokeOpacity, style.strokeOpacity);
            strokeWeight = interpolateNumbers(strokeWeight, style.strokeWeight);

            if (fillColor === undefined){
                fillColor = style.fillColor;
            } else {
                // interpolate fill color
                fillColor = blendHexColors(fillColor, style.fillColor, 0.5);
            }
            if (strokeColor === undefined){
                strokeColor = style.strokeColor;
            } else {
                // interpolate stroke color
                strokeColor = blendHexColors(strokeColor, style.strokeColor, 0.5);
            }

            // Just override the rest without interpolation...
            if (style.strokeDashArray !== null){
                strokeDashArray = style.strokeDashArray;
            }
            if (style.strokeDashOffset !== null){
                strokeDashOffset = style.strokeDashOffset;
            }
            strokeLineJoin = style.strokeLineJoin;
            strokeLineCap = style.strokeLineCap;
        }
        const polygonStyleProps = {
            // Path fill options.
            fill: drawFill,
            fillColor: fillColor,
            fillOpacity: fillOpacity,
            // Path stroke options
            stroke: drawStroke,
            weight: strokeWeight,
            opacity: strokeOpacity,
            color: strokeColor,
            dashArray: strokeDashArray,
            dashOffset: strokeDashOffset,
            lineCap: strokeLineCap as L.LineCapShape,
            lineJoin: strokeLineJoin as L.LineJoinShape,
        }

        // Inject style props into properties for layer serialization
        feature.properties.__style = polygonStyleProps;

        return polygonStyleProps;
    };
    return func as StyleFunction;
}

/**
 * Get styled properties for a marker div icon.
 * @param baseMediaUrl the base media url for the RUSH admin server.
 * @param markerStyle the marker style.
 */
function getMarkerDivIconProps(baseMediaUrl: string, markerStyle: Style): any{
    const markerBackgroundSize = 32;
    const markerImageWidth = 26;
    return {
        html: `
            <div 
                style="
                    width: ${markerBackgroundSize}px;
                    height: ${markerBackgroundSize}px;
                    background-color: ${markerStyle.markerBackgroundColor};
                    opacity: ${markerStyle.markerIconOpacity};
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                "
            >
                <img 
                    src="${baseMediaUrl + markerStyle.markerIcon}"
                    style="
                        width: ${markerImageWidth}px; 
                        height: ${markerImageWidth}px;
                    "
                />
            <div/>
        `,
        className: '', // Disable default Leaflet styles
        iconSize: [markerBackgroundSize, markerBackgroundSize],
        iconAnchor: [markerBackgroundSize/2, markerBackgroundSize/2], // Center the icon around the latlng
    };
}

/**
 * Get a function used to style Point GeoJSON features on a leaflet map.
 * @param baseMediaUrl the base URL for fetching media files from the server.
 * @param state the current map preview state.
 * @returns a function that returns a leaflet marker object.
 */
function getPointStyleFunc(baseMediaUrl: string, state: MapPreviewState): (feature: Feature<Point, any>, latlng: L.LatLng) => L.Marker {
    const func = (feature: Feature<Point, any>, latlng: L.LatLng) => {

        // Grab the first applied style that has a non-empty marker icon configured to be drawn
        let markerStyle: Style | null = null;
        const appliedStyles = getAppliedStyles(feature, state.stylesOnLayer);
        for (let appliedStyle of appliedStyles){
            const style = appliedStyle.style;
            if (style.drawMarker && style.markerIcon.trimStart().trimEnd() !== ""){
                markerStyle = style;
                break;
            }
        }

        if (markerStyle === null){
            // Return default leaflet marker style if no style is applied
            return L.marker(latlng);
        }

        // Inject marker div icon props into point feature properties for serialization
        const markerDivIconProps = getMarkerDivIconProps(baseMediaUrl, markerStyle);
        feature.properties.__pointDivIconStyleProps = markerDivIconProps;

        // Otherwise return the styled marker
        return L.marker(latlng, {
            icon: new L.DivIcon(markerDivIconProps),
        });
    };
    return func;
}

/**
 * Get a centroid Point from a group 
 * @param polygonCoords 
 * @returns 
 */
function getPolygonCentroid(polygonCoords: Position[]): L.Point{
    const points: Array<L.Point> = [];
    for (let coord of polygonCoords){
        points.push(new L.Point(coord[0], coord[1]))
    }
    return getCentroid(points);
}

async function showSpinner(){

    const saveBtn = expectQuerySelector(document.body, "input[name='_save']") as HTMLInputElement;
    const addAnotherBtn = expectQuerySelector(document.body, "input[name='_addanother']") as HTMLInputElement;
    const continueBtn = expectQuerySelector(document.body, "input[name='_continue']") as HTMLInputElement;
    saveBtn.disabled = true;
    addAnotherBtn.disabled = true;
    continueBtn.disabled = true;

    console.log("SHOWING SPINNER");
    const mapPreviewEl = document.getElementById("map-preview");
    const spinnerEl = document.getElementById("map-spinner");
    if (mapPreviewEl !== null && spinnerEl !== null){
        mapPreviewEl.classList.add('blur');
        spinnerEl.classList.remove('hidden');
    } else {
        console.error("Couldn't find map-preview and map-spinner in the DOM!");
    }

    // THIS IS BAD: SPINNER SHOWING QUERIES AN ASYNC REQUEST!!!
    // const mapDataSelectSpan = await waitForElementById("id_map_data");
    // const initialMapDataProviderState = (await mapDataFromSpan(mapDataSelectSpan))?.providerState;
    // if (initialMapDataProviderState && initialMapDataProviderState === "GEOJSON"){
    //     console.log("SHOWING SPINNER");
    //     const mapPreviewEl = document.getElementById("map-preview");
    //     const spinnerEl = document.getElementById("map-spinner");
    //     if (mapPreviewEl !== null && spinnerEl !== null){
    //         mapPreviewEl.classList.add('blur');
    //         spinnerEl.classList.remove('hidden');
    //     } else {
    //         console.error("Couldn't find map-preview and map-spinner in the DOM!");
    //     }
    // }
}

function hideSpinner(){
    
    const saveBtn = expectQuerySelector(document.body, "input[name='_save']") as HTMLInputElement;
    const addAnotherBtn = expectQuerySelector(document.body, "input[name='_addanother']") as HTMLInputElement;
    const continueBtn = expectQuerySelector(document.body, "input[name='_continue']") as HTMLInputElement;
    saveBtn.disabled = false;
    addAnotherBtn.disabled = false;
    continueBtn.disabled = false;
    
    const mapPreviewEl = document.getElementById("map-preview");
    const spinnerEl = document.getElementById("map-spinner");
    if (mapPreviewEl !== null && spinnerEl !== null){
        mapPreviewEl.classList.remove('blur');
        spinnerEl.classList.add('hidden');
    } else {
        console.error("Couldn't find map-preview and map-spinner in the DOM!");
    }
}

function showSpinnerAfter(numSeconds: number, state: MapPreviewState): void {
    setTimeout(() => {
        if (state.isUpdating){
            showSpinner();
        }
    }, numSeconds * 1000)
}

/**
 * Extract latitude / longitude positions from a set of geometry coordinates. This function is used to normalize
 * the feature geometry across Polygons and MultiPolygons because I have found that the array nesting is not consistent 
 * depending on the GeoJSON data being pushed into the system at runtime...
 * @param coordinates any leaflet "feature.geometry.coordinates" object.
 * @returns an array of "polygons", which are defined here as a list of lists of numbers, where the innermost list only ever 
 * has 2 elements (lat and long).
 */
function extractLatLngGroups(coordinates: any): Position[][] {
    const result: Position[][] = [];
    function traverse(node: any): void {
        if (Array.isArray(node) && node.length > 0) {
            if (typeof node[0] === 'number' && typeof node[1] === 'number') {
                // Base case: This is a Position, add as a group
                result.push([node as Position]);
            } else if (typeof node[0][0] === 'number') {
                // This is a flat array of Positions
                result.push(node as Position[]);
            } else {
                // Still nested, keep traversing
                for (const child of node) {
                    traverse(child);
                }
            }
        }
    }
    traverse(coordinates);
    return result;
}

/**
 * Get the popup metadata from the given popup template.
 * @param popupTemplate a string, or null, if no template exists.
 * @returns some popup metadata that can be used to tell leaflet how, and whether,
 * to render a popup.
 */
function getPopupMetadata(feature: Feature<Geometry, any>, popupTemplate: string | null): PopupMetadata {
    if (popupTemplate === null){
        return {
            __hasPopup: false,
            __popupHTML: null,
            __popupOptions: null,
        };
    }

    // Hack for resizing popup images to always fit inside the popup container. There is probably a better way to do this.
    let hasImage = false;
    popupTemplate = popupTemplate.replace(/<img(.*?)>/g, (match) => {
        hasImage = true;
        return match.replace('<img', '<img style="max-width:250px; height:auto;"');
    });
    const renderedPopup = Mustache.render(popupTemplate, feature.properties);
    const popupOptions = {
        maxWidth: 250,
        // Shrink the popup container to the size of the text if no image is present in the popup.
        // Otherwise, resize the image width to be 250 pixels and set the minimum popup container 
        // to be the same size as well.
        minWidth: hasImage ? 250 : 0,
    };

    return {
        __hasPopup: true,
        __popupHTML: renderedPopup,
        __popupOptions: popupOptions,
    };
}

/**
 * Get an optionally defined popup template from a list of applied styles.
 * @param appliedStyles a list of styles applied to some feature.
 * @returns a string template, or null if no popup template is defined in any of the applied styles.
 */
function getPopupTemplate(appliedStyles: Array<AppliedStyle>): string | null {
    let popupTemplate = null;
    for (let appliedStyle of appliedStyles){
        if (appliedStyle.popupTemplate !== null && appliedStyle.popupTemplate !== ""){
            popupTemplate = appliedStyle.popupTemplate;
        }
    }
    return popupTemplate;
}

function drawMapPreview(map: L.Map, state: MapPreviewState, update: MapPreviewUpdate): void {

    // Always remove the previous layer, if there is one, from the map. 
    // Otherwse, it overlaps with the new layer being drawn.
    if (state.currentLayer !== null){
        map.removeLayer(state.currentLayer);
    }
    state.centroidMarkers.clearLayers();

    // Update currentLayer if we are receiving new map data.
    if ("MapData" === update.type){
        const newGeoJson = (update as MapDataUpdate).newGeoJsonData;
        console.log("Re-drawing map layer from new map data update: ", update);
        if (newGeoJson === null){
            state.currentLayer = null;
        } else {
            state.currentLayer = L.geoJSON(newGeoJson);
            map.fitBounds(state.currentLayer.getBounds());
        }
    }

    // Update stylesOnLayer if we are receiving new style data
    else if ("Style" === update.type) {
        state.stylesOnLayer = (update as StyleUpdate).newStylesOnLayers;
    }

    /**
     * Begin drawing the map.
     */

    if (state.currentLayer === null){
        // Exit if there is no layer to draw at this point...
        return;
    }
    
    
    const baseMediaUrl = expectEl('injected-media-url').innerHTML;
    const anyMarkerStyles = state.stylesOnLayer.filter(styleOnLayer => styleOnLayer.style.drawMarker == true).length > 0;
    const styledGeoJsonData = L.geoJSON(state.currentLayer.toGeoJSON(), {
        style: getPolygonStyleFunc(state),
        pointToLayer: getPointStyleFunc(baseMediaUrl, state),
        onEachFeature: (feature, layer) => {

            const appliedStyles = getAppliedStyles(feature, state.stylesOnLayer);
            const popupTemplate = getPopupTemplate(appliedStyles);
            const popupMetadata = getPopupMetadata(feature, popupTemplate);
            if (popupMetadata.__hasPopup === true && popupMetadata.__popupHTML !== null && popupMetadata.__popupOptions !== null){
                layer.bindPopup(popupMetadata.__popupHTML, popupMetadata.__popupOptions);
                feature.properties = {...feature.properties, ...popupMetadata};
            }

            // Draw centroid icon markers when a marker icon style is applied to a polygon feature
            const isPolygon = feature.geometry.type === "MultiPolygon";
            if (isPolygon && anyMarkerStyles){
                const multiPolygonFeature = feature as Feature<MultiPolygon, any>;
                const markerStyles = appliedStyles.filter(appliedStyle => appliedStyle.style.drawMarker == true);
                if (markerStyles.length > 0){
                    const markerStyle = markerStyles[0].style; // Just take the first marker style if multiple applied.
                    for (let polygonCoords of multiPolygonFeature.geometry.coordinates){
                        const coords = (polygonCoords[0] as unknown) as Position[]; // For some reason there is another nested array in here at runtime, idk why...
                        const points: Array<L.Point> = [];
                        for (let coord of coords){
                            points.push(new L.Point(coord[0], coord[1]))
                        }
                        const centroid = getCentroid(points);
                        const markerDivIconProps = getMarkerDivIconProps(baseMediaUrl, markerStyle);

                        // Build the centroid marker icon feature with serializable divIcon and popup metadata
                        const centroidMarkerIconFeature = {
                            type: "Feature",
                            geometry: { type: "Point", coordinates: [centroid.x, centroid.y] },
                            properties: {
                                // Serialize leaflet markerDivIcon properties
                                __pointDivIconStyleProps: markerDivIconProps,

                                // Serialize leaflet popup metadata so it can be re-created later
                                ...popupMetadata,
                            },
                        } as Feature<Point, any>;

                        // Extract a leaflet marker from the feature.
                        const marker = L.geoJSON(centroidMarkerIconFeature, {
                            pointToLayer: (geoJsonPoint, latlng) => L.marker(latlng, {
                                icon: new L.DivIcon(markerDivIconProps),
                            }),
                        }).getLayers()[0];

                        // Bind a leaflet popup to the marker if necessary
                        if (popupMetadata.__hasPopup === true && popupMetadata.__popupHTML !== null && popupMetadata.__popupOptions !== null){
                            marker.bindPopup(popupMetadata.__popupHTML, popupMetadata.__popupOptions);
                        }
                        marker.addTo(state.centroidMarkers);
                    }
                }
            }
        },
    });
    state.currentLayer = styledGeoJsonData;
    styledGeoJsonData.addTo(map)
    hideSpinner();
    state.isUpdating = false;

    // Save serialized leaflet json to a hidden field so it can be saved on the Layer model
    const hiddenField = expectEl("id_serialized_leaflet_json") as HTMLInputElement;
    hiddenField.value = serializeLayer(state);

}

/**
 * Serialize the layer preview information as a Leaflet LayerGroup object.
 * @param state the current map preview state.
 * @returns a string of serialized JSON data with a LayerGroup containing the styled
 * data in the layer preview. 
 */
function serializeLayer(state: MapPreviewState): string {
    let allLayers = new L.LayerGroup(state.centroidMarkers.getLayers());
    state.currentLayer?.addTo(allLayers);
    return JSON.stringify({
        featureCollection: allLayers.toGeoJSON(),
    });
}

document.addEventListener("DOMContentLoaded", () => {(async () => {
    
    const TILE_LAYER_OPTS = {
        minZoom: 0,
        maxZoom: 22,
        updateWhenIdle: true,
        zIndex: 0,
        attribution: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
    }
    const MAPBOX_USER = 'rushadmin'
    const MAPBOX_STYLEID = 'clw2m6f9b018001obfxcc747g'
    const MAPBOX_TOKEN = 'pk.eyJ1IjoicnVzaGFkbWluIiwiYSI6ImNsdzJtYmRydzBuNDIyam5yZ2pwMG16cnUifQ.SkSSdHcrPq4u8HSitBvJcg'
    const API_URL = `https://api.mapbox.com/styles/v1/`
    const API_TILE_PATH = `${MAPBOX_USER}/${MAPBOX_STYLEID}/tiles/256/{z}/{x}/{y}@2x`
    const API_PARAMS = `?access_token=${MAPBOX_TOKEN}`

    // Initialize leaflet map
    let map = L.map('map-preview').setView([0, 0], 2);
    L.tileLayer(API_URL + API_TILE_PATH + API_PARAMS, TILE_LAYER_OPTS).addTo(map);

    // Initialize object to track map preview state
    let mapPreviewState: MapPreviewState = {
        isUpdating: true,
        stylesOnLayer: [],
        currentLayer: null,
        centroidMarkers: new L.LayerGroup(),
    };
    mapPreviewState.centroidMarkers.addTo(map);

    // Move spinner from top of page to inside the map preview box and show the spinner initially as the map preview is drawn
    const mapDataSelectSpan = await waitForElementById("id_map_data");
    (await waitForElementById('id_map_data_helptext')).appendChild(await waitForElementById("map-spinner"));
    const initialMapDataProviderState = (await mapDataFromSpan(mapDataSelectSpan))?.providerState;
    hideSpinner(); // Spinner should be turned off by default... (this is needed so non-gejson map data layers don't initialize with a spinner that never goes away.)
    if (initialMapDataProviderState && initialMapDataProviderState === "GEOJSON"){
        // Render the spinner initially if the being edited is for GEOJSON map-data.
        showSpinner();
    }
    
    // Shorthand for redrawing the map by fetching new styles / popup info
    const doStyleUpdate = () => {
        mapDataFromSpan(mapDataSelectSpan).then((mapData) => {
            if (mapData?.providerState === "GEOJSON"){
                mapPreviewState.isUpdating = true;
                showSpinnerAfter(1, mapPreviewState);
                getStyleUpdate().then(styleUpdate => {
                    drawMapPreview(map, mapPreviewState, styleUpdate);
                });
            }
        });
    };

    // Some update events need to be throttled for performance
    const throttledStyleUpdate = new ThrottledSignalReceiver(1000, doStyleUpdate);

    // Manage events declaratively, since new inline rows can be added 
    const subscriberManager = new DynamicSubscriberManager(document.body);

    // Style select dropdowns
    subscriberManager.subscribeMutationObserver({childList: true, subtree: true}, "span[id*='select2-id_stylesonlayer_set']", (_) => {
        doStyleUpdate();
    });

    // Feature mapping textareas
    subscriberManager.subscribeEventListener("input", "textarea[id*='-feature_mapping']", (_) => {
        throttledStyleUpdate.trigger();
    });

    // // Popup editors
    // subscriberManager.subscribeMutationObserver({childList: true, subtree: true, characterData: true}, "textarea[id*='popup']", (_) => {
    //     console.log('POPUP CHANGED: ', _);
    //     throttledStyleUpdate.trigger();
    // });
    // ^^^ not sure why this doesnt work but the below code does...

    // HACK FOR DFG PRESENTATION TODAY
    // I just want to get popup editing to refresh the map preview!
    // This is ineffecient!!! TODO: Fix me...
    let previousHash = 0;
    const pollPopupChanges = () => {
        const popupTemplates = [];
        for (let inlineRow of document.querySelectorAll("tr[id*='stylesonlayer_set-']")){
            const popupTemplate = (inlineRow.querySelector("textarea[id*='popup']") as HTMLInputElement | null)?.value;
            popupTemplates.push(popupTemplate);
        }
        const hash = cyrb53(JSON.stringify(popupTemplates));
        if (hash !== previousHash){
            previousHash = hash;
            doStyleUpdate();
        }
        setTimeout(pollPopupChanges, 1000);
    };
    pollPopupChanges();
    
    // Listen to redraw the map when the tab is refocused (the user leaves and then comes back).
    // This can happen after a user edits one of the inline styles and then clicks on the layer edit tab.
    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') {
            mapPreviewState.isUpdating = true;
            showSpinnerAfter(1, mapPreviewState);
            getStyleUpdate().then(styleUpdate => {
                drawMapPreview(map, mapPreviewState, styleUpdate);
            });
        }
    });

    // Listen to redraw the map when the map-data is changed.
    const mapPreviewEl = await waitForElementById("map-preview");
    const stylesOnLayersGroupEl = await waitForElementById("stylesonlayer_set-group");
    async function onMapDataDropdownChange(){
        const mapData = await mapDataFromSpan(mapDataSelectSpan);
        const hideMapPreviewAndStyles = () => {
            console.log("Hiding ", mapPreviewEl, stylesOnLayersGroupEl);
            mapPreviewEl.style.display = 'none';
            stylesOnLayersGroupEl.style.display = 'none';
        };
        const showMapPreviewAndStyles = () => {
            mapPreviewEl.style.display = 'block';
            stylesOnLayersGroupEl.style.display = 'block';
        };
        console.log(mapData?.providerState);
        if (mapData?.providerState === "GEOJSON"){
            showMapPreviewAndStyles();
            mapPreviewState.isUpdating = true;
            showSpinnerAfter(1, mapPreviewState);
            getMapDataUpdate(mapDataSelectSpan).then((mapDataUpdate) => drawMapPreview(map, mapPreviewState, mapDataUpdate));
        } else {
            // Hide map preview and styles on layers when we are not dealing with GEOJSON map data for this layer...
            hideMapPreviewAndStyles();
        }
    };
    onMapDataDropdownChange(); // for initial load
    mapDataSelectSpan.addEventListener("change", onMapDataDropdownChange);

    // Draw the initial map using the current map-data and style info.
    Promise.all([
        getStyleUpdate(), 
        getMapDataUpdate(mapDataSelectSpan),
    ]).then(([styleUpdate, mapDataUpdate]: [StyleUpdate, MapDataUpdate]) => {
        // Inefficient, but meh.
        drawMapPreview(map, mapPreviewState, mapDataUpdate);
        mapPreviewState.isUpdating = true; // Still doing the initial update...
        drawMapPreview(map, mapPreviewState, styleUpdate);
    });

})();});
