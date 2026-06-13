import React from 'react';
import { Navigate,Route, Routes } from 'react-router-dom';

import { ChatPage } from '@/pages/chat/ChatPage';
import { DashboardDetail } from '@/pages/dashboards/DashboardDetail';
import { DashboardsPage } from '@/pages/dashboards/DashboardsPage';
import { DatasetDetail } from '@/pages/datasets/DatasetDetail';
import { DatasetsPage } from '@/pages/datasets/DatasetsPage';
import { QuestionDetail } from '@/pages/questions/QuestionDetail';
import { QuestionsPage } from '@/pages/questions/QuestionsPage';
import { Layout } from '@/shared/components/Layout';

/**
 *
 */
export function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/questions" element={<QuestionsPage />} />
        <Route path="/questions/:id" element={<QuestionDetail />} />
        <Route path="/dashboards" element={<DashboardsPage />} />
        <Route path="/dashboards/:id" element={<DashboardDetail />} />
        <Route path="/datasets" element={<DatasetsPage />} />
        <Route path="/datasets/:id" element={<DatasetDetail />} />
      </Routes>
    </Layout>
  );
}
