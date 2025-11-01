import { useEffect, useRef } from 'react';

/**
 * Hook for form auto-save functionality
 */
export function useAutoSave<T extends Record<string, any>>(
  formData: T,
  onSave: (data: T) => Promise<void>,
  delay: number = 3000
) {
  const timeoutRef = useRef<NodeJS.Timeout>();
  const lastSavedRef = useRef<string>('');

  useEffect(() => {
    // Skip if no changes
    const currentData = JSON.stringify(formData);
    if (currentData === lastSavedRef.current) {
      return;
    }

    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout
    timeoutRef.current = setTimeout(async () => {
      try {
        await onSave(formData);
        lastSavedRef.current = currentData;
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [formData, onSave, delay]);
}
