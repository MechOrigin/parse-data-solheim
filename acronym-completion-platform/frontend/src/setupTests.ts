// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
import React from 'react';
import { configure } from '@testing-library/react';

// Mock the fetch function
global.fetch = jest.fn();

// Configure testing-library
configure({
  testIdAttribute: 'data-testid',
});

// Create a component factory function that preserves props
const createComponent = (type: string) => {
  return React.forwardRef((props: any, ref: any) => {
    const { initial, animate, exit, children, ...rest } = props;
    return React.createElement(type, { ...rest, ref }, children);
  });
};

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: new Proxy({}, {
    get: function(target, prop) {
      if (typeof prop === 'string') {
        return createComponent(prop);
      }
      return undefined;
    }
  }),
  AnimatePresence: ({ children }: { children: React.ReactNode }) => React.createElement(React.Fragment, null, children),
}));

// Setup container for React to render into
beforeEach(() => {
  const container = document.createElement('div');
  container.id = 'root';
  document.body.appendChild(container);
});

// Cleanup after each test
afterEach(() => {
  document.body.innerHTML = '';
});

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

// Mock URL methods
window.URL.createObjectURL = jest.fn(() => 'mock-url');
window.URL.revokeObjectURL = jest.fn();

// Setup DOM environment
document.createRange = () => {
  const range = new Range();
  range.getBoundingClientRect = jest.fn();
  range.getClientRects = () => ({
    item: () => null,
    length: 0,
    [Symbol.iterator]: jest.fn()
  });
  return range;
};

// Mock document.createElement
const originalCreateElement = document.createElement;
document.createElement = (tagName: string) => {
  const element = originalCreateElement.call(document, tagName);
  if (tagName.toLowerCase() === 'a') {
    const anchor = element as HTMLAnchorElement;
    Object.defineProperty(anchor, 'style', {
      value: {},
      writable: true
    });
    Object.defineProperty(anchor, 'href', {
      value: '',
      writable: true
    });
    Object.defineProperty(anchor, 'download', {
      value: '',
      writable: true
    });
    Object.defineProperty(anchor, 'click', {
      value: jest.fn(),
      writable: true
    });
  }
  return element;
};

// Mock document.body methods
const originalAppendChild = document.body.appendChild;
const originalRemoveChild = document.body.removeChild;

Object.defineProperty(document.body, 'appendChild', {
  value: function(node: Node): Node {
    if (node instanceof HTMLElement) {
      return originalAppendChild.call(this, node);
    }
    return node;
  },
  writable: true,
  configurable: true
});

Object.defineProperty(document.body, 'removeChild', {
  value: function(node: Node): Node {
    if (node instanceof HTMLElement) {
      return originalRemoveChild.call(this, node);
    }
    return node;
  },
  writable: true,
  configurable: true
}); 