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

export const StyleSchema = z.object({

    id: z.string(),
    // TODO: Change opacity and weight to njumnbers and parse numbers correctly before safe-parsing.
    // NOTE: THERE may be some thing I can use native to Zod that will do this during parsing...

    // stroke options
    drawStroke: z.boolean(),
    strokeColor: z.string(),
    strokeWeight: z.string(),
    strokeOpacity: z.string(),
    strokeLineJoin: z.string(),
    strokeDashArray: z.string().nullable(),
    strokeDashOffset: z.string().nullable(),
    
    // fill options
    drawFill: z.boolean(),
    fillColor: z.string(),
    fillOpacity: z.string(),

}).describe(JSON.stringify({
    getByIdName: "style",
    getAllName: "allStyles",
}));
export type Style = z.infer<typeof StyleSchema>;
