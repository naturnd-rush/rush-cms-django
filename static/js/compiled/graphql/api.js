var d=Object.defineProperty;var l=(r,e,a)=>e in r?d(r,e,{enumerable:!0,configurable:!0,writable:!0,value:a}):r[e]=a;var c=(r,e,a)=>l(r,typeof e!="symbol"?e+"":e,a);import{S as h,Z as u}from"./schema.js";class o extends Error{constructor(e){super(e)}}class f{constructor(e){c(this,"schema");c(this,"metadata");this.schema=e,this.metadata=this.getSchemaMetadata(e)}getSchemaMetadata(e){const a=JSON.parse(e.description??"{}"),t=h.safeParse(a);if(!t.success)throw new Error("Invalid schema metadata: "+JSON.stringify(t.error));return t.data}getSchemaShape(){if(this.schema instanceof u)return this.schema.shape;throw new Error("Schema should always be an instance of a ZodObject, but instead is: "+typeof this.schema+"!")}buildGetById(e){const a=Object.keys(this.getSchemaShape()).join(`
`),s=`
            query ($id: UUID!) {
                ${this.metadata.getByIdName}(id: $id) {
                    ${a}
                }
            }
        `;return JSON.stringify({query:s,variables:{id:e}})}buildGetAll(){const e=Object.keys(this.getSchemaShape()).join(`
`),t=`
            query {
                ${this.metadata.getAllName} {
                    ${e}
                }
            }
        `;return JSON.stringify({query:t,variables:{}})}async executeQuery(e){const a=await fetch("/graphql/",{method:"POST",headers:{"Content-Type":"application/json",Accept:"application/json"},body:e}),t=await a.json();if(a.status!==200)throw t.errors===null||t.errors===void 0?new o("GraphQL response code ("+a.status+") is not 200 but no errors were sent back in the response!"):new o(JSON.stringify(t.errors));return t}async getById(e){const a=this.buildGetById(e),t=await this.executeQuery(a),s=t==null?void 0:t.data[this.metadata.getByIdName];if(s==null)return null;const i=this.schema.safeParse(s);if(!i.success)throw new o("Failed to parse: "+i.error);return i.data}async getAll(){const e=this.buildGetAll(),a=await this.executeQuery(e),t=a==null?void 0:a.data[this.metadata.getAllName];if(t==null)throw new o("Failed to access "+this.metadata.getAllName+" on "+a+".");if(!(t instanceof Array))throw new o("Expected getAll query to return an Array, instead returned: "+t+".");let s=[];for(let i of t){const n=this.schema.safeParse(i);if(!n.success)throw new o("Failed to parse: "+n.error);s.push(n.data)}return s}}export{f as Q};
