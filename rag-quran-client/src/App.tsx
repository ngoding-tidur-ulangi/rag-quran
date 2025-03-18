import React, { useRef, useState } from "react"
import { Textarea } from "./components/ui/textarea"
import { ScrollArea } from "@radix-ui/react-scroll-area"
import { ArrowUp, BookOpenText, LoaderCircle } from "lucide-react"
import clsx from "clsx"
import { ScrollBar } from "./components/ui/scroll-area"
import Markdown from 'react-markdown'
import remarkGfm from "remark-gfm"
import { HoverCard, HoverCardContent, HoverCardTrigger } from "./components/ui/hover-card"

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [history, setHistory] = useState<{ messager: string, message: string, resources: { ayah_en: string, first_ayah_no_surah: number, last_ayah_no_surah: number, surah_no: number }[] }[]>([])

  const [message, setMessage] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = async () => {
    setIsLoading(true)
    const updatedHistory = [
      ...history,
      { messager: "USER", message: message, resources: [] },
    ];

    setHistory(updatedHistory);

    setMessage("");

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/rag`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: message,
          history: updatedHistory,
        }),
      });

      const data = await response.json();

      setHistory((prev) => [
        ...prev,
        {
          messager: "AGENT",
          message: data.response,
          resources: data.response === "No relevant documents found." ? [] : data.retrieved_docs,
        },
      ]);
    } catch (error) {
      console.error("Fetch error:", error);
    }
    setIsLoading(false)
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  return (
    <>
      <div className="bg-neutral-800 w-screen h-screen flex flex-col items-center justify-top text-neutral-50 text-base/7">
        <ScrollArea className={clsx("w-full flex justify-center custom-scrollbar overflow-auto", history.length !== 0 ? "h-[90vh]" : "h-[30vh]")}>
          <div className="w-3xl flex flex-col gap-4 my-8">
            {history.map((item, index) => (
              <div className={clsx(item.messager == "USER" && "flex justify-end")} key={index}>
                <div className={clsx("w-xl prose prose-sm", item.messager == "USER" && "bg-neutral-700 p-2 rounded-xl")}>
                  <Markdown remarkPlugins={[remarkGfm]}>
                    {item.message}
                  </Markdown>
                  <div className="flex max-w-3xl flex-wrap gap-2">
                    {item.resources.map((resource, index) => (
                      <HoverCard>
                        <HoverCardTrigger asChild>
                          <span key={index} className="block bg-neutral-500 px-2 py-1 rounded-full text-xs mr-2 min-w-max hover:cursor-pointer">
                            Q.S {surahs.find(surah => surah.number === resource.surah_no)?.name} {resource.first_ayah_no_surah === resource.last_ayah_no_surah ? resource.first_ayah_no_surah : `${resource.first_ayah_no_surah}-${resource.last_ayah_no_surah}`}
                          </span>
                        </HoverCardTrigger>
                        <HoverCardContent className="w-lg border-none bg-neutral-700 text-neutral-50">
                          <h4 className="font-bold">Q.S {surahs.find(surah => surah.number === resource.surah_no)?.name} {resource.first_ayah_no_surah === resource.last_ayah_no_surah ? resource.first_ayah_no_surah : `${resource.first_ayah_no_surah}-${resource.last_ayah_no_surah}`}</h4>
                          <p>{resource.ayah_en}</p>
                        </HoverCardContent>
                      </HoverCard>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <ScrollBar orientation="vertical" />
        </ScrollArea>
        <div>
          {
            history.length === 0 &&
            <div className="text-center flex flex-col items-center gap-2 mb-4">
              <BookOpenText size={64} color="currentColor" />
              <div className="text-2xl font-medium">What do you want to know from the Quran?</div>
            </div>
          }
          <div className="flex items-end bg-neutral-700 rounded-3xl shadow-sm p-2 w-3xl mb-4">
            <Textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => {
                setMessage(e.target.value);
                adjustTextareaHeight();
              }}
              onKeyDown={handleKeyDown}
              placeholder="Type a message... (Shift+Enter for new line)"
              className="border-none !text-base placeholder:text-gray-300 focus:border-transparent focus:outline-none focus:ring-0 focus-visible:ring-0 focus-visible:outline-none resize-none overflow-hidden max-h-48 bg-transparent"
            />
            <button onClick={handleSend} className="ml-2 p-2 cursor-pointer rounded-full bg-neutral-50 hover:bg-neutral-300 disabled:cursor-default disabled:hover:bg-neutral-50" disabled={isLoading || message === ""}>
              {isLoading ? <LoaderCircle className="animate-spin" size={24} color="black" /> : <ArrowUp size={24} color="black" />}
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

export default App

const surahs = [
  { number: 1, name: "Al-Fatihah" },
  { number: 2, name: "Al-Baqarah" },
  { number: 3, name: "Aal-E-Imran" },
  { number: 4, name: "An-Nisa" },
  { number: 5, name: "Al-Maidah" },
  { number: 6, name: "Al-An'am" },
  { number: 7, name: "Al-A'raf" },
  { number: 8, name: "Al-Anfal" },
  { number: 9, name: "At-Tawbah" },
  { number: 10, name: "Yunus" },
  { number: 11, name: "Hud" },
  { number: 12, name: "Yusuf" },
  { number: 13, name: "Ar-Ra'd" },
  { number: 14, name: "Ibrahim" },
  { number: 15, name: "Al-Hijr" },
  { number: 16, name: "An-Nahl" },
  { number: 17, name: "Al-Isra" },
  { number: 18, name: "Al-Kahf" },
  { number: 19, name: "Maryam" },
  { number: 20, name: "Taha" },
  { number: 21, name: "Al-Anbiya" },
  { number: 22, name: "Al-Hajj" },
  { number: 23, name: "Al-Mu’minun" },
  { number: 24, name: "An-Nur" },
  { number: 25, name: "Al-Furqan" },
  { number: 26, name: "Ash-Shu'ara" },
  { number: 27, name: "An-Naml" },
  { number: 28, name: "Al-Qasas" },
  { number: 29, name: "Al-Ankabut" },
  { number: 30, name: "Ar-Rum" },
  { number: 31, name: "Luqman" },
  { number: 32, name: "As-Sajdah" },
  { number: 33, name: "Al-Ahzab" },
  { number: 34, name: "Saba" },
  { number: 35, name: "Fatir" },
  { number: 36, name: "Ya-Sin" },
  { number: 37, name: "As-Saffat" },
  { number: 38, name: "Sad" },
  { number: 39, name: "Az-Zumar" },
  { number: 40, name: "Ghafir" },
  { number: 41, name: "Fussilat" },
  { number: 42, name: "Ash-Shura" },
  { number: 43, name: "Az-Zukhruf" },
  { number: 44, name: "Ad-Dukhan" },
  { number: 45, name: "Al-Jathiya" },
  { number: 46, name: "Al-Ahqaf" },
  { number: 47, name: "Muhammad" },
  { number: 48, name: "Al-Fath" },
  { number: 49, name: "Al-Hujurat" },
  { number: 50, name: "Qaf" },
  { number: 51, name: "Adh-Dhariyat" },
  { number: 52, name: "At-Tur" },
  { number: 53, name: "An-Najm" },
  { number: 54, name: "Al-Qamar" },
  { number: 55, name: "Ar-Rahman" },
  { number: 56, name: "Al-Waqia" },
  { number: 57, name: "Al-Hadid" },
  { number: 58, name: "Al-Mujadila" },
  { number: 59, name: "Al-Hashr" },
  { number: 60, name: "Al-Mumtahina" },
  { number: 61, name: "As-Saff" },
  { number: 62, name: "Al-Jumu'a" },
  { number: 63, name: "Al-Munafiqun" },
  { number: 64, name: "At-Taghabun" },
  { number: 65, name: "At-Talaq" },
  { number: 66, name: "At-Tahrim" },
  { number: 67, name: "Al-Mulk" },
  { number: 68, name: "Al-Qalam" },
  { number: 69, name: "Al-Haqqa" },
  { number: 70, name: "Al-Ma'arij" },
  { number: 71, name: "Nuh" },
  { number: 72, name: "Al-Jinn" },
  { number: 73, name: "Al-Muzzammil" },
  { number: 74, name: "Al-Muddathir" },
  { number: 75, name: "Al-Qiyama" },
  { number: 76, name: "Al-Insan" },
  { number: 77, name: "Al-Mursalat" },
  { number: 78, name: "An-Naba" },
  { number: 79, name: "An-Nazi'at" },
  { number: 80, name: "Abasa" },
  { number: 81, name: "At-Takwir" },
  { number: 82, name: "Al-Infitar" },
  { number: 83, name: "Al-Mutaffifin" },
  { number: 84, name: "Al-Inshiqaq" },
  { number: 85, name: "Al-Buruj" },
  { number: 86, name: "At-Tariq" },
  { number: 87, name: "Al-A'la" },
  { number: 88, name: "Al-Ghashiya" },
  { number: 89, name: "Al-Fajr" },
  { number: 90, name: "Al-Balad" },
  { number: 91, name: "Ash-Shams" },
  { number: 92, name: "Al-Lail" },
  { number: 93, name: "Ad-Duhaa" },
  { number: 94, name: "Ash-Sharh" },
  { number: 95, name: "At-Tin" },
  { number: 96, name: "Al-Alaq" },
  { number: 97, name: "Al-Qadr" },
  { number: 98, name: "Al-Bayyina" },
  { number: 99, name: "Az-Zalzala" },
  { number: 100, name: "Al-Adiyat" },
  { number: 101, name: "Al-Qaria" },
  { number: 102, name: "At-Takathur" },
  { number: 103, name: "Al-Asr" },
  { number: 104, name: "Al-Humaza" },
  { number: 105, name: "Al-Fil" },
  { number: 106, name: "Quraish" },
  { number: 107, name: "Al-Ma'un" },
  { number: 108, name: "Al-Kawthar" },
  { number: 109, name: "Al-Kafiroon" },
  { number: 110, name: "An-Nasr" },
  { number: 111, name: "Al-Masad" },
  { number: 112, name: "Al-Ikhlas" },
  { number: 113, name: "Al-Falaq" },
  { number: 114, name: "An-Nas" }
];
