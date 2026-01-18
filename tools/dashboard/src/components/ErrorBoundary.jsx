import React from 'react';
import { AlertTriangle } from 'lucide-react';

export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("ErrorBoundary caught an error", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-4 bg-red-900/20 border border-red-500/30 rounded-lg text-red-200 flex items-start space-x-3">
                    <AlertTriangle className="shrink-0 mt-1" />
                    <div>
                        <h3 className="font-bold">Component Error</h3>
                        <p className="font-mono text-sm mt-1">{this.state.error?.message || "Unknown error"}</p>
                        <button
                            onClick={() => this.setState({ hasError: false })}
                            className="mt-3 px-3 py-1 bg-red-500/20 hover:bg-red-500/30 rounded text-xs transition-colors"
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
