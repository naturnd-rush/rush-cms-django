/**
 * This module provides a way to retrieve data from the GraphQL API by defining different object
 * types whose attributes will be fetched from the API's corresponding object type and returned.
 */
/**
 * A GraphQL query failed.
 */
export class GraphQLQueryFailed {
    constructor(errors) { }
}
/**
 * Internal type for understanding the shape of a GraphQL query response.
 */
class GraphQLQueryResponse {
    constructor(data, errors) { }
}
/**
 * The object you're looking for could not be found.
 */
export class NotFound {
}
/**
 * A map layer style.
 */
export class Style {
    constructor(GRAPHQL_SINGLE_MODEL_NAME = "style", GRAPHQL_ALL_MODEL_NAMES = "allStyles", 
    // stroke options
    drawStroke, strokeColor, strokeWeight, strokeOpacty, strokeLineJoin, strokeDashArray, strokeDashOffset, 
    // fill options
    drawFill, fillColor, fillOpacity) {
        this.GRAPHQL_SINGLE_MODEL_NAME = GRAPHQL_SINGLE_MODEL_NAME;
        this.GRAPHQL_ALL_MODEL_NAMES = GRAPHQL_ALL_MODEL_NAMES;
        this.drawStroke = drawStroke;
        this.strokeColor = strokeColor;
        this.strokeWeight = strokeWeight;
        this.strokeOpacty = strokeOpacty;
        this.strokeLineJoin = strokeLineJoin;
        this.strokeDashArray = strokeDashArray;
        this.strokeDashOffset = strokeDashOffset;
        this.drawFill = drawFill;
        this.fillColor = fillColor;
        this.fillOpacity = fillOpacity;
    }
}
export function modelFromData(ModelClass, data) {
    // Create an uninitialized object
    const instance = Object.create(ModelClass.prototype);
    // Assign matching keys from `data` to the new instance
    const fields = Object.keys(data);
    for (const field of fields) {
        instance[field] = data[field];
    }
    return instance;
}
// /**
//  * 
//  * @param modelType the type of GraphQL model to get by ID.
//  * @param modelId the ID of the model to get.
//  * @returns 
//  */
// async function getById<T extends GraphQLModel>(modelType: T, modelId: string): Promise<T | NotFound | GraphQLQueryFailed> {
//     function buildQueryString(): string {
//         const fields = Object.keys(modelType)
//             .filter((key) => key !== "GRAPHQL_SINGLE_MODEL_NAME" && key !== "GRAPHQL_ALL_MODEL_NAMES")
//             .join("\n");
//         const query = `
//             query ($id: UUID!) {
//                 $modelName(id: $id) {
//                     $fieldss
//                 }
//             }
//         `;
//         return JSON.stringify({
//             query,
//             variables: {
//                 id: modelId,
//                 modelName: modelType.GRAPHQL_SINGLE_MODEL_NAME,
//                 fields: fields,
//             },
//         });
//     }
//     const queryString = buildQueryString();
//     console.log("Query string is: " + queryString);
//     const response = await fetch("/graphql/", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//             "Accept": "application/json",
//             // TODO Add CSRF token here
//         },
//         body: queryString,
//     });
//     const responseJson = await response.json();
//     if (200 !== response.status){
//         // HTTP status error
//         return new GraphQLQueryFailed(responseJson.errors);
//     }
//     const modelData: Object = responseJson?.data[modelType.GRAPHQL_SINGLE_MODEL_NAME];
//     if (modelData === null || modelData === undefined){
//         // no model data on query response
//         return NotFound
//     }
//     // if we have some model data, then try to construct the model object
// }
// /**
//  * Get "Style" data for a single object.
//  * @param styleModelId the Django "Style" model id to fetch.
//  * @returns Style data for the given object.
//  */
// export async function getStyleData(styleModelId: string): Promise<Style | StyleNotFound> {
//     const stylesOnLayerQuery = `
//         query ($id: UUID!) {
//             style(id: $id) {
//                 drawStroke
//                 strokeColor
//                 strokeWeight
//                 strokeOpacity
//                 strokeLineCap
//                 strokeLineJoin
//                 strokeDashArray
//                 strokeDashOffset
//                 drawFill
//                 fillColor
//                 fillOpacity
//             }
//         }
//     `;
//     const style = await queryGraphQL(
//         JSON.stringify({
//             query: stylesOnLayerQuery,
//             variables: {id: styleModelId},
//         }
//     ));
//     if (style?.data?.style === null || style?.data?.style === undefined){
//         return new StyleNotFound();
//     }
//     const styleData = style.data.style;
//     return new Style(
//         styleData.drawStroke,
//         styleData.strokeColor,
//         styleData.strokeWeight,
//         styleData.strokeOpacity,
//         styleData.strokeLineCap,
//         styleData.strokeLineJoin,
//         styleData.strokeDashOffset,
//         styleData.drawFill,
//         styleData.fillColor,
//         styleData.fillOpacity,
//     );
// }
