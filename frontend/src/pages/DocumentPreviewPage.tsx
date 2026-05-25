import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import PdfViewer from '../components/PdfViewer';

export default function DocumentPreviewPage(){
  const {id}=useParams();
  const nav=useNavigate();
  const [pdfUrl,setPdfUrl]=useState('');
  const [err,setErr]=useState('');

  useEffect(()=>{
    const load = async()=>{
      try{
        const r = await api.get(`/documents/${id}/preview`, {responseType:'blob'});
        const url = URL.createObjectURL(r.data);
        setPdfUrl(url);
      }catch(e:any){
        if(e?.response?.status===401){ localStorage.removeItem('token'); nav('/login'); return; }
        setErr(e?.response?.data?.detail||'Preview failed');
      }
    };
    load();
    return ()=>{ if(pdfUrl) URL.revokeObjectURL(pdfUrl); }
  },[id]);

  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>Document Preview</h2>
    {err && <div className='text-rose-600'>{err}</div>}
    {pdfUrl ? <PdfViewer url={pdfUrl}/> : <div className='bg-white border rounded p-4'>Loading preview...</div>}
  </div>
}
