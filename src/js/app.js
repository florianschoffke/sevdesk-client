// Main Application Class
import { AuthManager } from './utils/auth.js';
import { Router } from './utils/router.js';
import { ComponentManager } from './utils/component-manager.js';
import { LoadingManager } from './utils/loading.js';
import { Toast } from './utils/toast.js';

// Import Views
import { AuthView } from './components/auth.js';
import { DashboardView } from './components/dashboard.js';
import { BulkInvoicesView } from './components/bulk-invoices.js';

export class App {
  constructor() {
    this.authManager = new AuthManager();
    this.router = new Router();
    this.componentManager = new ComponentManager();
    this.loadingManager = new LoadingManager();
    
    // App state
    this.currentView = null;
    this.isInitialized = false;
  }

  async init() {
    try {
      this.showLoadingScreen();
      
      // Initialize core services
      await this.initializeServices();
      
      // Register views
      this.registerViews();
      
      // Setup event listeners
      this.setupEventListeners();
      
      // Initialize routing
      this.initializeRouting();
      
      this.isInitialized = true;
      this.hideLoadingScreen();
      
      console.log('SevDesk Client initialized successfully');
      
    } catch (error) {
      console.error('Failed to initialize app:', error);
      this.showError('Failed to initialize application. Please refresh and try again.');
      throw error;
    }
  }

  async initializeServices() {
    // Initialize authentication manager
    await this.authManager.init();
    
    // Initialize toast system
    Toast.init();
    
    // Initialize loading manager
    this.loadingManager.init();
  }

  registerViews() {
    // Register all application views
    this.componentManager.register('auth', AuthView);
    this.componentManager.register('dashboard', DashboardView);
    this.componentManager.register('bulk-invoices', BulkInvoicesView);
    
    console.log('Views registered:', this.componentManager.getRegisteredComponents());
  }

  setupEventListeners() {
    // Global keyboard shortcuts
    document.addEventListener('keydown', this.handleKeyboard.bind(this));
    
    // Auth state changes
    this.authManager.on('authenticated', this.handleAuthenticated.bind(this));
    this.authManager.on('unauthenticated', this.handleUnauthenticated.bind(this));
    
    // Router events
    this.router.on('route-change', this.handleRouteChange.bind(this));
    
    // Window events
    window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
    window.addEventListener('online', () => Toast.success('Connection restored'));
    window.addEventListener('offline', () => Toast.warning('Connection lost. Some features may not work.'));
  }

  initializeRouting() {
    // Define routes
    this.router.addRoute('/', () => this.showInitialView());
    this.router.addRoute('/auth', () => this.showView('auth'));
    this.router.addRoute('/dashboard', () => this.showView('dashboard'));
    this.router.addRoute('/bulk-invoices', () => this.showView('bulk-invoices'));
    
    // Start router
    this.router.start();
  }

  showInitialView() {
    // Determine which view to show based on auth state
    if (this.authManager.isAuthenticated()) {
      this.router.navigate('/dashboard');
    } else {
      this.router.navigate('/auth');
    }
  }

  async showView(viewName, data = {}) {
    try {
      // Hide current view
      if (this.currentView) {
        await this.currentView.hide();
      }
      
      // Create or get view instance
      const ViewClass = this.componentManager.get(viewName);
      if (!ViewClass) {
        throw new Error(`View '${viewName}' not found`);
      }
      
      // Create new view instance
      this.currentView = new ViewClass();
      
      // Initialize view with data
      await this.currentView.init(data);
      
      // Show view
      await this.currentView.show();
      
      console.log(`Showing view: ${viewName}`);
      
    } catch (error) {
      console.error(`Failed to show view '${viewName}':`, error);
      Toast.error(`Failed to load ${viewName}. Please try again.`);
    }
  }

  handleAuthenticated(user) {
    console.log('User authenticated:', user);
    Toast.success('Successfully connected to SevDesk!');
    this.router.navigate('/dashboard');
  }

  handleUnauthenticated() {
    console.log('User logged out');
    Toast.info('Logged out successfully');
    this.router.navigate('/auth');
  }

  handleRouteChange(route) {
    console.log('Route changed to:', route);
    // Update page title
    this.updatePageTitle(route);
  }

  updatePageTitle(route) {
    const titles = {
      '/': 'SevDesk Client',
      '/auth': 'Login - SevDesk Client',
      '/dashboard': 'Dashboard - SevDesk Client',
      '/bulk-invoices': 'Bulk Invoices - SevDesk Client'
    };
    
    document.title = titles[route] || 'SevDesk Client';
  }

  handleKeyboard(event) {
    // Global keyboard shortcuts
    if (event.ctrlKey || event.metaKey) {
      switch (event.key) {
        case 'k':
          event.preventDefault();
          // Future: Open command palette
          break;
        case '/':
          event.preventDefault();
          // Future: Open search
          break;
      }
    }
    
    // Escape key
    if (event.key === 'Escape') {
      // Close modals, cancel operations, etc.
      this.loadingManager.hide();
    }
  }

  handleBeforeUnload(event) {
    // Warn user if there are unsaved changes
    if (this.currentView && this.currentView.hasUnsavedChanges) {
      event.preventDefault();
      event.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
      return event.returnValue;
    }
  }

  showLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    const appContainer = document.getElementById('app-container');
    
    if (loadingScreen) loadingScreen.classList.remove('hidden');
    if (appContainer) appContainer.classList.add('hidden');
  }

  hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    const appContainer = document.getElementById('app-container');
    
    if (loadingScreen) {
      setTimeout(() => {
        loadingScreen.classList.add('hidden');
      }, 500); // Small delay for smooth transition
    }
    
    if (appContainer) appContainer.classList.remove('hidden');
  }

  showError(message) {
    const appContainer = document.getElementById('app-container');
    if (appContainer) {
      appContainer.innerHTML = `
        <div class="container">
          <div class="auth-card" style="margin-top: 10vh;">
            <div style="text-align: center; color: var(--color-danger);">
              <h2>⚠️ Application Error</h2>
              <p>${message}</p>
              <button onclick="window.location.reload()" class="btn btn-primary" style="margin-top: 20px;">
                Reload Application
              </button>
            </div>
          </div>
        </div>
      `;
    }
  }

  // Public API methods
  getAuthManager() {
    return this.authManager;
  }

  getRouter() {
    return this.router;
  }

  getCurrentView() {
    return this.currentView;
  }

  isReady() {
    return this.isInitialized;
  }
}