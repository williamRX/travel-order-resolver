import {
  HeroContainer,
  HeroContent,
  Sticker1Cell,
  Sticker2Cell,
  Sticker3Cell,
  Sticker4aCell,
  Sticker4bCell,
} from "../styles/Hero.css";
import { useIsPortrait } from "../hooks/useIsPortrait";
import sticker1 from "../assets/sticker1.svg";
import sticker2 from "../assets/sticker2.svg";
import sticker3 from "../assets/sticker3.svg";
import sticker4a from "../assets/sticker4a.svg";
import sticker4b from "../assets/sticker4b.svg";

export const Hero = () => {
  const isPortrait = useIsPortrait();
  return (
    <HeroContainer $isPortrait={isPortrait}>
      <HeroContent>
        <Sticker1Cell>
          <img src={sticker1} alt="Title sticker" />
        </Sticker1Cell>
        <Sticker2Cell>
          <img src={sticker2} alt="Train sticker" />
        </Sticker2Cell>
        <Sticker3Cell>
          <img src={sticker3} alt="Pin sticker" />
        </Sticker3Cell>
        <Sticker4aCell>
          <img src={sticker4a} alt="Star sticker" />
        </Sticker4aCell>
        <Sticker4bCell>
          <img src={sticker4b} alt="Small star sticker" />
        </Sticker4bCell>
      </HeroContent>
    </HeroContainer>
  );
};
