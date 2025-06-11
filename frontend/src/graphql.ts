import { z } from "zod"

/**
 * Typescript Schema for GraphQL models.
 * 
 * This module uses "Zod" to provide runtime type validation over input data (returned by GraphQL)
 * so we can be sure the data passing through our system at runtime conforms to TypeScript's type annotations.
 * See their docs: https://zod.dev/.
 */

/**
 * An error occurred during the GraphQL request.
 */
export class GraphQLRequestFailed extends Error {
    constructor(message: string){
      super(message);
    }
}

/**
 * Make an arbitrary query to GraphQL.
 * @param queryString the query-string to execute.
 * @returns A promise of Any data type. It is the responsibility of the
 * caller to make sure the typed response is correct.
 */
export async function executeQuery(queryString: string): Promise<any> {
    const response = await fetch("/graphql/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            // TODO Add CSRF token here
        },
        body: queryString,
    });
    const responseJson = await response.json();
    if (200 !== response.status){
        if (responseJson.errors === null || responseJson.errors === undefined){
            throw new GraphQLRequestFailed("GraphQL response code (" + response.status + ") is not 200 but no errors were sent back in the response!");
        }
        // something went wrong during the request
        throw new GraphQLRequestFailed(JSON.stringify(responseJson.errors));
    }
    // return full response json
    return responseJson;
}

export interface Style{
    // stroke options
    drawStroke: boolean,
    strokeColor: string,
    strokeWeight: number,
    strokeOpacity: number,
    strokeLineJoin: string,
    strokeDashArray: string | null,
    strokeDashOffset: number | null,

    // fill options
    drawFill: boolean,
    fillColor: string,
    fillOpacity: number,

    // marker options
    drawMarker: boolean,
    markerIcon: string, // relative path
    markerIconOpacity: number,
}

export async function getStyleById(styleId: string): Promise<Style | null> {
    const query = `
        query ($id: UUID!) {
            style(id: $id) {
                drawStroke
                strokeColor
                strokeWeight
                strokeOpacity
                strokeLineJoin
                strokeDashArray
                strokeDashOffset
                drawFill
                fillColor
                fillOpacity
                drawMarker
                markerIcon
                markerIconOpacity
            }
        }
    `;
    const response = await executeQuery(
        JSON.stringify({
            query,
            variables: {
                id: styleId
            }
        })
    );
    const style: Style | null = response.data.style;
    return style;
}

export interface MapData{
    geojson: string,
}

export async function getMapDataById(mapDataId: string): Promise<MapData | null>{
    const query = `
        query ($id: UUID!) {
            mapData(id: $id) {
                geojson
            }
        }
    `;
    const response = await executeQuery(
        JSON.stringify({
            query,
            variables: {
                id: mapDataId
            }
        })
    );
    const mapData: MapData | null = response.data.mapData;
    return mapData;
}
