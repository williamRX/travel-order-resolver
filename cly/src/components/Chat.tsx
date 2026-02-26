import { useState, useCallback } from "react";
import {
  ChatContainer,
  ChatMessagesArea,
  ChatStickerCell,
  ChatSticker6Cell,
  ChatSticker7aCell,
  ChatSticker7bCell,
  SettingsOverlay,
} from "../styles/Chat.css";
import sticker5 from "../assets/sticker5.svg";
import sticker6 from "../assets/sticker6.svg";
import sticker7a from "../assets/sticker7a.svg";
import sticker7b from "../assets/sticker7b.svg";
import { useIsPortrait } from "../hooks/useIsPortrait";
import { usePredictMutation } from "../api/predict";
import { getApiBase } from "../api/client";
import {
  loadSettings,
  saveSettings as persistSettings,
  type ChatMessage as ChatMessageType,
  type ChatSettings,
} from "./Chat/types";
import { ChatMessages } from "./Chat/ChatMessages";
import { ChatSettingsPanel } from "./Chat/ChatSettingsPanel";
import { ChatInput } from "./Chat/ChatInput";

function generateId() {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export const Chat = () => {
  const isPortrait = useIsPortrait();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [settings, setSettings] = useState<ChatSettings>(loadSettings);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const predictMutation = usePredictMutation();

  const addMessage = useCallback((msg: Omit<ChatMessageType, "id">) => {
    setMessages((prev) => [...prev, { ...msg, id: generateId() }]);
  }, []);

  const handleSend = useCallback(
    async (sentence: string) => {
      addMessage({ role: "user", content: sentence });
      try {
        const body = {
          sentence,
          route_mode: settings.routeMode,
          pathfinding_algorithm: settings.pathfindingAlgorithm,
        };
        if (settings.routeMode === "sncf_api" && settings.sncfApiKey) {
          (body as { sncf_api_key?: string }).sncf_api_key =
            settings.sncfApiKey;
        }
        const data = await predictMutation.mutateAsync(body);
        if (!data.valid) {
          addMessage({
            role: "bot",
            content: data.message ?? "Phrase invalide.",
            isError: true,
          });
        } else {
          addMessage({
            role: "bot",
            content: "", // ChatResult will render from data
            isSuccess: true,
            data,
          });
        }
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Erreur inconnue";
        const isNetworkError =
          message === "Load failed" ||
          message === "Failed to fetch" ||
          message === "NetworkError when attempting to fetch resource" ||
          (typeof message === "string" && message.includes("fetch"));
        const displayMessage = isNetworkError
          ? `Impossible de joindre l'API. Vérifiez que l'API est accessible sur ${getApiBase()}`
          : `Erreur : ${message}`;
        addMessage({
          role: "bot",
          content: `❌ ${displayMessage}`,
          isError: true,
        });
      }
    },
    [addMessage, settings, predictMutation],
  );

  const handleSaveSettings = useCallback((newSettings: ChatSettings) => {
    setSettings(newSettings);
    persistSettings(newSettings);
  }, []);

  const handleSettingsSavedFeedback = useCallback(() => {
    addMessage({
      role: "bot",
      content: "✅ Paramètres enregistrés avec succès !",
      isSuccess: true,
    });
  }, [addMessage]);

  const handleCloseSettings = useCallback(() => {
    setSettingsOpen(false);
  }, []);

  const handleOpenSettings = useCallback(() => {
    setSettingsOpen(true);
  }, []);

  const handleCsvClick = useCallback(() => {
    window.location.hash = "csv";
  }, []);

  const handleSaveSettingsAndNotify = useCallback(
    (newSettings: ChatSettings) => {
      handleSaveSettings(newSettings);
      handleSettingsSavedFeedback();
    },
    [handleSaveSettings, handleSettingsSavedFeedback],
  );

  const handleExampleClick = useCallback(
    (text: string) => {
      handleSend(text);
    },
    [handleSend],
  );

  return (
    <ChatContainer $isPortrait={isPortrait}>
      <SettingsOverlay
        $open={settingsOpen}
        onClick={handleCloseSettings}
        aria-hidden
      />
      <ChatSettingsPanel
        open={settingsOpen}
        onClose={handleCloseSettings}
        initialSettings={settings}
        onSave={handleSaveSettingsAndNotify}
      />
      <ChatStickerCell>
        <img src={sticker5} alt="" aria-hidden />
      </ChatStickerCell>
      <ChatSticker6Cell>
        <img src={sticker6} alt="" aria-hidden />
      </ChatSticker6Cell>
      <ChatSticker7aCell
        onClick={handleCsvClick}
        role="button"
        title="Traitement par fichier CSV"
        aria-label="Traitement par fichier CSV"
      >
        <img src={sticker7a} alt="" aria-hidden />
      </ChatSticker7aCell>
      <ChatSticker7bCell
        onClick={handleOpenSettings}
        role="button"
        title="Paramètres"
        aria-label="Paramètres"
      >
        <img src={sticker7b} alt="" aria-hidden />
      </ChatSticker7bCell>
      <ChatMessagesArea>
        <ChatMessages messages={messages} onExampleClick={handleExampleClick} />
      </ChatMessagesArea>
      <ChatInput
        onSend={handleSend}
        disabled={predictMutation.isPending}
        isLoading={predictMutation.isPending}
      />
    </ChatContainer>
  );
};
