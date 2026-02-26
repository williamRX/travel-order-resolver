import styled from "styled-components";

export const LayoutContainer = styled.div<{ $isPortrait: boolean }>`
  display: flex;
  flex-direction: ${({ $isPortrait }) => ($isPortrait ? "column" : "row")};
  width: 100%;
  height: 100%;
  overflow-y: ${({ $isPortrait }) => ($isPortrait ? "scroll" : "hidden")};
  overflow-x: hidden;
`;
