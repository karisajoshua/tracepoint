import {useState} from 'react';
import {AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer} from 'recharts';
type Summary={total_events:number;total_alerts:number;events_by_type:Record<string,number>;alerts_by_severity:Record<string,number>};
type Bucket={time:string;events:number};
type Alert={id:number;severity:string;event_type:string;source:string;reason:string};
type Event={event_id:string;event_type:string;source:string;timestamp:string};
async function get<T>(path:string,key:string):Promise<T>{const r=await fetch(path,{headers:{'X-API-Key':key}});if(!r.ok)throw new Error('Request failed: '+r.status);return r.json();}
export default function App(){
 const [key,setKey]=useState('');const [summary,setSummary]=useState<Summary|null>(null);
 const [buckets,setBuckets]=useState<Bucket[]>([]);const [alerts,setAlerts]=useState<Alert[]>([]);
 const [events,setEvents]=useState<Event[]>([]);const [error,setError]=useState('');
 const [hours,setHours]=useState(24);const [loading,setLoading]=useState(false);
 async function refresh(period=hours){if(!key)return;setLoading(true);setError('');
 try{const [s,b,a,e]=await Promise.all([get<Summary>('/api/v1/summary',key),get<{buckets:Bucket[]}>('/api/v1/activity?hours='+period,key),get<{items:Alert[]}>('/api/v1/alerts',key),get<{items:Event[]}>('/api/v1/events',key)]);
 setSummary(s);setBuckets(b.buckets);setAlerts(a.items);setEvents(e.items);}
 catch(e){setError(e instanceof Error?e.message:'Unable to load');}finally{setLoading(false);}}
 return <div className="layout"><aside><div className="logo">◈ TRACEPOINT</div><div className="subtitle">SECURITY OPERATIONS</div><nav><a href="#overview">Overview</a><a href="#alerts">Threat Alerts</a><a href="#events">Security Events</a></nav><div className="foot">Every event tells a story.</div></aside>
 <main id="overview"><header><div><div className="eyebrow">SECURITY MONITORING & THREAT ANALYSIS</div><h1>Security Overview</h1><p>Live event activity and threat detection</p></div><button onClick={()=>void refresh()} disabled={loading||!key}>{loading?'Loading…':'↻ Refresh'}</button></header>
 <section className="connect"><label htmlFor="key">Development API key</label><input id="key" type="password" autoComplete="off" value={key} onChange={e=>setKey(e.target.value)} placeholder="Enter API key"/><button disabled={!key||loading} onClick={()=>void refresh()}>Connect</button></section>
 {error&&<div className="error" role="alert">{error}</div>}
 <section className="metrics"><article><span>Total Events</span><strong>{summary?.total_events??'—'}</strong><small>Received security events</small></article><article><span>Detected Alerts</span><strong>{summary?.total_alerts??'—'}</strong><small>Rule-generated findings</small></article><article><span>High Severity</span><strong>{summary?.alerts_by_severity.high??'—'}</strong><small>Priority investigations</small></article><article><span>Event Categories</span><strong>{summary?Object.keys(summary.events_by_type).length:'—'}</strong><small>Unique event types</small></article></section>
 <section className="panel"><div className="heading"><div><h2>Event Activity</h2><p>Security events grouped by hour</p></div><select value={hours} onChange={e=>{const n=Number(e.target.value);setHours(n);void refresh(n);}}><option value={6}>6 hours</option><option value={24}>24 hours</option><option value={168}>7 days</option></select></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={buckets}><XAxis dataKey="time" tickFormatter={v=>v.slice(11,16)} stroke="#7893a6"/><YAxis allowDecimals={false} stroke="#7893a6"/><Tooltip contentStyle={{background:'#17283a',border:'1px solid #365067'}}/><Area type="monotone" dataKey="events" stroke="#2bd3be" fill="#16695f" strokeWidth={3}/></AreaChart></ResponsiveContainer></div></section>
 <div className="columns"><section className="panel" id="alerts"><h2>Recent Alerts</h2><table><thead><tr><th>Severity</th><th>Detection</th><th>Source</th></tr></thead><tbody>{alerts.length?alerts.map(a=><tr key={a.id}><td className="danger">{a.severity}</td><td title={a.reason}>{a.event_type}</td><td>{a.source}</td></tr>):<tr><td colSpan={3}>No alerts yet</td></tr>}</tbody></table></section>
 <section className="panel" id="events"><h2>Recent Events</h2><table><thead><tr><th>Type</th><th>Source</th><th>Time</th></tr></thead><tbody>{events.length?events.map(e=><tr key={e.event_id}><td>{e.event_type}</td><td>{e.source}</td><td>{new Date(e.timestamp).toLocaleTimeString()}</td></tr>):<tr><td colSpan={3}>No events yet</td></tr>}</tbody></table></section></div>
 <footer>Tracepoint prototype • Synthetic events only • Not production ready</footer></main></div>;
}
