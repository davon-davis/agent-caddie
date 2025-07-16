import { useEffect, useRef, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { ShotChat } from './ShotChat'


function App() {
  const [response, setResponse] = useState("")
  const didFetch = useRef(false)

  const payload = {
    user_id: "1",
    scenario_text: "Tee shot from the fairway, ball just off the green",
    distance: 140,
    lie: "fairway",
    ball_pos: "front",
    elevation: 0,
    wind_dir: "NE",
    wind_speed: 8
  };
  
  const getRecommendation = async () => {
    const res = await fetch(`/api/caddie/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(res.statusText);
  
    const reader  = res.body!.getReader();
    const decoder = new TextDecoder();
    let done  = false;
    setResponse(""); 
  
    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      if (!value) continue;
  
      const chunkText = decoder.decode(value, { stream: true });
      for (const char of chunkText) {
        setResponse((r) => r + char);
        await new Promise((resolve) => setTimeout(resolve, 20));
      }
    }
  }

  return (
    <div>
      {/* <h1>V-Caddie</h1>
      <div>
        <Button onClick={getRecommendation}>
          Get Recommendation
        </Button>
      </div>
      <div className="card">
        <p>{response}</p>
      </div> */}
      <ShotChat />
    </div>
  )
}

export default App
