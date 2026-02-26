import { MessageWrapper } from "../../styles/Chat.css";
import type { ChatMessage as ChatMessageType } from "./types";
import { ChatResult } from "./ChatResult";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isStructuredSuccess =
    message.role === "bot" && message.isSuccess && message.data && message.data.valid;

  return (
    <MessageWrapper
      $role={message.role}
      $isError={message.isError}
      $isSuccess={message.isSuccess}
    >
      <div className="message-content">
        {isStructuredSuccess && message.data ? (
          <ChatResult data={message.data} />
        ) : (
          <span dangerouslySetInnerHTML={{ __html: message.content }} />
        )}
      </div>
    </MessageWrapper>
  );
}
