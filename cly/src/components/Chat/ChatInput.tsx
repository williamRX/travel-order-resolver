import { useRef, useState, useCallback } from "react";
import {
  ChatSticker7cCell,
  ChatSticker7dCell,
  SentenceInput,
  VoiceStatus,
} from "../../styles/Chat.css";
import sticker7c from "../../assets/sticker7c.svg";
import sticker7d from "../../assets/sticker7d.svg";
import sticker7e from "../../assets/sticker7e.svg";

interface ChatInputProps {
  onSend: (sentence: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  /** Ref appelé au clic sur le sticker « envoyer » pour déclencher l’envoi. */
  /** Ref appelé au clic sur le sticker « micro » pour déclencher le micro. */
}

export function ChatInput({ onSend, disabled, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [voiceStatus, setVoiceStatus] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [voiceActive, setVoiceActive] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const initSpeechRecognition = useCallback(() => {
    if (typeof window === "undefined") return null;
    const SpeechRecognition =
      (window as unknown as { SpeechRecognition?: new () => SpeechRecognition })
        .SpeechRecognition ||
      (
        window as unknown as {
          webkitSpeechRecognition?: new () => SpeechRecognition;
        }
      ).webkitSpeechRecognition;
    if (!SpeechRecognition) return null;
    const rec = new SpeechRecognition();
    rec.lang = "fr-FR";
    rec.continuous = false;
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onstart = () => {
      setIsRecording(true);
      setVoiceStatus("Enregistrement en cours... Parlez maintenant.");
      setVoiceActive(true);
    };
    rec.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript.trim());
      setVoiceStatus(
        "✅ Transcription terminée. Cliquez sur « Envoyer » ou parlez à nouveau.",
      );
      setVoiceActive(true);
      setTimeout(() => {
        setVoiceStatus("");
        setVoiceActive(false);
      }, 2000);
    };
    rec.onerror = (event: SpeechRecognitionErrorEvent) => {
      let msg = "Erreur de reconnaissance vocale.";
      switch (event.error) {
        case "no-speech":
          msg = "Aucune parole détectée. Réessayez.";
          break;
        case "audio-capture":
          msg = "Aucun microphone trouvé.";
          break;
        case "not-allowed":
          msg = "Permission microphone refusée.";
          break;
        case "network":
          msg = "Erreur réseau.";
          break;
      }
      setVoiceStatus(msg);
      setVoiceActive(true);
      setTimeout(() => {
        setVoiceStatus("");
        setVoiceActive(false);
      }, 3000);
    };
    rec.onend = () => {
      setIsRecording(false);
      setVoiceStatus("");
      setVoiceActive(false);
    };
    return rec;
  }, []);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSend();
  };

  const toggleVoice = () => {
    if (!recognitionRef.current) {
      recognitionRef.current = initSpeechRecognition();
    }
    const rec = recognitionRef.current;
    if (!rec) {
      setVoiceStatus(
        "⚠️ Reconnaissance vocale non disponible. Utilisez Chrome ou Edge.",
      );
      setVoiceActive(true);
      setTimeout(() => setVoiceStatus(""), 3000);
      return;
    }
    if (isRecording) {
      rec.stop();
    } else {
      try {
        rec.start();
      } catch (err) {
        setVoiceStatus(
          "Erreur : " + (err instanceof Error ? err.message : "inconnue"),
        );
        setVoiceActive(true);
      }
    }
  };

  return (
    <>
      <SentenceInput
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Tapez votre phrase ici..."
        disabled={disabled}
      />
      <VoiceStatus $active={voiceActive}>{voiceStatus}</VoiceStatus>
      <ChatSticker7cCell
        onClick={disabled ? undefined : toggleVoice}
        role="button"
        title="Reconnaissance vocale"
        aria-label="Reconnaissance vocale"
        style={disabled ? { opacity: 0.6, cursor: "not-allowed" } : undefined}
      >
        <img src={voiceActive ? sticker7e : sticker7c} alt="" aria-hidden />
      </ChatSticker7cCell>
      <ChatSticker7dCell
        onClick={disabled || isLoading ? undefined : handleSend}
        role="button"
        title="Envoyer"
        aria-label="Envoyer"
        style={
          disabled || isLoading
            ? { opacity: 0.6, cursor: "not-allowed" }
            : undefined
        }
      >
        <img src={sticker7d} alt="" aria-hidden />
      </ChatSticker7dCell>
    </>
  );
}
