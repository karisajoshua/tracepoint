import Map3D from './Map3D';
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
 const [mode,setMode]=useState<'2d'|'3d'>('2d');
 const holder=useRef<HTMLDivElement>(null);const mapRef=useRef<LeafletMap|null>(null);
 const [error,setError]=useState('');
 const [place,setPlace]=useState('');
 const [matches,setMatches]=useState<{display_name:string;lat:string;lon:string;boundingbox:string[]}[]>([]);
 const [searching,setSearching]=useState(false);
 const [searchError,setSearchError]=useState('');
 const [zoomDetail,setZoomDetail]=useState('');
 async function findPlace(e:React.FormEvent<HTMLFormElement>){
 e.preventDefault();const q=place.trim();if(q.length<2)return;
 setSearching(true);setSearchError('');setMatches([]);
 try{
 const response=await fetch('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&addressdetails=0&q='+encodeURIComponent(q),{headers:{'Accept':'application/json'}});
 if(!response.ok)throw new Error('Place search is temporarily unavailable');
 const found=await response.json() as {display_name:string;lat:string;lon:string;boundingbox:string[]}[];
 setMatches(found);if(!found.length)setSearchError('No matching places found. Try a more specific name.');
 }catch(err){setSearchError(err instanceof Error?err.message:'Unable to search locations');}
 finally{setSearching(false);}
 }
 function goToPlace(p:{display_name:string;lat:string;lon:string;boundingbox:string[]}){
 const b=p.boundingbox.map(Number);
 if(b.length===4&&b.every(Number.isFinite)){mapRef.current?.fitBounds([[b[0],b[2]],[b[1],b[3]]],{padding:[24,24],maxZoom:17});}
 else mapRef.current?.flyTo([Number(p.lat),Number(p.lon)],14);
 setZoomDetail(p.display_name);setMatches([]);
 }
 useEffect(()=>{if(mode==='3d')return;let cancelled=false;loadLeaflet().then(L=>{
 if(cancelled||!holder.current)return;
 const map=L.map(holder.current,{zoomControl:true,scrollWheelZoom:false,worldCopyJump:true,attributionControl:true,maxZoom:19}).setView([18,8],2);
 mapRef.current=map;
 L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,minZoom:1,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'}).addTo(map);
 if(demo)samples.forEach(([lat,lon,city])=>{L.circleMarker([lat,lon],{radius:7,color:'#f8b778',fillColor:'#f16662',fillOpacity:.85,weight:2}).addTo(map).bindPopup('<strong>Sample location</strong><div>'+city+'</div><small>Demonstration only — not a detected attack</small>');});
 requestAnimationFrame(()=>map.invalidateSize());
 }).catch(e=>{if(!cancelled)setError(e instanceof Error?e.message:'Map unavailable');});
 return()=>{cancelled=true;mapRef.current?.remove();mapRef.current=null;};
 },[demo,mode]);
 return <div className="map-mode-wrapper"><div className="map-mode-switch" role="group" aria-label="Map dimension"><button className={mode==='2d'?'active':''} onClick={()=>setMode('2d')}>2D</button><button className={mode==='3d'?'active':''} onClick={()=>setMode('3d')}>3D</button></div>{mode==='3d'?<Map3D demo={demo}/>:<div className="world-map real-world-map" aria-label={demo?'Interactive OpenStreetMap world map with synthetic example locations':'Interactive OpenStreetMap world map; no geolocated threat data'}>
 <div className="leaflet-holder" ref={holder}/>
 <div className="map-search">
 <form onSubmit={findPlace}><input aria-label="Search country, city, street or address" placeholder="Search country, city, street…" value={place} onChange={e=>setPlace(e.target.value)} minLength={2}/><button type="submit" disabled={searching}>{searching?'…':'⌕ Search'}</button></form>
 {matches.length>0&&<div className="map-results" role="listbox" aria-label="Matching places">{matches.map((p,i)=><button type="button" key={i} onClick={()=>goToPlace(p)}>{p.display_name}</button>)}</div>}
 {searchError&&<div className="map-search-error" role="status">{searchError}</div>}
 </div>
 <div className="map-tools"><button type="button" onClick={()=>{mapRef.current?.setView([18,8],2);setZoomDetail('');setMatches([]);}}>World</button><button type="button" onClick={()=>{if(demo)mapRef.current?.fitBounds(samples.map(([a,b])=>[a,b]),{padding:[24,24]});}}>Fit markers</button></div>
 {zoomDetail&&<div className="map-selected" title={zoomDetail}>Viewing: {zoomDetail}</div>}
 {error&&<div className="map-error" role="status">{error}. Check network access.</div>}
 <div className="map-status">{demo?'● SAMPLE MARKERS — NOT LIVE THREATS':'○ NO GEOLOCATED EVENTS AVAILABLE'}</div>
 </div>}</div>;
}
