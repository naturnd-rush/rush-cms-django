import { z } from "zod"

/**
 * Typescript Schema for GraphQL models.
 * 
 * This module uses "Zod" to provide runtime type validation over input data (returned by GraphQL)
 * so we can be sure the data passing through our system at runtime conforms to TypeScript's type annotations.
 * See their docs: https://zod.dev/.
 */


export const StyleSchema = z.object({

    // stroke options
    drawStroke: z.boolean(),
    strokeColor: z.string(),
    strokeWeight: z.number(),
    strokeOpacty: z.number(),
    strokeLineJoin: z.string(),
    strokeDashArray: z.string(),
    strokeDashOffset: z.string(),
    
    // fill options
    drawFill: z.boolean(),
    fillColor: z.string(),
    fillOpacity: z.number(),

}); export type Style = z.infer<typeof StyleSchema>;
