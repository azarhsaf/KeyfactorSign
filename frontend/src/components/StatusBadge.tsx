export default function StatusBadge({status}:{status:string}){
  const map: Record<string,string> = {
    'Completed':'bg-emerald-100 text-emerald-700','Pending Signature':'bg-amber-100 text-amber-700','In Progress':'bg-blue-100 text-blue-700','Failed':'bg-rose-100 text-rose-700','Rejected':'bg-gray-200 text-gray-700'
  }
  return <span className={`px-2 py-1 rounded text-xs font-semibold ${map[status]||'bg-slate-100 text-slate-700'}`}>{status}</span>
}
