// FAKE OR REAL — Background Service Worker (background.js)

chrome.runtime.onInstalled.addListener(() => {
  console.log('FAKE OR REAL Guard extension installed successfully.');
  
  // Set default badge state
  chrome.action.setBadgeText({ text: 'ON' });
  chrome.action.setBadgeBackgroundColor({ color: '#06b6d4' });
});

// Update badge when tab switches
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    if (!tab || !tab.url) return;

    const url = tab.url.toLowerCase();
    if (url.includes('.xyz') || url.includes('careers-') || url.includes('offer-')) {
      chrome.action.setBadgeText({ tabId: activeInfo.tabId, text: '!' });
      chrome.action.setBadgeBackgroundColor({ tabId: activeInfo.tabId, color: '#ef4444' });
    } else if (url.startsWith('https://')) {
      chrome.action.setBadgeText({ tabId: activeInfo.tabId, text: '✓' });
      chrome.action.setBadgeBackgroundColor({ tabId: activeInfo.tabId, color: '#10b981' });
    } else {
      chrome.action.setBadgeText({ tabId: activeInfo.tabId, text: '?' });
      chrome.action.setBadgeBackgroundColor({ tabId: activeInfo.tabId, color: '#f59e0b' });
    }
  } catch (e) {
    // Tab closed or restricted
  }
});
