import {type Style, getStyleById, getMapDataByName} from "./graphql"
import type { FeatureCollection, Geometry, Feature, Point, Position, Polygon } from 'geojson';
import type {PathOptions, StyleFunction} from "leaflet"
import * as L from 'leaflet';
import { waitForElementById, coerceNumbersDeep, blendHexColors, interpolateNumbers, expectEl, getCentroid } from "./utils";
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

/**
 * Find which styles apply to a given GeoJSON feature.
 * @param feature the feature to get applied styles for.
 * @param stylesOnLayer the styles present on the current map layer.
 * @returns an array of styles that should be applied to the given feature.
 */
function getAppliedStyles(feature: Feature<Geometry, any>, stylesOnLayer: Array<StyleOnLayer>): Array<Style>{
    const parser = new Parser();
    let applied: Array<Style> = [];
    for (let styleOnLayer of stylesOnLayer){
        const fieldMappingContainer = styleOnLayer.inlineRow.querySelector("td[class*='feature_mapping']");
        const fieldMappingErrors = fieldMappingContainer?.querySelector("div[id*='errors']");
        try{
            const expr = parser.parse(styleOnLayer.feature_mapping);
            if (expr.evaluate(coerceNumbersDeep(feature.properties)) === true){
                applied.push(styleOnLayer.style);
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
        if (state.stylesOnLayer.length == 0){
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

        for (let style of appliedStyles){

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
        return {
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
        };
    };
    return func as StyleFunction;
}

function getMarkerDivIcon(baseMediaUrl: string, markerStyle: Style): L.DivIcon {
    const markerBackgroundSize = 32;
    const markerImageWidth = 26;
    return L.divIcon({
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
    });
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
        for (let style of appliedStyles){
            if (style.drawMarker && style.markerIcon.trimStart().trimEnd() !== ""){
                markerStyle = style;
                break;
            }
        }

        if (markerStyle === null){
            // Return default leaflet marker style if no style is applied
            return L.marker(latlng);
        }

        // Otherwise return the styled marker
        return L.marker(latlng, {
            icon: getMarkerDivIcon(baseMediaUrl, markerStyle),
        });
    };
    return func;
}

function drawMapPreview(map: L.Map, state: MapPreviewState, update: MapPreviewUpdate): void{

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
    
    
    const baseMediaUrl = expectEl('injected-media-url').innerHTML;
    const anyMarkerStyles = state.stylesOnLayer.filter(styleOnLayer => styleOnLayer.style.drawMarker == true).length > 0;
    const styledGeoJsonData = L.geoJSON(state.currentLayer.toGeoJSON(), {
        style: getPolygonStyleFunc(state),
        pointToLayer: getPointStyleFunc(baseMediaUrl, state),
        onEachFeature: (feature, layer) => {
            // Draw centroid icon markers when a marker icon style is applied to a polygon feature
            const isPolygon = feature.geometry.type.toUpperCase().includes("POLYGON");
            if (isPolygon && anyMarkerStyles){
                const multiPolygonFeature = feature as Feature<Polygon, any>;
                const appliedStyles = getAppliedStyles(feature, state.stylesOnLayer);
                const markerStyles = appliedStyles.filter(style => style.drawMarker == true);
                if (markerStyles.length > 0){
                    const markerStyle = markerStyles[0]; // Just take the first marker style if multiple applied.
                    for (let polygonCoords of multiPolygonFeature.geometry.coordinates){
                        const coords = (polygonCoords[0] as unknown) as Position[]; // For some reason there is another nested array in here at runtime, idk why...
                        const points: Array<L.Point> = [];
                        for (let coord of coords){
                            points.push(new L.Point(coord[0], coord[1]))
                        }
                        const centroid = getCentroid(points);

                        const marker = L.marker(new L.LatLng(centroid.y, centroid.x), {
                            icon: getMarkerDivIcon(baseMediaUrl, markerStyle),
                        });
                        marker.addTo(map);
                    }
                }
            }
        },
    });
    state.currentLayer = styledGeoJsonData;
    styledGeoJsonData.addTo(map)
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
    
    // Listen to redraw the map when the tab is refocused (the user leaves and then comes back).
    // This can happen after a user edits one of the inline styles and then clicks on the layer edit tab.
    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') {
            getStyleUpdate().then(styleUpdate => {
                drawMapPreview(map, mapPreviewState, styleUpdate);
            });
        }
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
