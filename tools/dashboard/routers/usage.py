"""Usage and Quotas Router - Provides visibility into API limits and consumption."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["usage"])

# Configuration
PROJECT_ID = "videogenerator-482919"
SERVICE = "aiplatform.googleapis.com"


class QuotaInfo(BaseModel):
    """Individual quota limit information."""

    name: str
    metric: str
    quota_id: str
    refresh_interval: str | None = None
    is_precise: bool = False
    dimensions: list[dict[str, Any]] = []


class UsageMetric(BaseModel):
    """Usage metric with time series data."""

    metric_type: str
    description: str
    unit: str
    data_points: list[dict[str, Any]] = []


class UsageResponse(BaseModel):
    """Combined usage and quota response."""

    project_id: str
    service: str
    quotas: list[QuotaInfo]
    usage_metrics: list[UsageMetric]
    telemetry_status: str
    errors: list[str] = []


@router.get("/usage", response_model=UsageResponse)
async def get_usage() -> UsageResponse:
    """
    Get current quota limits and usage metrics for AI Platform.

    Returns:
        Combined quota limits from Cloud Quotas API and
        usage metrics from Cloud Monitoring.
    """
    errors: list[str] = []
    quotas: list[QuotaInfo] = []
    usage_metrics: list[UsageMetric] = []
    telemetry_status = "unknown"

    # Part 1: Fetch Quota Limits
    try:
        from google.cloud import cloudquotas_v1

        client = cloudquotas_v1.CloudQuotasClient()
        parent = f"projects/{PROJECT_ID}/locations/global/services/{SERVICE}"

        request = cloudquotas_v1.ListQuotaInfosRequest(parent=parent)
        page_result = client.list_quota_infos(request=request)

        for quota_info in page_result:
            name_lower = quota_info.name.lower()
            # Filter for Gemini-related quotas
            if "gemini" in name_lower or "generatecontent" in name_lower.replace(
                "_", ""
            ):
                dimensions = []
                if quota_info.dimensions_infos:
                    for dim in quota_info.dimensions_infos[:5]:  # Limit to 5
                        dimensions.append(
                            {
                                "labels": dict(dim.dimensions),
                                "value": dim.details.value if dim.details else None,
                            }
                        )

                quotas.append(
                    QuotaInfo(
                        name=quota_info.name.split("/")[-1],
                        metric=quota_info.metric or "",
                        quota_id=quota_info.quota_id or "",
                        refresh_interval=str(quota_info.refresh_interval)
                        if quota_info.refresh_interval
                        else None,
                        is_precise=quota_info.is_precise,
                        dimensions=dimensions,
                    )
                )

        logger.info(f"Fetched {len(quotas)} Gemini quotas")

    except ImportError:
        errors.append("google-cloud-quotas not installed")
    except Exception as e:
        logger.exception("Error fetching quotas")
        errors.append(f"Quota fetch error: {type(e).__name__}: {e}")

    # Part 2: Fetch Usage Metrics from Cloud Monitoring
    try:
        import time

        from google.cloud import monitoring_v3

        monitoring_client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{PROJECT_ID}"

        # List relevant metrics
        metrics_request = monitoring_v3.ListMetricDescriptorsRequest(
            name=project_name,
            filter='metric.type = starts_with("aiplatform.googleapis.com")',
        )

        all_metrics = list(
            monitoring_client.list_metric_descriptors(request=metrics_request)
        )

        # Filter for interesting ones
        interesting_keywords = ["token", "request", "generate_content"]
        interesting = [
            m
            for m in all_metrics
            if any(kw in m.type.lower() for kw in interesting_keywords)
        ][:10]

        for m in interesting:
            usage_metrics.append(
                UsageMetric(
                    metric_type=m.type,
                    description=m.description[:200] if m.description else "",
                    unit=m.unit or "1",
                    data_points=[],  # Will be populated on detail request
                )
            )

        logger.info(f"Found {len(usage_metrics)} usage metrics")

    except ImportError:
        errors.append("google-cloud-monitoring not installed")
    except Exception as e:
        logger.exception("Error fetching usage metrics")
        errors.append(f"Monitoring fetch error: {type(e).__name__}: {e}")

    # Part 3: Check Telemetry Status (Phoenix)
    try:
        import socket

        phoenix_hosts = ["phoenix", "host.docker.internal", "localhost"]
        for host in phoenix_hosts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, 6006))
                sock.close()
                if result == 0:
                    telemetry_status = f"active ({host}:6006)"
                    break
            except Exception:
                continue
        else:
            telemetry_status = "inactive"

    except Exception as e:
        telemetry_status = f"error: {e}"

    return UsageResponse(
        project_id=PROJECT_ID,
        service=SERVICE,
        quotas=quotas,
        usage_metrics=usage_metrics,
        telemetry_status=telemetry_status,
        errors=errors,
    )


@router.get("/usage/quota/{quota_id}")
async def get_quota_detail(quota_id: str) -> dict[str, Any]:
    """Get detailed information for a specific quota."""
    try:
        from google.cloud import cloudquotas_v1

        client = cloudquotas_v1.CloudQuotasClient()
        parent = f"projects/{PROJECT_ID}/locations/global/services/{SERVICE}"

        request = cloudquotas_v1.ListQuotaInfosRequest(parent=parent)
        page_result = client.list_quota_infos(request=request)

        for quota_info in page_result:
            if quota_id in quota_info.name:
                return {
                    "name": quota_info.name,
                    "metric": quota_info.metric,
                    "quota_id": quota_info.quota_id,
                    "refresh_interval": str(quota_info.refresh_interval),
                    "is_precise": quota_info.is_precise,
                    "container_type": str(quota_info.container_type),
                    "dimensions": [
                        {
                            "labels": dict(d.dimensions),
                            "value": d.details.value if d.details else None,
                            "locations": list(d.applicable_locations)[:5],
                        }
                        for d in quota_info.dimensions_infos
                    ],
                }

        raise HTTPException(status_code=404, detail=f"Quota {quota_id} not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching quota detail")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/usage/metrics/{metric_name}/timeseries")
async def get_metric_timeseries(metric_name: str, hours: int = 24) -> dict[str, Any]:
    """Get time series data for a specific metric."""
    try:
        import time

        from google.cloud import monitoring_v3

        monitoring_client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{PROJECT_ID}"

        now = time.time()
        interval = monitoring_v3.TimeInterval(
            {
                "end_time": {"seconds": int(now)},
                "start_time": {"seconds": int(now - hours * 3600)},
            }
        )

        metric_type = f"aiplatform.googleapis.com/{metric_name}"

        results = monitoring_client.list_time_series(
            request={
                "name": project_name,
                "filter": f'metric.type = "{metric_type}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )

        time_series = []
        for ts in results:
            points = []
            for pt in ts.points[:100]:  # Limit points
                val = pt.value.int64_value or pt.value.double_value
                points.append(
                    {"time": pt.interval.end_time.isoformat(), "value": val}
                )

            time_series.append(
                {"labels": dict(ts.metric.labels), "points": points}
            )

        return {"metric": metric_name, "hours": hours, "time_series": time_series}

    except Exception as e:
        logger.exception("Error fetching time series")
        raise HTTPException(status_code=500, detail=str(e)) from e
