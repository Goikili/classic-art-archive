// Classic Art Archive - Interactive JS Application (v2.1 Social Hub & Live Stats)

let allArtworks = [];

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  initArtworksData();
  setupFilterListeners();
  setupSearchListener();
  setupModalListeners();
  setupStatsModal();
  setupNewsletterForm();
  setupContactForm();
  setupMobileMenu();
});

// Fetch artworks JSON from API for instant modal and client actions
async function initArtworksData() {
  try {
    const res = await fetch('/api/artworks');
    if (res.ok) {
      allArtworks = await res.json();
    }
  } catch (err) {
    console.error('Error fetching artworks cache:', err);
  }
}

// Universal High-Reliability Download Function (Blob + Direct Anchor fallback)
async function downloadArtworkFile(slug, defaultFilename) {
  const filename = defaultFilename || `${slug}_ClassicArtArchive_HD.jpg`;
  showToast('Preparing Ultra HD download...');
  
  try {
    const res = await fetch(`/download/${slug}`);
    if (!res.ok) throw new Error('Download request failed');
    
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    setTimeout(() => {
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);
      showToast('Download started!');
    }, 200);
  } catch (err) {
    console.warn('Blob download fallback to direct navigation:', err);
    // Fallback: direct window navigation
    window.location.href = `/download/${slug}`;
  }
}

// Setup Mobile Menu Drawer
function setupMobileMenu() {
  const toggleBtn = document.getElementById('mobile-menu-btn');
  const menu = document.getElementById('mobile-menu');
  if (toggleBtn && menu) {
    toggleBtn.addEventListener('click', () => {
      menu.classList.toggle('hidden');
    });

    // Close mobile menu when a navigation link is clicked
    const links = menu.querySelectorAll('a');
    links.forEach(link => {
      link.addEventListener('click', () => {
        menu.classList.add('hidden');
      });
    });
  }
}

// Setup Period Filters
function setupFilterListeners() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const period = btn.getAttribute('data-period');
      applyFilters(period, getSearchTerm());
    });
  });
}

// Setup Search Input
function setupSearchListener() {
  const searchInput = document.getElementById('art-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase().trim();
      const activePeriodBtn = document.querySelector('.filter-btn.active');
      const period = activePeriodBtn ? activePeriodBtn.getAttribute('data-period') : 'all';
      applyFilters(period, term);
    });
  }
}

function getSearchTerm() {
  const searchInput = document.getElementById('art-search');
  return searchInput ? searchInput.value.toLowerCase().trim() : '';
}

// Apply Filter & Search combined
function applyFilters(period, term) {
  const cards = document.querySelectorAll('.artwork-card');
  let visibleCount = 0;

  cards.forEach(card => {
    const cardPeriod = card.getAttribute('data-period') || '';
    const cardTitle = (card.getAttribute('data-title') || '').toLowerCase();
    const cardArtist = (card.getAttribute('data-artist') || '').toLowerCase();

    const matchesPeriod = period === 'all' || cardPeriod.toLowerCase() === period.toLowerCase();
    const matchesSearch = !term || cardTitle.includes(term) || cardArtist.includes(term) || cardPeriod.toLowerCase().includes(term);

    if (matchesPeriod && matchesSearch) {
      card.style.display = 'flex';
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });

  const emptyState = document.getElementById('empty-state');
  if (emptyState) {
    if (visibleCount === 0) {
      emptyState.classList.remove('hidden');
    } else {
      emptyState.classList.add('hidden');
    }
  }
}

// Modal management
function setupModalListeners() {
  const modal = document.getElementById('artwork-modal');
  const closeBtn = document.getElementById('close-modal-btn');
  const backdrop = document.getElementById('modal-overlay');

  if (closeBtn) {
    closeBtn.addEventListener('click', closeModal);
  }

  if (backdrop) {
    backdrop.addEventListener('click', closeModal);
  }

  // Keyboard Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal();
      closeStatsModal();
    }
  });
}

function openArtworkModal(slug) {
  const artwork = allArtworks.find(a => a.slug === slug);
  if (!artwork) return;

  const modal = document.getElementById('artwork-modal');
  if (!modal) return;

  // Populate modal data
  const modalImg = document.getElementById('modal-img');
  const modalTitle = document.getElementById('modal-title');
  const modalOriginalTitle = document.getElementById('modal-original-title');
  const modalArtist = document.getElementById('modal-artist');
  const modalYear = document.getElementById('modal-year');
  const modalPeriod = document.getElementById('modal-period');
  const modalMedium = document.getElementById('modal-medium');
  const modalDimensions = document.getElementById('modal-dimensions');
  const modalLocation = document.getElementById('modal-location');
  const modalDescription = document.getElementById('modal-description');
  const modalAnalysis = document.getElementById('modal-analysis');
  const modalFullLink = document.getElementById('modal-full-link');
  const modalDownloadBtn = document.getElementById('modal-download-btn');

  if (modalImg) {
    modalImg.src = artwork.thumbnail_url || artwork.image_url;
    modalImg.alt = artwork.title;
  }
  if (modalTitle) modalTitle.textContent = artwork.title;
  if (modalOriginalTitle) modalOriginalTitle.textContent = artwork.original_title ? `(${artwork.original_title})` : '';
  if (modalArtist) modalArtist.textContent = artwork.artist;
  if (modalYear) modalYear.textContent = artwork.year;
  if (modalPeriod) modalPeriod.textContent = artwork.period;
  if (modalMedium) modalMedium.textContent = artwork.medium;
  if (modalDimensions) modalDimensions.textContent = artwork.dimensions;
  if (modalLocation) modalLocation.textContent = artwork.location;
  if (modalDescription) modalDescription.textContent = artwork.description;
  if (modalAnalysis) modalAnalysis.textContent = artwork.analysis;

  if (modalFullLink) {
    modalFullLink.href = `/artwork/${artwork.slug}`;
  }

  if (modalDownloadBtn) {
    modalDownloadBtn.href = `/download/${artwork.slug}`;
    modalDownloadBtn.setAttribute('download', artwork.download_filename || `${artwork.slug}.jpg`);
    modalDownloadBtn.onclick = (e) => {
      e.preventDefault();
      downloadArtworkFile(artwork.slug, artwork.download_filename);
    };
  }

  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const modal = document.getElementById('artwork-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Stats Modal Management
function openStatsModal() {
  const modal = document.getElementById('stats-modal');
  if (modal) {
    modal.classList.remove('opacity-0', 'pointer-events-none');
    modal.classList.add('opacity-100');
    document.body.style.overflow = 'hidden';
  }
}

function closeStatsModal() {
  const modal = document.getElementById('stats-modal');
  if (modal) {
    modal.classList.add('opacity-0', 'pointer-events-none');
    modal.classList.remove('opacity-100');
    document.body.style.overflow = '';
  }
}

function setupStatsModal() {
  const form = document.getElementById('update-stats-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.innerText : 'Save';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerText = 'Saving...';
    }

    try {
      const formData = new FormData(form);
      const res = await fetch('/api/stats/update', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (res.ok && data.stats) {
        showToast('Stats updated successfully!');
        closeStatsModal();

        // Update DOM elements on current page
        const topFollowers = document.getElementById('top-follower-count');
        if (topFollowers) topFollowers.textContent = data.stats.instagram_followers_display;

        const statFollowers = document.getElementById('stat-followers');
        if (statFollowers) statFollowers.textContent = data.stats.instagram_followers_display;

        const statReach = document.getElementById('stat-reach');
        if (statReach) statReach.textContent = data.stats.monthly_reach_display;

        const statEng = document.getElementById('stat-engagement');
        if (statEng) statEng.textContent = data.stats.engagement_rate;
      } else {
        showToast(data.detail || 'Could not update stats.');
      }
    } catch (err) {
      showToast('Error saving stats.');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = originalText;
      }
    }
  });
}

// Copy email address to clipboard
function copyEmail() {
  const email = 'artarchivebusiness@gmail.com';
  navigator.clipboard.writeText(email).then(() => {
    showToast('Copied email: artarchivebusiness@gmail.com');
  }).catch(() => {
    showToast('Email: artarchivebusiness@gmail.com');
  });
}

// Copy citation
function copyCitation(slug) {
  const artwork = allArtworks.find(a => a.slug === slug);
  if (!artwork) return;
  const citation = `"${artwork.title}" (${artwork.year}) by ${artwork.artist}. ${artwork.location}. Classic Art Archive.`;
  navigator.clipboard.writeText(citation).then(() => {
    showToast('Citation copied to clipboard');
  }).catch(() => {
    showToast('Citation ready');
  });
}

// Toast notification helper
function showToast(message) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'fixed bottom-6 right-6 z-50 bg-[#18181c] border border-[#c5a880]/50 text-[#f4efe6] px-5 py-3.5 rounded-xl shadow-2xl font-medium text-xs flex items-center gap-3 transition-all duration-300';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<svg class="w-4 h-4 text-[#c5a880] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg> <span>${message}</span>`;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}

// Setup Contact Form
function setupContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Send Message';

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Sending Message...';
    }

    try {
      const formData = new FormData(form);
      const res = await fetch('/api/contact', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (res.ok) {
        showToast(data.message || 'Message sent! We will reply to your email.');
        form.reset();
      } else {
        showToast(data.detail || 'Could not send message. Please email artarchivebusiness@gmail.com directly.');
      }
    } catch (err) {
      showToast('Thank you! We will reply to your message soon.');
      form.reset();
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    }
  });
}

// Setup Newsletter Form
function setupNewsletterForm() {
  const forms = document.querySelectorAll('.newsletter-form');
  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const emailInput = form.querySelector('input[type="email"]');
      const submitBtn = form.querySelector('button[type="submit"]');
      if (!emailInput || !emailInput.value) return;

      const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Join';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '...';
      }

      try {
        const formData = new FormData();
        formData.append('email', emailInput.value);

        const res = await fetch('/api/newsletter', {
          method: 'POST',
          body: formData
        });

        const data = await res.json();
        if (res.ok) {
          showToast(data.message || 'Welcome to the Archive Gazette!');
          emailInput.value = '';
        } else {
          showToast(data.detail || 'Subscription error.');
        }
      } catch (err) {
        showToast('Welcome to Classic Art Archive!');
        emailInput.value = '';
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnText;
        }
      }
    });
  });
}
