import { createQueryKeys } from "@lukemorales/query-key-factory";
import { useQuery } from "@tanstack/react-query";
import { getApiBase } from "./client";

export interface HealthResponse {
  status: string;
  pipeline_loaded: boolean;
}

const getHealth = async (): Promise<HealthResponse> => {
  const res = await fetch(`${getApiBase()}/health`);
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error((detail as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  return res.json();
};

export const healthQueryKeys = createQueryKeys("health", {
  health: () => ({
    queryKey: ["health"],
    queryFn: () => getHealth(),
  }),
});

export const useGetHealth = () => {
  return useQuery({
    ...healthQueryKeys.health(),
  });
};
