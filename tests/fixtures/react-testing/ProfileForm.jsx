import React, { useState } from 'react';

export function ProfileForm({ save }) {
  const [name, setName] = useState('');
  const [status, setStatus] = useState('Ready');
  const [error, setError] = useState('');
  async function submit(event) {
    event.preventDefault();
    setStatus('Saving');
    setError('');
    try {
      await save(name.trim());
      setStatus('Saved');
    } catch {
      setStatus('Ready');
      setError('Could not save');
    }
  }
  return (
    <form onSubmit={submit} aria-label="Profile">
      <label>Display name<input value={name} onChange={event => setName(event.target.value)} /></label>
      <button disabled={!name.trim() || status === 'Saving'}>Save</button>
      <p role="status">{status}</p>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
