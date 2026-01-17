import React from 'react';
import StatusPanel from './StatusPanel';
import DockerMonitor from './DockerMonitor';
import VerificationRunner from './VerificationRunner';

export function SystemOperations() {
    return (
        <div className="space-y-8">
            <section>
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white">System Status</h2>
                    <p className="text-gray-400">Real-time operational status of all agents and services.</p>
                </div>
                <StatusPanel />
            </section>

            <section>
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white">Container Infrastructure</h2>
                    <p className="text-gray-400">Docker container monitoring and logs.</p>
                </div>
                <DockerMonitor />
            </section>

            <section>
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white">System Verification</h2>
                    <p className="text-gray-400">Run system-wide integrity checks.</p>
                </div>
                <VerificationRunner />
            </section>
        </div>
    );
}
