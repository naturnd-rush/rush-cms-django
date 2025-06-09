import { z, ZodObject } from "zod"

/**
 * Typescript Schema for GraphQL models.
 * 
 * This module uses "Zod" to provide runtime type validation over input data (returned by GraphQL)
 * so we can be sure the data passing through our system at runtime conforms to TypeScript's type annotations.
 * See their docs: https://zod.dev/.
 */

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
