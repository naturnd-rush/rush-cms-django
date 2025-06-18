import {type Style, getStyleById, getMapDataByName} from "./graphql"
import type { FeatureCollection, Geometry, Feature } from 'geojson';
import type {PathOptions, StyleFunction} from "leaflet"
import * as L from 'leaflet';
import { waitForElementById, coerceNumbersDeep, blendHexColors, interpolateNumbers } from "./utils";
import { Parser } from 'expr-eval';

/************
 * This script draws a map layer preview based on the currently selected map-data object and
 * the combination of style on layer objects currently being applied to the map layer.
 ************/

export interface StyleOnLayer{
    style: Style,
    feature_mapping: string,
    inlineRow: Element,
}

export interface MapPreviewState {
    stylesOnLayer: Array<StyleOnLayer>,
    currentLayer: L.GeoJSON<any, Geometry> | null,
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

/**
 * Get the currently configured style data for this layer.
 */
export async function getStyleUpdate(): Promise<StyleUpdate> {
    const stylesOnLayers: Array<StyleOnLayer> = [];
    for (let inlineRow of document.querySelectorAll("tr[id*='stylesonlayer_set-']")){
        // for each styleOnLayer inline group
        const styleId = (inlineRow.querySelector("select[id*='-style']") as HTMLSelectElement)?.value;
        const featureMapping = (inlineRow.querySelector("textarea[id*='feature_mapping']") as HTMLInputElement | null)?.value;
        if (!(styleId && featureMapping)){
            // most likely an empty inline
            continue;
        }
        const style = await getStyleById(styleId);
        if (style !== null){
            stylesOnLayers.push({
                style: style,
                feature_mapping: featureMapping,
                inlineRow: inlineRow,
            });
        }
    }
    return {
        type: "Style",
        newStylesOnLayers: stylesOnLayers,
    };
}

/**
 * Fetch GeoJSON using the UUID present in the map-data input field.
 */
export async function getMapDataUpdate(mapDataSelectSpan: HTMLSpanElement): Promise<MapDataUpdate>{
    const clearMapData = {type: "MapData", newGeoJsonData: null} as MapDataUpdate;
    const mapDataName = mapDataSelectSpan.title;
    if (mapDataName === null || mapDataName === ""){
        return clearMapData;
    }
    const mapData = await getMapDataByName(mapDataName);
    if (mapData === null){
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
};

export function drawMapPreview(map: L.Map, state: MapPreviewState, update: MapPreviewUpdate): void{

    // Always remove the previous layer, if there is one, from the map. 
    // Otherwse, it overlaps with the new layer being drawn.
    if (state.currentLayer !== null){
        map.removeLayer(state.currentLayer);
    }

    // Update currentLayer if we are receiving new map data.
    if ("MapData" === update.type){
        const newGeoJson = (update as MapDataUpdate).newGeoJsonData;
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

    const parser = new Parser();
    const styleFunc = (feature: Feature<Geometry, any>): PathOptions => {

        // Find which styles should be applied to this feature by testing
        // the feature mapping against the feature's properties.
        // TODO: Error propagating code is NOT efficient! I should probably make this faster...
        let appliedStyles: Array<Style> = [];
        for (let styleOnLayer of state.stylesOnLayer){
            const fieldMappingContainer = styleOnLayer.inlineRow.querySelector("td[class*='feature_mapping']");
            const fieldMappingErrors = fieldMappingContainer?.querySelector("div[id*='errors']");
            try{
                const expr = parser.parse(styleOnLayer.feature_mapping);
                if (expr.evaluate(coerceNumbersDeep(feature.properties)) === true){
                    appliedStyles.push(styleOnLayer.style);
                    if (fieldMappingErrors && fieldMappingContainer){
                        fieldMappingContainer.removeChild(fieldMappingErrors);
                    }
                }
            } catch (error){
                // TODO: If a variable isn't in ANY of the features then we can display it here, othgerwise if it's 
                // being used at least once I don't think I should display an error since the style is technically 
                // being applied.

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

        // Build path options from the styles. If there are multiple
        // styles being applied to the same feature, we just give our
        // best guess at how the user wants their map to look by using
        // linear interpolation on what we can and overriding the rest...
        // TODO: Talked with Doug today and decided to send serialized JSON leaflet
        //       map layer object back to the frontend, so that we can resolve multiple styled
        //       applied to the same feature in a single location, and simplify the frontend code.
        //       Mark this TODO as done when an endpoint is exposed via GraphQL to get serialized leaflet
        //       layer data, which is serialized on layer model save.
        
        let drawFill = false;
        let drawStroke = false;
        let drawMarker = false;

        let fillOpacity = undefined;
        let strokeOpacity = undefined;
        let markerIconOpacity = undefined;

        let fillColor = undefined;
        let strokeColor = undefined;
        
        let strokeWeight = undefined;

        // Style attributes that can't be interpolated (just take the most recent one from the applied styles)
        let markerIcon = undefined;
        let strokeDashArray = "";
        let strokeDashOffset = undefined; // technically can be interpolated but I don't think it would be intuitive for a user
        let strokeLineCap = "round";
        let strokeLineJoin = "round";


        for (let style of appliedStyles){

            // If one style draws something then the combined style will also draw that thing
            if (style.drawFill === true){
                drawFill = true;
            }
            if (style.drawStroke === true){
                drawStroke = true;
            }
            if (style.drawMarker === true){
                drawMarker = true;
            }

            fillOpacity = interpolateNumbers(fillOpacity, style.fillOpacity);
            strokeOpacity = interpolateNumbers(strokeOpacity, style.strokeOpacity);

            // if (markerIconOpacity === undefined){
            //     markerIconOpacity = style.markerIconOpacity;
            // } else {
            //     // interpolate marker-icon opacity
            //     markerIconOpacity = (markerIconOpacity + style.markerIconOpacity) / 2;
            // }

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

            strokeWeight = interpolateNumbers(strokeWeight, style.strokeWeight);
            // if (strokeWeight === undefined){
            //     strokeWeight = style.strokeWeight;
            // } else {
            //     // interpolate stroke weight
            //     strokeWeight = (strokeWeight + style.strokeWeight) / 2;
            // }

            // just set / override the rest of the attributes
            if (style.markerIcon !== ""){
                markerIcon === style.markerIcon;
            }
            if (style.strokeDashArray !== null){
                strokeDashArray = style.strokeDashArray;
            }
            if (style.strokeDashOffset !== null){
                strokeDashOffset = style.strokeDashOffset;
            }
            strokeLineJoin = style.strokeLineJoin;
            strokeLineCap = style.strokeLineCap;
        }
        const featureStyle = {
            
            fill: drawFill,
            fillColor: fillColor,
            fillOpacity: fillOpacity,

            stroke: drawStroke,
            weight: strokeWeight,
            color: strokeColor,
            dashArray: strokeDashArray,
            dashOffset: strokeDashOffset,
            lineCap: strokeLineCap as L.LineCapShape,
            lineJoin: strokeLineJoin as L.LineJoinShape,

            // TODO: Handle markers
        };
        return featureStyle;
    };
    
    const styledGeoJsonData = L.geoJSON(state.currentLayer.toGeoJSON(), {
        style: styleFunc as StyleFunction,
        onEachFeature: (feature, layer) => {
            // // Optionally bind popups or other handlers
            // if (feature.properties && feature.properties.name) {
            //     layer.bindPopup(`Name: ${feature.properties.name}`);
            // }
        }
    });
    state.currentLayer = styledGeoJsonData;
    styledGeoJsonData.addTo(map)
}

document.addEventListener("DOMContentLoaded", () => {(async () => {

    // Initialize leaflet map
    let map = L.map('map-preview').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors',
    }).addTo(map);

    // Initialize object to track map preview state
    let mapPreviewState: MapPreviewState = {
        stylesOnLayer: [],
        currentLayer: null,
    };
    
    // Listen to redraw the map when a feature-mapping is changed. Because I want to update the
    // map live while the user is typing in the feature mapping text areas, I use the HTML "input"
    // event. However, it is likely that this will create too many updates, and subsequent API calls
    // to the GraphQL API for style data. To fix this, I simply keep track of whether we should update
    // the style data using this even listener, and check to dispatch this update every second or so.
    let fmUpdate = false;
    inlineElements.featureMappings.addEventListener(() => fmUpdate = true);
    const sendFmUpdateAndPoll = () => {
        if (fmUpdate === true){
            getStyleUpdate().then(styleUpdate => {
                drawMapPreview(map, mapPreviewState, styleUpdate);
            });
        }
        fmUpdate = false;
        setTimeout(sendFmUpdateAndPoll, 1000);
    };
    setTimeout(sendFmUpdateAndPoll, 1000);

    // Listen to redraw the map when a style is changed.
    inlineElements.styles.addEventListener(() => {
        getStyleUpdate().then(styleUpdate => {
            drawMapPreview(map, mapPreviewState, styleUpdate);
        });
    });

    // Hook into the map-data selection element
    const mapDataSelectSpanId = "select2-id_map_data-container";
    const mapDataSelectSpan = await waitForElementById(mapDataSelectSpanId);

    // Listen to redraw the map when the map-data is changed.
    const mapDataChangeObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === "childList") {
                getMapDataUpdate(mapDataSelectSpan).then((mapDataUpdate) => drawMapPreview(map, mapPreviewState, mapDataUpdate));
            }
        });
    });
    mapDataChangeObserver.observe(mapDataSelectSpan!, {childList: true});

    // Draw the initial map using the current map-data and style info.
    Promise.all([
        getStyleUpdate(), 
        getMapDataUpdate(mapDataSelectSpan),
    ]).then(([styleUpdate, mapDataUpdate]: [StyleUpdate, MapDataUpdate]) => {
        // Inefficient, but meh.
        drawMapPreview(map, mapPreviewState, mapDataUpdate);
        drawMapPreview(map, mapPreviewState, styleUpdate);
    });

})();});
