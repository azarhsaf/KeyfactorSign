import { useEffect, useState } from 'react'; import { Link } from 'react-router-dom';
import { api } from '../api/client'; import DocumentTable from '../components/DocumentTable';
export default function PendingSignaturesPage(){const [rows,setRows]=useState<any[]>([]); const [err,setErr]=useState('');
  const load=()=>api.get('/documents/pending').then(r=>setRows(r.data)).catch(e=>setErr(e?.response?.data?.detail||'Failed'));
  useEffect(()=>{load()},[])
  const sign=async(wid:number)=>{try{await api.post(`/workflows/${wid}/sign`);load()}catch(e:any){alert(e?.response?.data?.detail||'Sign failed')}}
  const reject=async(wid:number)=>{const reason=prompt('Reject reason')||''; if(!reason)return; try{const d=new FormData(); d.append('reason',reason); await api.post(`/workflows/${wid}/reject`,d);load()}catch(e:any){alert(e?.response?.data?.detail||'Reject failed')}}
  return <div className='space-y-4'><h2 className='text-2xl font-semibold'>Pending Signatures</h2>{err&&<div className='text-rose-600'>{err}</div>}<DocumentTable rows={rows} actions={(r)=><div className='flex gap-2'><Link to={`/document-preview/${r.id}`} className='text-blue-600'>View</Link><button onClick={()=>sign(r.workflow_id)} className='text-emerald-600'>Sign</button><button onClick={()=>reject(r.workflow_id)} className='text-rose-600'>Reject</button></div>}/></div>
}
