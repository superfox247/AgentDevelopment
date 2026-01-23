import { useEffect, useState } from 'react';
import { Activity, Gauge, Wifi, WifiOff, ExternalLink } from 'lucide-react';

interface QuotaInfo {
    name: string;
    metric: string;
    quota_id: string;
    refresh_interval: string | null;
    is_precise: boolean;
    dimensions: Array<{
        labels: Record<string, string>;
        value: number | null;
    }>;
}

interface UsageMetric {
    metric_type: string;
    description: string;
    unit: string;
}

interface UsageResponse {
    project_id: string;
    service: string;
    quotas: QuotaInfo[];
    usage_metrics: UsageMetric[];
    telemetry_status: string;
    errors: string[];
}

const API_BASE = 'http://localhost:8010/api';

export function UsageView() {
    const [data, setData] = useState<UsageResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch(`${API_BASE}/usage`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then((result: UsageResponse) => {
                setData(result);
                setLoading(false);
            })
            .catch(err => {
                setError(err instanceof Error ? err.message : String(err));
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="p-8 text-center text-gray-400">
                <Activity className="w-8 h-8 animate-spin mx-auto mb-4" />
                Loading usage data...
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-8 text-center text-red-400">
                <p>Error: {error}</p>
                <p className="text-sm mt-2 text-gray-500">
                    Make sure the dashboard backend is running on port 8010.
                </p>
            </div>
        );
    }

    if (!data) return null;

    const telemetryActive = data.telemetry_status.startsWith('active');

    return (
        <div className="space-y-8">
            {/* Header */}
            <header>
                <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
                    Usage & Quotas
                </h2>
                <p className="text-gray-400 mt-2">
                    Monitor your API limits and consumption for {data.service}
                </p>
            </header>

            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Project Info */}
                <div className="glass-card p-6 rounded-xl">
                    <div className="text-sm text-gray-500 mb-1">Project</div>
                    <div className="font-mono text-white">{data.project_id}</div>
                </div>

                {/* Telemetry Status */}
                <div className="glass-card p-6 rounded-xl">
                    <div className="text-sm text-gray-500 mb-1">Telemetry</div>
                    <div className="flex items-center space-x-2">
                        {telemetryActive ? (
                            <>
                                <Wifi className="w-5 h-5 text-green-400" />
                                <span className="text-green-400">Active</span>
                            </>
                        ) : (
                            <>
                                <WifiOff className="w-5 h-5 text-yellow-400" />
                                <span className="text-yellow-400">Inactive</span>
                            </>
                        )}
                    </div>
                </div>

                {/* Console Link */}
                <a
                    href={`https://console.cloud.google.com/iam-admin/quotas?project=${data.project_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="glass-card p-6 rounded-xl hover:bg-white/5 transition-colors group"
                >
                    <div className="text-sm text-gray-500 mb-1">Cloud Console</div>
                    <div className="flex items-center space-x-2 text-cyan-400">
                        <ExternalLink className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        <span>View All Quotas</span>
                    </div>
                </a>
            </div>

            {/* Errors */}
            {data.errors.length > 0 && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                    <h3 className="text-red-400 font-semibold mb-2">Errors</h3>
                    {data.errors.map((err, i) => (
                        <p key={i} className="text-sm text-red-300">{err}</p>
                    ))}
                </div>
            )}

            {/* Quota Limits */}
            <section>
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                    <Gauge className="w-5 h-5 text-cyan-400" />
                    <span>Gemini Quota Limits ({data.quotas.length})</span>
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {data.quotas.slice(0, 8).map((quota) => (
                        <div key={quota.quota_id} className="glass-card p-5 rounded-xl">
                            <div className="flex justify-between items-start mb-3">
                                <h4 className="font-medium text-white text-sm">
                                    {quota.name.replace(/PerMinute|PerProject|PerBaseModel/g, ' ').trim()}
                                </h4>
                                {quota.refresh_interval && (
                                    <span className="text-xs bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded">
                                        {quota.refresh_interval}
                                    </span>
                                )}
                            </div>

                            <div className="space-y-2">
                                {quota.dimensions.slice(0, 3).map((dim, i) => (
                                    <div key={i} className="flex justify-between text-sm">
                                        <span className="text-gray-500 font-mono text-xs">
                                            {Object.values(dim.labels).join(' / ') || 'default'}
                                        </span>
                                        <span className="text-white font-mono">
                                            {dim.value?.toLocaleString() ?? 'N/A'}
                                        </span>
                                    </div>
                                ))}
                                {quota.dimensions.length > 3 && (
                                    <div className="text-xs text-gray-500">
                                        +{quota.dimensions.length - 3} more dimensions
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                {data.quotas.length > 8 && (
                    <p className="text-sm text-gray-500 mt-4">
                        Showing 8 of {data.quotas.length} quotas. View all in Cloud Console.
                    </p>
                )}
            </section>

            {/* Available Metrics */}
            <section>
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                    <Activity className="w-5 h-5 text-purple-400" />
                    <span>Available Usage Metrics ({data.usage_metrics.length})</span>
                </h3>

                <div className="glass-card rounded-xl overflow-hidden">
                    <table className="w-full text-sm">
                        <thead className="bg-white/5">
                            <tr>
                                <th className="text-left p-3 text-gray-400">Metric</th>
                                <th className="text-left p-3 text-gray-400">Description</th>
                                <th className="text-left p-3 text-gray-400">Unit</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.usage_metrics.slice(0, 10).map((metric) => (
                                <tr key={metric.metric_type} className="border-t border-white/5 hover:bg-white/5">
                                    <td className="p-3 font-mono text-xs text-cyan-300">
                                        {metric.metric_type.split('/').pop()}
                                    </td>
                                    <td className="p-3 text-gray-300 text-xs">
                                        {metric.description.slice(0, 80)}...
                                    </td>
                                    <td className="p-3 text-gray-400">{metric.unit}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    );
}
