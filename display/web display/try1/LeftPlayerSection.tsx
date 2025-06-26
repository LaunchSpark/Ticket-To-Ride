import React from "react";

const LeftPlayerSection = (): JSX.Element => {
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
    <section className="flex items-center justify-center rotate-[-90deg] w-full h-auto">
      <div className="relative flex items-center gap-4">
        <img className="w-[35px] h-auto rotate-[90deg]" alt="Cards" src="" />

        <div className="relative flex items-center w-[557px] h-4">
          {cardPositions.map((position, index) => (
            <div
              key={`card-${index}`}
              className={`absolute w-2 h-4 top-0 ${position.left} [font-family:'Inter-Regular',Helvetica] font-normal text-white text-[15px] text-center tracking-[0] leading-[normal] whitespace-nowrap`}
            >
              #
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default LeftPlayerSection;
