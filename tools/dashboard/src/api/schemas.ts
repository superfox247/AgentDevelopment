import { z } from 'zod';

// --- System Status ---
export const SystemStatusSchema = z.object({
    status: z.string(),
    orchestrator: z.string().optional(),
    content_builder: z.string().optional(),
    image_generator: z.string().optional(),
    customer_service: z.string().optional(),
});
export type SystemStatus = z.infer<typeof SystemStatusSchema>;

// --- Docker ---
export const DockerContainerInfoSchema = z.object({
    id: z.string(),
    name: z.string(),
    status: z.string(),
    image: z.string(),
});
export type DockerContainerInfo = z.infer<typeof DockerContainerInfoSchema>;

export const DockerStatsResponseSchema = z.object({
    containers: z.array(DockerContainerInfoSchema),
});
export type DockerStatsResponse = z.infer<typeof DockerStatsResponseSchema>;

export const ContainerControlResponseSchema = z.object({
    status: z.string(),
    action: z.string(),
    id: z.string(),
});

export const ContainerLogsResponseSchema = z.object({
    logs: z.string(),
});

// --- Agents ---
export const AgentInfoSchema = z.object({
    domain: z.string(),
    name: z.string(),
    path: z.string(),
});
export type AgentInfo = z.infer<typeof AgentInfoSchema>;

export const AgentsResponseSchema = z.object({
    agents: z.array(AgentInfoSchema),
});
export type AgentsResponse = z.infer<typeof AgentsResponseSchema>;

// --- Models ---
export const ModelInfoSchema = z.object({
    name: z.string(),
    display_name: z.string(),
    description: z.string(),
    input_token_limit: z.number(),
    output_token_limit: z.number(),
    top_p: z.number().nullable().optional(),
    temperature: z.number().nullable().optional(),
});
export type ModelInfo = z.infer<typeof ModelInfoSchema>;

export const ModelsResponseSchema = z.object({
    models: z.array(ModelInfoSchema),
});
export type ModelsResponse = z.infer<typeof ModelsResponseSchema>;

// --- Skills ---
export const SkillInfoSchema = z.object({
    name: z.string(),
    path: z.string(),
});
export type SkillInfo = z.infer<typeof SkillInfoSchema>;

export const SkillsResponseSchema = z.object({
    skills: z.array(SkillInfoSchema),
});
export type SkillsResponse = z.infer<typeof SkillsResponseSchema>;

// --- Artifacts ---
export const ArtifactInfoSchema = z.object({
    name: z.string(),
    path: z.string(),
    type: z.string(),
});
export type ArtifactInfo = z.infer<typeof ArtifactInfoSchema>;

export const ArtifactsResponseSchema = z.object({
    artifacts: z.array(ArtifactInfoSchema),
});
export type ArtifactsResponse = z.infer<typeof ArtifactsResponseSchema>;

// --- System Fix ---
export const SystemFixResponseSchema = z.object({
    success: z.boolean(),
    stdout: z.string(),
    stderr: z.string(),
});
