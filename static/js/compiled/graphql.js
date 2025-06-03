/**
 * This module provides a way to interface with the GraphQL API.
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
/**
 * Something went wrong while trying to access the GraphQL API.
 */
export class GraphQLError extends Error {
    constructor(status, responseBody) {
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
export function queryGraphQL(query) {
    return __awaiter(this, void 0, void 0, function* () {
        const response = yield fetch("/graphql/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                // TODO Add CSRF token here
            },
            body: query,
        });
        if (200 === response.status) {
            return response.json();
        }
        const errorText = yield response.text();
        throw new GraphQLError(response.status, errorText);
    });
}
