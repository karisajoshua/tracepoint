import {useEffect,useRef,useState} from 'react';
/**
 * Geographic world basemap from OpenStreetMap raster tiles, rendered by Leaflet.
 * Preview markers are synthetic. Live mode never fabricates locations.
 * Attribution is shown on-map as required by OpenStreetMap.
 */
type LeafletMap={setView:(coords:[number,number],zoom:number)=>LeafletMap;remove:()=>void;invalidateSize:()=>void};
type LeafletAPI={map:(el:HTMLElement,opts:Record<string,unknown>)=>LeafletMap;tileLayer:(url:string,opts:Record<string,unknown>)=>{addTo:(map:LeafletMap)=>unknown};circleMarker:(latlng:[number,number],opts:Record<string,unknown>)=>{addTo:(map:LeafletMap)=>{bindPopup:(html:string)=>unknown}}};
declare global{interface Window{L?:LeafletAPI}}
const leafletJs='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
const leafletCss='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
let loading:Promise<LeafletAPI>|undefined;
function loadLeaflet():Promise<LeafletAPI>{
 if(window.L)return Promise.resolve(window.L);
 if(loading)return loading;
 loading=new Promise((resolve,reject)=>{
 if(!document.querySelector('link[data-tracepoint-leaflet]')){const css=document.createElement('link');css.rel='stylesheet';css.href=leafletCss;css.dataset.tracepointLeaflet='1';document.head.appendChild(css);}
 const script=document.createElement('script');script.src=leafletJs;script.async=true;script.onload=()=>window.L?resolve(window.L):reject(new Error('Map library unavailable'));script.onerror=()=>reject(new Error('Could not load map library'));document.head.appendChild(script);
 }).catch(e=>{loading=undefined;throw e;});
 return loading;
}
const samples:[number,number,string][]=[[40.71,-74.01,'New York'],[51.51,-0.13,'London'],[-1.29,36.82,'Nairobi'],[1.35,103.82,'Singapore'],[35.68,139.69,'Tokyo'],[-33.87,151.21,'Sydney']];
export default function WorldMap({demo}:{demo:boolean}){
 const holder=useRef<HTMLDivElement>(null);const mapRef=useRef<LeafletMap|null>(null);
 const [error,setError]=useState('');
 useEffect(()=>{let cancelled=false;loadLeaflet().then(L=>{
 if(cancelled||!holder.current)return;
 const map=L.map(holder.current,{zoomControl:true,scrollWheelZoom:false,worldCopyJump:true,attributionControl:true}).setView([18,8],2);
 mapRef.current=map;
 L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,minZoom:1,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>'}).addTo(map);
 if(demo)samples.forEach(([lat,lon,city])=>{L.circleMarker([lat,lon],{radius:5,color:'#f8b778',fillColor:'#f16662',fillOpacity:.85,weight:2}).addTo(map).bindPopup('Synthetic example: '+city);});
 requestAnimationFrame(()=>map.invalidateSize());
 }).catch(e=>{if(!cancelled)setError(e instanceof Error?e.message:'Map unavailable');});
 return()=>{cancelled=true;mapRef.current?.remove();mapRef.current=null;};
 },[demo]);
 return <div className="world-map real-world-map" aria-label={demo?'Interactive OpenStreetMap world map with synthetic example locations':'Interactive OpenStreetMap world map; no geolocated threat data'}>
 <div className="leaflet-holder" ref={holder}/>
 {error&&<div className="map-error" role="status">{error}. Check network access.</div>}
 <div className="map-status">{demo?'● SAMPLE MARKERS — NOT LIVE THREATS':'○ NO GEOLOCATED EVENTS AVAILABLE'}</div>
 </div>;
}
