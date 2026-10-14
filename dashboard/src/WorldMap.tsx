import {useEffect,useRef,useState} from 'react';
/**
 * Geographic world basemap from OpenStreetMap raster tiles, rendered by Leaflet.
 * Preview markers are synthetic. Live mode never fabricates locations.
 * Attribution is shown on-map as required by OpenStreetMap.
 */
type LeafletMap={setView:(coords:[number,number],zoom:number)=>LeafletMap;remove:()=>void;invalidateSize:()=>void;flyTo:(coords:[number,number],zoom:number)=>void;fitBounds:(bounds:[number,number][],options?:Record<string,unknown>)=>void};
type LeafletAPI={map:(el:HTMLElement,opts:Record<string,unknown>)=>LeafletMap;tileLayer:(url:string,opts:Record<string,unknown>)=>{addTo:(map:LeafletMap)=>unknown};circleMarker:(latlng:[number,number],opts:Record<string,unknown>)=>{addTo:(map:LeafletMap)=>{bindPopup:(html:string)=>unknown}}};
declare global{interface Window{L?:LeafletAPI}}
const leafletJs='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
const leafletCss='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
let loading:Promise<LeafletAPI>|undefined;
function loadLeaflet():Promise<LeafletAPI>{
 if(window.L)return Promise.resolve(window.L);
 if(loading)return loading;
 loading=new Promise<LeafletAPI>((resolve,reject)=>{
 if(!document.querySelector('link[data-tracepoint-leaflet]')){const css=document.createElement('link');css.rel='stylesheet';css.href=leafletCss;css.dataset.tracepointLeaflet='1';document.head.appendChild(css);}
 const script=document.createElement('script');script.src=leafletJs;script.async=true;script.onload=()=>window.L?resolve(window.L):reject(new Error('Map library unavailable'));script.onerror=()=>reject(new Error('Could not load map library'));document.head.appendChild(script);
 }).catch(e=>{loading=undefined;throw e;});
 return loading!;
}
const samples:[number,number,string][]=[[40.71,-74.01,'New York'],[51.51,-0.13,'London'],[-1.29,36.82,'Nairobi'],[1.35,103.82,'Singapore'],[35.68,139.69,'Tokyo'],[-33.87,151.21,'Sydney']];
export default function WorldMap({demo}:{demo:boolean}){
 const holder=useRef<HTMLDivElement>(null);const mapRef=useRef<LeafletMap|null>(null);
 const [error,setError]=useState('');const [layer,setLayer]=useState<'street'|'terrain'>('street');
 useEffect(()=>{let cancelled=false;loadLeaflet().then(L=>{
 if(cancelled||!holder.current)return;
 const map=L.map(holder.current,{zoomControl:true,scrollWheelZoom:false,worldCopyJump:true,attributionControl:true}).setView([18,8],2);
 mapRef.current=map;
 L.tileLayer(layer==='street'?'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png':'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',{maxZoom:layer==='street'?18:17,minZoom:1,attribution:layer==='street'?'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>':'&copy; OpenStreetMap contributors, SRTM | <a href="https://opentopomap.org">OpenTopoMap</a>'}).addTo(map);
 if(demo)samples.forEach(([lat,lon,city])=>{L.circleMarker([lat,lon],{radius:7,color:'#f8b778',fillColor:'#f16662',fillOpacity:.85,weight:2}).addTo(map).bindPopup('<strong>Sample location</strong><div>'+city+'</div><small>Demonstration only — not a detected attack</small>');});
 requestAnimationFrame(()=>map.invalidateSize());
 }).catch(e=>{if(!cancelled)setError(e instanceof Error?e.message:'Map unavailable');});
 return()=>{cancelled=true;mapRef.current?.remove();mapRef.current=null;};
 },[demo,layer]);
 return <div className="world-map real-world-map" aria-label={demo?'Interactive OpenStreetMap world map with synthetic example locations':'Interactive OpenStreetMap world map; no geolocated threat data'}>
 <div className="leaflet-holder" ref={holder}/><div className="map-tools"><button type="button" onClick={()=>mapRef.current?.setView([18,8],2)}>World</button><button type="button" onClick={()=>{if(demo)mapRef.current?.fitBounds(samples.map(([a,b])=>[a,b]),{padding:[24,24]});}}>Fit markers</button><select aria-label="Map layer" value={layer} onChange={e=>setLayer(e.target.value as 'street'|'terrain')}><option value="street">Street map</option><option value="terrain">Terrain</option></select></div>
 {error&&<div className="map-error" role="status">{error}. Check network access.</div>}
 <div className="map-status">{demo?'● SAMPLE MARKERS — NOT LIVE THREATS':'○ NO GEOLOCATED EVENTS AVAILABLE'}</div>
 </div>;
}
