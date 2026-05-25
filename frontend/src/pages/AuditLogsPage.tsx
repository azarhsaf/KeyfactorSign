
import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';

export default function AuditLogsPage(){
  const [rows,setRows]=useState<any[]>([]);
  const [action,setAction]=useState('');
  const [user,setUser]=useState('');
  const [status,setStatus]=useState('');
  const [q,setQ]=useState('');
  const [openId,setOpenId]=useState<number|null>(null);

  useEffect(()=>{api.get('/audit').then(r=>setRows(r.data))},[])

  const filtered = useMemo(()=>rows.filter((r:any)=>
    (!action || String(r.action||'').toLowerCase().includes(action.toLowerCase())) &&
    (!user || String(r.user_id||'').includes(user)) &&
    (!status || String(r.status||'').toLowerCase().includes(status.toLowerCase())) &&
    (!q || JSON.stringify(r).toLowerCase().includes(q.toLowerCase()))
  ),[rows,action,user,status,q])

  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>Audit Logs</h2>
    <div className='bg-white border rounded p-3 grid md:grid-cols-4 gap-2'>
      <input className='border rounded p-2' placeholder='Filter by action' value={action} onChange={e=>setAction(e.target.value)} />
      <input className='border rounded p-2' placeholder='Filter by user id' value={user} onChange={e=>setUser(e.target.value)} />
      <input className='border rounded p-2' placeholder='Filter by status' value={status} onChange={e=>setStatus(e.target.value)} />
      <input className='border rounded p-2' placeholder='Search details' value={q} onChange={e=>setQ(e.target.value)} />
    </div>
    <div className='bg-white rounded border overflow-x-auto'>
      <table className='w-full text-sm'>
        <thead className='bg-slate-50'><tr><th className='p-2 text-left'>Time</th><th>User</th><th>Action</th><th>Document</th><th>IP</th><th>Status</th><th>Details</th></tr></thead>
        <tbody>{filtered.map((r:any)=><>
          <tr key={r.id} className='border-t align-top cursor-pointer' onClick={()=>setOpenId(openId===r.id?null:r.id)}>
            <td className='p-2 whitespace-nowrap'>{r.created_at?.slice(0,19).replace('T',' ')}</td><td>{r.user_id||'-'}</td><td>{r.action}</td><td>{r.document_id||'-'}</td><td>{r.ip_address||'-'}</td><td>{r.status||'info'}</td><td className='max-w-[280px] break-words'>{(r.details||'-').slice(0,90)}{(r.details||'').length>90?'…':''}</td>
          </tr>
          {openId===r.id && <tr className='bg-slate-50'><td></td><td colSpan={6} className='p-3 text-xs break-words whitespace-pre-wrap'>{r.details||'-'}</td></tr>}
        </>)}</tbody>
      </table>
    </div>
  </div>
}
