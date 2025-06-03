/**
 * This script refreshes map data using the GraphQL API whenever the "map_data" Django
 * admin field is changed and injects it into the page as a hidden element so it can be
 * used to render the Layer's map preview.
 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
/// <reference types="leaflet" />
import * as L from "leaflet";
import { queryGraphQL } from "graphql";
/**
 * The related StyleOnLayerInline data from all styles.
 */
function getStyleData() {
    return __awaiter(this, void 0, void 0, function* () {
        const styles = [];
        const stylesOnLayerSelector = "[id^='id_stylesonlayer_set-'][id$='-style']";
        const stylesOnLayerEls = document.querySelectorAll(stylesOnLayerSelector);
        const stylesOnLayerQuery = `
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
        for (const stylesOnLayerEl of stylesOnLayerEls) {
            const styleId = stylesOnLayerEl.nodeValue;
            console.log('getStyleData() found styleId: ' + styleId);
            const styleQuery = JSON.stringify({
                query: stylesOnLayerQuery,
                variables: { id: styleId },
            });
            const styleData = yield queryGraphQL(styleQuery);
            styles.push(styleData);
        }
        return styles;
    });
}
document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('id_map_data');
    const stylesOnLayersGroup = document.getElementById('stylesonlayer_set-group');
    // Initialize leaflet map
    let map = L.map('map-preview').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    let geoJsonLayer; // updated by drawMapPreview
    const drawMapPreview = () => {
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
                variables: { id: select.value },
            }),
        })
            .then((res) => res.json())
            .then((response) => {
            let mapData = response.data.mapData.geojson;
            try {
                mapData = JSON.parse(mapData);
            }
            catch (e) {
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
                                variables: { id: styleId },
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
            }
        })
            .catch((err) => {
            console.error("GraphQL error:", err);
        });
    };
    // Add event-listener to id_map_data so that when it changes we draw the map preview.
    const mapDataEl = document.getElementById('id_map_data');
    if (mapDataEl) {
        mapDataEl.addEventListener('change', function () {
            drawMapPreview();
        });
    }
    if (stylesOnLayersGroup) {
        stylesOnLayersGroup.addEventListener('change', function () {
            drawMapPreview();
        });
    }
    // Draw map preview after initial page load
    drawMapPreview();
});
