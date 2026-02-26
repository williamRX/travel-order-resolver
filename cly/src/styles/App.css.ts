import styled from "styled-components";

export const AppContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100vw;
  background-color: #7751fd;
`;

export const AppContent = styled.div<{ $isPortrait: boolean }>`
  box-sizing: content-box;
  aspect-ratio: ${({ $isPortrait }) => ($isPortrait ? "9 / 16" : "16 / 9")};
  width: ${({ $isPortrait }) =>
    $isPortrait
      ? "min(100%, calc((100vh) * 9 / 16))"
      : "min(100%, calc((100vh) * 16 / 9))"};
  background-color: red;
`;
