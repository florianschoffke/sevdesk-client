// Simple Client-side Router
import { EventEmitter } from './event-emitter.js';

export class Router extends EventEmitter {
  constructor() {
    super();
    this.routes = new Map();
    this.currentRoute = null;
    this.isStarted = false;
  }

  addRoute(path, handler) {
    this.routes.set(path, handler);
  }

  removeRoute(path) {
    this.routes.delete(path);
  }

  start() {
    if (this.isStarted) return;
    
    this.isStarted = true;
    
    // Handle browser back/forward
    window.addEventListener('popstate', this.handlePopState.bind(this));
    
    // Handle initial route
    this.handleRoute(window.location.pathname);
  }

  stop() {
    this.isStarted = false;
    window.removeEventListener('popstate', this.handlePopState.bind(this));
  }

  navigate(path, replace = false) {
    if (this.currentRoute === path) return;
    
    if (replace) {
      window.history.replaceState({}, '', path);
    } else {
      window.history.pushState({}, '', path);
    }
    
    this.handleRoute(path);
  }

  replace(path) {
    this.navigate(path, true);
  }

  back() {
    window.history.back();
  }

  forward() {
    window.history.forward();
  }

  handlePopState(event) {
    this.handleRoute(window.location.pathname);
  }

  handleRoute(path) {
    const previousRoute = this.currentRoute;
    this.currentRoute = path;
    
    // Emit route change event
    this.emit('route-change', path, previousRoute);
    
    // Find and execute route handler
    const handler = this.routes.get(path);
    if (handler) {
      try {
        handler(path);
      } catch (error) {
        console.error(`Error handling route '${path}':`, error);
        this.emit('route-error', error, path);
      }
    } else {
      // Handle 404
      this.emit('route-not-found', path);
      console.warn(`No handler found for route: ${path}`);
    }
  }

  getCurrentRoute() {
    return this.currentRoute;
  }

  getRoutes() {
    return Array.from(this.routes.keys());
  }
}