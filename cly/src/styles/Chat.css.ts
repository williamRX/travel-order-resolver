import styled from "styled-components";

export const ChatContainer = styled.div<{ $isPortrait: boolean }>`
  flex: ${({ $isPortrait }) => ($isPortrait ? "0 0 100%" : "1 1 0")};
  width: ${({ $isPortrait }) => ($isPortrait ? "100%" : "50%")};
  height: 100%;
  display: grid;
  grid-template-columns: repeat(48, 1fr);
  grid-template-rows: repeat(32, 1fr);
  background-color: #7751fd;
  overflow: hidden;
`;

export const ChatStickerCell = styled.div`
  grid-row: 2 / 32;
  grid-column: 2 / 50;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  pointer-events: none;
  z-index: 0;
  position: relative;

  & img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
`;

export const ChatSticker6Cell = styled.div`
  grid-row: 5 / 12;
  grid-column: 38 / 50;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  pointer-events: none;
  z-index: 2;
  position: relative;

  & img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
`;

export const ChatSticker7aCell = styled.div`
  grid-row: 7 / 10;
  grid-column: 8 / 20;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  pointer-events: auto;
  z-index: 1;
  position: relative;
  cursor: pointer;

  & img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transition: transform 0.2s ease;
  }
  &:hover img {
    transform: scale(1.05);
  }
`;

export const ChatSticker7bCell = styled.div`
  grid-row: 7 / 10;
  grid-column: 23 / 35;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  pointer-events: auto;
  z-index: 1;
  position: relative;
  cursor: pointer;

  & img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transition: transform 0.2s ease;
  }
  &:hover img {
    transform: scale(1.05);
  }
`;

export const ChatSticker7cCell = styled.div`
  grid-row: 28 / 30;
  grid-column: 5 / 14;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  pointer-events: auto;
  z-index: 1;
  position: relative;
  cursor: pointer;

  & img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transition: transform 0.2s ease;
  }
  &:hover img {
    transform: scale(1.05);
  }
`;

export const ChatSticker7dCell = styled.div`
  grid-row: 27 / 31;
  grid-column: 36 / 45;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  pointer-events: auto;
  z-index: 1;
  position: relative;
  cursor: pointer;

  & img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transition: transform 0.2s ease;
  }
  &:hover img {
    transform: scale(1.05);
  }
`;

export const ChatMessagesArea = styled.div`
  grid-row: 10 / 27;
  grid-column: 5 / 47;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  position: relative;
  z-index: 1;
`;

export const ChatMessagesScroll = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgb(255, 255, 255);
`;

export const MessageWrapper = styled.div<{
  $role: "user" | "bot";
  $isError?: boolean;
  $isSuccess?: boolean;
}>`
  margin-bottom: 15px;
  display: flex;
  animation: fadeIn 0.3s ease-in;
  justify-content: ${({ $role }) =>
    $role === "user" ? "flex-end" : "flex-start"};
  .message-content {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 18px;
    word-wrap: break-word;
    background: ${({ $role, $isError, $isSuccess }) =>
      $role === "user"
        ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        : $isError
          ? "#fee"
          : $isSuccess
            ? "#efe"
            : "white"};
    color: ${({ $role, $isError, $isSuccess }) =>
      $role === "user"
        ? "white"
        : $isError
          ? "#c33"
          : $isSuccess
            ? "#3c3"
            : "#333"};
    border: 1px solid
      ${({ $role, $isError, $isSuccess }) =>
        $role === "user"
          ? "transparent"
          : $isError
            ? "#fcc"
            : $isSuccess
              ? "#cfc"
              : "#e0e0e0"};
    border-bottom-right-radius: ${({ $role }) =>
      $role === "user" ? "4px" : "18px"};
    border-bottom-left-radius: ${({ $role }) =>
      $role === "bot" ? "4px" : "18px"};
  }
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

export const WelcomeBlock = styled.div`
  text-align: center;
  color: #666;
  padding: 20px;
  h2 {
    color: #667eea;
    margin-bottom: 10px;
  }
`;

export const ExamplesBlock = styled.div`
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 10px;
  border: 1px solid #e0e0e0;
  h3 {
    color: #667eea;
    margin-bottom: 10px;
    font-size: 14px;
  }
`;

export const ExampleItem = styled.button`
  display: block;
  width: 100%;
  padding: 8px;
  margin: 5px 0;
  background: #f8f9fa;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
  text-align: left;
  &:hover {
    background: #e9ecef;
  }
`;

export const InputSection = styled.div`
  flex-shrink: 0;
  padding: 0;
  background: white;
  border-top: 1px solid #e0e0e0;
`;

export const InputRow = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

export const SentenceInput = styled.input`
  grid-row: 28 / 30;
  grid-column: 15 / 34;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  pointer-events: auto;
  z-index: 1;
  position: relative;
  cursor: pointer;
  outline: none;
  background: #fff;
  color: #000;
  border-radius: 8px;
  padding-left: 12px;
  transition: border-color 0.3s;
  &:focus {
    border-color: #667eea;
  }
`;

export const SendButton = styled.button`
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
  }
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

export const VoiceButton = styled.button<{ $recording?: boolean }>`
  padding: 12px;
  background: ${({ $recording }) =>
    $recording
      ? "linear-gradient(135deg, #dc3545 0%, #c82333 100%)"
      : "linear-gradient(135deg, #28a745 0%, #20c997 100%)"};
  color: white;
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: ${({ $recording }) =>
    $recording
      ? "0 0 20px rgba(220, 53, 69, 0.6)"
      : "0 2px 8px rgba(40, 167, 69, 0.3)"};
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
  }
  ${({ $recording }) =>
    $recording &&
    `
    animation: pulse 1.5s infinite;
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.1); }
    }
  `}
`;

export const VoiceStatus = styled.div<{ $active?: boolean }>`
  grid-row: 30 / 30;
  grid-column: 7 / 44;
  position: relative;
  z-index: 10;
  font-size: 12px;
  color: #fff;
  font-weight: ${({ $active }) => ($active ? "bold" : "normal")};
  text-align: center;
  min-height: 16px;
`;

export const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

/* Settings panel */
export const SettingsOverlay = styled.div<{ $open: boolean }>`
  display: ${({ $open }) => ($open ? "block" : "none")};
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
`;

export const SettingsPanel = styled.div<{ $open: boolean }>`
  position: fixed;
  top: 0;
  right: ${({ $open }) => ($open ? "0" : "-400px")};
  width: 380px;
  max-width: 100%;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  z-index: 1000;
  overflow-y: auto;
`;

export const SettingsPanelHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  h2 {
    margin: 0;
    font-size: 20px;
  }
`;

export const CloseSettingsButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const SettingsContent = styled.div`
  padding: 20px;
`;

export const SettingsSection = styled.div`
  margin-bottom: 25px;
  h3 {
    color: #667eea;
    margin-bottom: 15px;
    font-size: 16px;
  }
`;

export const FormGroup = styled.div`
  margin-bottom: 20px;
  label {
    display: block;
    margin-bottom: 8px;
    color: #333;
    font-weight: 500;
    font-size: 14px;
  }
  select,
  input {
    width: 100%;
    padding: 10px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 14px;
    outline: none;
    transition: border-color 0.3s;
  }
  select:focus,
  input:focus {
    border-color: #667eea;
  }
  input[type="password"] {
    font-family: monospace;
  }
  small {
    display: block;
    margin-top: 5px;
    color: #666;
    font-size: 12px;
  }
  small a {
    color: #667eea;
  }
`;

export const SaveSettingsButton = styled.button`
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s;
  &:hover {
    transform: translateY(-2px);
  }
`;

/* Result box (bot message content) */
export const ResultBox = styled.div`
  background: #f0f4ff;
  border: 2px solid #667eea;
  border-radius: 10px;
  padding: 15px;
  margin-top: 10px;
  h3 {
    color: #667eea;
    margin-bottom: 10px;
    font-size: 16px;
  }
`;

export const ResultItem = styled.div`
  margin: 8px 0;
  padding: 8px;
  background: white;
  border-radius: 5px;
  border-left: 4px solid #667eea;
  strong {
    color: #667eea;
    display: inline-block;
    min-width: 80px;
  }
`;

export const RoutePath = styled.div<{ $variant?: "sncf" | "graph" }>`
  font-size: 16px;
  padding: 12px;
  background: ${({ $variant }) =>
    $variant === "sncf"
      ? "linear-gradient(135deg, #fff5e6 0%, #ffe8cc 100%)"
      : "linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%)"};
  border-left: 4px solid
    ${({ $variant }) => ($variant === "sncf" ? "#ff9800" : "#28a745")};
  text-align: center;
  strong {
    color: #667eea;
    padding: 4px 8px;
    background: white;
    border-radius: 4px;
    margin: 0 2px;
    display: inline-block;
    min-width: auto;
  }
`;

export const RoutePathGraph = styled(RoutePath)`
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border-left-color: #4caf50;
`;

export const RouteBadge = styled.span<{
  $kind: "sncf" | "graph" | "dijkstra" | "astar";
}>`
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
  margin-left: 8px;
  vertical-align: middle;
  background: ${({ $kind }) =>
    $kind === "sncf"
      ? "#ff9800"
      : $kind === "graph"
        ? "#4caf50"
        : $kind === "dijkstra"
          ? "#2196f3"
          : "#9c27b0"};
  color: white;
`;

export const RouteSourceInfo = styled.div`
  margin-top: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 6px;
  font-size: 12px;
  color: #666;
`;

export const SncfSummary = styled.div`
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  border: 1px solid #e0e0e0;
`;

export const SncfSummaryItem = styled.div<{ $highlight?: boolean }>`
  display: flex;
  align-items: center;
  margin: 8px 0;
  padding: 8px;
  background: ${({ $highlight }) => ($highlight ? "#fff3cd" : "#f9f9f9")};
  border-radius: 4px;
  border-left: ${({ $highlight }) =>
    $highlight ? "3px solid #ff9800" : "none"};
  strong {
    min-width: 120px;
    color: #ff9800;
  }
`;

export const SncfDetailsToggle = styled.button`
  margin-top: 15px;
  padding: 10px 15px;
  background: #fff;
  border: 2px solid #ff9800;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: bold;
  color: #ff9800;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-size: 14px;
  &:hover {
    background: #fff5e6;
    border-color: #f57c00;
  }
`;

export const SncfDetailsContent = styled.div<{ $expanded: boolean }>`
  max-height: ${({ $expanded }) => ($expanded ? "1000px" : "0")};
  overflow: hidden;
  transition: max-height 0.3s ease-out;
  margin-top: 10px;
`;

export const SncfSectionDetail = styled.div<{ $type: "train" | "transfer" }>`
  padding: 10px;
  margin: 8px 0;
  background: ${({ $type }) => ($type === "train" ? "#fff5e6" : "#f5f5f5")};
  border-left: 4px solid
    ${({ $type }) => ($type === "train" ? "#ff9800" : "#999")};
  border-radius: 4px;
  font-size: 13px;
  color: ${({ $type }) => ($type === "transfer" ? "#666" : "inherit")};
  font-style: ${({ $type }) => ($type === "transfer" ? "italic" : "normal")};
`;

export const ResultHr = styled.hr`
  margin: 10px 0;
  border: none;
  border-top: 1px solid #e0e0e0;
`;

export const ResultMeta = styled.div`
  font-size: 12px;
  color: #666;
`;
