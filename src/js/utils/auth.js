// Authentication Manager
import { EventEmitter } from './event-emitter.js';
import { SevDeskAPI } from './api.js';

export class AuthManager extends EventEmitter {
  constructor() {
    super();
    this.apiKey = null;
    this.apiUrl = 'https://my.sevdesk.de/api/v1';
    this.api = null;
    this.user = null;
    this.isAuthenticated = false;
  }

  async init() {
    // Load stored credentials
    this.loadStoredCredentials();
    
    if (this.apiKey) {
      // Test stored credentials
      try {
        await this.validateCredentials();
      } catch (error) {
        console.warn('Stored credentials invalid:', error);
        this.clearCredentials();
      }
    }
  }

  loadStoredCredentials() {
    try {
      this.apiKey = localStorage.getItem('sevdesk_api_key');
      this.apiUrl = localStorage.getItem('sevdesk_api_url') || this.apiUrl;
      
      if (this.apiKey) {
        this.api = new SevDeskAPI(this.apiKey, this.apiUrl);
      }
    } catch (error) {
      console.error('Failed to load stored credentials:', error);
    }
  }

  async authenticate(apiKey, apiUrl = null) {
    if (!apiKey) {
      throw new Error('API key is required');
    }

    this.apiUrl = apiUrl || this.apiUrl;
    this.api = new SevDeskAPI(apiKey, this.apiUrl);

    try {
      // Test the connection
      await this.validateCredentials();
      
      // Store credentials
      this.apiKey = apiKey;
      this.storeCredentials();
      
      this.isAuthenticated = true;
      this.emit('authenticated', this.user);
      
      return true;
    } catch (error) {
      this.api = null;
      throw error;
    }
  }

  async validateCredentials() {
    if (!this.api) {
      throw new Error('No API instance available');
    }

    try {
      // Test API connection by fetching user info or contacts
      const response = await this.api.get('/Contact', { limit: 1 });
      
      if (response && response.objects !== undefined) {
        this.user = {
          apiKey: this.apiKey,
          apiUrl: this.apiUrl,
          connectedAt: new Date().toISOString()
        };
        this.isAuthenticated = true;
        return true;
      } else {
        throw new Error('Invalid API response');
      }
    } catch (error) {
      this.isAuthenticated = false;
      throw new Error('Invalid API credentials or connection failed');
    }
  }

  storeCredentials() {
    try {
      localStorage.setItem('sevdesk_api_key', this.apiKey);
      localStorage.setItem('sevdesk_api_url', this.apiUrl);
    } catch (error) {
      console.error('Failed to store credentials:', error);
    }
  }

  clearCredentials() {
    try {
      localStorage.removeItem('sevdesk_api_key');
      localStorage.removeItem('sevdesk_api_url');
    } catch (error) {
      console.error('Failed to clear credentials:', error);
    }
    
    this.apiKey = null;
    this.api = null;
    this.user = null;
    this.isAuthenticated = false;
  }

  logout() {
    this.clearCredentials();
    this.emit('unauthenticated');
  }

  getAPI() {
    return this.api;
  }

  getUser() {
    return this.user;
  }

  isAuthenticated() {
    return this.isAuthenticated && this.api !== null;
  }

  getApiKey() {
    return this.apiKey;
  }

  getApiUrl() {
    return this.apiUrl;
  }
}