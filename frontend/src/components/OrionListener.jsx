import { useEffect, useState } from "react";
import DesktopListener from "./DesktopListener";
import MobileListener from "./MobileListener";

const OrionListener = () => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      const userAgent = navigator.userAgent || navigator.vendor || window.opera;
      const isMobileDevice = /android|ipad|iphone|ipod/i.test(userAgent);
      const isSmallScreen = window.innerWidth < 1024; // Increased breakpoint
      setIsMobile(isMobileDevice || isSmallScreen);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  return isMobile ? <MobileListener /> : <DesktopListener />;
};

export default OrionListener;
