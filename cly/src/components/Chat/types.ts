import type { SentenceResponse } from "../../api/predict";

export type ChatMessageRole = "user" | "bot";

export interface ChatMessage {
  id: string;
  role: ChatMessageRole;
  /** Texte brut ou HTML (pour les réponses bot formatées). */
  content: string;
  isError?: boolean;
  isSuccess?: boolean;
  /** Données de la réponse predict (pour affichage structuré optionnel). */
  data?: SentenceResponse;
}

export type RouteMode = "graph" | "sncf_api";
export type PathfindingAlgorithm = "dijkstra" | "astar";

export interface ChatSettings {
  routeMode: RouteMode;
  pathfindingAlgorithm: PathfindingAlgorithm;
  sncfApiKey: string;
}

export const DEFAULT_SETTINGS: ChatSettings = {
  routeMode: "graph",
  pathfindingAlgorithm: "dijkstra",
  sncfApiKey: "",
};

const SETTINGS_KEYS = {
  routeMode: "routeMode",
  pathfindingAlgorithm: "pathfindingAlgorithm",
  sncfApiKey: "sncfApiKey",
} as const;

export function loadSettings(): ChatSettings {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;
  return {
    routeMode: (localStorage.getItem(SETTINGS_KEYS.routeMode) as RouteMode) ?? DEFAULT_SETTINGS.routeMode,
    pathfindingAlgorithm:
      (localStorage.getItem(SETTINGS_KEYS.pathfindingAlgorithm) as PathfindingAlgorithm) ?? DEFAULT_SETTINGS.pathfindingAlgorithm,
    sncfApiKey: localStorage.getItem(SETTINGS_KEYS.sncfApiKey) ?? DEFAULT_SETTINGS.sncfApiKey,
  };
}

export function saveSettings(settings: ChatSettings): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(SETTINGS_KEYS.routeMode, settings.routeMode);
  localStorage.setItem(SETTINGS_KEYS.pathfindingAlgorithm, settings.pathfindingAlgorithm);
  if (settings.sncfApiKey) {
    localStorage.setItem(SETTINGS_KEYS.sncfApiKey, settings.sncfApiKey);
  }
}
