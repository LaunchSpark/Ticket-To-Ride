import React from "react";
import { CurrentPlayerSection } from "./CurrentPlayerSection";
import { LeftPlayerSection } from "./LeftPlayerSection";
import { OppositePlayerSection } from "./OppositePlayerSection";
import { RightPlayerSection } from "./RightPlayerSection";
import { SidebarSection } from "./SidebarSection";

export default function TicketToRide(): JSX.Element {
  return (
    <div className="bg-[#413e3e] flex flex-col justify-center w-full min-h-screen">
      <div className="bg-[#413e3e] overflow-hidden w-full max-w-[1440px] mx-auto">
        <div className="relative w-full h-screen">
          <div className="absolute top-0 left-[14%] w-[47%] h-[8%]">
            <OppositePlayerSection />
          </div>

          <div className="absolute top-0 right-0 w-[24%] h-full">
            <SidebarSection />
          </div>

          <div className="absolute top-[33%] left-0 w-[40%] h-[9%]">
            <LeftPlayerSection />
          </div>

          <div className="absolute top-[32%] left-[56%] w-[40%] h-[11%]">
            <RightPlayerSection />
          </div>

          <div className="absolute top-[8%] left-[14%] right-[24%] bottom-[24%] bg-[#d9d9d9]">
            {/* Game board area */}
          </div>

          <div className="absolute bottom-0 left-0 w-full h-[24%]">
            <CurrentPlayerSection />
          </div>
        </div>
      </div>
    </div>
  );
}
