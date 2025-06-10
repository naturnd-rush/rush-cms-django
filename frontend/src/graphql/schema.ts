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

export interface StyleOnLayer{
    id: string, 
    style: {
        drawStroke: boolean,
        strokeColor: string,
        strokeWeight: number,
    },
}

export async function getStylesOnLayerById(stylesOnLayerId: string): Promise<StyleOnLayer> {
    const query = `
        query ($id: UUID!) {
            stylesOnLayer(id: $id) {
                id
                style {
                    drawStroke
                    strokeColor
                    strokeWeight
                }
            }
        }
    `;
    const response = await executeQuery(
        JSON.stringify({
            query,
            variables: {
                id: stylesOnLayerId
            }
        })
    );
    const styleOnLayer: StyleOnLayer = response.data.stylesOnLayer;
    return styleOnLayer;
}

export const SchemaMetadataSchema = z.object({
    getByIdName: z.string(),
    getAllName: z.string(),
});
export type SchemaMetadata = z.infer<typeof SchemaMetadataSchema>;

const BOOLEAN = z.boolean();
const STRING = z.string();
const NUMBER = z.preprocess((v) => Number(v), z.number());
const NULLABLE_STRING = z.string().nullable();
const NULLABLE_NUMBER = z.preprocess((v) => Number(v), z.number().nullable());

export const StyleSchema = z.object({
    id: STRING,

    // stroke options
    drawStroke: BOOLEAN,
    strokeColor: STRING,
    strokeWeight: NUMBER,
    strokeOpacity: NUMBER,
    strokeLineJoin: STRING,
    strokeDashArray: NULLABLE_STRING,
    strokeDashOffset: NULLABLE_NUMBER,
    
    // fill options
    drawFill: BOOLEAN,
    fillColor: STRING,
    fillOpacity: NUMBER,

    // marker options
    drawMarker: BOOLEAN,
    markerIcon: STRING, // stored as the relative path of the icon
    markerIconOpacity: NUMBER,

}).describe(JSON.stringify({
    getByIdName: "style",
    getAllName: "allStyles",
}));
export type Style = z.infer<typeof StyleSchema>;
