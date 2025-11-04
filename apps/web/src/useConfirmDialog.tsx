import { useState, useCallback } from 'react';

interface ConfirmDialogOptions {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
}

interface ConfirmDialogState extends ConfirmDialogOptions {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function useConfirmDialog() {
  const [dialogState, setDialogState] = useState<ConfirmDialogState | null>(null);

  const confirm = useCallback(
    (options: ConfirmDialogOptions): Promise<boolean> => {
      return new Promise((resolve) => {
        setDialogState({
          ...options,
          isOpen: true,
          onConfirm: () => {
            setDialogState(null);
            resolve(true);
          },
          onCancel: () => {
            setDialogState(null);
            resolve(false);
          },
        });
      });
    },
    []
  );

  return {
    confirm,
    dialogState,
  };
}

