import { useState, useEffect } from "react";
import {
  SettingsPanel,
  SettingsPanelHeader,
  CloseSettingsButton,
  SettingsContent,
  SettingsSection,
  FormGroup,
  SaveSettingsButton,
} from "../../styles/Chat.css";
import type { ChatSettings, RouteMode, PathfindingAlgorithm } from "./types";

interface ChatSettingsPanelProps {
  open: boolean;
  onClose: () => void;
  initialSettings: ChatSettings;
  onSave: (settings: ChatSettings) => void;
}

export function ChatSettingsPanel({
  open,
  onClose,
  initialSettings,
  onSave,
}: ChatSettingsPanelProps) {
  const [routeMode, setRouteMode] = useState<RouteMode>(
    initialSettings.routeMode,
  );
  const [pathfindingAlgorithm, setPathfindingAlgorithm] =
    useState<PathfindingAlgorithm>(initialSettings.pathfindingAlgorithm);
  const [sncfApiKey, setSncfApiKey] = useState(initialSettings.sncfApiKey);

  useEffect(() => {
    if (open) {
      setRouteMode(initialSettings.routeMode);
      setPathfindingAlgorithm(initialSettings.pathfindingAlgorithm);
      setSncfApiKey(initialSettings.sncfApiKey);
    }
  }, [
    open,
    initialSettings.routeMode,
    initialSettings.pathfindingAlgorithm,
    initialSettings.sncfApiKey,
  ]);

  const handleSave = () => {
    onSave({
      routeMode,
      pathfindingAlgorithm,
      sncfApiKey,
    });
    onClose();
  };

  const showAlgorithm = routeMode === "graph";
  const showSncfKey = routeMode === "sncf_api";

  return (
    <SettingsPanel $open={open} role="dialog" aria-label="Paramètres">
      <SettingsPanelHeader>
        <h2>⚙️ Paramètres</h2>
        <CloseSettingsButton
          type="button"
          onClick={onClose}
          aria-label="Fermer"
        >
          ×
        </CloseSettingsButton>
      </SettingsPanelHeader>
      <SettingsContent>
        <SettingsSection>
          <h3>🔍 Mode de recherche d&apos;itinéraire</h3>
          <FormGroup>
            <label htmlFor="routeMode">Système de recherche :</label>
            <select
              id="routeMode"
              value={routeMode}
              onChange={(e) => setRouteMode(e.target.value as RouteMode)}
            >
              <option value="graph">Graphe local (A* / Dijkstra)</option>
              <option value="sncf_api">API SNCF (horaires réels)</option>
            </select>
            <small>
              Graphe : Rapide, local, basé sur distances | API SNCF : Données
              réelles, horaires en temps réel
            </small>
          </FormGroup>

          {showAlgorithm && (
            <FormGroup>
              <label htmlFor="pathfindingAlgorithm">
                Algorithme (graphe) :
              </label>
              <select
                id="pathfindingAlgorithm"
                value={pathfindingAlgorithm}
                onChange={(e) =>
                  setPathfindingAlgorithm(
                    e.target.value as PathfindingAlgorithm,
                  )
                }
              >
                <option value="dijkstra">Dijkstra</option>
                <option value="astar">A* (A-star)</option>
              </select>
              <small>
                Dijkstra : Plus simple | A* : Plus rapide avec heuristique
              </small>
            </FormGroup>
          )}

          {showSncfKey && (
            <FormGroup>
              <label htmlFor="sncfApiKey">Clé API SNCF :</label>
              <input
                type="password"
                id="sncfApiKey"
                placeholder="Votre clé API SNCF"
                value={sncfApiKey}
                onChange={(e) => setSncfApiKey(e.target.value)}
              />
              <small>
                Obtenez votre clé sur{" "}
                <a
                  href="https://www.sncf-connect.com/open-data/api"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  sncf-connect.com/open-data/api
                </a>
              </small>
            </FormGroup>
          )}
        </SettingsSection>

        <SaveSettingsButton type="button" onClick={handleSave}>
          💾 Enregistrer les paramètres
        </SaveSettingsButton>
      </SettingsContent>
    </SettingsPanel>
  );
}
