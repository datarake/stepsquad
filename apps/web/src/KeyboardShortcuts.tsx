import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

/**
 * Hook for keyboard shortcuts
 */
export function useKeyboardShortcuts() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K: Focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector<HTMLInputElement>('input[type="search"], #search');
        if (searchInput) {
          searchInput.focus();
        }
      }

      // Ctrl/Cmd + N: New competition (if admin)
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        navigate('/competitions/new');
      }

      // Escape: Close modals or go back
      if (e.key === 'Escape') {
        // Close any open modals or return to list
        if (window.location.pathname.includes('/edit')) {
          navigate(-1);
        }
      }

      // Ctrl/Cmd + /: Show keyboard shortcuts help
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        toast('Keyboard Shortcuts: Ctrl+K (Search), Ctrl+N (New), Esc (Back)', { icon: 'ℹ️' });
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigate]);
}

/**
 * Component that provides keyboard shortcuts
 */
export function KeyboardShortcuts() {
  useKeyboardShortcuts();
  return null;
}
