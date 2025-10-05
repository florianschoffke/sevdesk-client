// SevDesk API Client
export class SevDeskAPI {
  constructor(apiKey, baseUrl = 'https://my.sevdesk.de/api/v1') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.requestCount = 0;
    this.lastRequest = 0;
    this.rateLimitDelay = 100; // ms between requests
  }

  async request(method, endpoint, data = null, options = {}) {
    // Simple rate limiting
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequest;
    if (timeSinceLastRequest < this.rateLimitDelay) {
      await this.sleep(this.rateLimitDelay - timeSinceLastRequest);
    }

    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      method: method.toUpperCase(),
      headers: {
        'Authorization': this.apiKey,
        'Content-Type': 'application/json',
        ...options.headers
      }
    };

    if (data && (method.toLowerCase() === 'post' || method.toLowerCase() === 'put')) {
      config.body = JSON.stringify(data);
    }

    // Add query parameters for GET requests
    if (data && method.toLowerCase() === 'get') {
      const params = new URLSearchParams(data);
      const separator = url.includes('?') ? '&' : '?';
      const finalUrl = `${url}${separator}${params}`;
      config.url = finalUrl;
    }

    try {
      this.lastRequest = Date.now();
      this.requestCount++;

      const response = await fetch(config.url || url, config);
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = `API request failed: ${response.status} ${response.statusText}`;
        
        try {
          const errorData = JSON.parse(errorText);
          if (errorData.error && errorData.error.message) {
            errorMessage = errorData.error.message;
          }
        } catch (e) {
          // Use default error message
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      return result;

    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error: Please check your internet connection');
      }
      throw error;
    }
  }

  async get(endpoint, params = {}) {
    return this.request('GET', endpoint, params);
  }

  async post(endpoint, data = {}) {
    return this.request('POST', endpoint, data);
  }

  async put(endpoint, data = {}) {
    return this.request('PUT', endpoint, data);
  }

  async delete(endpoint) {
    return this.request('DELETE', endpoint);
  }

  // Invoice-specific methods
  async createInvoice(invoiceData) {
    return this.post('/Invoice/Factory/saveInvoice', invoiceData);
  }

  async getContacts(params = {}) {
    return this.get('/Contact', params);
  }

  async getContact(contactId) {
    return this.get(`/Contact/${contactId}`);
  }

  async getInvoices(params = {}) {
    return this.get('/Invoice', params);
  }

  async getInvoice(invoiceId) {
    return this.get(`/Invoice/${invoiceId}`);
  }

  // Utility methods
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  getRequestCount() {
    return this.requestCount;
  }

  resetStats() {
    this.requestCount = 0;
    this.lastRequest = 0;
  }
}