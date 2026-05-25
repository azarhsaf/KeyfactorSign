
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { api } from '../api/client';
import PdfViewer from '../components/PdfViewer';

export default function DocumentPreviewPage(){
  const {id}=useParams();
  const [search] = useSearchParams();
  const action = search.get('action');
  const nav=useNavigate();
  const [pdfUrl,setPdfUrl]=useState('');
  const [doc,setDoc]=useState<any>(null);
  const [wfId,setWfId]=useState<number|null>(null);
  const [placements,setPlacements]=useState<any[]>([]);
  const [audit,setAudit]=useState<any[]>([]);
  const [msg,setMsg]=useState('');
  const [err,setErr]=useState('');
  const [showConfirm,setShowConfirm]=useState(false);
  const [rejectReason,setRejectReason]=useState('');
  const [mode,setMode]=useState<'current'|'original'|'signed'>('current');
  const [selectedBox,setSelectedBox]=useState<number|null>(null);

  const previewEndpoint = useMemo(()=>{
    if(!id) return '';
    if(mode==='original') return `/documents/${id}/preview-original`;
    if(mode==='signed') return `/documents/${id}/preview-signed`;
    return `/documents/${id}/preview`;
  },[id,mode]);

  const load = async()=>{
    try{
      const [d, p, a] = await Promise.all([
        api.get(`/documents/${id}`),
        api.get(`/documents/${id}/signature-placement`).catch(()=>({data:[]})),
        api.get(`/audit/${id}`).catch(()=>({data:[]})),
      ]);
      setDoc(d.data); setPlacements(p.data); setAudit(a.data);
      const pending = await api.get('/documents/pending').catch(()=>({data:[]}));
      const mine = pending.data.find((x:any)=>String(x.id)===String(id));
      setWfId(mine?.workflow_id||null);
      const r = await api.get(previewEndpoint, {responseType:'blob'});
      const u = URL.createObjectURL(r.data); setPdfUrl(u);
      setErr('');
    }catch(e:any){
      if(e?.response?.status===401){ localStorage.removeItem('token'); nav('/login'); return; }
      setErr(e?.response?.data?.detail||'Preview failed');
    }
  }

  useEffect(()=>{load(); return ()=>{ if(pdfUrl) URL.revokeObjectURL(pdfUrl); }},[id,mode]);

  const sign = async()=>{
    if(!wfId){ setErr('No pending workflow action for this user/document.'); return; }
    if(placements.length && selectedBox===null){ setErr('Select your signature box before signing.'); return; }
    setErr('');
    try{
      await api.post(`/workflows/${wfId}/sign`);
      setMsg('Document signed successfully. Workflow updated.');
      setShowConfirm(false);
      await load();
    }catch(e:any){ setErr(e?.response?.data?.detail||'Sign failed'); }
  }

  const reject = async()=>{
    if(!wfId){ setErr('No pending workflow action for this user/document.'); return; }
    if(!rejectReason){ setErr('Please provide rejection reason.'); return; }
    const d=new FormData(); d.append('reason',rejectReason);
    try{ await api.post(`/workflows/${wfId}/reject`,d); setMsg('Document rejected.'); setRejectReason(''); await load(); }
    catch(e:any){ setErr(e?.response?.data?.detail||'Reject failed'); }
  }

  return <div className='space-y-4'>
    <div className='flex justify-between items-center'>
      <div>
        <h2 className='text-2xl font-semibold'>Signing Workspace</h2>
        <p className='text-sm text-slate-600'>{doc?.document_name||'Document'} • Status: {doc?.status||'-'} • Current signer: {doc?.current_signer||'-'}</p>
      </div>
      <div className='flex gap-2'>
        <button className='px-3 py-2 border rounded' onClick={()=>setMode('current')}>Current</button>
        <button className='px-3 py-2 border rounded' onClick={()=>setMode('original')}>Original</button>
        <button className='px-3 py-2 border rounded' onClick={()=>setMode('signed')}>Signed</button>
      </div>
    </div>

    {msg && <div className='bg-emerald-50 text-emerald-700 border border-emerald-200 rounded p-3'>{msg}</div>}
    {err && <div className='bg-rose-50 text-rose-700 border border-rose-200 rounded p-3'>{err}</div>}

    <div className='grid grid-cols-1 lg:grid-cols-4 gap-4'>
      <div className='lg:col-span-3'>
        {pdfUrl ? <PdfViewer url={pdfUrl}/> : <div className='bg-white border rounded p-4'>Loading preview...</div>}
        {placements.length>0 && <div className='mt-3 bg-white border rounded p-3'>
          <p className='font-medium mb-2'>Signature Fields</p>
          <div className='grid md:grid-cols-2 gap-2'>{placements.map((p:any)=><button key={p.id} onClick={()=>setSelectedBox(p.id)} className={`text-left border rounded p-2 ${selectedBox===p.id?'border-blue-600 bg-blue-50':'border-slate-200'}`}>Field #{p.id} • Page {p.page_number} • ({Math.round(p.x)},{Math.round(p.y)}) {p.width}x{p.height}</button>)}</div>
        </div>}
      </div>

      <div className='space-y-3'>
        <div className='bg-white border rounded p-3'>
          <h3 className='font-semibold mb-2'>Workflow Panel</h3>
          <div className='text-sm space-y-1'>
            <div>Action mode: {action||'view'}</div>
            <div>Pending workflow id: {wfId||'-'}</div>
            <div>Placement required: {placements.length>0?'Yes':'No'}</div>
          </div>
          <div className='mt-3 flex flex-col gap-2'>
            <button className='bg-slate-900 text-white rounded px-3 py-2' onClick={()=>setShowConfirm(true)}>Sign</button>
            <input className='border rounded p-2 text-sm' value={rejectReason} onChange={e=>setRejectReason(e.target.value)} placeholder='Reject reason'/>
            <button className='bg-rose-600 text-white rounded px-3 py-2' onClick={reject}>Reject</button>
            <button className='border rounded px-3 py-2' onClick={()=>window.open(`/api/documents/${id}/download-original`,'_blank')}>Download Original</button>
            <button className='border rounded px-3 py-2' onClick={()=>window.open(`/api/documents/${id}/download-signed`,'_blank')}>Download Signed</button>
          </div>
        </div>
        <div className='bg-white border rounded p-3'>
          <h3 className='font-semibold mb-2'>Audit Timeline</h3>
          <div className='space-y-2 max-h-72 overflow-auto'>{audit.map((a:any)=><div key={a.id} className='text-xs border-l-2 border-slate-300 pl-2'><div className='font-medium'>{a.action} {a.status?`(${a.status})`:''}</div><div>{a.created_at?.slice(0,19).replace('T',' ')}</div><div className='break-words text-slate-600'>{a.details||'-'}</div></div>)}</div>
        </div>
      </div>
    </div>

    {showConfirm && <div className='fixed inset-0 bg-black/30 flex items-center justify-center'>
      <div className='bg-white rounded-xl p-5 w-full max-w-md'>
        <h3 className='text-lg font-semibold mb-2'>Confirm Signing</h3>
        <p className='text-sm text-slate-600 mb-3'>You are about to sign this document. Ensure selected signature box and details are correct.</p>
        <div className='flex justify-end gap-2'>
          <button className='border rounded px-3 py-2' onClick={()=>setShowConfirm(false)}>Cancel</button>
          <button className='bg-slate-900 text-white rounded px-3 py-2' onClick={sign}>Sign Document</button>
        </div>
      </div>
    </div>}
  </div>
}
