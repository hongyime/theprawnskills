import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProfileForm } from './ProfileForm.jsx';

describe('profile form observable contract', () => {
  it('does not submit an empty or whitespace-only name', async () => {
    const user = userEvent.setup();
    const save = vi.fn();
    render(<ProfileForm save={save} />);
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled();
    await user.type(screen.getByLabelText('Display name'), '   ');
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled();
    expect(save).not.toHaveBeenCalled();
  });
  it('submits a trimmed name and reports completion', async () => {
    const user = userEvent.setup();
    const save = vi.fn().mockResolvedValue(undefined);
    render(<ProfileForm save={save} />);
    await user.type(screen.getByLabelText('Display name'), ' Ada ');
    await user.click(screen.getByRole('button', { name: 'Save' }));
    expect(await screen.findByText('Saved')).toBeVisible();
    expect(save).toHaveBeenCalledExactlyOnceWith('Ada');
  });
  it('reports a failed save and allows another attempt', async () => {
    const user = userEvent.setup();
    const save = vi.fn().mockRejectedValue(new Error('synthetic failure'));
    render(<ProfileForm save={save} />);
    await user.type(screen.getByLabelText('Display name'), 'Ada');
    await user.click(screen.getByRole('button', { name: 'Save' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not save');
    expect(screen.getByRole('button', { name: 'Save' })).toBeEnabled();
    expect(screen.queryByText('Saved')).not.toBeInTheDocument();
  });
  it('waits for an existing status to change after a pending save', async () => {
    const user = userEvent.setup();
    let finishSave;
    const save = vi.fn(() => new Promise(resolve => { finishSave = resolve; }));
    render(<ProfileForm save={save} />);
    expect(screen.getByRole('status')).toHaveTextContent('Ready');
    await user.type(screen.getByLabelText('Display name'), 'Ada');
    await user.click(screen.getByRole('button', { name: 'Save' }));
    expect(screen.getByRole('status')).toHaveTextContent('Saving');
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled();
    await act(async () => { finishSave(); });
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Saved'));
  });
});
