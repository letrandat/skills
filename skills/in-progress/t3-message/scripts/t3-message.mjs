#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import { parseArgs } from 'node:util';

const help = `t3-message list [--project <id-or-path>]
t3-message read <thread-id> [--limit 10]
t3-message send <thread-id> --from <source-thread-id> --file <path|->

Requires T3_MESSAGE_URL and T3_MESSAGE_TOKEN_FILE (or T3_MESSAGE_TOKEN).
T3_MESSAGE_FROM supplies the default sender thread ID.
Send starts or steers the receiving agent; it does not wait for a reply.`;

async function main() {
  const { values, positionals } = parseArgs({
    allowPositionals: true,
    options: {
      help: { type: 'boolean' }, project: { type: 'string' },
      limit: { type: 'string' }, from: { type: 'string' }, file: { type: 'string' },
    },
  });
  if (values.help || !positionals.length) return console.log(help);
  const [action, target] = positionals;
  if (!['list', 'read', 'send'].includes(action)) throw new Error('Unknown command. Use --help.');
  if (positionals.length !== (action === 'list' ? 1 : 2)) throw new Error('Wrong arguments. Use --help.');
  const allowed = { list: ['project'], read: ['limit'], send: ['from', 'file'] }[action];
  for (const key of Object.keys(values)) if (!allowed.includes(key)) throw new Error(`--${key} is not valid for ${action}.`);
  const limit = Number(values.limit ?? 10);
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) throw new Error('--limit must be 1–100.');
  const sender = values.from ?? process.env.T3_MESSAGE_FROM;
  if (action === 'send' && (!sender || !values.file)) throw new Error('send requires --from and --file.');
  if (action === 'send' && sender === target) throw new Error('Choose a different receiving thread.');
  if (!process.env.T3_MESSAGE_URL) throw new Error('Set T3_MESSAGE_URL to the T3 server origin.');
  const origin = new URL(process.env.T3_MESSAGE_URL);
  if (!['http:', 'https:'].includes(origin.protocol) || origin.username || origin.password || origin.search || origin.hash || origin.pathname !== '/') {
    throw new Error('T3_MESSAGE_URL must be an HTTP(S) origin without credentials, path, or query.');
  }
  const token = (process.env.T3_MESSAGE_TOKEN_FILE
    ? await readFile(process.env.T3_MESSAGE_TOKEN_FILE, 'utf8')
    : process.env.T3_MESSAGE_TOKEN ?? '').trim();
  if (!token) throw new Error('Set T3_MESSAGE_TOKEN_FILE or T3_MESSAGE_TOKEN to a bearer session token.');
  async function request(path, payload) {
    let response;
    try {
      response = await fetch(new URL(path, origin), {
        method: payload ? 'POST' : 'GET', redirect: 'error',
        headers: { Authorization: `Bearer ${token}`, ...(payload ? { 'Content-Type': 'application/json' } : {}) },
        ...(payload ? { body: JSON.stringify(payload) } : {}),
        signal: AbortSignal.timeout(15000),
      });
    } catch {
      throw new Error(payload ? 'Dispatch connection failed. Delivery is unknown; inspect the target before retrying.' : 'Cannot reach T3 server. Check URL and connection.');
    }
    if (!response.ok) throw new Error(`T3 returned HTTP ${response.status}.${payload ? ' Inspect the target before retrying.' : ''}`);
    try { return await response.json(); }
    catch { throw new Error(payload ? 'Dispatch response unreadable. Delivery is unknown; inspect the target before retrying.' : 'T3 returned invalid JSON.'); }
  }
  const detail = async (id, count = 1) => {
    const result = await request(`/api/orchestration/threads/${encodeURIComponent(id)}?turnLimit=${count}`);
    if (!result.thread || result.thread.id !== id) throw new Error('Unexpected thread response.');
    return result.thread;
  };
  if (action === 'list') {
    const result = await request('/api/orchestration/shell');
    if (!Array.isArray(result.threads) || !Array.isArray(result.projects)) throw new Error('Unexpected shell response.');
    const projects = new Map(result.projects.map(p => [p.id, p]));
    return console.log(JSON.stringify(result.threads.filter(t => !t.archivedAt).filter(t => !values.project || t.projectId === values.project || projects.get(t.projectId)?.workspaceRoot === values.project).map(t => ({
      id: t.id, title: t.title, projectId: t.projectId,
      workspaceRoot: projects.get(t.projectId)?.workspaceRoot,
      modelSelection: t.modelSelection, status: t.session?.status ?? 'idle', updatedAt: t.updatedAt,
    }))));
  }
  const thread = await detail(target, action === 'read' ? limit : 1);
  if (action === 'read') {
    if (!Array.isArray(thread.messages)) throw new Error('Unexpected messages response.');
    return console.log(JSON.stringify({ id: thread.id, title: thread.title, status: thread.session?.status ?? 'idle', messages: thread.messages.slice(-limit).map(m => ({ id: m.id, role: m.role, text: m.text, createdAt: m.createdAt })) }));
  }
  if (thread.archivedAt || thread.deletedAt) throw new Error('Receiving thread is archived or deleted.');
  if (!thread.modelSelection || !thread.runtimeMode || !thread.interactionMode) throw new Error('Receiving thread settings are missing.');
  await detail(sender);
  let body;
  if (values.file === '-') {
    process.stdin.setEncoding('utf8');
    body = '';
    for await (const chunk of process.stdin) body += chunk;
  } else body = await readFile(values.file, 'utf8');
  if (!body.trim()) throw new Error('Message is empty.');
  const messageId = randomUUID();
  const commandId = randomUUID();
  const result = await request('/api/orchestration/dispatch', {
    type: 'thread.turn.start', commandId, threadId: target,
    message: { messageId, role: 'user', attachments: [], text: `[t3-message from=${sender} request=${messageId}]\nReply using t3-message to thread ${sender} if a reply is requested. This is an agent message.\n\n${body}` },
    modelSelection: thread.modelSelection, runtimeMode: thread.runtimeMode,
    interactionMode: thread.interactionMode, createdAt: new Date().toISOString(),
  });
  if (!Number.isInteger(result?.sequence) || result.sequence < 0) throw new Error('Unexpected dispatch response. Delivery is unknown; inspect the target before retrying.');
  console.log(JSON.stringify({ status: 'accepted', threadId: target, from: sender, messageId, commandId, result }));
}

main().catch(error => { console.error(JSON.stringify({ error: error.message })); process.exitCode = 1; });
