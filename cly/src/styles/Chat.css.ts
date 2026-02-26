import styled from "styled-components";

/* Palette design (6 couleurs uniquement):
   #ffffff blanc | #000000 noir | #ffcc33 jaune | #ff9999 corail | #66ffcc turquoise | #cc99ff lavande */

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
  background: #ffffff;
  border-radius: 16px;
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
        ? "#cc99ff"
        : $isError
          ? "#ff9999"
          : $isSuccess
            ? "#cc99ff"
            : "#ffffff"};
    color: ${({ $role, $isError, $isSuccess }) =>
      $role === "user"
        ? "#ffffff"
        : $isError
          ? "#000000"
          : $isSuccess
            ? "#000000"
            : "#000000"};
    border: 2px solid #000000;
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
  color: #000000;
  padding: 20px;
  h2 {
    color: #cc99ff;
    margin-bottom: 10px;
    font-weight: bold;
  }
  p {
    color: #000000;
  }
`;

export const ExamplesBlock = styled.div`
  margin-top: 20px;
  padding: 15px;
  background: #ffffff;
  border-radius: 14px;
  border: 2px solid #000000;
  h3 {
    color: #cc99ff;
    margin-bottom: 10px;
    font-size: 14px;
    font-weight: bold;
  }
`;

export const ExampleItem = styled.button`
  display: block;
  width: 100%;
  padding: 10px 12px;
  margin: 6px 0;
  background: #ffffff;
  border: 2px solid #000000;
  border-radius: 12px;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s,
    color 0.2s;
  font-size: 14px;
  text-align: left;
  color: #000000;
  &:hover {
    background: #cc99ff;
    border-color: #000000;
    color: #ffffff;
  }
`;

export const InputSection = styled.div`
  flex-shrink: 0;
  padding: 0;
  background: #ffffff;
  border-top: 2px solid #000000;
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
  cursor: text;
  outline: none;
  background: #ffffff;
  color: #000000;
  border: 2px solid #000000;
  border-radius: 12px;
  padding: 10px 12px;
  box-sizing: border-box;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
  &:focus {
    border-color: #000000;
    box-shadow: 0 0 0 2px #000000;
  }
  &::placeholder {
    color: #000000;
    opacity: 0.5;
  }
`;

export const SendButton = styled.button`
  padding: 12px 24px;
  background: #cc99ff;
  color: #ffffff;
  border: 2px solid #000000;
  border-radius: 14px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
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
  background: ${({ $recording }) => ($recording ? "#ff9999" : "#cc99ff")};
  color: #ffffff;
  border: 2px solid #000000;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
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
  color: #ffffff;
  font-weight: ${({ $active }) => ($active ? "bold" : "normal")};
  text-align: center;
  min-height: 16px;
`;

export const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #000000;
  border-top: 3px solid #ffffff;
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

/* Settings panel - palette 6 couleurs */
export const SettingsOverlay = styled.div<{ $open: boolean }>`
  display: ${({ $open }) => ($open ? "block" : "none")};
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  z-index: 999;
`;

export const SettingsPanel = styled.div<{ $open: boolean }>`
  position: fixed;
  top: 0;
  right: ${({ $open }) => ($open ? "0" : "-400px")};
  width: 380px;
  max-width: 100%;
  height: 100vh;
  background: #ffffff;
  border-radius: 20px 0 0 20px;
  border: 4px solid #000000;
  border-right: none;
  box-shadow:
    inset 0 0 0 2px #000000,
    -4px 4px 12px rgba(0, 0, 0, 0.15);
  transition: right 0.3s ease;
  z-index: 1000;
  overflow-y: auto;
`;

export const SettingsPanelHeader = styled.div`
  background: #cc99ff;
  color: #ffffff;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 16px 0 0 0;
  text-shadow:
    0 1px 0 #000000,
    1px 0 0 #000000,
    0 -1px 0 #000000,
    -1px 0 0 #000000;
  h2 {
    margin: 0;
    font-size: 20px;
    font-weight: bold;
  }
`;

export const CloseSettingsButton = styled.button`
  background: transparent;
  border: 2px solid #000000;
  color: #ffffff;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    background 0.2s,
    transform 0.2s;
  &:hover {
    background: #ffffff;
    color: #cc99ff;
    transform: scale(1.05);
  }
`;

export const SettingsContent = styled.div`
  padding: 20px;
  background: #ffffff;
`;

export const SettingsSection = styled.div`
  margin-bottom: 25px;
  h3 {
    color: #cc99ff;
    margin-bottom: 15px;
    font-size: 16px;
    font-weight: bold;
  }
`;

export const FormGroup = styled.div`
  margin-bottom: 20px;
  label {
    display: block;
    margin-bottom: 8px;
    color: #000000;
    font-weight: 600;
    font-size: 14px;
  }
  select,
  input {
    box-sizing: border-box;
    width: 100%;
    max-width: 100%;
    padding: 10px 12px;
    border: 2px solid #000000;
    border-radius: 12px;
    font-size: 14px;
    outline: none;
    background: #ffffff;
    color: #000000;
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
  }
  select:focus,
  input:focus {
    border-color: #000000;
    box-shadow: 0 0 0 2px #000000;
  }
  input[type="password"] {
    font-family: monospace;
  }
  small {
    display: block;
    margin-top: 6px;
    color: #000000;
    font-size: 12px;
  }
  small a {
    color: #cc99ff;
    font-weight: 600;
    text-decoration: underline;
  }
  small a:hover {
    color: #cc99ff;
  }
`;

export const SaveSettingsButton = styled.button`
  width: 100%;
  padding: 14px;
  background: #cc99ff;
  color: #ffffff;
  border: 2px solid #000000;
  border-radius: 14px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  box-shadow: 0 2px 0 rgba(0, 0, 0, 0.1);
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
  &:active {
    transform: translateY(0);
  }
`;

/* Result box - palette 6 couleurs */
export const ResultBox = styled.div`
  background: #ffffff;
  border: 2px solid #000000;
  border-radius: 14px;
  padding: 15px;
  margin-top: 10px;
  h3 {
    color: #cc99ff;
    margin-bottom: 10px;
    font-size: 16px;
    font-weight: bold;
  }
`;

export const ResultItem = styled.div`
  margin: 8px 0;
  padding: 10px 12px;
  background: #ffffff;
  border-radius: 10px;
  border-left: 4px solid #000000;
  strong {
    color: #cc99ff;
    display: inline-block;
    min-width: 80px;
  }
`;

export const RoutePath = styled.div<{ $variant?: "sncf" | "graph" }>`
  font-size: 16px;
  padding: 12px;
  background: ${({ $variant }) =>
    $variant === "sncf" ? "#ffcc33" : "#cc99ff"};
  border: 2px solid #000000;
  border-radius: 12px;
  border-left: 4px solid #000000;
  text-align: center;
  strong {
    color: #000000;
    padding: 4px 8px;
    background: #ffffff;
    border-radius: 6px;
    margin: 0 2px;
    display: inline-block;
    min-width: auto;
    border: 2px solid #000000;
  }
`;

export const RoutePathGraph = styled(RoutePath)`
  background: #cc99ff;
  border-left-color: #000000;
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
  border: 2px solid #000000;
  background: ${({ $kind }) =>
    $kind === "sncf"
      ? "#ffcc33"
      : $kind === "graph"
        ? "#cc99ff"
        : $kind === "dijkstra"
          ? "#cc99ff"
          : "#cc99ff"};
  color: #000000;
`;

export const RouteSourceInfo = styled.div`
  margin-top: 8px;
  padding: 10px;
  background: #ffffff;
  border-radius: 10px;
  border: 2px solid #000000;
  font-size: 12px;
  color: #000000;
`;

export const SncfSummary = styled.div`
  background: #ffffff;
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 10px;
  border: 2px solid #000000;
`;

export const SncfSummaryItem = styled.div<{ $highlight?: boolean }>`
  display: flex;
  align-items: center;
  margin: 8px 0;
  padding: 8px;
  background: ${({ $highlight }) => ($highlight ? "#ffcc33" : "#ffffff")};
  border-radius: 8px;
  border-left: ${({ $highlight }) =>
    $highlight ? "4px solid #000000" : "3px solid #000000"};
  strong {
    min-width: 120px;
    color: #000000;
  }
`;

export const SncfDetailsToggle = styled.button`
  margin-top: 15px;
  padding: 10px 15px;
  background: #cc99ff;
  border: 2px solid #000000;
  border-radius: 12px;
  cursor: pointer;
  transition:
    background 0.2s,
    transform 0.2s;
  font-weight: bold;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-size: 14px;
  &:hover {
    background: #ffffff;
    color: #cc99ff;
    border-color: #000000;
    transform: translateY(-1px);
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
  background: ${({ $type }) => ($type === "train" ? "#ffcc33" : "#ffffff")};
  border: 2px solid #000000;
  border-left: 4px solid #000000;
  border-radius: 8px;
  font-size: 13px;
  color: #000000;
  font-style: ${({ $type }) => ($type === "transfer" ? "italic" : "normal")};
`;

export const ResultHr = styled.hr`
  margin: 10px 0;
  border: none;
  border-top: 2px solid #000000;
`;

export const ResultMeta = styled.div`
  font-size: 12px;
  color: #000000;
  strong {
    color: #cc99ff;
  }
`;
