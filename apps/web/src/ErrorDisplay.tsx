import React from 'react';
import { AlertCircle, XCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

interface ErrorDisplayProps {
  error: Error | string;
  onDismiss?: () => void;
  variant?: 'error' | 'warning' | 'info' | 'success';
}

export function ErrorDisplay({ error, onDismiss, variant = 'error' }: ErrorDisplayProps) {
  const errorMessage = error instanceof Error ? error.message : error;
  
  const variants = {
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: XCircle,
      iconColor: 'text-red-400',
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      icon: AlertTriangle,
      iconColor: 'text-yellow-400',
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      icon: Info,
      iconColor: 'text-blue-400',
    },
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: CheckCircle,
      iconColor: 'text-green-400',
    },
  };

  const variantStyle = variants[variant];
  const Icon = variantStyle.icon;

  return (
    <div className={`rounded-md ${variantStyle.bg} ${variantStyle.border} border p-4`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <Icon className={`h-5 w-5 ${variantStyle.iconColor}`} />
        </div>
        <div className="ml-3 flex-1">
          <p className={`text-sm font-medium ${variantStyle.text}`}>
            {errorMessage}
          </p>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <button
              onClick={onDismiss}
              className={`inline-flex rounded-md ${variantStyle.bg} ${variantStyle.text} hover:opacity-75 focus:outline-none`}
            >
              <XCircle className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

interface FieldErrorProps {
  error?: string;
}

export function FieldError({ error }: FieldErrorProps) {
  if (!error) return null;
  
  return (
    <div className="mt-1 flex items-center text-sm text-red-600">
      <AlertCircle className="h-4 w-4 mr-1" />
      <span>{error}</span>
    </div>
  );
}
