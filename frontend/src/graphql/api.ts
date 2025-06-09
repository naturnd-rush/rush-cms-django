import { SchemaMetadataSchema, type SchemaMetadata } from "./schema.js";
import { type ZodTypeAny, z, ZodObject } from 'zod';

/**
 * Something went wrong while making a request to GraphQL.
 */
export class GraphQLRequestFailed extends Error {
    constructor(message: string){
      super(message);
    }
}

/**
 * This class builds GraphQL query-strings for a given GraphQL model type (defined in schema.ts).
 * The model types and their fields should ALWAYS be a subset of the actual fields available for
 * retrieval in the GraphQL API (see rush/graphql.py for more information).
 */
export class QueryBuilder<Schema extends ZodTypeAny> {

    private schema: Schema;
    private metadata: SchemaMetadata;
    constructor(schema: Schema){
        this.schema = schema;
        this.metadata = this.getSchemaMetadata(schema);
    }

    /**
     * Get schema metadata (contains information about how to build queries for GraphQL.)
     * @param schema The schema instance to get metadata from.
     */
    protected getSchemaMetadata(schema: Schema): SchemaMetadata{
        const rawData = JSON.parse(schema.description ?? '{}');
        const result = SchemaMetadataSchema.safeParse(rawData);
        if (!result.success) {
            throw new Error("Invalid schema metadata: " + JSON.stringify(result.error));
        }
        return result.data; 
    }

    protected getSchemaShape(): any{
        // Because of weird type-inference stuff, ZodTypeAny must be used as the extension for 
        // the generic type, which means we don't know if the model instance has a shape property.
        // This is a hack. If you work on fixing this please increment the counter below:
        // num_hours_wasted = 3
        if (this.schema instanceof ZodObject) {
            return this.schema.shape;
        }
        throw new Error("Schema should always be an instance of a ZodObject, but instead is: " + typeof this.schema + "!");
    }

    protected buildGetById(modelId: string): string{
        const fieldNames = Object.keys(this.getSchemaShape()).join("\n");
        const modelName = this.metadata.getByIdName;
        const query = `
            query ($id: UUID!) {
                ${modelName}(id: $id) {
                    ${fieldNames}
                }
            }
        `;
        return JSON.stringify({
            query,
            variables: {
                id: modelId
            }
        });
    }

    protected buildGetAll(): string{
        const fieldNames = Object.keys(this.getSchemaShape()).join("\n");
        const modelName = this.metadata.getAllName;
        const query = `
            query {
                ${modelName} {
                    ${fieldNames}
                }
            }
        `;
        return JSON.stringify({query, variables: {}});
    }

    protected async executeQuery(queryString: string): Promise<any> {
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

    public async getById(id: string): Promise<z.infer<Schema> | null> {
        const queryString = this.buildGetById(id);
        const responseJson = await this.executeQuery(queryString);
        const modelData = responseJson?.data[this.metadata.getByIdName];
        if (modelData === null || modelData === undefined){
            // no model data on query response
            return null;
        }
        const result = this.schema.safeParse(modelData);
        if (!result.success){
            throw new GraphQLRequestFailed("Failed to parse: " + result.error);
        }
        return result.data;
    }

    public async getAll(): Promise<Array<z.infer<Schema>>>{
        const queryString = this.buildGetAll();
        const responseJson = await this.executeQuery(queryString);
        const modelDataList = responseJson?.data[this.metadata.getAllName];
        if (modelDataList === null || modelDataList === undefined){
            throw new GraphQLRequestFailed("Failed to access " + this.metadata.getAllName + " on " + responseJson + ".");
        }
        if (!(modelDataList instanceof Array)){
            throw new GraphQLRequestFailed("Expected getAll query to return an Array, instead returned: " + modelDataList + ".");
        }
        let parsedModels: Array<z.infer<Schema>> = [];
        for (let modelData of modelDataList){
            const result = this.schema.safeParse(modelData);
            if (!result.success){
                throw new GraphQLRequestFailed("Failed to parse: " + result.error);
            }
            parsedModels.push(result.data);
        }
        return parsedModels;
    }
}
