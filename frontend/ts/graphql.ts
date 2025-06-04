/**
 * This module provides a way to interface with the GraphQL API.
 */


/**
 * Something went wrong while trying to access the GraphQL API.
 */
export class GraphQLError extends Error {

    status: number;
    responseBody: string;

    constructor(status: number, responseBody: string) {
        super(`GraphQL request failed with status ${status}`);
        this.status = status;
        this.responseBody = responseBody;
    }
}

export class StyleNotFound {}
export class Style {
  constructor(
    
    // stroke options
    public drawStroke: boolean,
    public strokeColor: string,
    public strokeWeight: number,
    public strokeOpacty: number,
    public strokeLineJoin: string,
    public strokeDashArray: string,
    public strokeDashOffset: string,
    
    // fill options
    public drawFill: boolean,
    public fillColor: string,
    public fillOpacity: number,

  ) {}
}

/**
 * Query the GraphQL API.
 * @param query The GraphQL Query to execute.
 * @returns A JSON response Promise.
 * @throws GraphQLError when the request fails.
 */
export async function queryGraphQL(query: string): Promise<any> {
    const response = await fetch("/graphql/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            // TODO Add CSRF token here
        },
        body: query,
    });
    if (200 === response.status){
        return response.json();
    }
    const errorText = await response.text();
    throw new GraphQLError(response.status, errorText);
}

/**
 * Get "Style" data for a single object.
 * @param styleModelId the Django "Style" model id to fetch.
 * @returns Style data for the given object.
 */
export async function getStyleData(styleModelId: string): Promise<Style | StyleNotFound> {
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
    const style = await queryGraphQL(
        JSON.stringify({
            query: stylesOnLayerQuery,
            variables: {id: styleModelId},
        }
    ));
    if (style?.data?.style === null || style?.data?.style === undefined){
        return new StyleNotFound();
    }
    return style.data.style;
}
