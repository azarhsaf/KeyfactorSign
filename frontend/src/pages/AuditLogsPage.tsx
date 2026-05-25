import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';

export default function AuditLogsPage(){
  const [rows,setRows]=useState<any[]>([]);
  const [action,setAction]=useState('');
  const [user,setUser]=useState('');
  const [q,setQ]=useState('');

  useEffect(()=>{api.get('/audit').then(r=>setRows(r.data))},[])

  const filtered = useMemo(()=>rows.filter((r:any)=>
    (!action || String(r.action||'').toLowerCase().includes(action.toLowerCase())) &&
    (!user || String(r.user_id||'').includes(user)) &&
    (!q || JSON.stringify(r).toLowerCase().includes(q.toLowerCase()))
  ),[rows,action,user,q])

  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>Audit Logs</h2>
    <div className='bg-white border rounded p-3 grid md:grid-cols-3 gap-2'>
      <input className='border rounded p-2' placeholder='Filter by action' value={action} onChange={e=>setAction(e.target.value)} />
      <input className='border rounded p-2' placeholder='Filter by user id' value={user} onChange={e=>setUser(e.target.value)} />
      <input className='border rounded p-2' placeholder='Search details' value={q} onChange={e=>setQ(e.target.value)} />
    </div>
    <div className='bg-white rounded border overflow-x-auto'>
      <table className='w-full text-sm'>
        <thead className='bg-slate-50'><tr><th className='p-2 text-left'>Time</th><th>Action</th><th>User</th><th>Document</th><th>IP</th><th>Result</th><th>Details</th></tr></thead>
        <tbody>{filtered.map((r:any)=><tr key={r.id} className='border-t align-top'><td className='p-2 whitespace-nowrap'>{r.created_at?.slice(0,19).replace('T',' ')}</td><td>{r.action}</td><td>{r.user_id||'-'}</td><td>{r.document_id||'-'}</td><td>{r.ip_address||'-'}</td><td>{String(r.action||'').includes('FAILED')?'Failed':'Success/Info'}</td><td className='max-w-[380px] break-words'>{r.details||'-'}</td></tr>)}</tbody>
      </table>
    </div>
  </div>
}
