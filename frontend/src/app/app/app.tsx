import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import { ChatPage } from '@/pages/chat/chat-page';
import { DashboardDetail } from '@/pages/dashboards/dashboard-detail';
import { DashboardsPage } from '@/pages/dashboards/dashboards-page';
import { DatasetDetail } from '@/pages/datasets/dataset-detail';
import { DatasetsPage } from '@/pages/datasets/datasets-page';
import { QuestionDetail } from '@/pages/questions/question-detail';
import { QuestionsPage } from '@/pages/questions/questions-page';
import { Layout } from '@/shared/components/layout';

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
