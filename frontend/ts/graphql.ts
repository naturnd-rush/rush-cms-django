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

/**
 * Query the GraphQL API.
 * @param query The GraphQL Query to execute.
 * @returns A JSON response Promise.
 * @throws GraphQLError when the request fails.
 */
export async function queryGraphQL(query: string): Promise<JSON> {
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
