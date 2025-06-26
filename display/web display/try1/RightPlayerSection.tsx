import React from "react";

const RightPlayerSection = (): JSX.Element => {
  const cardPositions = [
    { left: "left-0" },
    { left: "left-[50px]" },
    { left: "left-[101px]" },
    { left: "left-[151px]" },
    { left: "left-[201px]" },
    { left: "left-[251px]" },
    { left: "left-[302px]" },
    { left: "left-[352px]" },
    { left: "left-[402px]" },
    { left: "left-[453px]" },
    { left: "left-[527px]" },
  ];

  return (
    <div className="w-full h-[87px] rotate-90 relative">
      <div className="relative w-[575px] h-[87px]">
        <img
          className="absolute w-[69px] h-[571px] top-[-251px] left-[251px] rotate-[-90deg]"
          alt="Cards"
          src=""
        />

        <div className="absolute w-[557px] h-[18px] top-[69px] left-[18px]">
          {cardPositions.map((position, index) => (
            <div
              key={index}
              className={`absolute w-2 h-[18px] top-0 ${position.left} [font-family:'Inter-Regular',Helvetica] font-normal text-white text-[15px] text-center tracking-[0] leading-[normal]`}
            >
              #
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RightPlayerSection;
