import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function SmtpSettingsPage(){
  const [cfg,setCfg]=useState<any>({}); const [to,setTo]=useState(''); const [result,setResult]=useState<any>(null); const [msg,setMsg]=useState('');
  useEffect(()=>{api.get('/admin/smtp/settings').then(r=>setCfg(r.data))},[])
  const save=async()=>{const d=new FormData(); Object.entries(cfg).forEach(([k,v])=>d.append(k,String(v??''))); await api.post('/admin/smtp/settings',d); setMsg('Saved')}
  const test=async()=>setResult((await api.post('/admin/smtp/test')).data)
  const send=async()=>{const d=new FormData(); d.append('to_email',to); setResult((await api.post('/admin/smtp/send-test',d)).data)}
  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>SMTP / Email Relay</h2>
    <div className='bg-white border rounded p-4 space-y-2 text-sm'>
      <div className='grid md:grid-cols-2 gap-2'>{Object.keys(cfg).map(k=><input key={k} className='border rounded p-2' value={String(cfg[k]??'')} onChange={e=>setCfg({...cfg,[k]:e.target.value})} placeholder={k}/>)}</div>
      <div className='flex gap-2'>
        <button onClick={save} className='bg-slate-900 text-white px-3 py-2 rounded'>Save</button>
        <button onClick={test} className='bg-blue-700 text-white px-3 py-2 rounded'>Test Connection</button>
        <input className='border rounded p-2' placeholder='test email recipient' value={to} onChange={e=>setTo(e.target.value)}/>
        <button onClick={send} className='bg-indigo-700 text-white px-3 py-2 rounded'>Send Test Email</button>
      </div>
      {msg&&<div className='text-emerald-600'>{msg}</div>}
      {result&&<pre className='bg-slate-50 p-2'>{JSON.stringify(result,null,2)}</pre>}
    </div>
  </div>
}
