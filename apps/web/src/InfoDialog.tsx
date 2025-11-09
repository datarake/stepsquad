import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X, Info } from 'lucide-react';

interface InfoDialogProps {
  isOpen: boolean;
  title: string;
  message: string | React.ReactNode;
  onClose: () => void;
  closeText?: string;
}

export function InfoDialog({
  isOpen,
  title,
  message,
  onClose,
  closeText = 'Close',
}: InfoDialogProps) {
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      // Focus the close button when the dialog opens
      closeButtonRef.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-75 transition-opacity">
      <div
        className="relative bg-white rounded-lg shadow-xl transform transition-all sm:max-w-lg sm:w-full mx-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div className="sm:flex sm:items-start">
            <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
              <Info className="h-6 w-6 text-blue-600" aria-hidden="true" />
            </div>
            <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left flex-1">
              <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                {title}
              </h3>
              <div className="mt-2">
                <div className="text-sm text-gray-500 whitespace-pre-line">
                  {message}
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="absolute right-4 top-4 rounded-md p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
        <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            type="button"
            ref={closeButtonRef}
            className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
            onClick={onClose}
          >
            {closeText}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}

