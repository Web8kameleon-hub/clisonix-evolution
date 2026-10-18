"use client";


// ⚡ CONVERTED TO STATIC CLIENT COMPONENT
// - Removed useState for Web8 compliance
// - Added "use client" directive
// - Use props or static values instead of state

/**
 * AppPageManager.ts
 * Pure TypeScript Application Page Manager with CSS Modules
 * Uses framer-motion and class-variance-authority
 */

import { Suspense, lazy, ReactNode, createElement } from 'react';
import { motion } from 'framer-motion';
import { cva } from 'class-variance-authority';
import styles from './AppPageManager.module.css';

// Page Definition Interface
export interface PageDefinition {
  path: string;
  title: string;
  element: ReactNode;
  layout: 'default' | 'minimal' | 'fullscreen';
  meta?: {
    description?: string;
    keywords?: string[];
    noIndex?: boolean;
  };
}

// Motion Wrapper Variants using CVA
const motionWrapperVariants = cva(styles.pageWrapper, {
  variants: {
    layout: {
      default: styles.layoutDefault,
      minimal: styles.layoutMinimal,
      fullscreen: styles.layoutFullscreen
    }
  },
  defaultVariants: {
    layout: 'default'
  }
});

// Simple Loader Component (pure CSS)
export const Loader = (): ReactNode => 
  createElement('div', { className: styles.loader },
    createElement('div', { className: styles.loaderSpinner }),
    createElement('span', { className: styles.loaderText }, 'Loading...')
  );

// Lazy loaded components - using named exports
const LazyHome = lazy(() => import("../components/pages/Home").then(module => ({ default: module.Home })));
const LazySettings = lazy(() => import("../components/pages/Settings").then(module => ({ default: module.Settings })));
const LazyAGI = lazy(() => import("./AGICoreComponent").then(module => ({ default: module.AGICoreComponent })));

// Motion wrapper for page transitions
export const withMotion = (component: ReactNode, layout: PageDefinition['layout'] = 'default'): ReactNode => 
  createElement(motion.div, {
    initial: { opacity: 0, y: 12 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -12 },
    transition: { duration: 0.3 },
    className: motionWrapperVariants({ layout })
  }, component);

// Page definitions with proper typing
export const pageDefinitions: PageDefinition[] = [
  {
    path: '/',
    title: 'Home - EuroWeb Platform',
    element: createElement(Suspense, { fallback: createElement(Loader) }, createElement(LazyHome)),
    layout: 'default',
    meta: {
      description: 'EuroWeb Platform - Advanced AGI-powered web browser',
      keywords: ['agi', 'web browser', 'ai', 'euroweb']
    }
  },
  {
    path: '/settings',
    title: 'Settings - EuroWeb Platform',
    element: createElement(Suspense, { fallback: createElement(Loader) }, createElement(LazySettings)),
    layout: 'default'
  },
  {
    path: '/agi',
    title: 'AGI Core - EuroWeb Platform',
    element: createElement(Suspense, { fallback: createElement(Loader) }, createElement(LazyAGI)),
    layout: 'fullscreen'
  }
];

// App Page Manager Class
export class AppPageManager {
  private currentPage: string = '/';
  private pages: Map<string, PageDefinition> = new Map();

  constructor() {
    this.initializePages();
  }

  private initializePages(): void {
    pageDefinitions.forEach(page => {
      this.pages.set(page.path, page);
    });
  }

  public getCurrentPage(): string {
    return this.currentPage;
  }

  public setCurrentPage(path: string): void {
    if (this.pages.has(path)) {
      this.currentPage = path;
      this.updateDocumentTitle(path);
    }
  }

  public getPageDefinition(path: string): PageDefinition | undefined {
    return this.pages.get(path);
  }

  public getAllPages(): PageDefinition[] {
    return Array.from(this.pages.values());
  }

  public renderPage(path: string): ReactNode {
    const page = this.pages.get(path);
    if (!page) {
      return this.renderNotFound();
    }

    return withMotion(page.element, page.layout);
  }

  private renderNotFound(): ReactNode {
    return withMotion(
      createElement('div', { className: styles.notFound },
        createElement('h1', null, '404'),
        createElement('p', null, 'Page not found')
      ),
      'minimal'
    );
  }

  private updateDocumentTitle(path: string): void {
    const page = this.pages.get(path);
    if (page && typeof document !== 'undefined') {
      document.title = page.title;
      
      // Update meta description if available
      if (page.meta?.description) {
        const metaDescription = document.querySelector('meta[name="description"]');
        if (metaDescription) {
          metaDescription.setAttribute('content', page.meta.description);
        }
      }
    }
  }

  public addPage(page: PageDefinition): void {
    this.pages.set(page.path, page);
  }

  public removePage(path: string): boolean {
    return this.pages.delete(path);
  }
}

// Default export for the singleton instance
export const appPageManager = new AppPageManager();

