import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import { QuestionDetail } from './question-detail';

const meta = {
  title: 'Pages/QuestionDetail',
  component: QuestionDetail,
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={['/questions/1']}>
        <Routes>
          <Route path="/questions/:id" element={<Story />} />
        </Routes>
      </MemoryRouter>
    ),
  ],
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof QuestionDetail>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
