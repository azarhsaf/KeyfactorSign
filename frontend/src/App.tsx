import { Navigate, Route, Routes } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import DashboardPage from './pages/DashboardPage';
import UploadDocumentPage from './pages/UploadDocumentPage';
import PendingSignaturesPage from './pages/PendingSignaturesPage';
import CompletedDocumentsPage from './pages/CompletedDocumentsPage';
import AuditLogsPage from './pages/AuditLogsPage';
import AdminSettingsPage from './pages/AdminSettingsPage';
import UsersPage from './pages/UsersPage';
import SignServerSettingsPage from './pages/SignServerSettingsPage';
import LdapSettingsPage from './pages/LdapSettingsPage';
import SmtpSettingsPage from './pages/SmtpSettingsPage';
import DocumentPreviewPage from './pages/DocumentPreviewPage';
import FailedDocumentsPage from './pages/FailedDocumentsPage';
import MyDocumentsPage from './pages/MyDocumentsPage';
import AppLayout from './layouts/AppLayout';
import { api } from './api/client';

const token = localStorage.getItem('token');
if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
const Wrap = (c: any) => <AppLayout admin={true}>{c}</AppLayout>;

export default function App() {
  const t = localStorage.getItem('token');
  return <Routes>
    <Route path='/login' element={<LoginPage />} />
    <Route path='/change-password' element={Wrap(<ChangePasswordPage />)} />
    <Route path='/dashboard' element={Wrap(<DashboardPage />)} />
    <Route path='/upload-document' element={Wrap(<UploadDocumentPage />)} />
    <Route path='/pending-signatures' element={Wrap(<PendingSignaturesPage />)} />
    <Route path='/completed-documents' element={Wrap(<CompletedDocumentsPage />)} />
    <Route path='/audit-logs' element={Wrap(<AuditLogsPage />)} />
    <Route path='/admin-settings' element={Wrap(<AdminSettingsPage />)} />
    <Route path='/users' element={Wrap(<UsersPage />)} />
    <Route path='/signserver-settings' element={Wrap(<SignServerSettingsPage />)} />
    <Route path='/ldap-settings' element={Wrap(<LdapSettingsPage />)} />
    <Route path='/smtp-settings' element={Wrap(<SmtpSettingsPage />)} />
    <Route path='/failed-documents' element={Wrap(<FailedDocumentsPage />)} />
    <Route path='/my-documents' element={Wrap(<MyDocumentsPage />)} />
    <Route path='/document-preview/:id' element={Wrap(<DocumentPreviewPage />)} />
    <Route path='/logout' element={<Navigate to='/login' />} />
    <Route path='*' element={<Navigate to={t ? '/dashboard' : '/login'} />} />
  </Routes>;
}
