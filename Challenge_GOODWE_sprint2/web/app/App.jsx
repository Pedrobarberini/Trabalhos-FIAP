import React, { useState } from 'react';
import { Sidebar } from './Sidebar.jsx';
import { Header } from './Header.jsx';
import { PageHeading } from './PageHeading.jsx';
import { DemoBanner } from './DemoBanner.jsx';
import { Footer } from './Footer.jsx';
import { Notification } from '../shared/components/Notification.jsx';
import { Modal } from '../shared/components/Modal.jsx';
import { useOperations } from '../shared/hooks/useOperations.mjs';
import { useMutation } from '../shared/hooks/useMutation.mjs';
import { useForecast } from '../features/intelligence/useForecast.mjs';
import { chargeOpsApi } from '../shared/api/client.mjs';
import { OverviewPage } from '../features/overview/OverviewPage.jsx';
import { SessionsPage } from '../features/sessions/SessionsPage.jsx';
import { InvoicesPage } from '../features/invoices/InvoicesPage.jsx';
import { IntelligencePage } from '../features/intelligence/IntelligencePage.jsx';
import { ResidentPage } from '../features/resident/ResidentPage.jsx';
import { RegisterForm } from '../features/sessions/RegisterForm.jsx';
import { ReviewForm } from '../features/sessions/ReviewForm.jsx';

export function App() {
  const [page, setPage] = useState('overview');
  const [month, setMonth] = useState('2026-09');
  const [sessionFilter, setSessionFilter] = useState('all');
  const [modal, setModal] = useState(null);
  const operations = useOperations(month);
  const prediction = useForecast(month, operations.revision);
  const mutation = useMutation();
  const data = operations.data;

  function navigate(nextPage) {
    mutation.clear();
    setPage(nextPage);
  }
  function openModal(value) {
    mutation.clear();
    setModal(value);
  }
  function openSessions(filter = 'all') {
    setSessionFilter(filter);
    navigate('sessions');
  }
  async function submit(work, message) {
    if (await mutation.run(work, message)) {
      setModal(null);
      operations.refresh();
    }
  }
  const onReview = (session) => openModal({ type: 'review', session });

  function renderPage() {
    const shared = {
      ...data,
      ...prediction,
      month,
      busy: mutation.busy,
      onReview,
      onOpenSessions: openSessions,
    };
    switch (page) {
      case 'overview':
        return <OverviewPage {...shared} onOpenInvoices={() => navigate('invoices')} />;
      case 'sessions':
        return (
          <SessionsPage
            key={`${month}-${sessionFilter}`}
            {...shared}
            initialFilter={sessionFilter}
            onImport={(file) =>
              submit(
                async () => chargeOpsApi.import(JSON.parse(await file.text())),
                'Lote importado e analisado pela IA.',
              )
            }
          />
        );
      case 'invoices':
        return (
          <InvoicesPage
            {...shared}
            onGenerate={(values) =>
              submit(
                () => chargeOpsApi.generateInvoices(values),
                'Mês fechado. Faturas individuais geradas e preservadas.',
              )
            }
          />
        );
      case 'intelligence':
        return <IntelligencePage {...shared} />;
      case 'resident':
        return <ResidentPage {...data} />;
      default:
        return null;
    }
  }

  return (
    <div className="app">
      <Sidebar page={page} pending={data?.dashboard.pending || 0} onNavigate={navigate} />
      <main>
        <Header page={page} />
        <div className="content">
          <PageHeading
            page={page}
            month={month}
            setMonth={setMonth}
            ready={Boolean(data) && !mutation.busy}
            onRegister={() => openModal({ type: 'register' })}
          />
          <DemoBanner catalog={data?.catalog} />
          <Notification
            message={mutation.error || operations.error}
            onClose={mutation.error ? mutation.clear : undefined}
          />
          <Notification type="success" message={mutation.notice} onClose={mutation.clear} />
          {data ? (
            renderPage()
          ) : (
            <div className="panel empty">
              {operations.error
                ? 'Não foi possível carregar a operação.'
                : 'Carregando a operação…'}
            </div>
          )}
          <Footer />
        </div>
      </main>
      {modal && data && (
        <Modal
          title={modal.type === 'review' ? 'Revisar sessão' : 'Registrar sessão'}
          busy={mutation.busy}
          onClose={() => setModal(null)}
        >
          {modal.type === 'review' ? (
            <ReviewForm
              session={modal.session}
              busy={mutation.busy}
              error={mutation.error}
              onSubmit={(values) =>
                submit(
                  () => chargeOpsApi.review(modal.session.id, values),
                  'Revisão registrada com justificativa.',
                )
              }
            />
          ) : (
            <RegisterForm
              catalog={data.catalog}
              month={month}
              busy={mutation.busy}
              error={mutation.error}
              onSubmit={(values) =>
                submit(
                  () => chargeOpsApi.register(values),
                  'Sessão registrada, normalizada e analisada pela IA.',
                )
              }
            />
          )}
        </Modal>
      )}
    </div>
  );
}
