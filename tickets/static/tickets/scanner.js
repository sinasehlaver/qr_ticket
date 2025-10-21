// scanner.js
// ...existing code...
document.addEventListener('DOMContentLoaded', function () {
  const resultDiv = document.getElementById('qr-result');
  const ticketInfoDiv = document.getElementById('ticket-info');
  const template = document.getElementById('ticket-template');
  
  
  function showMessage(text, kind='info') {
    resultDiv.innerHTML = `<div class="alert alert-${kind}">${text}</div>`;
  }
  
  function fetchTicketAndShow(uuid) {
    // fetch details from server (we will just get status by trying to fetch via GET on ticket page)
    // But better experience: call backend to retrieve ticket info (we will use fetch to ticket display page JSON - here we call no endpoint)
    // We'll just show basic info by requesting ticket page via fetch and parsing minimal info - simpler approach is to provide an endpoint.
    // To keep it simple and avoid extra endpoints, we will fetch ticket info from /ticket/<uuid>/ by calling that page and parsing HTML is brittle.
    // Instead the scanner will call a dedicated validate endpoint (POST) when pressing Check-In.
    // For display prior to check-in we call a small endpoint we can simulate by retrieving ticket fields via AJAX - but we don't have one; hence:
    // We'll show basic scanned UUID and present "Check-In" button; upon pressing it we'll call scanner/validate/ to check-in and get ticket info.
    ticketInfoDiv.innerHTML = '';
    const cloned = template.content.cloneNode(true);
    cloned.querySelector('#t-event').textContent = 'Ticket UUID: ' + uuid;
    cloned.querySelector('#t-details').textContent = 'UUID tarandı. Lütfen "Check-In" butonuna basın.';
    // store uuid on button
    const btn = cloned.querySelector('#check-in-btn');
    btn.dataset.uuid = uuid;
    btn.addEventListener('click', onCheckIn);
    ticketInfoDiv.appendChild(cloned);
  }
  
  function onCheckIn(ev) {
    const uuid = ev.currentTarget.dataset.uuid;
    fetch(window.location.origin + '/tickets/scanner/validate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ticket_uuid: uuid})
    }).then(r => r.json()).then(data => {
      if (data.ok) {
        showMessage(data.message, 'success');
        // Show returned ticket info if present
        if (data.ticket) {
          ticketInfoDiv.innerHTML = `
          <div class="card">
          <div class="card-body">
          <h5 class="card-title">${data.ticket.event}</h5>
          <p><strong>Tarih:</strong> ${data.ticket.event_date}</p>
          <p><strong>Yer:</strong> ${data.ticket.event_location}</p>
          <p><strong>Ad:</strong> ${data.ticket.attendee_name}</p>
          <p><strong>Plus ones:</strong> ${data.ticket.plus_ones}</p>
          <p><strong>Durum:</strong> ${data.ticket.status}</p>
          </div>
          </div>
          `;
        }
      } else {
        showMessage(data.error || 'Bir hata oluştu', 'danger');
      }
    }).catch(err => {
      showMessage('Sunucu ile bağlantı kurulamadı', 'danger');
      console.error(err);
    });
  }
  
  // html5-qrcode initialization
  const html5QrCode = new html5Qrcode("qr-reader");
  const qrConfig = { fps: 10, qrbox: 250 };
  console.log('scanner.js loaded, html5QrCode=', typeof html5QrCode);
  
  function onScanSuccess(decodedText, decodedResult) {
    // decodedText contains the UUID
    showMessage('QR kod okundu: ' + decodedText, 'info');
    fetchTicketAndShow(decodedText);
    // stop scanning (optional) — but we can stop to avoid multiple reads
    try {
      html5QrCode.stop().then(ignore => {
        // scanning stopped
      }).catch(err => {
        console.warn('stop error', err);
      });
    } catch(e) {}
  }

  function onScanFailure(error) {
    // no-op for continuous scans
  }

  Html5Qrcode.getCameras().then(cameras => {
    if (cameras && cameras.length) {
      const cameraId = cameras[0].id;
      html5QrCode.start(
        { facingMode: "environment" }, // or cameraId
        qrConfig,
        onScanSuccess,
        onScanFailure
      ).catch(err => {
        showMessage('Kameraya erişilemedi: ' + err, 'danger');
      });
    } else {
      showMessage('Cihazda kamera bulunamadı', 'warning');
    }
  }).catch(err => {
    showMessage('Kameralar alınamadı: ' + err, 'danger');
  });

  // helper to get csrf cookie
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
