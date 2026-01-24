# System Component Inventory

This document maps all active services, agents, and infrastructure components within the Antigravity Agent Platform.

## 1. Domain Agents & Services

| Component Name | Type | Source Path | Docker Service | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Content Creation Orchestrator** | Agent (Root) | `domains/content_creation/orchestrator` | `content_creation-orchestrator` | Root router for the content creation domain. |
| **Customer Service** | Agent (Sub) | `domains/content_creation/customer_service` | `content_creation-customer_service` | Handles initial user intent and topic extraction. |
| **Image Generator** | Agent (Sub) | `domains/content_creation/image_generator` | `content_creation-image_generator` | Generates visual assets using multimodals. |
| **Content Builder** | Agent (Remote) | `domains/content_creation/content_builder` | `content_creation-content_builder` | Transforms research into structured content. |
| **Researcher** | Agent (Remote) | `domains/content_creation/researcher` | `content_creation-researcher` | Performs deep search and information gathering. |
| **Judge** | Agent (Remote) | `domains/content_creation/judge` | `content_creation-judge` | Evaluates research findings for quality. |

## 2. Platform Core

| Component Name | Type | Source Path | Description |
| :--- | :--- | :--- | :--- |
| **Agent Platform** | Lib | `agent_platform/` | Shared core for Auth, Observability, and Config. |
| **Dashboard Backend** | Service | `tools/dashboard/server.py` | FastAPI backend for the Agent Central Dashboard. |
| **Dashboard Frontend** | UI | `tools/dashboard/src/` | React/Vite frontend for Agent Central. |

## 3. Infrastructure & Observability

| Component Name | Type | Container / Image | access |
| :--- | :--- | :--- | :--- |
| **Phoenix** | Service | `arize/phoenix` | `http://localhost:6006` |
| **Redis** | Database | `redis:alpine` | Internal (Port 6379) |

## 4. Documentation Strategy

The Single Source of Truth for all documentation is the [Knowledge Base](../knowledge).
Projects `docs/` folder mirrors key standards but should be updated from the Knowledge Base.
