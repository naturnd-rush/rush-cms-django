import{g as h}from"./graphql.js";import{e as d}from"./utils.js";function w(t){let r=0,n=0;for(let i of t)r+=i.x,n+=i.y;return{x:r/=t.length,y:n/=t.length}}function v(t){let r="";for(let n of t)r+=n.x+","+n.y+" ";return r}function N(t){const l=[{x:20,y:20},{x:100,y:40},{x:140,y:80},{x:60,y:120},{x:20,y:80}];let a=`
    <svg 
        width="200px"
        height="150px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${v(l)}"
    `;t.drawStroke&&(a+=`
            stroke="${t.strokeOptions.color}"
            stroke-width="${t.strokeOptions.weight}"
            stroke-opacity="${t.strokeOptions.opacity}"
            stroke-linecap="${t.strokeOptions.lineCap}"
            stroke-linejoin="${t.strokeOptions.lineJoin}"
            stroke-dasharray="${t.strokeOptions.dashArray}"
            stroke-dashoffset="${t.strokeOptions.dashOffset}"
        `),t.drawFill?a+=`
            fill="${t.fillOptions.color}"
            fill-opacity="${t.fillOptions.opacity}"
        `:a+='fill="none"',a+="/>";const e=w(l);return t.drawMarker&&(a+=`
        <circle 
            id="marker-centroid"
            r="16px"
            fill=${t.markerOptions.bgColor}
            opacity=${t.markerOptions.opacity}
            cx=${e.x}
            cy=${e.y}
        />
        `),a+="</svg>",t.drawMarker&&t.markerOptions.data!==null&&(a+=`
        <img 
            id="marker-image"
            src="${t.markerOptions.data}"
            width="26"
            height="26"
            style='
                position: absolute;
                left: ${e.x-26/2}px;
                top: ${e.y-26/2}px;
                opacity: ${t.markerOptions.opacity}
            '
        />'
        `),a}function u(t){let r=t.parentElement;for(;r!==null&&!r.classList.contains("form-row");)r=r.parentElement;return r}function p(t,r,n){var o;(o=u(r))==null||o.style.setProperty("background-color","#FFFFFF");for(let l of y(t,n)){const a=u(l);a!==null&&(a.style.display="none")}}function m(t,r,n){var o;(o=u(r))==null||o.style.setProperty("background-color","#E2DBC4");for(let l of y(t,n)){const a=u(l);a!==null&&(a.style.display="block")}}function y(t,r){let n=[];for(let i of r)i.groupName===t&&i.el!==null&&n.push(i.el);return n}function f(t){return new Promise((r,n)=>{const i=new FileReader;i.onload=()=>r(i.result),i.onerror=()=>n(i.error),i.readAsDataURL(t)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var a;const t=document.querySelector("form");t&&t.addEventListener("submit",function(){console.log("Form is being submitted!")});const r=d("style_preview"),n=d("injected-style-id").innerHTML,i=d("injected-media-url").innerHTML;let o={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",opacity:1,data:null}};const l=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?m("Stroke",e,l):p("Stroke",e,l),o.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?m("Fill",e,l):p("Fill",e,l),o.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?m("Marker",e,l):p("Marker",e,l),o.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>o.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>o.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>o.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>o.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>o.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>o.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>o.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>o.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>o.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_icon"),update:async e=>{let s=null;if(console.log(e.files),e.files&&(s=e.files[0]),s){const c=await f(s);o.markerOptions.data=c}else if(console.log("Getting old marker icon data from injected style id: ",n),n!==""){const c=await h(n);if(c!==null){const k=i+c.markerIcon,g=await fetch(k);console.log(g,k);const O=await g.blob(),_=await f(O);o.markerOptions.data=_}}else o.markerOptions.data=null},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>o.markerOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>o.markerOptions.bgColor=e.value,eventName:"input"}];for(let e of l){const s=async()=>{e.el!==null&&(await e.update(e.el),r.innerHTML=N(o))};(a=e==null?void 0:e.el)==null||a.addEventListener(e.eventName,s),await s()}})()});
