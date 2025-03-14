'use client';

import { MCPPolicyForm } from './components/MCPPolicyForm';

export default function Home() {
  return (
    <main className="container">
      <h1>MCP Policy Management</h1>
      <MCPPolicyForm />
    </main>
  );
}
