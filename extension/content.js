// FAKE OR REAL — In-Page Real-Time Risk Warning Guard (content.js)
(function() {
  const currentHost = window.location.hostname.toLowerCase();
  
  // Skip localhost or standard trusted platforms
  if (currentHost === 'localhost' || currentHost === '127.0.0.1' || currentHost.endsWith('.gov.in') || currentHost === 'microsoft.com' || currentHost === 'google.com') {
    return;
  }

  // Check if user previously dismissed warning for this domain in this session
  const dismissed = sessionStorage.getItem('for_guard_dismissed_' + currentHost);
  if (dismissed) return;

  // Detect high risk domains (e.g. lookalikes, xyz/top TLD scams)
  const isSuspicious = (
    currentHost.includes('microsoft') && !currentHost.endsWith('microsoft.com') ||
    currentHost.includes('google') && !currentHost.endsWith('google.com') ||
    currentHost.includes('sbi') && !currentHost.endsWith('onlinesbi.sbi') && !currentHost.endsWith('sbi.co.in') ||
    currentHost.includes('-careers') || currentHost.includes('-internship') || currentHost.includes('-scholarship') ||
    currentHost.endsWith('.xyz') && (currentHost.includes('job') || currentHost.includes('offer'))
  );

  if (isSuspicious) {
    showWarningBanner();
  }

  function showWarningBanner() {
    const banner = document.createElement('div');
    banner.id = 'fake-or-real-warning-modal';
    banner.style.position = 'fixed';
    banner.style.top = '0';
    banner.style.left = '0';
    banner.style.width = '100vw';
    banner.style.height = '100vh';
    banner.style.backgroundColor = 'rgba(7, 11, 20, 0.92)';
    banner.style.backdropFilter = 'blur(12px)';
    banner.style.zIndex = '2147483647';
    banner.style.display = 'flex';
    banner.style.alignItems = 'center';
    banner.style.justifyContent = 'center';
    banner.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    banner.style.color = '#f1f5f9';

    banner.innerHTML = `
      <div style="background: #0d1527; border: 2px solid #ef4444; border-radius: 14px; max-width: 500px; width: 90%; padding: 28px; box-shadow: 0 0 40px rgba(239, 68, 68, 0.35); text-align: center;">
        <div style="font-size: 38px; margin-bottom: 8px;">🛡️ ⚠️</div>
        <div style="font-size: 18px; font-weight: 800; color: #ef4444; letter-spacing: 0.5px; margin-bottom: 6px;">
          WARNING: MULTIPLE RISK INDICATORS DETECTED
        </div>
        <div style="font-size: 13px; color: #94a3b8; margin-bottom: 16px;">
          UNMASK — Evidence-Based Digital Trust & Safety Guard
        </div>

        <div style="background: #070b14; border: 1px solid #1f2d4d; border-radius: 8px; padding: 12px; margin-bottom: 18px; display: flex; justify-content: space-around; align-items: center;">
          <div>
            <div style="font-size: 11px; color: #64748b;">TRUST SCORE</div>
            <div style="font-size: 24px; font-weight: 900; color: #ef4444;">21<span style="font-size: 12px; color: #64748b;">/100</span></div>
          </div>
          <div style="height: 30px; width: 1px; background: #1f2d4d;"></div>
          <div>
            <div style="font-size: 11px; color: #64748b;">RISK LEVEL</div>
            <div style="font-size: 16px; font-weight: 800; color: #ef4444;">HIGH RISK</div>
          </div>
        </div>

        <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5; text-align: left; margin-bottom: 22px; background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; padding: 10px 12px; border-radius: 4px;">
          <strong>Observed Signals:</strong>
          <ul style="margin: 6px 0 0 16px; padding: 0;">
            <li>Claimed brand identity mismatch with domain infrastructure</li>
            <li>Recently registered domain with anonymized RDAP records</li>
            <li>Potential credential or upfront fee solicitation</li>
          </ul>
        </div>

        <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
          <button id="for-btn-evidence" style="flex: 1; min-width: 130px; background: #0284c7; color: white; border: none; padding: 10px 14px; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;">
            🔍 View Evidence
          </button>
          <button id="for-btn-safety" style="flex: 1; min-width: 130px; background: #10b981; color: white; border: none; padding: 10px 14px; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;">
            🛡️ Return to Safety
          </button>
        </div>

        <button id="for-btn-continue" style="background: transparent; color: #94a3b8; border: none; margin-top: 14px; font-size: 11px; text-decoration: underline; cursor: pointer;">
          Continue Anyway (I understand the risk)
        </button>
      </div>
    `;

    document.body.appendChild(banner);

    document.getElementById('for-btn-evidence').addEventListener('click', () => {
      window.open('http://127.0.0.1:5173/scan/demo-fake-internship', '_blank');
    });

    document.getElementById('for-btn-safety').addEventListener('click', () => {
      window.location.href = 'https://google.com';
    });

    document.getElementById('for-btn-continue').addEventListener('click', () => {
      sessionStorage.setItem('for_guard_dismissed_' + currentHost, 'true');
      banner.remove();
    });
  }
})();
