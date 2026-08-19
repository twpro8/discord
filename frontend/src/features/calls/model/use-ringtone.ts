// third party
import { useEffect } from "react";

const RINGTONE_SRC = "/sounds/ringtone.mp3";

export function useRingtone(active: boolean) {
  useEffect(() => {
    if (!active) return;

    const audio = new Audio(RINGTONE_SRC);
    audio.loop = true;
    void audio.play().catch(() => {});

    return () => {
      audio.pause();
      audio.currentTime = 0;
    };
  }, [active]);
}
