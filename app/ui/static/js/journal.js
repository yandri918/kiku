/**
 * KikuLog — journal page logic
 * Handles note submission, draft display, and approval.
 */

const { API, activityLabel, statusBadge, formatDate, setDefaultWorkingDate } = window.KikuLog;

document.addEventListener('DOMContentLoaded', () => {
  setDefaultWorkingDate('note-date');
  setupCharCounter();
  setupNoteForm();
  loadHouses();
});

function setupCharCounter() {
  const textarea = document.getElementById('note-text');
  const counter  = document.getElementById('char-count');
  if (!textarea || !counter) return;
  textarea.addEventListener('input', () => {
    counter.textContent = `${textarea.value.length} / 4000`;
  });
}

function setupNoteForm() {
  const form = document.getElementById('note-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submit-note-btn');
    btn.disabled = true;
    btn.textContent = 'Extracting...';

    try {
      const body = {
        text:         document.getElementById('note-text').value.trim(),
        working_date: document.getElementById('note-date').value || null,
      };
      const draft = await API.post('/api/notes/submit', body);
      renderDraft(draft);
    } catch (err) {
      alert(`Extraction failed: ${err.message}\n\nYou can enter events manually.`);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Extract Draft';
    }
  });
}

function renderDraft(draft) {
  const section = document.getElementById('draft-section');
  if (!section) return;
  section.hidden = false;

  // Clarifications
  const clarBox  = document.getElementById('clarification-box');
  const clarList  = document.getElementById('clarification-list');
  if (draft.clarifications && draft.clarifications.length) {
    clarList.innerHTML = draft.clarifications.map(c => `<li>${c}</li>`).join('');
    clarBox.hidden = false;
  } else {
    clarBox.hidden = true;
  }

  // Events
  const container = document.getElementById('draft-events');
  if (!draft.events || !draft.events.length) {
    container.innerHTML = '<p class="empty-state">No events extracted. Please check the note or enter manually.</p>';
    return;
  }
  container.innerHTML = draft.events.map((ev, i) => `
    <div class="draft-event-card" data-index="${i}">
      <div class="draft-event-header">
        <span class="draft-event-activity">${activityLabel(ev.activity)}</span>
        ${statusBadge(ev.status)}
      </div>
      <div style="font-size:0.82rem;color:var(--color-text-muted);margin-bottom:6px;">
        House: ${ev.house_id || '—'} &nbsp;|&nbsp;
        Date: ${ev.occurred_on ? formatDate(ev.occurred_on) : (ev.planned_on ? formatDate(ev.planned_on) : '—')}
      </div>
      <div class="draft-event-evidence">"${ev.evidence}"</div>
      <div style="margin-top:12px;">
        <button class="btn btn-ghost" style="font-size:0.8rem;padding:4px 12px;"
          onclick="removeEvent(${i})" id="remove-event-${i}">Remove</button>
      </div>
    </div>
  `).join('');

  // Store draft for approval
  window._currentDraft = draft;

  // Approve / discard
  document.getElementById('approve-btn').onclick = approveDraft;
  document.getElementById('discard-btn').onclick = discardDraft;
}

function removeEvent(index) {
  const card = document.querySelector(`[data-index="${index}"]`);
  if (card) card.remove();
  if (window._currentDraft) {
    window._currentDraft.events.splice(index, 1);
  }
}

async function approveDraft() {
  if (!window._currentDraft) return;
  const btn = document.getElementById('approve-btn');
  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    await API.post('/api/notes/approve', {
      draft_id: window._currentDraft.draft_id,
      approved_events: window._currentDraft.events,
    });
    discardDraft();
    loadHouses(); // refresh journal
    alert('Events saved.');
  } catch (err) {
    alert(`Save failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save Approved Events';
  }
}

function discardDraft() {
  const section = document.getElementById('draft-section');
  if (section) section.hidden = true;
  window._currentDraft = null;
  document.getElementById('draft-events').innerHTML = '';
  document.getElementById('note-text').value = '';
  document.getElementById('char-count').textContent = '0 / 4000';
}

async function loadHouses() {
  try {
    const houses = await API.get('/api/houses/');
    const select = document.getElementById('house-filter');
    if (!select) return;
    const current = select.value;
    select.innerHTML = '<option value="">All houses</option>' +
      houses.map(h => `<option value="${h.id}">${h.display_name}</option>`).join('');
    select.value = current;
    select.onchange = () => loadJournal(select.value);
    loadJournal(select.value);
  } catch (_) {
    // API not yet implemented; ignore silently during dev
  }
}

async function loadJournal(houseId) {
  if (!houseId) return;
  try {
    const events = await API.get(`/api/houses/${houseId}/journal`);
    const list = document.getElementById('event-list');
    if (!list) return;
    if (!events.length) {
      list.innerHTML = '<p class="empty-state">No events for this house.</p>';
      return;
    }
    list.innerHTML = events.map(ev => `
      <div class="task-item">
        <div>
          <div class="task-activity">${activityLabel(ev.activity)}</div>
          <div class="task-meta">${formatDate(ev.occurred_on || ev.planned_on)} &nbsp;|&nbsp; ${ev.evidence || ''}</div>
        </div>
        ${statusBadge(ev.status)}
      </div>
    `).join('');
  } catch (_) {
    // ignore during dev
  }
}
