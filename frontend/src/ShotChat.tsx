// src/components/ShotChat.tsx
import React, { useState } from 'react'
import { Button } from '@/components/ui/button'

type Answer = string | number

const questions: { key: keyof Payload; question: string }[] = [
  { key: 'scenario_text', question: 'Describe your shot scenario (e.g. “Tee shot from the fairway”).' },
  { key: 'distance',      question: 'Distance to the pin (yards)?' },
  { key: 'lie',           question: 'What is the lie? (fairway, rough, bunker…)' },
  { key: 'ball_pos',      question: 'Ball position: front/middle/back of the green?' },
  { key: 'elevation',     question: 'Elevation change (feet, positive or negative)?' },
  { key: 'wind_dir',      question: 'Wind direction (e.g. N, SW)?' },
  { key: 'wind_speed',    question: 'Wind speed (mph)?' },
]

interface Payload {
  user_id: string
  scenario_text: string
  distance: number
  lie: string
  ball_pos: string
  elevation: number
  wind_dir: string
  wind_speed: number
}

export function ShotChat() {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState<Partial<Payload>>({ user_id: '1' })
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<string | null>(null)

  const isDone = step >= questions.length

  const handleNext = (answer: Answer) => {
    // safe to index because this only runs when step < questions.length
    const { key } = questions[step]
    setAnswers(prev => ({ 
      ...prev, 
      [key]: typeof answer === 'number' ? answer : answer.trim() 
    }))
    setStep(prev => prev + 1)
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const fullPayload = answers as Payload
      const res = await fetch('/api/caddie/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullPayload),
      })
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
    } catch (err: any) {
      setResponse(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  // 1) Show the recommendation & reset button
  if (response) {
    return (
      <div className="p-4">
        <h2 className="text-xl font-semibold mb-2">Recommendation:</h2>
        <p className="whitespace-pre-line">{response}</p>
        <Button onClick={() => {
          setResponse(null)
          setStep(0)
          setAnswers({ user_id: '1' })
        }}>
          Start Over
        </Button>
      </div>
    )
  }

  // 2) Ask questions one‑by‑one
  if (!isDone) {
    const { key, question } = questions[step]
    return (
      <div className="p-4 space-y-4">
        <p className="text-lg">{question}</p>
        <InputPrompt
          keyType={key}
          onSubmit={handleNext}
          isNumeric={['distance', 'elevation', 'wind_speed'].includes(key)}
        />
      </div>
    )
  }

  // 3) Final “Get Recommendation” button
  return (
    <div className="p-4">
      <Button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Fetching…' : 'Get Recommendation'}
      </Button>
    </div>
  )
}

// Helper component
function InputPrompt({
  keyType,
  onSubmit,
  isNumeric,
}: {
  keyType: keyof Payload
  onSubmit: (val: Answer) => void
  isNumeric: boolean
}) {
  const [input, setInput] = useState('')
  return (
    <form onSubmit={e => {
      e.preventDefault()
      if (!input.trim()) return
      onSubmit(isNumeric ? Number(input) : input)
      setInput('')
    }}>
      <input
        type={isNumeric ? 'number' : 'text'}
        value={input}
        onChange={e => setInput(e.target.value)}
        className="border p-2 rounded w-full"
      />
      <Button type="submit" className="mt-2">Next</Button>
    </form>
  )
}
