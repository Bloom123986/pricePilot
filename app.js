const form = document.getElementById('scrape-form');
const urlInput = document.getElementById('product-url');
const statusBox = document.getElementById('status');
const resultsBox = document.getElementById('results');

const apiUrl = 'http://127.0.0.1:8000/compare';

function renderResults(data) {
  resultsBox.innerHTML = '';
  const offers = Array.isArray(data?.offers) ? data.offers : [];
  const bestOffer = data?.best_offer || offers[0] || null;

  populateBestDeal(bestOffer, offers);

  const summaryCard = document.createElement('div');
  summaryCard.className = 'result-card best-match';
  summaryCard.innerHTML = `
    <h3>Best Match</h3>
    <p><strong>${bestOffer?.title || 'No result yet'}</strong></p>
    <p>${bestOffer?.price ? `Price: ${bestOffer.price}` : 'Price unavailable'}</p>
    <p>${bestOffer?.platform ? `Platform: ${bestOffer.platform}` : ''}</p>
    <p>${bestOffer?.rating ? `Rating: ${bestOffer.rating}/5` : 'Rating unavailable'}</p>
  `;
  resultsBox.appendChild(summaryCard);

  if (offers.length) {
    const offersGrid = document.createElement('div');
    offersGrid.className = 'offers-grid';

    offers.forEach((offer) => {
      const card = document.createElement('div');
      card.className = 'result-card offer-card';
      card.innerHTML = `
        <h3>${offer.platform}</h3>
        ${offer.image ? `<img src="${offer.image}" alt="${offer.title}" onerror="this.style.display='none'" />` : ''}
        <p><strong>${offer.title}</strong></p>
        <p>Price: ${offer.price || 'Not listed'}</p>
        <p>Rating: ${offer.rating || 'Not listed'}</p>
        <a href="${offer.url}" target="_blank" rel="noreferrer">View offer</a>
      `;
      offersGrid.appendChild(card);
    });

    resultsBox.appendChild(offersGrid);
  } else {
    const emptyCard = document.createElement('div');
    emptyCard.className = 'result-card';
    emptyCard.innerHTML = '<h3>No matches</h3><p>Try a broader product name such as "phone" or "headphones".</p>';
    resultsBox.appendChild(emptyCard);
  }
}
function clearBestDeal() {
  document.getElementById('deal-title').textContent = 'No product yet';
  document.getElementById('deal-sub').textContent = 'Search a product to see recommendations';
  document.getElementById('deal-price').textContent = '-';
  document.getElementById('deal-rating').textContent = '-';
  document.getElementById('deal-delivery').textContent = '-';
  document.getElementById('deal-rows').innerHTML = '<tr><td colspan="4">No data</td></tr>';
  document.getElementById('deal-image').innerHTML = '';
  document.getElementById('ai-reco').textContent = 'AI Recommendation will appear here.';
}

function populateBestDeal(best, offers) {
  if (!best) {
    clearBestDeal();
    return;
  }
  document.getElementById('deal-title').textContent = best.title || '—';
  document.getElementById('deal-sub').textContent = best.platform ? `${best.platform}` : '';
  document.getElementById('deal-price').textContent = best.price || '-';
  document.getElementById('deal-rating').textContent = best.rating ? `${best.rating}/5` : '-';
  document.getElementById('deal-delivery').textContent = best.delivery || '—';
  const imgWrap = document.getElementById('deal-image');
  imgWrap.innerHTML = best.image ? `<img src="${best.image}" alt="${best.title}" />` : '<div style="color:var(--muted)">No image</div>';

  const rows = offers && offers.length ? offers.map(o => `<tr><td>${o.platform}</td><td>${o.price||'-'}</td><td>${o.rating||'-'}</td><td>${o.delivery||'-'}</td></tr>`).join('') : '<tr><td colspan="4">No data</td></tr>';
  document.getElementById('deal-rows').innerHTML = rows;

  // Simple AI recommendation text
  document.getElementById('ai-reco').textContent = best.platform ? `${best.platform} looks like the best option based on price and rating.` : 'No recommendation available.';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const query = urlInput.value.trim();
  if (!query) {
    statusBox.textContent = 'Please enter a product name.';
    statusBox.className = 'status error';
    return;
  }

  statusBox.textContent = 'Comparing products across marketplaces...';
  statusBox.className = 'status loading';
  resultsBox.innerHTML = '';

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Request failed');
    }

    const data = await response.json();
    renderResults(data);
    statusBox.textContent = data.message || 'Comparison complete.';
    statusBox.className = 'status';
  } catch (error) {
    statusBox.textContent = error.message || 'An unexpected error occurred.';
    statusBox.className = 'status error';
  }
});
