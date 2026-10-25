/**
 * WanderAI — Pure Vanilla JavaScript Application Controller (ES6+)
 * Consumer-Facing AI Travel Planner
 * Orchestrates API communication with FastAPI, LangGraph SSE streaming,
 * and dynamic UI rendering (Itinerary, Budget Breakdown, Packing Checklist, Guide).
 */

// Dynamically determine the backend API base URL
const API_BASE_URL = window.location.origin.includes(':8000')
  ? window.location.origin
  : 'http://127.0.0.1:8000';

// API Error message extraction helper
function formatApiError(data, fallback = 'An unexpected error occurred.') {
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map(item => item.msg || item.message || JSON.stringify(item)).join('; ');
  }
  if (data.message && typeof data.message === 'string') return data.message;
  return fallback;
}

// Application State
let currentPlan = null;
let packingCheckedState = {}; // { itemKey: boolean }

// User Authentication State
let currentUser = null;
let authToken = localStorage.getItem('wanderai_auth_token') || null;

function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  return headers;
}

// Currency Symbol Map
const CURRENCY_SYMBOLS = {
  USD: '$',
  EUR: '€',
  GBP: '£',
  INR: '₹',
  JPY: '¥',
  CAD: 'CA$',
  AUD: 'AU$'
};

function formatCurrency(amount, currencyCode = 'USD') {
  const sym = CURRENCY_SYMBOLS[currencyCode] || `${currencyCode} `;
  const num = Number(amount) || 0;
  return `${sym} ${num.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
}

// DOM Elements
const brandEl = document.getElementById('nav-brand');
const formEl = document.getElementById('trip-form');
const heroSection = document.getElementById('hero');
const planningSection = document.getElementById('planning-section');
const trackerSection = document.getElementById('tracker-section');
const dossierSection = document.getElementById('dossier-section');
const terminalContainer = document.getElementById('terminal-feed-container');
const errorBanner = document.getElementById('error-banner');
const errorMessageText = document.getElementById('error-message-text');
const btnDismissError = document.getElementById('btn-dismiss-error');
const btnNewPlan = document.getElementById('btn-new-plan');
const submitBtn = document.getElementById('btn-submit-plan');
const submitText = document.getElementById('submit-text');

// Mobile Navigation
const btnMobileMenu = document.getElementById('btn-mobile-menu');
const mobileNavDrawer = document.getElementById('mobile-nav-drawer');
const btnMobileSavedTrips = document.getElementById('btn-mobile-saved-trips');

// Modals
const modalSettings = document.getElementById('modal-settings');
const btnOpenSettings = document.getElementById('btn-open-settings');
const btnCloseSettings = document.getElementById('close-modal-settings');
const formSettings = document.getElementById('settings-form');
const selectSettingsProvider = document.getElementById('settings-provider');
const inputSettingsApiKey = document.getElementById('settings-api-key');

const modalSavedTrips = document.getElementById('modal-saved-trips');
const btnOpenSavedTrips = document.getElementById('btn-open-saved-trips');
const btnCloseSavedTrips = document.getElementById('close-modal-saved-trips');
const savedTripsList = document.getElementById('saved-trips-list');

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  initDateDefault();
  initQuickDestinations();
  initDestinationShowcase();
  initExperienceCards();
  initTravelerSelection();
  initTabs();
  initModals();
  initAuth();
  initAuthModals();
  initMobileNav();
  initExportActions();
  initChatWidget();
  handleInitialUrlHash();
  fetchBackendHealth();

  // Handle URL hash changes dynamically
  window.addEventListener('hashchange', handleInitialUrlHash);

  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }
});

// Handle initial URL hash for direct modal opening
function handleInitialUrlHash() {
  const hash = window.location.hash;
  if (!hash) return;
  if (hash === '#modal-saved-trips' || hash === '#saved-trips') {
    if (modalSavedTrips) {
      modalSavedTrips.classList.add('active');
      loadSavedTrips();
    }
  } else if (hash === '#login' || hash === '#modal-auth-login') {
    if (typeof window.openLoginModal === 'function') window.openLoginModal();
  } else if (hash === '#register' || hash === '#modal-auth-register') {
    if (typeof window.openRegisterModal === 'function') window.openRegisterModal();
  }
}

// Set default travel date to 14 days from today
function initDateDefault() {
  const dateInput = document.getElementById('input-start-date');
  if (dateInput) {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    dateInput.value = d.toISOString().split('T')[0];
  }
}

// Check backend health
async function fetchBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (res.ok) {
      const data = await res.json();
      console.log('Backend connected:', data.status, '| Provider:', data.provider);
    }
  } catch (err) {
    console.warn('Backend server not connected yet on http://127.0.0.1:8000:', err);
  }
}

// Quick destination chips
function initQuickDestinations() {
  const chips = document.querySelectorAll('.quick-chip');
  const destInput = document.getElementById('input-destination');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      if (destInput) {
        destInput.value = chip.getAttribute('data-dest');
        destInput.focus();
      }
    });
  });
}

// Destination inspiration cards in Hero
function initDestinationShowcase() {
  const cards = document.querySelectorAll('.dest-card');
  const destInput = document.getElementById('input-destination');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      const dest = card.getAttribute('data-dest');
      if (destInput) {
        destInput.value = dest;
      }
      // Update quick chips if matching
      document.querySelectorAll('.quick-chip').forEach(c => {
        if (c.getAttribute('data-dest') === dest) {
          c.classList.add('active');
        } else {
          c.classList.remove('active');
        }
      });
      // Smooth scroll to form
      if (planningSection) {
        planningSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// Footer destination selector helper
window.setDestinationFromFooter = function(dest) {
  const destInput = document.getElementById('input-destination');
  if (destInput) {
    destInput.value = dest;
    planningSection.scrollIntoView({ behavior: 'smooth' });
  }
};

// "How do you experience it?" interactive selection cards
function initExperienceCards() {
  const cards = document.querySelectorAll('.experience-card');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      const isSelected = card.classList.contains('selected');
      if (isSelected) {
        card.classList.remove('selected');
        card.setAttribute('aria-pressed', 'false');
      } else {
        card.classList.add('selected');
        card.setAttribute('aria-pressed', 'true');
      }
    });
  });
}

// Get selected interests from experience cards
function getSelectedInterests() {
  const selectedCards = document.querySelectorAll('.experience-card.selected');
  const interests = [];
  selectedCards.forEach(c => {
    const val = c.getAttribute('data-interest');
    if (val) interests.push(val);
  });
  return interests.length > 0 ? interests : ['Culture & History', 'Culinary & Dining'];
}

// ================= TRAVELER OPTIONS & COUNTS CONTROLLER =================
let currentTravelersCount = 2;
let currentTravelerType = 'Couple';

function initTravelerSelection() {
  const selectType = document.getElementById('select-traveler-type');
  const familyControls = document.getElementById('sub-family-controls');
  const friendsControls = document.getElementById('sub-friends-controls');
  const partyCountDisplay = document.getElementById('party-count-display');
  const hintText = document.getElementById('traveler-hint-text');

  const inputAdults = document.getElementById('input-family-adults');
  const inputChildren = document.getElementById('input-family-children');
  const inputFriends = document.getElementById('input-friends-count');

  const btnAdultsMinus = document.getElementById('btn-adults-minus');
  const btnAdultsPlus = document.getElementById('btn-adults-plus');
  const btnChildrenMinus = document.getElementById('btn-children-minus');
  const btnChildrenPlus = document.getElementById('btn-children-plus');
  const btnFriendsMinus = document.getElementById('btn-friends-minus');
  const btnFriendsPlus = document.getElementById('btn-friends-plus');

  function updateTravelerSummary() {
    const type = selectType ? selectType.value : 'Couple';
    currentTravelerType = type;

    if (type === 'Solo') {
      currentTravelersCount = 1;
      if (familyControls) familyControls.style.display = 'none';
      if (friendsControls) friendsControls.style.display = 'none';
      if (hintText) hintText.textContent = '1 traveler selected (1 room needed)';
    } else if (type === 'Couple') {
      currentTravelersCount = 2;
      if (familyControls) familyControls.style.display = 'none';
      if (friendsControls) friendsControls.style.display = 'none';
      if (hintText) hintText.textContent = '2 travelers selected (1 room needed)';
    } else if (type === 'Family') {
      if (familyControls) familyControls.style.display = 'block';
      if (friendsControls) friendsControls.style.display = 'none';
      const adults = Math.max(1, Number(inputAdults ? inputAdults.value : 2) || 2);
      const children = Math.max(0, Number(inputChildren ? inputChildren.value : 0) || 0);
      currentTravelersCount = adults + children;
      const rooms = Math.max(1, Math.ceil(currentTravelersCount / 2.5));
      if (hintText) hintText.textContent = `${currentTravelersCount} travelers (${adults} adults, ${children} children • ~${rooms} room(s))`;
    } else if (type === 'Friends') {
      if (familyControls) familyControls.style.display = 'none';
      if (friendsControls) friendsControls.style.display = 'block';
      currentTravelersCount = Math.max(3, Number(inputFriends ? inputFriends.value : 4) || 4);
      const rooms = Math.max(1, Math.ceil(currentTravelersCount / 2));
      if (hintText) hintText.textContent = `${currentTravelersCount} friends selected (~${rooms} rooms needed)`;
    }

    if (partyCountDisplay) {
      partyCountDisplay.textContent = currentTravelersCount;
    }
  }

  if (selectType) {
    selectType.addEventListener('change', updateTravelerSummary);
  }

  // Adults stepper
  if (btnAdultsMinus && inputAdults) {
    btnAdultsMinus.addEventListener('click', () => {
      inputAdults.value = Math.max(1, (Number(inputAdults.value) || 2) - 1);
      updateTravelerSummary();
    });
  }
  if (btnAdultsPlus && inputAdults) {
    btnAdultsPlus.addEventListener('click', () => {
      inputAdults.value = Math.min(10, (Number(inputAdults.value) || 2) + 1);
      updateTravelerSummary();
    });
  }
  if (inputAdults) {
    inputAdults.addEventListener('input', updateTravelerSummary);
  }

  // Children stepper
  if (btnChildrenMinus && inputChildren) {
    btnChildrenMinus.addEventListener('click', () => {
      inputChildren.value = Math.max(0, (Number(inputChildren.value) || 0) - 1);
      updateTravelerSummary();
    });
  }
  if (btnChildrenPlus && inputChildren) {
    btnChildrenPlus.addEventListener('click', () => {
      inputChildren.value = Math.min(10, (Number(inputChildren.value) || 0) + 1);
      updateTravelerSummary();
    });
  }
  if (inputChildren) {
    inputChildren.addEventListener('input', updateTravelerSummary);
  }

  // Friends stepper
  if (btnFriendsMinus && inputFriends) {
    btnFriendsMinus.addEventListener('click', () => {
      inputFriends.value = Math.max(3, (Number(inputFriends.value) || 4) - 1);
      updateTravelerSummary();
    });
  }
  if (btnFriendsPlus && inputFriends) {
    btnFriendsPlus.addEventListener('click', () => {
      inputFriends.value = Math.min(20, (Number(inputFriends.value) || 4) + 1);
      updateTravelerSummary();
    });
  }
  if (inputFriends) {
    inputFriends.addEventListener('input', updateTravelerSummary);
  }

  // Notes listener for natural language traveler count extraction
  const notesEl = document.getElementById('input-notes');
  if (notesEl) {
    notesEl.addEventListener('blur', () => {
      parseNotesForTravelerCount(notesEl.value);
    });
  }

  updateTravelerSummary();
}

function parseNotesForTravelerCount(notesText) {
  if (!notesText) return;
  const t = notesText.toLowerCase();

  // Pattern 1: "me and X friends" -> X + 1 travelers
  const meFriendsMatch = t.match(/me\s+and\s+(\d+)\s+friends?/i);
  if (meFriendsMatch) {
    const friendCount = parseInt(meFriendsMatch[1], 10);
    const total = friendCount + 1;
    const selectType = document.getElementById('select-traveler-type');
    const inputFriends = document.getElementById('input-friends-count');
    if (selectType && inputFriends) {
      selectType.value = 'Friends';
      inputFriends.value = Math.max(3, total);
      selectType.dispatchEvent(new Event('change'));
    }
    return;
  }

  // Pattern 2: "we are X people" or "party of X" or "X of us"
  const groupMatch = t.match(/(?:we\s+are|party\s+of|group\s+of)\s+(\d+)(?:\s+people|\s+travelers|\s+persons)?/i) ||
                     t.match(/(\d+)\s+of\s+us/i);
  if (groupMatch) {
    const total = parseInt(groupMatch[1], 10);
    const selectType = document.getElementById('select-traveler-type');
    const inputFriends = document.getElementById('input-friends-count');
    if (selectType && total >= 3) {
      selectType.value = 'Friends';
      if (inputFriends) inputFriends.value = total;
      selectType.dispatchEvent(new Event('change'));
    } else if (selectType && total === 2) {
      selectType.value = 'Couple';
      selectType.dispatchEvent(new Event('change'));
    } else if (selectType && total === 1) {
      selectType.value = 'Solo';
      selectType.dispatchEvent(new Event('change'));
    }
    return;
  }
}

// Tab navigation for Generated Itinerary Dashboard
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const targetId = btn.getAttribute('data-tab');
      document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.style.display = 'none';
      });

      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.style.display = 'block';
      }

      if (window.lucide) window.lucide.createIcons();
    });
  });
}

// Mobile navigation drawer
function initMobileNav() {
  if (btnMobileMenu && mobileNavDrawer) {
    btnMobileMenu.addEventListener('click', () => {
      mobileNavDrawer.classList.toggle('active');
    });

    document.querySelectorAll('.mobile-nav-link').forEach(link => {
      link.addEventListener('click', () => {
        mobileNavDrawer.classList.remove('active');
      });
    });
  }

  if (btnMobileSavedTrips) {
    btnMobileSavedTrips.addEventListener('click', () => {
      mobileNavDrawer.classList.remove('active');
      if (modalSavedTrips) {
        modalSavedTrips.classList.add('active');
        loadSavedTrips();
      }
    });
  }
}

// Modals management
function initModals() {
  // Settings Modal
  if (btnOpenSettings && modalSettings) {
    btnOpenSettings.addEventListener('click', () => {
      let savedProvider = localStorage.getItem('wanderai_provider') || 'auto';
      if (savedProvider === 'mock' || savedProvider === 'offline') {
        savedProvider = 'auto';
        localStorage.setItem('wanderai_provider', 'auto');
      }
      const savedApiKey = localStorage.getItem('wanderai_api_key') || '';
      if (selectSettingsProvider) selectSettingsProvider.value = savedProvider;
      if (inputSettingsApiKey) inputSettingsApiKey.value = savedApiKey;
      modalSettings.classList.add('active');
    });
  }

  if (btnCloseSettings && modalSettings) {
    btnCloseSettings.addEventListener('click', () => {
      modalSettings.classList.remove('active');
    });
  }

  if (formSettings) {
    formSettings.addEventListener('submit', (e) => {
      e.preventDefault();
      localStorage.setItem('wanderai_provider', selectSettingsProvider.value);
      localStorage.setItem('wanderai_api_key', inputSettingsApiKey.value);
      modalSettings.classList.remove('active');
      fetchBackendHealth();
    });
  }

  // Saved Trips Modal
  if (btnOpenSavedTrips && modalSavedTrips) {
    btnOpenSavedTrips.addEventListener('click', () => {
      modalSavedTrips.classList.add('active');
      loadSavedTrips();
    });
  }

  if (btnCloseSavedTrips && modalSavedTrips) {
    btnCloseSavedTrips.addEventListener('click', () => {
      modalSavedTrips.classList.remove('active');
    });
  }

  // Close modals on backdrop click
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  });

  // Reset / Plan New Trip
  if (btnNewPlan) {
    btnNewPlan.addEventListener('click', resetToPlanningView);
  }
  if (brandEl) {
    brandEl.addEventListener('click', (e) => {
      e.preventDefault();
      resetToPlanningView();
    });
  }

  // Dismiss Error
  if (btnDismissError && errorBanner) {
    btnDismissError.addEventListener('click', () => {
      errorBanner.style.display = 'none';
    });
  }
}

function resetToPlanningView() {
  currentPlan = null;
  dossierSection.style.display = 'none';
  trackerSection.style.display = 'none';
  planningSection.style.display = 'block';
  btnNewPlan.style.display = 'none';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(msg) {
  if (errorBanner && errorMessageText) {
    errorMessageText.textContent = msg;
    errorBanner.style.display = 'flex';
    errorBanner.scrollIntoView({ behavior: 'smooth' });
  }
}

// Export actions (.md, JSON, Print/PDF)
function initExportActions() {
  const btnExportMd = document.getElementById('btn-export-md');
  const btnDownloadJson = document.getElementById('btn-download-json');
  const btnPrintPdf = document.getElementById('btn-print-pdf');

  if (btnExportMd) {
    btnExportMd.addEventListener('click', async () => {
      if (!currentPlan) return;
      try {
        const res = await fetch(`${API_BASE_URL}/api/export/markdown`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(currentPlan),
        });
        if (!res.ok) throw new Error('Markdown export failed');
        const blob = await res.blob();
        downloadBlob(blob, `${(currentPlan.destination || 'Trip').replace(/[^a-zA-Z0-9]/g, '_')}_itinerary.md`);
      } catch (err) {
        // Fallback to client-side Markdown generator
        generateClientMarkdownExport(currentPlan);
      }
    });
  }

  if (btnDownloadJson) {
    btnDownloadJson.addEventListener('click', () => {
      if (!currentPlan) return;
      const jsonStr = JSON.stringify(currentPlan, null, 2);
      const blob = new Blob([jsonStr], { type: 'application/json' });
      downloadBlob(blob, `${(currentPlan.destination || 'Trip').replace(/[^a-zA-Z0-9]/g, '_')}_itinerary.json`);
    });
  }

  if (btnPrintPdf) {
    btnPrintPdf.addEventListener('click', () => {
      window.print();
    });
  }
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

function generateClientMarkdownExport(plan) {
  const dest = plan.destination || 'Trip';
  const currency = plan.currency || 'USD';
  const totalCost = getEstimatedTotalCost(plan);
  let md = `# Travel Itinerary: ${plan.title || dest}\n\n`;
  md += `**Destination:** ${dest} | **Duration:** ${plan.duration_days} Days\n`;
  md += `**Estimated Total:** ${formatCurrency(totalCost, currency)}\n\n`;
  md += `## Daily Itinerary\n`;

  (plan.itinerary || []).forEach(day => {
    let dayHead = `\n### ${day.date_label || `Day ${day.day_number}`} — ${day.theme || 'Day Schedule'}`;
    if (day.current_city) {
      dayHead += ` [${day.current_city}]`;
    }
    md += `${dayHead}\n`;
    if (day.travel_leg) {
      md += `**Travel Leg:** ${day.travel_leg}\n\n`;
    }
    if (day.overnight_stay) {
      md += `**Overnight Stay:** ${day.overnight_stay}\n\n`;
    }
    md += `${day.summary || ''}\n\n`;
    (day.activities || []).forEach(act => {
      md += `- **${act.time_slot} (${act.time || ''}):** ${act.title}\n`;
      md += `  *Location:* ${act.location || ''} | *Cost:* ${formatCurrency(act.estimated_cost, currency)}\n`;
      md += `  ${act.description || ''}\n`;
    });
  });

  const blob = new Blob([md], { type: 'text/markdown' });
  downloadBlob(blob, `${dest.replace(/[^a-zA-Z0-9]/g, '_')}_itinerary.md`);
}

// ================= FORM SUBMISSION & WORKFLOW EXECUTION =================
if (formEl) {
  formEl.addEventListener('submit', async (e) => {
    e.preventDefault();

    const destination = document.getElementById('input-destination').value.trim();
    const origin = document.getElementById('input-origin').value.trim();
    const duration = Math.min(14, Math.max(1, Number(document.getElementById('input-duration').value) || 5));
    const startDate = document.getElementById('input-start-date').value;
    const budgetTotal = Math.max(50, Number(document.getElementById('input-budget').value) || 2500);
    const currency = document.getElementById('select-currency').value || 'USD';
    const travelerType = document.getElementById('select-traveler-type').value;
    const accommodation = document.getElementById('select-accommodation').value;
    const pace = document.getElementById('select-pace').value;
    const interests = getSelectedInterests();
    const notes = document.getElementById('input-notes').value.trim();

    if (!destination) {
      showError('Please enter a destination to plan your trip.');
      document.getElementById('input-destination').focus();
      return;
    }

    if (!origin) {
      showError('Please enter your starting departure city.');
      document.getElementById('input-origin').focus();
      return;
    }

    let provider = localStorage.getItem('wanderai_provider') || 'auto';
    if (provider === 'mock' || provider === 'offline') {
      provider = 'auto';
      localStorage.setItem('wanderai_provider', 'auto');
    }
    const apiKey = localStorage.getItem('wanderai_api_key') || null;

    let travelersCount = currentTravelersCount || 2;
    let adultsCount = null;
    let childrenCount = null;

    if (travelerType === 'Solo') {
      travelersCount = 1;
    } else if (travelerType === 'Couple') {
      travelersCount = 2;
    } else if (travelerType === 'Family') {
      const inputAdults = document.getElementById('input-family-adults');
      const inputChildren = document.getElementById('input-family-children');
      adultsCount = Math.max(1, Number(inputAdults ? inputAdults.value : 2) || 2);
      childrenCount = Math.max(0, Number(inputChildren ? inputChildren.value : 0) || 0);
      travelersCount = adultsCount + childrenCount;
    } else if (travelerType === 'Friends') {
      const inputFriends = document.getElementById('input-friends-count');
      travelersCount = Math.max(3, Number(inputFriends ? inputFriends.value : 4) || 4);
    }

    const payload = {
      origin,
      destination,
      duration_days: duration,
      start_date: startDate,
      budget_total: budgetTotal,
      currency,
      travelers_count: travelersCount,
      traveler_type: travelerType,
      adults_count: adultsCount,
      children_count: childrenCount,
      is_per_person_budget: false, // Critical Rule: Group total budget
      accommodation_type: accommodation,
      pace,
      interests,
      notes,
      provider,
      api_key: apiKey
    };

    // UI Loading state
    submitBtn.disabled = true;
    submitText.textContent = 'Planning Your Dream Trip...';
    trackerSection.style.display = 'block';
    resetStepProgressBoxes();
    clearTerminal();
    trackerSection.scrollIntoView({ behavior: 'smooth' });

    try {
      // Connect to FastAPI SSE Stream
      const response = await fetch(`${API_BASE_URL}/api/plan-trip/stream`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.replace('data: ', ''));

              if (eventData.type === 'log') {
                updateStepProgress(eventData.node, 'running');
                if (eventData.log) {
                  appendTerminalLog(eventData.log);
                }
              } else if (eventData.type === 'complete') {
                markAllStepsCompleted();
                currentPlan = eventData.data;
                renderFullDossier(currentPlan);
                finishLoadingState();
                return;
              } else if (eventData.type === 'error') {
                throw new Error(eventData.message || 'Stream processing error');
              }
            } catch (err) {
              console.warn('Error parsing SSE event:', err);
            }
          }
        }
      }
    } catch (streamErr) {
      console.warn('SSE stream failed, falling back to standard POST:', streamErr);
      // Fallback to standard synchronous POST /api/plan-trip
      try {
        const fbRes = await fetch(`${API_BASE_URL}/api/plan-trip`, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify(payload),
        });

        if (!fbRes.ok) {
          const errDetail = await fbRes.json().catch(() => ({}));
          throw new Error(errDetail.detail || 'Plan generation failed');
        }

        const data = await fbRes.json();
        markAllStepsCompleted();
        currentPlan = data;
        renderFullDossier(currentPlan);
        finishLoadingState();
      } catch (fallbackErr) {
        showError(fallbackErr.message || 'Could not connect to FastAPI backend on http://127.0.0.1:8000. Please verify the server is running.');
        finishLoadingState();
      }
    }
  });
}

function finishLoadingState() {
  submitBtn.disabled = false;
  submitText.textContent = 'Plan My Trip';
  if (currentPlan) {
    btnNewPlan.style.display = 'inline-flex';
  }
}

// Progress Steps
const STEP_IDS = [
  'destination_agent', 'budget_agent', 'preferences_agent',
  'research_agent', 'itinerary_generator', 'budget_calculator', 'final_planner'
];

function resetStepProgressBoxes() {
  STEP_IDS.forEach(id => {
    const el = document.getElementById(`node-${id}`);
    if (el) {
      el.className = 'step-progress-box';
      const icon = el.querySelector('.step-state-icon');
      if (icon) icon.innerHTML = '<i data-lucide="circle" style="width: 14px; height: 14px; color: var(--text-dim);"></i>';
    }
  });
  if (window.lucide) window.lucide.createIcons();
}

function updateStepProgress(stepId, state) {
  const el = document.getElementById(`node-${stepId}`);
  if (!el) return;

  if (state === 'running') {
    el.classList.add('running');
    const icon = el.querySelector('.step-state-icon');
    if (icon) icon.innerHTML = '<i data-lucide="loader-2" class="spin" style="width: 14px; height: 14px; color: var(--accent-purple);"></i>';
  } else if (state === 'completed') {
    el.classList.remove('running');
    el.classList.add('completed');
    const icon = el.querySelector('.step-state-icon');
    if (icon) icon.innerHTML = '<i data-lucide="check-circle-2" style="width: 14px; height: 14px; color: var(--accent-emerald);"></i>';
  }
  if (window.lucide) window.lucide.createIcons();
}

function markAllStepsCompleted() {
  STEP_IDS.forEach(id => {
    updateStepProgress(id, 'completed');
  });
  const statusBadge = document.getElementById('pipeline-status-badge');
  if (statusBadge) {
    statusBadge.innerHTML = '<span class="badge-tag badge-green" style="display: flex; align-items: center; gap: 4px;"><i data-lucide="check-circle-2" style="width: 12px; height: 12px;"></i> Itinerary Ready</span>';
  }
  if (window.lucide) window.lucide.createIcons();
}

function clearTerminal() {
  if (terminalContainer) {
    terminalContainer.innerHTML = '';
  }
}

function appendTerminalLog(log) {
  if (!terminalContainer) return;
  const line = document.createElement('div');
  line.className = 'terminal-line';
  const cleanStep = (log.step || log.agent || 'Trip Guide').replace('Agent', '').trim();
  line.innerHTML = `
    <span class="terminal-time">[${log.timestamp || new Date().toLocaleTimeString()}]</span>
    <span class="terminal-agent">${escapeHtml(cleanStep)}:</span>
    <span class="terminal-msg">${escapeHtml(log.message || '')}</span>
  `;
  terminalContainer.appendChild(line);
  terminalContainer.scrollTop = terminalContainer.scrollHeight;
}

// ================= COST CALCULATION & DATA SANITIZATION =================
// Crucial: NEVER display a fabricated $0 cost when valid trip data is available!
function getEstimatedTotalCost(plan) {
  if (!plan) return 0;
  const budget = plan.budget_breakdown || {};
  if (budget.estimated_total_cost && Number(budget.estimated_total_cost) > 0) {
    return Number(budget.estimated_total_cost);
  }
  if (plan.estimated_cost && Number(plan.estimated_cost) > 0) {
    return Number(plan.estimated_cost);
  }

  // Fallback 1: Category allocations sum
  if (budget.categories) {
    let catSum = 0;
    Object.values(budget.categories).forEach(c => {
      catSum += Number(c.allocated_amount || 0);
    });
    if (catSum > 0) return Number(catSum.toFixed(2));
  }

  // Fallback 2: Sum day_total_cost from daily itinerary
  const itinerary = plan.itinerary || [];
  let daysSum = 0;
  itinerary.forEach(d => {
    if (d.day_total_cost && Number(d.day_total_cost) > 0) {
      daysSum += Number(d.day_total_cost);
    } else if (Array.isArray(d.activities)) {
      d.activities.forEach(a => {
        daysSum += Number(a.estimated_cost || 0);
      });
    }
  });
  if (daysSum > 0) return Number(daysSum.toFixed(2));

  // Fallback 3: total_budget from request
  if (budget.total_budget && Number(budget.total_budget) > 0) {
    return Number(budget.total_budget);
  }

  return Number(plan.budget_total || 2500);
}

// ================= ITINERARY DOSSIER RENDERING =================

function renderFullDossier(plan) {
  if (!plan) return;

  dossierSection.style.display = 'flex';
  planningSection.style.display = 'none';

  renderOverview(plan);
  renderItinerary(plan);
  renderBudget(plan);
  renderPacking(plan);
  renderLocalGuide(plan);

  // Switch to Day-by-Day Schedule tab
  const tabItineraryBtn = document.querySelector('.tab-btn[data-tab="tab-itinerary"]');
  if (tabItineraryBtn) tabItineraryBtn.click();

  dossierSection.scrollIntoView({ behavior: 'smooth' });
  if (window.lucide) window.lucide.createIcons();
}

function renderOverview(plan) {
  const budget = plan.budget_breakdown || {};
  const currency = plan.currency || 'USD';
  const totalCost = getEstimatedTotalCost(plan);
  const targetBudget = Number(budget.total_budget || plan.budget_total || plan.total_budget || 2500);
  const travelersCount = Math.max(1, Number(budget.travelers_count || plan.travelers_count) || 1);
  const durationDays = Math.max(1, Number(budget.duration_days || plan.duration_days) || 1);
  
  // Strict mathematical consistency:
  // cost per person = total estimated cost ÷ travelers
  // cost per person per day = cost per person ÷ duration
  const perPersonCost = Number((totalCost / travelersCount).toFixed(2));
  const dailyPerPerson = Number((perPersonCost / durationDays).toFixed(2));
  const variance = Number((targetBudget - totalCost).toFixed(2));
  const shortfall = variance < 0 ? Number(Math.abs(variance).toFixed(2)) : 0;
  const remaining = variance > 0 ? Number(variance.toFixed(2)) : 0;
  const isUnder = variance >= 0;

  document.getElementById('dossier-duration-badge').textContent = `${durationDays} Days Trip`;
  
  const statusBadge = document.getElementById('dossier-status-badge');
  if (statusBadge) {
    statusBadge.textContent = isUnder ? 'Within Budget' : 'Budget Shortfall';
    statusBadge.className = isUnder ? 'badge-tag badge-green' : 'badge-tag badge-amber';
  }

  const providerBadge = document.getElementById('dossier-provider-badge');
  if (providerBadge) {
    if (plan.is_fallback || (plan.provider && plan.provider.includes('Fallback'))) {
      providerBadge.style.display = 'inline-flex';
      providerBadge.className = 'badge-tag badge-amber';
      providerBadge.textContent = '⚡ Offline Engine (Fallback)';
      providerBadge.title = plan.fallback_reason || 'Offline Heuristic Engine';
    } else {
      providerBadge.style.display = 'inline-flex';
      providerBadge.className = 'badge-tag badge-purple';
      providerBadge.textContent = `✨ AI: ${plan.provider || 'Google Gemini'}`;
    }
  }

  document.getElementById('dossier-title').textContent = plan.title || `${plan.destination} Itinerary`;
  document.getElementById('dossier-vibe').textContent = plan.vibe_summary || 'An immersive journey through culture, landmarks, and cuisine.';

  // 4 Key Metrics Display
  const targetValEl = document.getElementById('metric-target-budget-val');
  if (targetValEl) targetValEl.textContent = formatCurrency(targetBudget, currency);

  const estEl = document.getElementById('metric-est-cost');
  if (estEl) estEl.textContent = formatCurrency(totalCost, currency);

  const ppEl = document.getElementById('metric-per-person-cost');
  if (ppEl) ppEl.textContent = formatCurrency(perPersonCost, currency);

  const dailyEl = document.getElementById('metric-daily-cost');
  if (dailyEl) dailyEl.textContent = formatCurrency(dailyPerPerson, currency);

  const travSub = document.getElementById('metric-travelers-sub');
  if (travSub) travSub.textContent = `${travelersCount} traveler${travelersCount > 1 ? 's' : ''} total`;

  const durSub = document.getElementById('metric-duration-sub');
  if (durSub) durSub.textContent = `${durationDays} days duration`;

  // Budget Status & Trade-Offs Banner
  const statusBanner = document.getElementById('budget-status-banner');
  const balanceBadge = document.getElementById('budget-balance-badge');
  const balanceAmount = document.getElementById('budget-balance-amount');
  const tradeoffsBox = document.getElementById('budget-tradeoffs-box');
  const tradeoffsList = document.getElementById('budget-tradeoffs-list');

  if (statusBanner && balanceBadge && balanceAmount) {
    if (shortfall > 0) {
      statusBanner.className = 'budget-status-banner shortfall-mode';
      balanceBadge.className = 'badge-tag badge-amber';
      balanceBadge.textContent = '⚠️ Budget Shortfall';
      balanceAmount.className = 'budget-balance-amount shortfall-text';
      balanceAmount.textContent = `- ${formatCurrency(shortfall, currency)}`;

      if (tradeoffsBox && tradeoffsList) {
        tradeoffsBox.style.display = 'block';
        const tips = budget.saving_tips || [];
        if (tips.length > 0) {
          tradeoffsList.innerHTML = tips.map(t => `<li>${escapeHtml(t)}</li>`).join('');
        } else {
          tradeoffsList.innerHTML = `
            <li>Opt for sleeper class trains or state express buses instead of flights or private cabs.</li>
            <li>Choose verified budget hotels, guest houses, or family rooms instead of 3/4-star properties.</li>
            <li>Mix authentic street food and local thali eateries to cut dining costs in half.</li>
            <li>Consider adjusting duration to ${Math.max(2, durationDays - 1)} days to comfortably bridge the ${formatCurrency(shortfall, currency)} gap.</li>
          `;
        }
      }
    } else {
      statusBanner.className = 'budget-status-banner surplus-mode';
      balanceBadge.className = 'badge-tag badge-green';
      balanceBadge.textContent = '✅ Within Budget';
      balanceAmount.className = 'budget-balance-amount surplus-text';
      balanceAmount.textContent = `+ ${formatCurrency(remaining, currency)} Surplus`;

      if (tradeoffsBox) {
        tradeoffsBox.style.display = 'none';
      }
    }
  }

  const climateText = document.getElementById('metric-climate-text');
  if (climateText) climateText.textContent = plan.climate_guide || 'Favorable seasonal weather conditions.';
}

function renderItinerary(plan) {
  const container = document.getElementById('itinerary-days-container');
  if (!container) return;

  const days = plan.itinerary || [];
  const currency = plan.currency || 'USD';

  if (days.length === 0) {
    container.innerHTML = '<div style="text-align: center; color: var(--text-dim); padding: 40px;">No days generated yet.</div>';
    return;
  }

  let html = '';
  days.forEach(day => {
    // If day_total_cost is missing or 0, compute from activities
    let dayTotal = Number(day.day_total_cost || 0);
    if (dayTotal === 0 && Array.isArray(day.activities)) {
      day.activities.forEach(a => { dayTotal += Number(a.estimated_cost || 0); });
    }

    html += `
      <div class="glass-panel itinerary-day-card">
        <div class="day-header">
          <div>
            <div class="day-label" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <span>${escapeHtml(day.date_label || `Day ${day.day_number}`)}</span>
              ${day.current_city ? `<span class="badge-tag" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: 600;">📍 ${escapeHtml(day.current_city)}</span>` : ''}
              ${day.overnight_stay ? `<span class="badge-tag" style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: 500;">🏨 Stay: ${escapeHtml(day.overnight_stay)}</span>` : ''}
            </div>
            <h3 class="day-theme-title">${escapeHtml(day.theme || 'Day Schedule')}</h3>
            <p class="day-summary-text">${escapeHtml(day.summary || '')}</p>
          </div>
          <div class="day-total-badge">
            <span class="day-total-label">Estimated Day Total</span>
            <div class="day-total-val">
              ${formatCurrency(dayTotal, currency)}
            </div>
          </div>
        </div>

        ${day.travel_leg ? `
          <div class="travel-leg-banner" style="margin: 10px 0 14px 0; padding: 8px 14px; background: rgba(99, 102, 241, 0.12); border-left: 3px solid #6366f1; border-radius: 6px; font-size: 0.85rem; color: #c7d2fe; display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.1rem;">🚗</span>
            <span><strong>Intercity Travel Leg:</strong> ${escapeHtml(day.travel_leg)}</span>
          </div>
        ` : ''}

        <div class="activities-list">
    `;

    (day.activities || []).forEach(act => {
      let badgeStyle = 'background: rgba(99, 102, 241, 0.15); color: #a5b4fc;';
      const cat = (act.category || '').toLowerCase();
      if (cat.includes('din') || cat.includes('culinary') || cat.includes('food')) {
        badgeStyle = 'background: rgba(245, 158, 11, 0.15); color: #fcd34d;';
      } else if (cat.includes('cult') || cat.includes('art') || cat.includes('history')) {
        badgeStyle = 'background: rgba(168, 85, 247, 0.15); color: #d8b4fe;';
      } else if (cat.includes('nature') || cat.includes('park') || cat.includes('beach')) {
        badgeStyle = 'background: rgba(16, 185, 129, 0.15); color: #6ee7b7;';
      }

      html += `
        <div class="activity-card">
          <div class="activity-time-col">
            <span class="activity-slot-name">${escapeHtml(act.time_slot)}</span>
            <span class="activity-time-text">${escapeHtml(act.time || '')}</span>
          </div>
          <div class="activity-content-col">
            <div class="activity-top-row">
              <h4 class="activity-title">${escapeHtml(act.title)}</h4>
              <span class="activity-badge" style="${badgeStyle}">
                ${escapeHtml(act.category || 'Sight')}
              </span>
            </div>
            <p class="activity-desc">${escapeHtml(act.description || '')}</p>
            <div class="activity-meta-row">
              <span>📍 <strong>Location:</strong> ${escapeHtml(act.location || 'Local Area')}</span>
              <span>💰 <strong>Est. Cost:</strong> ${formatCurrency(act.estimated_cost, currency)}</span>
              ${act.tips ? `<span style="color: #fbbf24;">💡 <strong>Tip:</strong> ${escapeHtml(act.tips)}</span>` : ''}
            </div>
          </div>
        </div>
      `;
    });

    if (day.transit_tips) {
      html += `
        <div class="transit-guideline-box">
          🚇 <strong>Transit Guideline:</strong> ${escapeHtml(day.transit_tips)}
        </div>
      `;
    }

    html += `
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function renderBudget(plan) {
  const container = document.getElementById('budget-categories-list');
  const tipsContainer = document.getElementById('budget-saving-tips-list');
  const summaryBox = document.getElementById('budget-summary-card');
  if (!container) return;

  const budget = plan.budget_breakdown || {};
  const categories = budget.categories || {};
  const currency = plan.currency || 'USD';
  const totalCost = getEstimatedTotalCost(plan);
  const targetBudget = Number(budget.total_budget || plan.budget_total || plan.total_budget || 2500);
  const travelersCount = Math.max(1, Number(budget.travelers_count || plan.travelers_count) || 1);
  const durationDays = Math.max(1, Number(budget.duration_days || plan.duration_days) || 1);
  
  // Strict mathematical consistency:
  const perPersonCost = Number((totalCost / travelersCount).toFixed(2));
  const dailyPerPerson = Number((perPersonCost / durationDays).toFixed(2));
  const variance = Number((targetBudget - totalCost).toFixed(2));
  const shortfall = variance < 0 ? Number(Math.abs(variance).toFixed(2)) : 0;
  const remaining = variance > 0 ? Number(variance.toFixed(2)) : 0;

  // Render 5-figure group budget overview card
  if (summaryBox) {
    summaryBox.innerHTML = `
      <div class="budget-summary-item">
        <span class="budget-summary-label">1. Total Group Budget</span>
        <span class="budget-summary-val" style="color: var(--accent-amber);">${formatCurrency(targetBudget, currency)}</span>
        <span class="budget-summary-sub">Combined group ceiling</span>
      </div>
      <div class="budget-summary-item">
        <span class="budget-summary-label">2. Estimated Total Cost</span>
        <span class="budget-summary-val" style="color: var(--accent-emerald);">${formatCurrency(totalCost, currency)}</span>
        <span class="budget-summary-sub">All itemized categories</span>
      </div>
      <div class="budget-summary-item">
        <span class="budget-summary-label">3. Total Cost / Person</span>
        <span class="budget-summary-val" style="color: var(--accent-sky);">${formatCurrency(perPersonCost, currency)}</span>
        <span class="budget-summary-sub">Across ${travelersCount} travelers</span>
      </div>
      <div class="budget-summary-item">
        <span class="budget-summary-label">4. Cost / Person / Day</span>
        <span class="budget-summary-val" style="color: var(--accent-indigo);">${formatCurrency(dailyPerPerson, currency)}</span>
        <span class="budget-summary-sub">Over ${durationDays} days</span>
      </div>
      <div class="budget-summary-item">
        <span class="budget-summary-label">5. Budget Balance</span>
        <span class="budget-summary-val" style="color: ${shortfall > 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
          ${shortfall > 0 ? `Shortfall: -${formatCurrency(shortfall, currency)}` : `Surplus: +${formatCurrency(remaining, currency)}`}
        </span>
        <span class="budget-summary-sub">${shortfall > 0 ? 'Exceeds budget' : 'Comfortably funded'}</span>
      </div>
    `;
  }

  let html = '';
  Object.keys(categories).forEach(catKey => {
    const cat = categories[catKey];
    html += `
      <div class="budget-cat-item">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <strong style="font-size: 0.95rem;">${escapeHtml(cat.name)}</strong>
          <span style="font-weight: 700; color: var(--accent-purple);">
            ${formatCurrency(cat.allocated_amount, currency)} (${cat.percentage || 0}%)
          </span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${cat.percentage || 15}%;"></div>
        </div>
        <div style="font-size: 0.76rem; color: var(--text-muted);">${escapeHtml(cat.description || '')}</div>
      </div>
    `;
  });

  html += `
    <div class="budget-disclaimer-note" style="grid-column: 1 / -1; margin-top: 12px; padding: 10px 14px; background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px; font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 8px;">
      <span>ℹ️</span>
      <span><strong>Pricing Note:</strong> Intercity transport and hotel tariffs are realistic benchmark estimates. Live airfare and room availability depend on exact travel dates and booking lead time.</span>
    </div>
  `;

  container.innerHTML = html;

  if (tipsContainer) {
    const tips = budget.saving_tips || [];
    tipsContainer.innerHTML = tips.map(tip => `<li>${escapeHtml(tip)}</li>`).join('');
  }
}

function renderPacking(plan) {
  const container = document.getElementById('packing-categories-container');
  const counter = document.getElementById('packing-counter');
  const progressBar = document.getElementById('packing-progress-bar');
  if (!container) return;

  const checklist = plan.packing_checklist || [];
  let totalItems = 0;
  let checkedItems = 0;
  let html = '';

  checklist.forEach((group, groupIdx) => {
    html += `
      <div class="packing-category-box">
        <h4 class="packing-category-title">${escapeHtml(group.category)}</h4>
        <div class="packing-items-col">
    `;

    (group.items || []).forEach((item, itemIdx) => {
      totalItems++;
      const itemKey = `${groupIdx}_${itemIdx}`;
      const isChecked = Boolean(packingCheckedState[itemKey]);
      if (isChecked) checkedItems++;

      html += `
        <div class="packing-item-row ${isChecked ? 'checked' : ''}" onclick="togglePackingItem('${itemKey}')">
          <span>${isChecked ? '☑️' : '◻️'}</span>
          <span>${escapeHtml(item)}</span>
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;
  });

  container.innerHTML = html;

  const percent = totalItems > 0 ? Math.round((checkedItems / totalItems) * 100) : 0;
  if (counter) counter.textContent = `${checkedItems} / ${totalItems} (${percent}%)`;
  if (progressBar) progressBar.style.width = `${percent}%`;
}

window.togglePackingItem = function(itemKey) {
  packingCheckedState[itemKey] = !packingCheckedState[itemKey];
  if (currentPlan) {
    renderPacking(currentPlan);
  }
};

function renderLocalGuide(plan) {
  const customsContainer = document.getElementById('cultural-customs-list');
  const emergencyContainer = document.getElementById('emergency-contacts-grid');

  if (customsContainer) {
    const customs = plan.local_customs || [];
    customsContainer.innerHTML = customs.map((c, i) => `
      <div class="custom-item-card">
        <span class="custom-num">${i + 1}.</span>
        <span>${escapeHtml(c)}</span>
      </div>
    `).join('');
  }

  if (emergencyContainer) {
    let contacts = plan.emergency_contacts;
    if (!contacts || (typeof contacts === 'object' && Object.keys(contacts).length === 0)) {
      const isIndia = (plan.destination && /india/i.test(plan.destination)) || plan.currency === 'INR';
      contacts = isIndia ? {
        "police": "100 / 112",
        "ambulance": "102 / 108",
        "tourist_helpline": "1363",
        "national_emergency": "112"
      } : {
        "police": "112 / 911",
        "ambulance": "112 / 911",
        "general_emergency": "112",
        "tourist_helpline": "112"
      };
    }

    let html = '';
    Object.keys(contacts).forEach(svc => {
      html += `
        <div class="emergency-box">
          <div class="emergency-label">${escapeHtml(svc.replace(/_/g, ' '))}</div>
          <div class="emergency-number">${escapeHtml(String(contacts[svc]))}</div>
        </div>
      `;
    });
    emergencyContainer.innerHTML = html;
  }
}

// ============================================================================
// USER AUTHENTICATION CONTROLLER
// ============================================================================

async function initAuth() {
  if (!authToken) {
    updateAuthUI();
    return;
  }

  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: getAuthHeaders(),
      credentials: 'include',
    });

    if (res.ok) {
      currentUser = await res.json();
    } else if (res.status === 401 || res.status === 403) {
      // Session expired or token invalid
      authToken = null;
      currentUser = null;
      localStorage.removeItem('wanderai_auth_token');
    } else {
      console.warn('Backend returned non-auth status when verifying session:', res.status);
    }
  } catch (err) {
    console.warn('Could not verify existing session:', err);
  }

  updateAuthUI();
}

function updateAuthUI() {
  const navLoggedOut = document.getElementById('nav-auth-logged-out');
  const navLoggedIn = document.getElementById('nav-auth-logged-in');
  const mobileLoggedOut = document.getElementById('mobile-auth-logged-out');
  const mobileLoggedIn = document.getElementById('mobile-auth-logged-in');
  const userDisplayName = document.getElementById('user-display-name');
  const mobileUserDisplayName = document.getElementById('mobile-user-display-name');
  const navSavedTripsText = document.getElementById('nav-saved-trips-text');
  const mobileSavedTripsText = document.getElementById('mobile-saved-trips-text');
  const savedTripsTitle = document.getElementById('saved-trips-modal-title');
  const userBanner = document.getElementById('saved-trips-user-banner');
  const userBannerText = document.getElementById('saved-trips-user-text');

  if (currentUser) {
    if (navLoggedOut) navLoggedOut.style.display = 'none';
    if (navLoggedIn) navLoggedIn.style.display = 'flex';
    if (mobileLoggedOut) mobileLoggedOut.style.display = 'none';
    if (mobileLoggedIn) mobileLoggedIn.style.display = 'flex';

    const firstName = currentUser.full_name ? currentUser.full_name.split(' ')[0] : 'Traveler';
    if (userDisplayName) userDisplayName.textContent = firstName;
    if (mobileUserDisplayName) mobileUserDisplayName.textContent = currentUser.full_name;

    if (navSavedTripsText) navSavedTripsText.textContent = 'My Trips';
    if (mobileSavedTripsText) mobileSavedTripsText.textContent = 'My Trips';
    if (savedTripsTitle) savedTripsTitle.textContent = 'My Saved Itineraries';

    if (userBanner && userBannerText) {
      userBanner.style.display = 'flex';
      userBannerText.innerHTML = `👤 Logged in as <strong>${escapeHtml(currentUser.full_name)}</strong> (${escapeHtml(currentUser.email)})`;
    }
  } else {
    if (navLoggedOut) navLoggedOut.style.display = 'flex';
    if (navLoggedIn) navLoggedIn.style.display = 'none';
    if (mobileLoggedOut) mobileLoggedOut.style.display = 'flex';
    if (mobileLoggedIn) mobileLoggedIn.style.display = 'none';

    if (navSavedTripsText) navSavedTripsText.textContent = 'Saved Trips';
    if (mobileSavedTripsText) mobileSavedTripsText.textContent = 'Saved Trips';
    if (savedTripsTitle) savedTripsTitle.textContent = 'Saved Itineraries';

    if (userBanner && userBannerText) {
      userBanner.style.display = 'flex';
      userBannerText.innerHTML = `ℹ️ You are in Guest Mode. <button type="button" class="btn-text-link" onclick="openLoginModal()" style="font-size: 0.8rem;">Log in</button> or <button type="button" class="btn-text-link" onclick="openRegisterModal()" style="font-size: 0.8rem;">create an account</button> to link your trips.`;
    }
  }

  if (window.lucide) window.lucide.createIcons();
}

function initAuthModals() {
  const modalLogin = document.getElementById('modal-auth-login');
  const modalRegister = document.getElementById('modal-auth-register');
  const btnOpenLogin = document.getElementById('btn-open-login');
  const btnOpenRegister = document.getElementById('btn-open-register');
  const btnMobileLogin = document.getElementById('btn-mobile-login');
  const btnMobileRegister = document.getElementById('btn-mobile-register');
  const btnCloseLogin = document.getElementById('close-modal-login');
  const btnCloseRegister = document.getElementById('close-modal-register');
  const switchToRegister = document.getElementById('switch-to-register');
  const switchToLogin = document.getElementById('switch-to-login');
  const btnLogout = document.getElementById('btn-logout');
  const btnMobileLogout = document.getElementById('btn-mobile-logout');
  const formLogin = document.getElementById('form-auth-login');
  const formRegister = document.getElementById('form-auth-register');

  window.openLoginModal = function() {
    if (modalRegister) modalRegister.classList.remove('active');
    if (modalSavedTrips) modalSavedTrips.classList.remove('active');
    clearAuthAlerts();
    if (modalLogin) modalLogin.classList.add('active');
    const emailInput = document.getElementById('login-email');
    if (emailInput) emailInput.focus();
    if (window.lucide) window.lucide.createIcons();
  };

  window.openRegisterModal = function() {
    if (modalLogin) modalLogin.classList.remove('active');
    if (modalSavedTrips) modalSavedTrips.classList.remove('active');
    clearAuthAlerts();
    if (modalRegister) modalRegister.classList.add('active');
    const nameInput = document.getElementById('register-name');
    if (nameInput) nameInput.focus();
    if (window.lucide) window.lucide.createIcons();
  };

  if (btnOpenLogin) btnOpenLogin.addEventListener('click', window.openLoginModal);
  if (btnMobileLogin) btnMobileLogin.addEventListener('click', () => {
    if (mobileNavDrawer) mobileNavDrawer.classList.remove('active');
    window.openLoginModal();
  });

  if (btnOpenRegister) btnOpenRegister.addEventListener('click', window.openRegisterModal);
  if (btnMobileRegister) btnMobileRegister.addEventListener('click', () => {
    if (mobileNavDrawer) mobileNavDrawer.classList.remove('active');
    window.openRegisterModal();
  });

  if (btnCloseLogin && modalLogin) {
    btnCloseLogin.addEventListener('click', () => modalLogin.classList.remove('active'));
    modalLogin.addEventListener('click', (e) => {
      if (e.target === modalLogin) modalLogin.classList.remove('active');
    });
  }

  if (btnCloseRegister && modalRegister) {
    btnCloseRegister.addEventListener('click', () => modalRegister.classList.remove('active'));
    modalRegister.addEventListener('click', (e) => {
      if (e.target === modalRegister) modalRegister.classList.remove('active');
    });
  }

  if (switchToRegister) {
    switchToRegister.addEventListener('click', (e) => {
      e.preventDefault();
      window.openRegisterModal();
    });
  }

  if (switchToLogin) {
    switchToLogin.addEventListener('click', (e) => {
      e.preventDefault();
      window.openLoginModal();
    });
  }

  // Logout Handlers
  async function handleLogout() {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
      });
    } catch (e) {
      console.warn('Logout request failed:', e);
    }
    authToken = null;
    currentUser = null;
    localStorage.removeItem('wanderai_auth_token');
    updateAuthUI();
    if (modalSavedTrips && modalSavedTrips.classList.contains('active')) {
      loadSavedTrips();
    }
  }

  if (btnLogout) btnLogout.addEventListener('click', handleLogout);
  if (btnMobileLogout) btnMobileLogout.addEventListener('click', () => {
    if (mobileNavDrawer) mobileNavDrawer.classList.remove('active');
    handleLogout();
  });

  // Login Form Submission
  let isLoginSubmitting = false;
  if (formLogin) {
    formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (isLoginSubmitting) return;
      clearAuthAlerts();

      const emailEl = document.getElementById('login-email');
      const passEl = document.getElementById('login-password');
      const emailErr = document.getElementById('login-email-error');
      const passErr = document.getElementById('login-password-error');
      const alertErr = document.getElementById('login-alert-error');
      const btnSubmit = document.getElementById('btn-submit-login');

      const email = emailEl ? emailEl.value.trim() : '';
      const password = passEl ? passEl.value : '';

      let hasError = false;
      if (!email || !email.includes('@')) {
        if (emailErr) emailErr.textContent = 'Please enter a valid email address.';
        hasError = true;
      }
      if (!password) {
        if (passErr) passErr.textContent = 'Please enter your password.';
        hasError = true;
      }
      if (hasError) return;

      isLoginSubmitting = true;
      if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="btn-text">Logging in...</span>';
      }

      try {
        const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email, password }),
        });

        let data = null;
        try {
          data = await res.json();
        } catch (_) {
          data = null;
        }

        if (!res.ok) {
          throw new Error(formatApiError(data, 'Login failed. Please check your credentials.'));
        }

        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('wanderai_auth_token', authToken);

        updateAuthUI();
        if (modalLogin) modalLogin.classList.remove('active');
        formLogin.reset();

        // Refresh saved trips
        if (modalSavedTrips && modalSavedTrips.classList.contains('active')) {
          loadSavedTrips();
        }
      } catch (err) {
        if (alertErr) {
          alertErr.textContent = err.message || 'Login failed.';
          alertErr.style.display = 'block';
        }
      } finally {
        isLoginSubmitting = false;
        if (btnSubmit) {
          btnSubmit.disabled = false;
          btnSubmit.innerHTML = '<span class="btn-text">Log In</span>';
        }
      }
    });
  }

  // Register Form Submission
  let isRegisterSubmitting = false;
  if (formRegister) {
    formRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (isRegisterSubmitting) return;
      clearAuthAlerts();

      const nameEl = document.getElementById('register-name');
      const emailEl = document.getElementById('register-email');
      const passEl = document.getElementById('register-password');
      const confEl = document.getElementById('register-confirm-password');

      const nameErr = document.getElementById('register-name-error');
      const emailErr = document.getElementById('register-email-error');
      const passErr = document.getElementById('register-password-error');
      const confErr = document.getElementById('register-confirm-password-error');
      const alertErr = document.getElementById('register-alert-error');
      const btnSubmit = document.getElementById('btn-submit-register');

      const full_name = nameEl ? nameEl.value.trim() : '';
      const email = emailEl ? emailEl.value.trim() : '';
      const password = passEl ? passEl.value : '';
      const confirm_password = confEl ? confEl.value : '';

      let hasError = false;
      if (!full_name || full_name.length < 2) {
        if (nameErr) nameErr.textContent = 'Name must be at least 2 characters long.';
        hasError = true;
      }
      if (!email || !email.includes('@')) {
        if (emailErr) emailErr.textContent = 'Please enter a valid email address.';
        hasError = true;
      }
      if (!password || password.length < 8) {
        if (passErr) passErr.textContent = 'Password must be at least 8 characters long.';
        hasError = true;
      }
      if (password !== confirm_password) {
        if (confErr) confErr.textContent = 'Passwords do not match.';
        hasError = true;
      }
      if (hasError) return;

      isRegisterSubmitting = true;
      if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="btn-text">Creating account...</span>';
      }

      try {
        const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ full_name, email, password }),
        });

        let data = null;
        try {
          data = await res.json();
        } catch (_) {
          data = null;
        }

        if (!res.ok) {
          throw new Error(formatApiError(data, 'Registration failed.'));
        }

        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('wanderai_auth_token', authToken);

        updateAuthUI();
        if (modalRegister) modalRegister.classList.remove('active');
        formRegister.reset();

        // Refresh saved trips
        if (modalSavedTrips && modalSavedTrips.classList.contains('active')) {
          loadSavedTrips();
        }
      } catch (err) {
        if (alertErr) {
          alertErr.textContent = err.message || 'Registration failed.';
          alertErr.style.display = 'block';
        }
      } finally {
        isRegisterSubmitting = false;
        if (btnSubmit) {
          btnSubmit.disabled = false;
          btnSubmit.innerHTML = '<span class="btn-text">Create Account</span>';
        }
      }
    });
  }
}

function clearAuthAlerts() {
  ['login-alert-error', 'login-alert-success', 'register-alert-error', 'register-alert-success'].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.style.display = 'none'; el.textContent = ''; }
  });
  ['login-email-error', 'login-password-error', 'register-name-error', 'register-email-error', 'register-password-error', 'register-confirm-password-error'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = '';
  });
}

// ============================================================================
// SAVED TRIPS CONTROLLER (COMPLETE ITINERARY PERSISTENCE & USER ISOLATION)
// ============================================================================

// Load trips saved in SQLite database
async function loadSavedTrips() {
  if (!savedTripsList) return;
  savedTripsList.innerHTML = '<div class="empty-saved-message">Loading saved itineraries...</div>';

  try {
    const endpoint = currentUser ? `${API_BASE_URL}/api/auth/my-trips` : `${API_BASE_URL}/api/trips`;
    const res = await fetch(endpoint, {
      headers: getAuthHeaders(),
      credentials: 'include',
    });

    if (!res.ok) throw new Error('Failed to retrieve trips');
    const data = await res.json();
    const trips = data.trips || [];

    if (trips.length === 0) {
      savedTripsList.innerHTML = `
        <div class="empty-saved-message">
          <i data-lucide="compass" style="width: 32px; height: 32px; margin-bottom: 8px; color: var(--accent-indigo); display: block; margin: 0 auto 8px;"></i>
          ${currentUser ? 'You have no saved trips yet. Plan your first adventure above!' : 'No saved trips found. Plan your first adventure above or create an account!'}
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    let html = '';
    trips.forEach(t => {
      const currency = t.currency || 'USD';
      html += `
        <div class="saved-trip-item">
          <div class="saved-trip-info">
            <h4>${escapeHtml(t.title || t.destination)}</h4>
            <div class="saved-trip-meta">
              <span>📍 ${escapeHtml(t.destination)}</span>
              <span>🗓️ ${t.duration_days} Days</span>
              <span>💰 ${formatCurrency(t.estimated_cost || t.total_budget, currency)}</span>
            </div>
          </div>
          <div class="saved-trip-actions">
            <button type="button" class="btn btn-sm btn-primary" onclick="loadSavedTripById('${t.id}')">View</button>
            <button type="button" class="btn btn-sm btn-outline" style="color: var(--accent-rose); border-color: rgba(244, 63, 94, 0.3);" onclick="deleteSavedTripById('${t.id}')">Delete</button>
          </div>
        </div>
      `;
    });

    savedTripsList.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    savedTripsList.innerHTML = `<div class="empty-saved-message" style="color: var(--accent-rose);">Could not load trips: ${err.message}</div>`;
  }
}

window.loadSavedTripById = async function(tripId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/trips/${tripId}`, {
      headers: getAuthHeaders(),
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Trip not found or unauthorized');
    const trip = await res.json();
    currentPlan = (trip && trip.full_data) ? trip.full_data : trip;
    if (modalSavedTrips) modalSavedTrips.classList.remove('active');
    renderFullDossier(currentPlan);
  } catch (err) {
    alert('Error loading trip: ' + err.message);
  }
};

window.deleteSavedTripById = async function(tripId) {
  if (!confirm('Are you sure you want to delete this itinerary?')) return;
  try {
    const res = await fetch(`${API_BASE_URL}/api/trips/${tripId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Delete failed or unauthorized');
    loadSavedTrips();
  } catch (err) {
    alert('Error deleting trip: ' + err.message);
  }
};

// HTML Escaping Utility
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ==========================================================================
// AI TRAVEL CHATBOT CONTROLLER
// ==========================================================================
let chatHistory = [];
let isChatOpen = false;
let isChatSending = false;

const btnChatToggle = document.getElementById('btn-chat-toggle');
const chatPanel = document.getElementById('chat-panel');
const btnChatMinimize = document.getElementById('btn-chat-minimize');
const btnChatClear = document.getElementById('btn-chat-clear');
const chatMessages = document.getElementById('chat-messages');
const chatTypingIndicator = document.getElementById('chat-typing-indicator');
const chatInputForm = document.getElementById('chat-input-form');
const chatInput = document.getElementById('chat-input');
const chatContextBanner = document.getElementById('chat-context-banner');
const chatContextText = document.getElementById('chat-context-text');

function initChatWidget() {
  if (!btnChatToggle || !chatPanel) return;

  // Toggle chat window open/closed
  btnChatToggle.addEventListener('click', () => {
    toggleChat();
  });

  // Minimize chat
  if (btnChatMinimize) {
    btnChatMinimize.addEventListener('click', () => {
      toggleChat(false);
    });
  }

  // Clear chat history
  if (btnChatClear) {
    btnChatClear.addEventListener('click', () => {
      clearChat();
    });
  }

  // Submit message via form
  if (chatInputForm) {
    chatInputForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleChatSubmit();
    });
  }

  // Handle Enter key inside input
  if (chatInput) {
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleChatSubmit();
      }
    });
  }

  // Quick Prompt Chips
  initQuickPromptChips();

  // Close chat on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isChatOpen) {
      toggleChat(false);
    }
  });
}

function toggleChat(forceState = null) {
  if (!chatPanel || !btnChatToggle) return;
  
  isChatOpen = (forceState !== null) ? forceState : !isChatOpen;

  const chatIcon = btnChatToggle.querySelector('.launcher-chat-icon');
  const closeIcon = btnChatToggle.querySelector('.launcher-close-icon');

  if (isChatOpen) {
    chatPanel.style.display = 'flex';
    btnChatToggle.classList.add('active');
    if (chatIcon) chatIcon.style.display = 'none';
    if (closeIcon) closeIcon.style.display = 'inline-block';
    updateChatContextBanner();
    scrollChatToBottom();
    if (chatInput) setTimeout(() => chatInput.focus(), 150);
  } else {
    chatPanel.style.display = 'none';
    btnChatToggle.classList.remove('active');
    if (chatIcon) chatIcon.style.display = 'inline-block';
    if (closeIcon) closeIcon.style.display = 'none';
  }

  if (window.lucide) window.lucide.createIcons();
}

function updateChatContextBanner() {
  if (!chatContextBanner || !chatContextText) return;

  const ctx = getActiveTripContext();
  if (ctx && ctx.destination) {
    chatContextText.textContent = `Context: ${ctx.destination} (${ctx.duration_days || 5} Days)`;
    chatContextBanner.style.display = 'flex';
  } else {
    chatContextBanner.style.display = 'none';
  }
}

function getActiveTripContext() {
  if (currentPlan) {
    return {
      destination: currentPlan.destination,
      duration_days: currentPlan.duration_days,
      currency: currentPlan.currency,
      travelers_count: currentPlan.travelers_count || (currentPlan.budget_breakdown && currentPlan.budget_breakdown.travelers_count) || 2,
      traveler_type: currentPlan.traveler_type,
      budget_total: currentPlan.budget_total || (currentPlan.budget_breakdown && currentPlan.budget_breakdown.total_budget),
      notes: currentPlan.notes || '',
      itinerary: currentPlan.itinerary
    };
  }

  const destInput = document.getElementById('input-destination');
  if (destInput && destInput.value.trim()) {
    const durationInput = document.getElementById('input-duration');
    const currencySelect = document.getElementById('select-currency');
    const travelerSelect = document.getElementById('select-traveler-type');
    const budgetInput = document.getElementById('input-budget');
    return {
      destination: destInput.value.trim(),
      duration_days: durationInput ? Number(durationInput.value) : 5,
      currency: currencySelect ? currencySelect.value : 'USD',
      travelers_count: currentTravelersCount || 2,
      traveler_type: travelerSelect ? travelerSelect.value : 'Couple',
      budget_total: budgetInput ? Number(budgetInput.value) : 2500,
      notes: document.getElementById('input-notes') ? document.getElementById('input-notes').value.trim() : ''
    };
  }

  return null;
}

function initQuickPromptChips() {
  const chips = document.querySelectorAll('.chat-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const msg = chip.getAttribute('data-msg');
      if (msg && !isChatSending) {
        if (chatInput) chatInput.value = msg;
        handleChatSubmit();
      }
    });
  });
}

async function handleChatSubmit() {
  if (!chatInput || isChatSending) return;
  const userText = chatInput.value.trim();
  if (!userText) return;

  // Clear input
  chatInput.value = '';

  // Render user bubble
  appendChatBubble('user', userText);
  chatHistory.push({ role: 'user', content: userText });

  // Hide quick chips once first question is asked
  const quickChips = document.getElementById('chat-quick-chips');
  if (quickChips) quickChips.style.display = 'none';

  // Show typing indicator
  setChatTyping(true);
  isChatSending = true;

  try {
    const payload = {
      message: userText,
      history: chatHistory.slice(-8), // send recent conversation turns
      trip_context: getActiveTripContext(),
      provider: localStorage.getItem('wanderai_provider') || 'auto',
      api_key: localStorage.getItem('wanderai_api_key') || null
    };

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const data = await response.json();
    const assistantReply = data.reply || "I'm ready to help with any travel ideas or questions!";

    setChatTyping(false);
    appendChatBubble('assistant', assistantReply);
    chatHistory.push({ role: 'assistant', content: assistantReply });
  } catch (err) {
    console.warn('Chat request failed:', err);
    setChatTyping(false);
    appendChatBubble('assistant', "I'm having a little trouble connecting right now. Please ensure the backend server is running, or feel free to try again!");
  } finally {
    isChatSending = false;
    if (chatInput) chatInput.focus();
  }
}

function appendChatBubble(role, content) {
  if (!chatMessages) return;

  const bubbleEl = document.createElement('div');
  bubbleEl.className = `chat-bubble chat-bubble-${role}`;

  if (role === 'assistant') {
    const formattedHtml = formatChatMarkdown(content);
    bubbleEl.innerHTML = `
      <div class="bubble-avatar">
        <i data-lucide="bot"></i>
      </div>
      <div class="bubble-content">
        ${formattedHtml}
      </div>
    `;
  } else {
    bubbleEl.innerHTML = `
      <div class="bubble-content">
        <p>${escapeHtml(content)}</p>
      </div>
    `;
  }

  chatMessages.appendChild(bubbleEl);
  scrollChatToBottom();
  if (window.lucide) window.lucide.createIcons();
}

function setChatTyping(isTyping) {
  if (!chatTypingIndicator) return;
  chatTypingIndicator.style.display = isTyping ? 'flex' : 'none';
  if (isTyping) {
    scrollChatToBottom();
    if (window.lucide) window.lucide.createIcons();
  }
}

function scrollChatToBottom() {
  if (!chatMessages) return;
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatChatMarkdown(text) {
  if (!text) return '';
  let html = escapeHtml(text);

  // Bold text: **text**
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Italic text: *text*
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Process lines into paragraphs and list items
  const lines = html.split('\n');
  let inList = false;
  let formatted = '';

  lines.forEach(line => {
    const trimmed = line.trim();
    if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
      if (!inList) {
        formatted += '<ul>';
        inList = true;
      }
      formatted += `<li>${trimmed.substring(2)}</li>`;
    } else if (/^\d+\.\s/.test(trimmed)) {
      if (!inList) {
        formatted += '<ol>';
        inList = true;
      }
      formatted += `<li>${trimmed.replace(/^\d+\.\s/, '')}</li>`;
    } else {
      if (inList) {
        formatted += '</ul>';
        inList = false;
      }
      if (trimmed) {
        formatted += `<p>${trimmed}</p>`;
      }
    }
  });

  if (inList) formatted += '</ul>';
  return formatted || `<p>${html}</p>`;
}

function clearChat() {
  chatHistory = [];
  if (!chatMessages) return;

  chatMessages.innerHTML = `
    <div class="chat-bubble chat-bubble-assistant">
      <div class="bubble-avatar">
        <i data-lucide="bot"></i>
      </div>
      <div class="bubble-content">
        <p>Conversation refreshed! 👋 How can I help you explore, plan, or budget today?</p>
      </div>
    </div>
    <div class="chat-quick-chips" id="chat-quick-chips">
      <button type="button" class="chat-chip" data-msg="What are the top hidden culinary gems?">🍜 Top culinary gems</button>
      <button type="button" class="chat-chip" data-msg="How can I save money on daily transit and food?">💰 Money-saving tips</button>
      <button type="button" class="chat-chip" data-msg="What should I pack for this trip?">🎒 What should I pack?</button>
      <button type="button" class="chat-chip" data-msg="Suggest a relaxed afternoon activity.">🌿 Relaxed afternoon ideas</button>
    </div>
  `;

  initQuickPromptChips();
  updateChatContextBanner();
  scrollChatToBottom();
  if (window.lucide) window.lucide.createIcons();
}

