import { Card, CardContent } from "@/components/ui/card";
import React from "react";

const gameScores = [
  {
    nameCardSrc: "",
    scoreCardSrc: "",
    name: "Placeholder name",
    score: "42",
  },
  {
    nameCardSrc: "",
    scoreCardSrc: "",
    name: "Placeholder name",
    score: "42",
  },
  {
    nameCardSrc: "",
    scoreCardSrc: "",
    name: "Placeholder name",
    score: "42",
  },
  {
    nameCardSrc: "",
    scoreCardSrc: "",
    name: "Placeholder name",
    score: "42",
  },
];

const matchStats = [
  {
    playerSrc: "",
    playerName: "Player 1",
    avgScore: "42",
  },
  {
    playerSrc: "",
    playerName: "Player 2",
    avgScore: "42",
  },
  {
    playerSrc: "",
    playerName: "Player 3",
    avgScore: "42",
  },
  {
    playerSrc: "",
    playerName: "Player 4",
    avgScore: "42",
  },
];

export const SidebarSection = (): JSX.Element => {
  return (
    <div className="w-full h-full">
      <div className="relative w-full h-full bg-[#313347] border-2 border-solid border-black shadow-[0px_4px_4px_3px_#00000040]">
        <div className="flex flex-col h-full">
          <div className="flex-none">
            <div className="pt-0 pb-4">
              <div className="text-center py-4">
                <div className="[font-family:'Impact-Regular',Helvetica] font-normal text-white text-3xl tracking-[0] leading-[normal]">
                  This Game
                </div>
              </div>

              <div className="space-y-0">
                {gameScores.map((player, index) => (
                  <div
                    key={`game-score-${index}`}
                    className="relative h-[52px]"
                  >
                    <div className="flex items-center h-full">
                      <img
                        className="w-[287px] h-[52px]"
                        alt="Name card"
                        src=""
                      />
                      <img
                        className="w-[102px] h-[52px] -ml-[38px]"
                        alt="Score card"
                        src=""
                      />
                    </div>

                    <div className="absolute top-0 left-3 w-[237px] h-[51px] flex items-center [font-family:'Impact-Regular',Helvetica] font-normal text-black text-3xl tracking-[0] leading-[normal]">
                      {player.name}
                    </div>

                    <div className="absolute top-0 right-[19px] w-[82px] h-[51px] flex items-center justify-center [font-family:'Impact-Regular',Helvetica] font-normal text-white text-[45px] tracking-[0] leading-[normal] whitespace-nowrap">
                      {player.score}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex-1 pt-8">
            <div className="text-center pb-6">
              <div className="[font-family:'Impact-Regular',Helvetica] font-normal text-white text-[35px] tracking-[0] leading-[normal]">
                MATCH&nbsp;&nbsp;STATS
              </div>
            </div>

            <div className="px-3 space-y-3">
              {matchStats.map((player, index) => (
                <Card
                  key={`match-stat-${index}`}
                  className="bg-transparent border-0 p-0"
                >
                  <CardContent className="p-0">
                    <img className="w-full h-[79px]" alt="Player" src="" />
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
