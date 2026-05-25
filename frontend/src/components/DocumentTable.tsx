import StatusBadge from './StatusBadge'
export default function DocumentTable({rows,actions}:{rows:any[],actions?:(r:any)=>any}){
  return <div className='bg-white rounded-xl border overflow-x-auto'><table className='w-full text-sm'><thead className='bg-slate-50'><tr><th className='p-3 text-left'>Document</th><th>Uploaded By</th><th>Status</th><th>Current Signer</th><th>Created</th><th>Actions</th></tr></thead><tbody>{rows.map(r=><tr key={r.id} className='border-t'><td className='p-3'>{r.document_name}</td><td>{r.uploaded_by_name||'-'}</td><td><StatusBadge status={r.status}/></td><td>{r.current_signer||'-'}</td><td>{r.created_at?.slice(0,19).replace('T',' ')}</td><td>{actions?actions(r):null}</td></tr>)}</tbody></table></div>
}
