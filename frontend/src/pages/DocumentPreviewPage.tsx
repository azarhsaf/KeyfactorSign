import { useParams } from 'react-router-dom'; import PdfViewer from '../components/PdfViewer';
export default function DocumentPreviewPage(){const {id}=useParams(); return <div className='space-y-4'><h2 className='text-2xl font-semibold'>Document Preview</h2><PdfViewer url={`/api/documents/${id}/preview`}/></div>}
