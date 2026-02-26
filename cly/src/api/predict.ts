import { useMutation } from "@tanstack/react-query";
import { getApiBase } from "./client";

export interface SentenceRequest {
  sentence: string;
  route_mode?: "graph" | "sncf_api";
  pathfinding_algorithm?: "dijkstra" | "astar";
  sncf_api_key?: string;
}

export interface SncfSection {
  type: string;
  from?: string;
  to?: string;
  line?: string;
  departure_time?: string;
  arrival_time?: string;
  duration?: number;
}

export interface SentenceResponse {
  valid: boolean;
  message?: string;
  departure?: string;
  arrival?: string;
  route?: string[];
  route_distance?: number;
  route_time?: number;
  route_source?: string;
  route_algorithm?: string;
  sncf_departure_time?: string;
  sncf_arrival_time?: string;
  sncf_next_train?: string;
  sncf_transfers?: number;
  sncf_sections?: SncfSection[];
  sncf_departure_uic?: string;
  sncf_arrival_uic?: string;
  sncf_departure_time_raw?: string;
}

async function postPredict(body: SentenceRequest): Promise<SentenceResponse> {
  const res = await fetch(`${getApiBase()}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof data.detail === "string" ? data.detail : "Erreur lors de la requête";
    throw new Error(detail);
  }
  return data as SentenceResponse;
}

export function usePredictMutation() {
  return useMutation({
    mutationFn: postPredict,
  });
}
