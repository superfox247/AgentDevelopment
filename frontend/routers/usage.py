"""Usage and Quotas Router - Provides visibility into API limits and consumption."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from frontend.models import MetricTimeseriesResponse, QuotaDetailResponse

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
    quotas, quota_errors = _fetch_quotas()
    usage_metrics, metric_errors = _fetch_usage_metrics()
    telemetry_status = _check_telemetry_status()

    return UsageResponse(
        project_id=PROJECT_ID,
        service=SERVICE,
        quotas=quotas,
        usage_metrics=usage_metrics,
        telemetry_status=telemetry_status,
        errors=quota_errors + metric_errors,
    )


def _process_quota(quota_info: Any) -> QuotaInfo | None:
    """Process a single quota info object."""
    name_lower = quota_info.name.lower()
    # Filter for Gemini-related quotas
    if "gemini" not in name_lower and "generatecontent" not in name_lower.replace(
        "_", ""
    ):
        return None

    dimensions = []
    if quota_info.dimensions_infos:
        for dim in quota_info.dimensions_infos[:5]:  # Limit to 5
            dimensions.append(
                {
                    "labels": dict(dim.dimensions),
                    "value": dim.details.value if dim.details else None,
                }
            )

    return QuotaInfo(
        name=quota_info.name.split("/")[-1],
        metric=quota_info.metric or "",
        quota_id=quota_info.quota_id or "",
        refresh_interval=str(quota_info.refresh_interval)
        if quota_info.refresh_interval
        else None,
        is_precise=quota_info.is_precise,
        dimensions=dimensions,
    )


def _fetch_quotas() -> tuple[list[QuotaInfo], list[str]]:
    """Fetch Quota Limits from Cloud Quotas API."""
    quotas: list[QuotaInfo] = []
    errors: list[str] = []
    try:
        from google.cloud import cloudquotas_v1

        client = cloudquotas_v1.CloudQuotasClient()
        parent = f"projects/{PROJECT_ID}/locations/global/services/{SERVICE}"

        request = cloudquotas_v1.ListQuotaInfosRequest(parent=parent)
        page_result = client.list_quota_infos(request=request)

        for quota_info in page_result:
            if processed := _process_quota(quota_info):
                quotas.append(processed)

        logger.info(f"Fetched {len(quotas)} Gemini quotas")
    except ImportError:
        errors.append("google-cloud-quotas not installed")
    except Exception as e:
        logger.exception("Error fetching quotas")
        errors.append(f"Quota fetch error: {type(e).__name__}: {e}")

    return quotas, errors


def _fetch_usage_metrics() -> tuple[list[UsageMetric], list[str]]:
    """Fetch Usage Metrics from Cloud Monitoring."""
    usage_metrics: list[UsageMetric] = []
    errors: list[str] = []
    try:
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

    return usage_metrics, errors


def _check_telemetry_status() -> str:
    """Check Telemetry Status (Phoenix)."""
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
                    return f"active ({host}:6006)"
            except (OSError, socket.error, socket.timeout) as e:
                # Network errors are expected when checking connectivity
                logger.debug(f"Could not connect to {host}:6006: {e}")
                continue
        return "inactive"
    except Exception as e:
        logger.error(f"Unexpected error checking telemetry status: {e}", exc_info=True)
        return f"error: {e}"


@router.get("/usage/quota/{quota_id}", response_model=QuotaDetailResponse)
async def get_quota_detail(quota_id: str) -> QuotaDetailResponse:
    """Get detailed information for a specific quota."""
    try:
        from google.cloud import cloudquotas_v1

        client = cloudquotas_v1.CloudQuotasClient()
        parent = f"projects/{PROJECT_ID}/locations/global/services/{SERVICE}"

        request = cloudquotas_v1.ListQuotaInfosRequest(parent=parent)
        page_result = client.list_quota_infos(request=request)

        for quota_info in page_result:
            if quota_id in quota_info.name:
                return QuotaDetailResponse(
                    name=quota_info.name,
                    metric=quota_info.metric,
                    quota_id=quota_info.quota_id,
                    refresh_interval=str(quota_info.refresh_interval),
                    is_precise=quota_info.is_precise,
                    container_type=str(quota_info.container_type),
                    dimensions=[
                        {
                            "labels": dict(d.dimensions),
                            "value": d.details.value if d.details else None,
                            "locations": list(d.applicable_locations)[:5],
                        }
                        for d in quota_info.dimensions_infos
                    ],
                )

        raise HTTPException(status_code=404, detail=f"Quota {quota_id} not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching quota detail")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/usage/metrics/{metric_name}/timeseries", response_model=MetricTimeseriesResponse
)
async def get_metric_timeseries(
    metric_name: str, hours: int = 24
) -> MetricTimeseriesResponse:
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
                points.append({"time": pt.interval.end_time.isoformat(), "value": val})

            time_series.append({"labels": dict(ts.metric.labels), "points": points})

        return MetricTimeseriesResponse(
            metric_name=metric_name,
            hours=hours,
            data_points=time_series,
        )

    except Exception as e:
        logger.exception("Error fetching time series")
        raise HTTPException(status_code=500, detail=str(e)) from e
