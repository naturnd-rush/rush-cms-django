import {type Style, type MapData, getStyleById, getMapDataById} from "./graphql"
import * as L from 'leaflet';

/************
 * This script refreshes map data using the GraphQL API whenever the "map_data" Django
 * admin field is changed and injects it into the page as a hidden element so it can be
 * used to render the Layer's map preview.
 ************/

interface StyleOnLayer{
    style: Style,
    feature_mapping: string,
}

interface MapPreviewState {
    geojson: string,
    stylesOnLayer: Array<StyleOnLayer>,
};

/**
 * Get the currently configured style data for this layer.
 */
async function getLayerStyleData(): Promise<Array<StyleOnLayer>> {
    const result: Array<StyleOnLayer> = [];
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
            result.push({
                style: style,
                feature_mapping: featureMapping,
            });
        }
    }
    return result;
}

/**
 * Fetch GeoJSON using the UUID present in the map-data input field.
 */
async function getGeojsonData(mapDataSelectEl: HTMLSelectElement): Promise<any>{    
    let mapDataId = mapDataSelectEl.value;
    if (mapDataId === null || mapDataId === ""){
        return JSON.parse("\{\}");
    }
    let mapData = await getMapDataById(mapDataId);
    if (mapData === null){
        return JSON.parse("\{\}");
    }
    return JSON.parse(mapData.geojson);
}

/**
 * Namespaced accessor for adding inline element event listeners. This code isn't the most
 * efficient, but I'm leaving it for now because it works...
 */
const inlineElements = {
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

function drawMapPreview(map: L.Map, state: MapPreviewState): void{
    console.log("Drawing map preview with state: ", state);
}

document.addEventListener('DOMContentLoaded', () => {

    // Initialize leaflet map
    let map = L.map('map-preview').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors',
    }).addTo(map);

    // Initialize object to track map preview state
    let mapPreviewState: MapPreviewState = {
        geojson: JSON.parse("\{\}"),
        stylesOnLayer: [],
    };

    // Hook into the map-data selection element
    const mapDataSelectEl = (document.getElementById('id_map_data') as HTMLSelectElement);
    if (mapDataSelectEl === null){
        throw new Error("Expected to find a DOM element with id='id_map_data'.");
    }

    const redrawOnStyleChange = () => {
        getLayerStyleData().then(stylesOnLayer => {
            mapPreviewState.stylesOnLayer = stylesOnLayer;
            drawMapPreview(map, mapPreviewState);
        });
    };

    const redrawOnGeojsonChange = () => {
        getGeojsonData(mapDataSelectEl).then(geojson => {
            mapPreviewState.geojson = geojson;
            drawMapPreview(map, mapPreviewState);
        })
    };

    // Listen to redraw the map when a style or feature-mapping is changed.
    inlineElements.featureMappings.addEventListener(redrawOnStyleChange);
    inlineElements.styles.addEventListener(redrawOnStyleChange);
    
    // Listen to redraw the map when the underlying map-data is changed.
    mapDataSelectEl.addEventListener("change", redrawOnGeojsonChange);

    // Draw the initial map using the current map-data and style info.
    Promise.all([
        getLayerStyleData(), 
        getGeojsonData(mapDataSelectEl),
    ]).then(([stylesOnLayer, geojson]: [Array<StyleOnLayer>, any]) => {
        mapPreviewState.stylesOnLayer = stylesOnLayer;
        mapPreviewState.geojson = geojson;
        drawMapPreview(map, mapPreviewState);
    });







    let geoJsonLayer; // updated by drawMapPreview
    const drawMapPreviewOld = () => {

        if (!select.value) {
            let emptyMapData = JSON.parse("\{\}"); // empty GeoJson data
            if (geoJsonLayer) {
                map.removeLayer(geoJsonLayer);
            }
            geoJsonLayer = L.geoJSON(emptyMapData).addTo(map);
            map.fitBounds(geoJsonLayer.getBounds());
        }
        const query = `
            query ($id: UUID!) {
                mapData(id: $id) {
                    geojson
                }
            }
        `;
        fetch("/graphql/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                // TODO Add CSRF token here
            },
            body: JSON.stringify({
                query: query,
                variables: {id: select.value},
            }),
        })
        .then((res) => res.json())
        .then((response) => {
            let mapData = response.data.mapData.geojson;
            try {
                mapData = JSON.parse(mapData);
            } catch (e) {
                console.warn("Invalid GeoJSON:", e);
                mapData = JSON.parse("\{\}"); // empty GeoJson data
            }
            finally {
                if (geoJsonLayer) {
                    map.removeLayer(geoJsonLayer);
                }

                // Get styles on layers object ids
                const styles = [];
                document.querySelectorAll("[id^='id_stylesonlayer_set-'][id$='-style']").forEach(input => {
                    if (input.value) {
                        let styleId = input.value;
                        const query = `
                            query ($id: UUID!) {
                                style(id: $id) {
                                    drawStroke
                                    strokeColor
                                    strokeWeight
                                    strokeOpacity
                                    strokeLineCap
                                    strokeLineJoin
                                    strokeDashArray
                                    strokeDashOffset
                                    drawFill
                                    fillColor
                                    fillOpacity
                                }
                            }
                        `;
                        fetch("/graphql/", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                                // TODO Add CSRF token here
                            },
                            body: JSON.stringify({
                                query: query,
                                variables: {id: styleId},
                            }),
                        })
                        .then((res) => res.json())
                        .then((response) => {
                            let style = response.data.style;
                            styles.push(style);
                            const mainStyle = styles[0];
                            console.log('main style vvv');
                            console.log(mainStyle);
                            let geoJsonLayer = L.geoJSON(mapData, {
                                style: function (feature) {
                                    return {
                                        color: mainStyle.strokeColor,
                                        weight: mainStyle.strokeWeight,
                                        opacity: mainStyle.strokeOpacity,
                                        lineCap: mainStyle.strokeLineCap,
                                        lineJoin: mainStyle.strokeLineJoin,
                                        dashArray: mainStyle.strokeDashArray,
                                        dashOffset: mainStyle.strokeDashOffset, 
                                        fillColor: mainStyle.fillColor,
                                        fillOpacity: parseFloat(mainStyle.fillOpacity),
                                    };
                                }
                            }).addTo(map);
                            map.fitBounds(geoJsonLayer.getBounds());
                        });
                    }
                });
                // // Default styles
                // geoJsonLayer = L.geoJSON(mapData, {
                //     style: function (feature) {
                //         return {
                //         color: "purple",         // stroke color
                //         weight: 2,               // stroke width
                //         opacity: 1.0,            // stroke opacity
                //         fillColor: "transparent",// no fill
                //         fillOpacity: 0
                //         };
                //     }
                // }).addTo(map);

            }})
        .catch((err) => {
            console.error("GraphQL error:", err);
        });
    };

    // Add event-listener to id_map_data so that when it changes we draw the map preview.
    const mapDataEl = document.getElementById('id_map_data');
    if (mapDataEl) {
        mapDataEl.addEventListener('change', function () {
            // drawMapPreview();
        });
    }

    if (stylesOnLayersGroup) {
        stylesOnLayersGroup.addEventListener('change', function () {
            // drawMapPreview();
        });
    }

    // Draw map preview after initial page load
    // drawMapPreview();

});