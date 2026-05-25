import { useEffect, useState } from 'react';
import { api } from '../api/client';
import StatCard from '../components/StatCard';
import DocumentTable from '../components/DocumentTable';

export default function DashboardPage(){
  const [summary,setSummary]=useState<any>({});
  const [docs,setDocs]=useState<any[]>([]);
  useEffect(()=>{api.get('/dashboard/summary').then(r=>setSummary(r.data)); api.get('/documents').then(r=>setDocs(r.data.slice(0,6)));},[])
  return <div className='space-y-6'>
    <h2 className='text-2xl font-semibold'>Dashboard</h2>
    <div className='grid grid-cols-1 md:grid-cols-7 gap-4'>
      <StatCard label='Total Documents' value={summary.total_documents||0}/>
      <StatCard label='Pending My Signature' value={summary.pending_my_signature||0}/>
      <StatCard label='Uploaded by Me' value={summary.uploaded_by_me||0}/>
      <StatCard label='Completed' value={summary.completed_documents||0}/>
      <StatCard label='Failed Signing Jobs' value={summary.failed_signing_jobs||0}/>
      <StatCard label='Emails Sent' value={summary.emails_sent||0}/>
      <StatCard label='Emails Failed' value={summary.emails_failed||0}/>
    </div>
    <div><h3 className='font-semibold mb-2'>Recent Documents</h3><DocumentTable rows={docs}/></div>
  </div>
}
