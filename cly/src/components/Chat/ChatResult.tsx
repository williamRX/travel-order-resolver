import { useState } from "react";
import type { SentenceResponse, SncfSection } from "../../api/predict";
import {
  ResultBox,
  ResultItem,
  RoutePath,
  RoutePathGraph,
  RouteBadge,
  RouteSourceInfo,
  SncfSummary,
  SncfSummaryItem,
  SncfDetailsToggle,
  SncfDetailsContent,
  SncfSectionDetail,
  ResultHr,
  ResultMeta,
} from "../../styles/Chat.css";

interface ChatResultProps {
  data: SentenceResponse;
}

function formatTime(iso?: string): string {
  if (!iso) return "N/A";
  const part = iso.split("T")[1];
  return part ? part.substring(0, 5) : "N/A";
}

function SncfDetails({ sections }: { sections: SncfSection[] }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <>
      <SncfDetailsToggle type="button" onClick={() => setExpanded((e) => !e)}>
        <span>📋 Détails du trajet</span>
        <span style={{ transform: expanded ? "rotate(180deg)" : undefined }}>▼</span>
      </SncfDetailsToggle>
      <SncfDetailsContent $expanded={expanded}>
        {sections.map((section, idx) =>
          section.type === "train" ? (
            <SncfSectionDetail key={idx} $type="train">
              <div style={{ display: "flex", alignItems: "center", marginBottom: 5 }}>
                <span style={{ fontSize: 18, marginRight: 8 }}>🚂</span>
                <strong style={{ color: "#ffcc33" }}>{section.line || "Train"}</strong>
              </div>
              <div style={{ paddingLeft: 26 }}>
                <div>
                  <strong>{section.from ?? "N/A"}</strong> ({formatTime(section.departure_time)})
                </div>
                <div style={{ margin: "5px 0", color: "#000000" }}>→</div>
                <div>
                  <strong>{section.to ?? "N/A"}</strong> ({formatTime(section.arrival_time)})
                </div>
                {section.duration != null && (
                  <div style={{ marginTop: 5, fontSize: 12, color: "#000000" }}>
                    ⏱️ Durée : {Math.round(section.duration / 60)} min
                  </div>
                )}
              </div>
            </SncfSectionDetail>
          ) : section.type === "transfer" ? (
            <SncfSectionDetail key={idx} $type="transfer">
              <span style={{ fontSize: 16, marginRight: 8 }}>⚡</span>
              <strong>Correspondance</strong> -{" "}
              {section.duration != null ? Math.round(section.duration / 60) : "?"} min
            </SncfSectionDetail>
          ) : null
        )}
      </SncfDetailsContent>
    </>
  );
}

export function ChatResult({ data }: ChatResultProps) {
  const hasRoute = data.route && data.route.length > 0;
  const routeSource = data.route_source ?? "graph";
  const routeAlgorithm = data.route_algorithm ?? "";
  const isSNCF = routeSource === "sncf_api";
  const isGraph = routeSource === "graph";

  return (
    <>
      <p>✅ Phrase valide !</p>
      {hasRoute ? (
        <ResultBox>
          <h3>
            {isSNCF ? "🚆" : "🗺️"}{" "}
            {isSNCF ? "Itinéraire SNCF (horaires réels)" : "Itinéraire calculé (graphe local)"}{" "}
            {isSNCF && <RouteBadge $kind="sncf">API SNCF</RouteBadge>}
            {isGraph && (
              <>
                <RouteBadge $kind="graph">Graphe</RouteBadge>
                {routeAlgorithm && (
                  <RouteBadge $kind={routeAlgorithm === "astar" ? "astar" : "dijkstra"}>
                    {routeAlgorithm === "astar" ? "A*" : "Dijkstra"}
                  </RouteBadge>
                )}
              </>
            )}
          </h3>
          {data.route &&
            (isSNCF ? (
              <RoutePath $variant="sncf">
                {data.route.map((step, i) => (
                  <span key={i}>
                    {i > 0 && " → "}
                    <strong>{step}</strong>
                  </span>
                ))}
              </RoutePath>
            ) : (
              <RoutePathGraph>
                {data.route.map((step, i) => (
                  <span key={i}>
                    {i > 0 && " → "}
                    <strong>{step}</strong>
                  </span>
                ))}
              </RoutePathGraph>
            ))}
          {data.route_distance != null && (
            <ResultItem>
              <strong>Distance totale :</strong> {data.route_distance.toFixed(1)} km
            </ResultItem>
          )}
          {data.route_time != null && (
            <ResultItem>
              <strong>Temps estimé :</strong> {data.route_time.toFixed(1)} h (
              {Math.round(data.route_time * 60)} min)
            </ResultItem>
          )}
          {isSNCF && (
            <>
              <SncfSummary>
                {data.sncf_departure_time && data.sncf_arrival_time && (
                  <SncfSummaryItem>
                    <strong>⏱️ Horaires :</strong>{" "}
                    <span>
                      {data.sncf_departure_time} → {data.sncf_arrival_time}
                    </span>
                  </SncfSummaryItem>
                )}
                {data.sncf_next_train && (
                  <SncfSummaryItem $highlight>
                    <strong>🚆 Prochain train :</strong> <span>{data.sncf_next_train}</span>
                  </SncfSummaryItem>
                )}
                {data.sncf_transfers != null && (
                  <SncfSummaryItem>
                    <strong>🔄 Correspondances :</strong>{" "}
                    <span>
                      {data.sncf_transfers === 0
                        ? "Direct ✨"
                        : `${data.sncf_transfers} correspondance${data.sncf_transfers > 1 ? "s" : ""}`}
                    </span>
                  </SncfSummaryItem>
                )}
              </SncfSummary>
              {data.sncf_sections && data.sncf_sections.length > 0 && (
                <SncfDetails sections={data.sncf_sections} />
              )}
              <RouteSourceInfo style={{ marginTop: 15 }}>
                📡 Source : API SNCF - Horaires en temps réel avec correspondances réelles
              </RouteSourceInfo>
            </>
          )}
          {isGraph && (
            <RouteSourceInfo style={{ marginTop: 15 }}>
              📊 Source : Graphe local - Calcul basé sur distances géographiques (
              {routeAlgorithm === "astar" ? "A* (A-star)" : "Dijkstra"})
            </RouteSourceInfo>
          )}
          <ResultHr />
          <ResultMeta>
            {data.departure && <div><strong>Départ :</strong> {data.departure}</div>}
            {data.arrival && <div><strong>Arrivée :</strong> {data.arrival}</div>}
          </ResultMeta>
        </ResultBox>
      ) : data.departure || data.arrival ? (
        <ResultBox>
          <h3>Destinations extraites :</h3>
          <ResultItem>
            <strong>Départ :</strong> {data.departure ?? <em>Non détecté</em>}
          </ResultItem>
          <ResultItem>
            <strong>Arrivée :</strong> {data.arrival ?? <em>Non détecté</em>}
          </ResultItem>
        </ResultBox>
      ) : (
        <p>⚠️ Aucune destination détectée dans la phrase.</p>
      )}
    </>
  );
}
