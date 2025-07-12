import React from "react";

export default function OppositePlayerSection(): JSX.Element {
  // Array of card positions with their respective left positions
  const cardPositions = [0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 629];

  // Array of card colors (these would ideally come from your design system)
  const cardColors = [
    "bg-red-500",
    "bg-blue-500",
    "bg-yellow-400",
    "bg-orange-500",
    "bg-green-500",
    "bg-purple-500",
    "bg-purple-500",
    "bg-gray-800",
    "bg-cyan-400",
    "bg-amber-500",
    "bg-emerald-500",
  ];

  return (
    <section className="relative w-full h-[66px] flex flex-col items-center">
      <div className="relative w-full max-w-[681px] h-6 mt-7 flex justify-between">
        {cardColors.map((color, index) => (
          <div
            key={`card-${index}`}
            className={`h-full w-14 ${color} flex items-center justify-center`}
            aria-label={`Card ${index + 1}`}
          />
        ))}
      </div>

      <div className="relative w-full max-w-[660px] h-3.5 mt-2 flex justify-between">
        {cardPositions.map((_, index) => (
          <div
            key={`hash-${index}`}
            className="w-2.5 h-3.5 [font-family:'Inter-Regular',Helvetica] font-normal text-white text-[15px] text-center tracking-[0] leading-[normal] whitespace-nowrap"
          >
            #
          </div>
        ))}
      </div>
    </section>
  );
}
