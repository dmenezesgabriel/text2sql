import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import { DatasetDetail } from './dataset-detail';

const meta = {
  title: 'Pages/DatasetDetail',
  component: DatasetDetail,
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={['/datasets/1']}>
        <Routes>
          <Route path="/datasets/:id" element={<Story />} />
        </Routes>
      </MemoryRouter>
    ),
  ],
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof DatasetDetail>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
