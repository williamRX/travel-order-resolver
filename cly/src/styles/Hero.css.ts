import styled from "styled-components";

export const HeroContainer = styled.div<{ $isPortrait: boolean }>`
  flex: ${({ $isPortrait }) => ($isPortrait ? "0 0 100%" : "1 1 0")};
  width: ${({ $isPortrait }) => ($isPortrait ? "100%" : "50%")};
  height: 100%;
  background-color: #7751fd;
`;

export const HeroContent = styled.div`
  display: grid;
  width: 100%;
  height: 100%;
  grid-template-columns: repeat(16, 1fr);
  grid-template-rows: repeat(32, 1fr);
`;

const StickerCell = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;

  & img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
`;

export const Sticker1Cell = styled(StickerCell)`
  grid-row: 9 / 25;
  grid-column: 3 / 15;
`;

export const Sticker2Cell = styled(StickerCell)`
  grid-row: 26 / 31;
  grid-column: 3 / 7;
`;

export const Sticker3Cell = styled(StickerCell)`
  grid-row: 3 / 8;
  grid-column: 13 / 15;
`;

export const Sticker4aCell = styled(StickerCell)`
  grid-row: 4 / 7;
  grid-column: 3 / 5;
`;

export const Sticker4bCell = styled(StickerCell)`
  grid-row: 27 / 29;
  grid-column: 14 / 15;
`;
