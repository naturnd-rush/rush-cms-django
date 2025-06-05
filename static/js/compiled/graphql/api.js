import{S as r}from"./schema.js";function a(){const t=r.safeParse({drawStroke:!0});if(!t.success)throw new Error("Invalid style data: "+JSON.stringify(t.error));return t.data}export{a as t};
