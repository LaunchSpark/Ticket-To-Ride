import { Card, CardContent } from "@/components/ui/card";
import React from "react";

const colorSquares = [
  { bg: "bg-[#c83c2b]", left: "left-0" },
  { bg: "bg-[#0ca9dd]", left: "left-[101px]" },
  { bg: "bg-[#efe748]", left: "left-[202px]" },
  { bg: "bg-[#f88411]", left: "left-[303px]" },
  { bg: "bg-[#94bf48]", left: "left-[405px]" },
  { bg: "bg-[#d788ac]", left: "left-[507px]" },
  { bg: "bg-white", left: "left-[609px]" },
  { bg: "bg-black", left: "left-[710px]", border: "border-[3px] border-solid" },
  { bg: "bg-[#00e9ff]", left: "left-[810px]" },
];

const hashSymbols = [
  { left: "left-0" },
  { left: "left-[101px]" },
  { left: "left-[203px]" },
  { left: "left-[304px]" },
  { left: "left-[405px]" },
  { left: "left-[507px]" },
  { left: "left-[608px]" },
  { left: "left-[710px]" },
  { left: "left-[810px]" },
];

const gameCards = [
  { top: "top-0", bgImage: "bg-[url(/vector-3.svg)]" },
  { top: "top-11", bgImage: "bg-[url(/vector-2.svg)]" },
  { top: "top-[87px]", bgImage: "bg-[url(/image.svg)]" },
  { top: "top-[131px]", bgImage: "bg-[url(/vector.svg)]" },
];

export default function CurrentPlayerSection(): JSX.Element {
  return (
    <section className="w-full relative">
      <div className="relative h-[238px]">
        <div className="flex flex-col gap-[29px]">
          <div className="w-[325px] h-[30px]">
            <div className="relative w-[324px] h-[31px] bg-[url(/name-card-2.svg)] bg-[100%_100%]">
              <div className="absolute w-[267px] h-[30px] top-px left-[13px] [font-family:'Impact-Regular',Helvetica] font-normal text-black text-3xl tracking-[0] leading-[normal] whitespace-nowrap">
                Placeholder name
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <Card className="flex-1 max-w-[1102px] h-[178px] bg-[#dee1f1] border border-solid border-black shadow-[3px_0px_4px_3px_#00000040]">
              <CardContent className="relative p-0 h-full">
                <div className="absolute w-[844px] h-[29px] top-[93px] left-[70px]">
                  {hashSymbols.map((hash, index) => (
                    <div
                      key={`hash-${index}`}
                      className={`absolute w-4 h-[29px] top-0 ${hash.left} [font-family:'Inter-Regular',Helvetica] font-normal text-black text-3xl text-center tracking-[0] leading-[normal] whitespace-nowrap`}
                    >
                      #
                    </div>
                  ))}
                </div>

                <div className="absolute w-[899px] h-[82px] top-[127px] left-[33px]">
                  {colorSquares.map((square, index) => (
                    <div
                      key={`square-${index}`}
                      className={`absolute w-[${index === 1 || index === 2 || index === 7 ? "88" : index === 0 || index === 4 || index === 8 ? "89" : "90"}px] h-[82px] top-0 ${square.left} ${square.bg} ${square.border || "border-[3px] border-solid border-black"}`}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="w-[354px] h-44">
              <div className="relative w-[360px] h-44">
                {gameCards.map((card, index) => (
                  <div
                    key={`card-${index}`}
                    className={`${card.top} absolute w-[360px] h-[45px] left-0`}
                  >
                    <div
                      className={`relative w-[354px] h-[45px] ${card.bgImage} bg-[100%_100%]`}
                    >
                      <div className="top-[11px] left-[15px] absolute w-[105px] h-6 [font-family:'Impact-Regular',Helvetica] font-normal text-[#763d07] text-[27px] tracking-[0] leading-[normal] whitespace-nowrap">
                        MOSCOW
                      </div>
                      <div className="top-2.5 left-[231px] text-right absolute w-[105px] h-6 [font-family:'Impact-Regular',Helvetica] font-normal text-[#763d07] text-[27px] tracking-[0] leading-[normal] whitespace-nowrap">
                        MOSCOW
                      </div>
                      <div className="absolute w-10 h-8 top-[3px] left-[156px] [font-family:'Impact-Regular',Helvetica] font-normal text-[#362301] text-[35px] text-center tracking-[0] leading-[normal] whitespace-nowrap">
                        23
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
