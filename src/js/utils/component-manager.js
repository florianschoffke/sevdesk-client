// Component Manager for registering and creating view components
export class ComponentManager {
  constructor() {
    this.components = new Map();
    this.instances = new Map();
  }

  register(name, ComponentClass) {
    this.components.set(name, ComponentClass);
  }

  unregister(name) {
    this.components.delete(name);
    this.instances.delete(name);
  }

  get(name) {
    return this.components.get(name);
  }

  has(name) {
    return this.components.has(name);
  }

  getInstance(name, forceNew = false) {
    if (forceNew || !this.instances.has(name)) {
      const ComponentClass = this.components.get(name);
      if (!ComponentClass) {
        throw new Error(`Component '${name}' not found`);
      }
      
      const instance = new ComponentClass();
      this.instances.set(name, instance);
      return instance;
    }
    
    return this.instances.get(name);
  }

  destroyInstance(name) {
    const instance = this.instances.get(name);
    if (instance && typeof instance.destroy === 'function') {
      instance.destroy();
    }
    this.instances.delete(name);
  }

  getRegisteredComponents() {
    return Array.from(this.components.keys());
  }

  clear() {
    // Destroy all instances
    this.instances.forEach((instance, name) => {
      this.destroyInstance(name);
    });
    
    // Clear registrations
    this.components.clear();
    this.instances.clear();
  }
}