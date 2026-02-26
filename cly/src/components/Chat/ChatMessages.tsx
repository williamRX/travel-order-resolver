import { useRef, useEffect } from "react";
import { ChatMessagesScroll, WelcomeBlock, ExamplesBlock, ExampleItem } from "../../styles/Chat.css";
import { ChatMessage } from "./ChatMessage";
import type { ChatMessage as ChatMessageType } from "./types";

const WELCOME_EXAMPLES = [
  "Je vais de Paris à Lyon",
  "Billet Marseille Nice demain",
  "Trajet la gare de Lille vers l'aéroport de Lyon",
] as const;

interface ChatMessagesProps {
  messages: ChatMessageType[];
  onExampleClick: (text: string) => void;
}

export function ChatMessages({ messages, onExampleClick }: ChatMessagesProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const showWelcome = messages.length === 0;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <ChatMessagesScroll ref={scrollRef}>
      {showWelcome && (
        <WelcomeBlock>
          <h2>Bienvenue ! 👋</h2>
          <p>Je peux extraire les destinations de départ et d&apos;arrivée depuis vos phrases.</p>
          <ExamplesBlock>
            <h3>Exemples de phrases valides :</h3>
            {WELCOME_EXAMPLES.map((text) => (
              <ExampleItem key={text} type="button" onClick={() => onExampleClick(text)}>
                &quot;{text}&quot;
              </ExampleItem>
            ))}
          </ExamplesBlock>
        </WelcomeBlock>
      )}
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}
    </ChatMessagesScroll>
  );
}
