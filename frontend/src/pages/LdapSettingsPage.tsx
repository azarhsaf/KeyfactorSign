import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function LdapSettingsPage(){
  const [cfg,setCfg]=useState<any>({}); const [test,setTest]=useState<any>(null); const [users,setUsers]=useState<any[]>([]); const [q,setQ]=useState(''); const [msg,setMsg]=useState(''); const [err,setErr]=useState('');
  useEffect(()=>{api.get('/admin/ldap/settings').then(r=>setCfg(r.data))},[])
  const save=async()=>{setErr(''); const d=new FormData(); Object.entries(cfg).forEach(([k,v])=>d.append(k,String(v??''))); await api.post('/admin/ldap/settings',d); setMsg('Saved')}
  const search=async()=>{setErr(''); try{setUsers((await api.get('/admin/ldap/search-users',{params:{query:q}})).data)}catch(e:any){setErr(e?.response?.data?.detail||'LDAP search failed')}}
  const testLogin=async()=>{const u=prompt('LDAP username'); const p=prompt('LDAP password'); if(!u||!p) return; const d=new FormData(); d.append('username',u); d.append('password',p); setTest((await api.post('/admin/ldap/test-login',d)).data)}
  const sync=async(u:any)=>{const d=new FormData(); d.append('username',u.username); d.append('role','signer'); await api.post('/admin/ldap/sync-user',d); alert('Synced')}
  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>Users & Directory — LDAP</h2>
    <div className='bg-white shadow-sm border rounded-xl p-4 grid md:grid-cols-2 gap-2'>
      {Object.keys(cfg).map(k=><input key={k} className='border p-2 rounded-lg focus:ring-2 focus:ring-blue-400' value={String(cfg[k]??'')} onChange={e=>setCfg({...cfg,[k]:e.target.value})} placeholder={k}/>) }
      <div className='flex gap-2 md:col-span-2'>
        <button onClick={save} className='bg-slate-900 text-white px-3 py-2 rounded-lg'>Save</button>
        <button onClick={async()=>setTest((await api.get('/admin/ldap/test')).data)} className='bg-blue-700 text-white px-3 py-2 rounded-lg'>Test Connection</button>
        <button onClick={testLogin} className='bg-indigo-700 text-white px-3 py-2 rounded-lg'>Test Login</button>
      </div>
      {msg&&<div className='text-emerald-600 md:col-span-2'>{msg}</div>}
      {err&&<div className='text-rose-600 md:col-span-2'>{err}</div>}
      {test&&<pre className='bg-slate-50 p-2 md:col-span-2 rounded'>{JSON.stringify(test,null,2)}</pre>}
    </div>

    <div className='bg-white shadow-sm border rounded-xl p-4'>
      <div className='flex gap-2 mb-3'>
        <input className='border p-2 rounded-lg flex-1' value={q} onChange={e=>setQ(e.target.value)} placeholder='Search LDAP users (username/display/email)'/>
        <button onClick={search} className='bg-slate-900 text-white px-4 py-2 rounded-lg'>Search</button>
      </div>
      {users.length===0 ? <div className='text-slate-500 py-6 text-center'>No LDAP users found</div> :
      <div className='overflow-x-auto'><table className='w-full text-sm'><thead className='bg-slate-50'><tr><th className='p-2 text-left'>Username</th><th>Display Name</th><th>Email</th><th>Distinguished Name</th><th>Groups</th><th>Action</th></tr></thead><tbody>{users.map((u:any)=><tr key={u.username+u.distinguished_name} className='border-t align-top'><td className='p-2'>{u.username}</td><td>{u.display_name}</td><td>{u.email||'-'}</td><td className='max-w-[280px] break-words'>{u.distinguished_name}</td><td className='max-w-[220px] break-words'>{(u.groups||[]).join(', ')||'-'}</td><td><button onClick={()=>sync(u)} className='text-blue-700 font-medium'>Import/Sync</button></td></tr>)}</tbody></table></div>}
    </div>
  </div>
}
