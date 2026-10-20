/**
 * KikuLog — shared JavaScript utilities
 * No emoji output anywhere in this file or the UI.
 */

(function () {
  const API = {
    async get(path) {
      const res = await fetch(path);
      if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
      return res.json();
    },
    async post(path, body) {
      const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `POST ${path} failed: ${res.status}`);
      }
      return res.json();
    },
  };

  function activityLabel(code) {
    const labels = {
      clear_old_plants:    'Clear old plants',
      remove_net:          'Remove net',
      remove_stakes:       'Remove stakes',
      tillage_1:           'Tillage (1st)',
      cover_plastic_1:     'Cover plastic (1st)',
      uncover_plastic_1:   'Uncover plastic (1st)',
      basal_fertilization: 'Basal fertilization',
      tillage_2:           'Tillage (2nd)',
      make_beds:           'Make beds',
      planting:            'Planting',
      cover_plastic_2:     'Cover plastic (after planting)',
      uncover_plastic_2:   'Uncover plastic (14 DAP)',
      install_net:         'Install net (14 DAP)',
      inspect_net:         'Inspect net',
      raise_net:           'Raise net',
      cutting:             'Cutting',
      packing:             'Packing',
      other:               'Other',
    };
    return labels[code] || code;
  }

  function statusBadge(status) {
    const map = {
      done:        'badge-done',
      in_progress: 'badge-in-progress',
      planned:     'badge-planned',
      not_done:    'badge-overdue',
      postponed:   'badge-postponed',
      cancelled:   'badge-postponed',
      overdue:     'badge-overdue',
    };
    const cls = map[status] || 'badge-planned';
    const label = status.replace('_', ' ');
    return `<span class="badge ${cls}">${label}</span>`;
  }

  function formatDate(isoDate) {
    if (!isoDate) return '—';
    const d = new Date(isoDate + 'T00:00:00');
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  // Set default date input to today in Asia/Tokyo
  function setDefaultWorkingDate(inputId) {
    const el = document.getElementById(inputId);
    if (!el) return;
    const now = new Date();
    const tokyoStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Tokyo' }); // YYYY-MM-DD
    el.value = tokyoStr;
  }

  window.KikuLog = { API, activityLabel, statusBadge, formatDate, setDefaultWorkingDate };
})();
